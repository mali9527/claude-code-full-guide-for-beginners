"""Offline illustration production packs, immutable candidates and source-aware checks.

The CLI never calls an image provider. A generation tool consumes prompt.txt; import
records what actually ran, and selection requires a review of those exact bytes.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shutil
import struct
import zlib
from functools import lru_cache
from .common import StudioError, atomic_write, load_yaml, dump_yaml, safe_path, git_commit

MANAGED = re.compile(r'<!-- diagram: (FIG-\d+) -->[\s\S]*?<!-- /diagram: \1 -->')

def digest(value):
    if not isinstance(value, bytes):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(value).hexdigest()

def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise StudioError(str(exc))

def save_json(path, value):
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def local(root, relative):
    root = Path(root).resolve()
    path = safe_path(root, relative)
    if '.git' in path.relative_to(root).parts or path.resolve() == root.resolve():
        raise StudioError('不能使用 Git 内部或根目录')
    return path

def png_info(path):
    data = Path(path).read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise StudioError('候选必须为真实 PNG：' + str(path))
    pos, chunks, compressed = 8, [], bytearray()
    width = height = None
    pixel_format = None
    transparency_key = False
    while pos + 12 <= len(data):
        length = struct.unpack('>I', data[pos:pos+4])[0]
        kind = data[pos+4:pos+8]; body = data[pos+8:pos+8+length]
        end = pos + 12 + length
        if end > len(data) or (zlib.crc32(kind + body) & 0xffffffff) != struct.unpack('>I', data[end-4:end])[0]:
            raise StudioError('PNG 数据损坏：' + str(path))
        chunks.append(kind)
        if kind == b'IHDR':
            if length != 13: raise StudioError('PNG IHDR 无效')
            width, height = struct.unpack('>II', body[:8])
            pixel_format = tuple(body[8:13])
        if kind == b'IDAT': compressed.extend(body)
        if kind == b'tRNS': transparency_key = True
        pos = end
        if kind == b'IEND': break
    if not chunks or chunks[0] != b'IHDR' or chunks[-1] != b'IEND' or pos != len(data) or not width or not height:
        raise StudioError('PNG 结构不完整')
    try:
        pixels = zlib.decompress(compressed)
        if not pixels: raise ValueError('empty')
    except (zlib.error, ValueError): raise StudioError('PNG 像素数据不可解码')
    depth, color, compression, filtering, interlace = pixel_format
    if transparency_key: raise StudioError('方格纸插图不能声明透明色')
    if depth != 8 or interlace != 0 or color not in (0, 2, 4, 6) or compression or filtering:
        raise StudioError('需使用 8 位非隔行灰度或 RGB PNG 以核对黑白与不透明性')
    metrics = pixel_metrics(bytes(pixels), width, height, color)
    return {'format': 'PNG', 'opaque': True, **metrics, 'width': width, 'height': height, 'bytes': len(data), 'sha256': digest(data)}

@lru_cache(maxsize=48)
def pixel_metrics(pixels, width, height, color):
    """Read-only decode; never recolor or flatten an image to make it pass."""
    stride = {0: 1, 2: 3, 4: 2, 6: 4}[color]
    line = width * stride
    if len(pixels) != height * (line + 1):
        raise StudioError('PNG 像素长度无效')
    previous = bytearray(line)
    max_delta = chromatic_noise = 0
    for y in range(height):
        offset = y * (line + 1)
        method = pixels[offset]
        current = bytearray(pixels[offset + 1:offset + 1 + line])
        if method not in range(5): raise StudioError('PNG 过滤类型无效')
        if method:
            for i in range(line):
                left = current[i-stride] if i >= stride else 0
                above = previous[i]
                diagonal = previous[i-stride] if i >= stride else 0
                if method == 1: predictor = left
                elif method == 2: predictor = above
                elif method == 3: predictor = (left+above)//2
                else:
                    value = left+above-diagonal
                    dl, da, dd = abs(value-left), abs(value-above), abs(value-diagonal)
                    predictor = left if dl <= da and dl <= dd else above if da <= dd else diagonal
                current[i] = (current[i] + predictor) & 255
        if color in (4, 6) and any(a != 255 for a in current[stride-1::stride]):
            raise StudioError('透明背景不允许入稿：必须使用不透明白色细方格纸')
        if color in (2, 6):
            for r, g, b in zip(current[0::stride], current[1::stride], current[2::stride]):
                delta = max(r, g, b) - min(r, g, b)
                max_delta = max(max_delta, delta)
                if delta > 24: raise StudioError('彩色像素不允许入稿：必须是黑白中性笔手绘')
                chromatic_noise += delta > 12
        previous = current
    fraction = chromatic_noise / (width * height)
    if fraction > 0.005:
        raise StudioError('整图存在色偏：只允许中性灰纸底和黑色墨迹')
    return {'monochrome': True, 'max_channel_delta': max_delta,
            'chroma_noise_fraction': round(fraction, 8), 'color_check': 'neutral-gray-v1'}

def figures(root):
    root = Path(root).resolve()
    book = load_yaml(root / 'book.yaml')
    return book, [d for d in book.get('diagrams', []) if isinstance(d, dict) and d.get('type') == 'illustration']

def resolve(root, figure_id):
    root = Path(root).resolve()
    book, records = figures(root)
    matches = [d for d in records if d.get('id') == figure_id]
    if len(matches) != 1: raise StudioError('插图必须唯一登记：' + str(figure_id))
    record = matches[0]
    spec = local(root, record.get('spec'))
    brief = load_yaml(spec)
    if not isinstance(brief, dict) or brief.get('schema_version') != 1:
        raise StudioError(str(spec) + ': 不支持的 brief 格式')
    for field in ('title', 'reader_question', 'takeaway', 'composition', 'content_guard', 'style', 'source_sections', 'labels', 'placement'):
        if not brief.get(field): raise StudioError(str(spec) + ': 缺少 ' + field)
    units = [u for u in book['units'] if u['id'] == record['unit']]
    if len(units) != 1: raise StudioError('所属单元不唯一')
    return book, record, brief, spec.parent, units[0]

def section(text, heading):
    text = MANAGED.sub('', text)
    text = re.sub(r'<!-- studio:nav -->[\s\S]*?<!-- /studio:nav -->', '', text)
    headings = list(re.finditer(r'(?m)^(#{1,6}) (.+?)\s*$', text))
    found = [m for m in headings if m.group(2) == heading]
    if len(found) != 1: raise StudioError('来源标题必须唯一命中：' + str(heading))
    start = found[0]
    stop = next((m.start() for m in headings if m.start() > start.start() and len(m.group(1)) <= len(start.group(1))), len(text))
    # Ignore whitespace introduced by inserting/removing managed figures.
    return re.sub(r'\n{3,}', '\n\n', text[start.start():stop]).strip()

def inputs(root, figure_id):
    root = Path(root).resolve()
    book, record, brief, folder, unit = resolve(root, figure_id)
    style = local(root, 'assets/illustrations/styles/' + brief['style'])
    style_files = ('style.md', 'prefix.txt', 'reference.png', 'paper.png', 'approval.json')
    hashes = {name: digest((style / name).read_bytes()) for name in style_files}
    labels = load_yaml(local(root, (folder / brief['labels']).relative_to(root).as_posix()))
    if not isinstance(labels, list) or any(not isinstance(v, str) or not v for v in labels):
        raise StudioError('labels 必须是非空字符串列表')
    source = local(root, unit['path']).read_text(encoding='utf-8')
    snippets = [{'heading': h, 'text': section(source, h)} for h in brief['source_sections']]
    fact_data = load_yaml(root / 'facts.yaml') if (root / 'facts.yaml').exists() else []
    facts = [f for f in fact_data if f.get('id') in unit.get('facts', [])]
    prefix = (style / 'prefix.txt').read_text(encoding='utf-8').strip()
    required = ('BLACK GEL PEN', 'grid', 'OPAQUE', 'R=G=B')
    if not prefix or re.search(r'\b(?:undefined|null|None)\b', prefix) or any(word not in prefix for word in required):
        raise StudioError('风格前缀缺失或不完整：必须明确黑色中性笔、不透明方格纸和全图灰度')
    prompt = (prefix + '\n\nTITLE (exact): ' + brief['title'] + '\nVISUAL COMPOSITION: ' + brief['composition'] +
              '\nREQUIRED LABELS (exact; use each only where it belongs): ' + json.dumps(labels, ensure_ascii=False) +
              '\nFACTUAL AND SEMANTIC CONSTRAINTS: ' + brief['content_guard'])
    if '界面示意，布局随版本变化' in prompt:
        raise StudioError('已废止的重复界面注释不能进入生成提示词')
    payload = {'schema_version': 1, 'figure': figure_id, 'unit': record['unit'], 'source_path': unit['path'],
               'brief': brief, 'labels': labels, 'sources': snippets, 'facts': facts, 'style_files': hashes,
               'prompt_sha256': digest(prompt.encode())}
    return payload, digest(payload), prompt

def pack(root, figure_id, destination):
    root = Path(root).resolve()
    payload, fingerprint, prompt = inputs(root, figure_id)
    dest = local(root, destination)
    if dest.exists(): raise StudioError('生产包目录已存在，使用新目录')
    dest.mkdir(parents=True)
    save_json(dest / 'inputs.json', {'fingerprint': fingerprint, 'inputs': payload,
              'base_commit': git_commit(root), 'input_kind': 'working-tree-snapshot', 'created_at': datetime.now(timezone.utc).isoformat()})
    atomic_write(dest / 'prompt.txt', prompt + '\n')
    return {'ok': True, 'outputs': [str(dest)], 'network': '未访问', 'generation': '未执行'}

def import_candidate(root, figure_id, source, production_pack, revision, tool, reference_used=False):
    root = Path(root).resolve()
    if not re.fullmatch(r'r\d{2,}', revision): raise StudioError('修订号应为 r01 等')
    if not tool: raise StudioError('需要记录实际生成工具')
    _, _, _, folder, _ = resolve(root, figure_id)
    payload, fingerprint, prompt = inputs(root, figure_id)
    pack_dir = local(root, production_pack)
    saved = read_json(pack_dir / 'inputs.json')
    actual_prompt = (pack_dir / 'prompt.txt').read_text(encoding='utf-8').rstrip('\n')
    if saved.get('fingerprint') != fingerprint or saved.get('inputs') != payload or actual_prompt != prompt:
        raise StudioError('生产包与当前正文/标签/风格不一致，请重新核对')
    image = png_info(source)
    if image['width'] < 1400: raise StudioError('图片宽度不足 1400 px')
    dest = folder / 'revisions' / revision
    if dest.exists(): raise StudioError('修订号已存在，禁止覆盖候选或采用字节')
    staging = folder / 'revisions' / ('.' + revision + '-import')
    staging.mkdir(parents=True, exist_ok=False)
    try:
        shutil.copy2(source, staging / 'zh-CN.png')
        if png_info(staging / 'zh-CN.png') != image: raise StudioError('导入过程中图片变化')
        save_json(staging / 'inputs.json', saved)
        atomic_write(staging / 'prompt.txt', actual_prompt + '\n')
        save_json(staging / 'provenance.json', {'schema_version': 1, 'figure': figure_id,
                  'input_fingerprint': fingerprint, 'image': image, 'tool': tool, 'model': 'unknown',
                  'cost': 'unknown', 'reference_image_actually_passed': reference_used,
                  'created_at': datetime.now(timezone.utc).isoformat()})
        staging.rename(dest)
    except Exception:
        shutil.rmtree(staging)
        raise
    return {'ok': True, 'outputs': [str(dest)], 'status': 'candidate'}

def validate_review(review, image_hash, fingerprint):
    if not isinstance(review, dict) or review.get('image_sha256') != image_hash or review.get('input_fingerprint') != fingerprint:
        raise StudioError('审校对象与本次图片/输入摘要不一致')
    if not review.get('reviewer') or not review.get('checked_on'):
        raise StudioError('审校须记录人员/引擎与日期')
    if any(review.get(k) != 'pass' for k in ('content', 'text', 'visual', 'background', 'monochrome')):
        raise StudioError('采用须通过内容、文字、视觉、黑白与统一纸底审校')

def select(root, figure_id, revision, review_path):
    root = Path(root).resolve()
    if not re.fullmatch(r'r\d{2,}', revision): raise StudioError('无效修订号')
    _, _, brief, folder, unit = resolve(root, figure_id)
    _, fingerprint, _ = inputs(root, figure_id)
    dest = folder / 'revisions' / revision
    provenance = read_json(dest / 'provenance.json')
    image = png_info(dest / 'zh-CN.png')
    if provenance.get('image') != image or provenance.get('input_fingerprint') != fingerprint:
        raise StudioError('候选已变化或来源过期')
    review = read_json(review_path)
    validate_review(review, image['sha256'], fingerprint)
    source = local(root, unit['path'])
    old_text = source.read_text(encoding='utf-8')
    image_link = os.path.relpath(dest / 'zh-CN.png', source.parent)
    caption = brief.get('caption', brief['takeaway'])
    block = ('<!-- diagram: ' + figure_id + ' -->\n![' + brief['title'] + '](' + image_link + ')\n\n' +
             '*图：' + caption + '*\n<!-- /diagram: ' + figure_id + ' -->')
    existing = [m for m in MANAGED.finditer(old_text) if m.group(1) == figure_id]
    if len(existing) > 1: raise StudioError('正文重复插图标记')
    if existing:
        m = existing[0]; new_text = old_text[:m.start()] + block + old_text[m.end():]
    else:
        heading = brief['placement']
        matches = list(re.finditer(r'(?m)^#{1,6} ' + re.escape(heading) + r'\s*$', old_text))
        if len(matches) != 1: raise StudioError('放置标题必须唯一命中')
        # Place immediately after the introductory paragraph, before subheadings.
        position = matches[0].end()
        rest = old_text[position:].lstrip('\n')
        paragraph_end = rest.find('\n\n')
        if paragraph_end >= 0 and not rest.startswith(('#', '```', '|')):
            position = len(old_text) - len(rest) + paragraph_end
        new_text = old_text[:position] + '\n\n' + block + '\n\n' + old_text[position:].lstrip('\n')
    selection = folder / 'selection.yaml'
    before = selection.read_text() if selection.exists() else None
    # Keep the exact review next to the immutable candidate before switching.
    review_dest = dest / 'review.json'
    if review_dest.exists() and read_json(review_dest) != review:
        raise StudioError('该修订已有不同审校记录；保留现场，使用新修订')
    save_json(review_dest, review)
    try:
        dump_yaml(selection, {'revision': revision, 'language': 'zh-CN', 'image_sha256': image['sha256'],
                  'input_fingerprint': fingerprint})
        atomic_write(source, new_text)
    except Exception:
        if before is None: selection.unlink(missing_ok=True)
        else: atomic_write(selection, before)
        atomic_write(source, old_text)
        raise
    return {'ok': True, 'outputs': [str(source), str(selection)], 'status': 'placed',
            'pending': ['入稿阅读检查与实际跨引擎审校另行记录']}

def audit(root, publication=False, scope=None):
    root = Path(root).resolve()
    book, records = figures(root)
    issues, rows = [], []
    for record in records:
        fid = record.get('id')
        row = {'id': fid, 'unit': record.get('unit'), 'stage': 'planned', 'source': 'unknown'}
        def issue(code, message, level='error'):
            issues.append({'level': level, 'code': code, 'path': record.get('spec', 'book.yaml'), 'message': str(fid) + ': ' + message})
        try:
            _, _, brief, folder, unit = resolve(root, fid)
            payload, fingerprint, prompt = inputs(root, fid)
            if not (folder / 'selection.yaml').exists():
                issue('illustration_unselected', '尚未采用图片', 'error' if publication else 'warning')
            else:
                selection = load_yaml(folder / 'selection.yaml')
                revision = selection.get('revision', '')
                if not re.fullmatch(r'r\d{2,}', revision): raise StudioError('无效选择修订')
                dest = folder / 'revisions' / revision
                image = png_info(dest / 'zh-CN.png')
                provenance = read_json(dest / 'provenance.json')
                review = read_json(dest / 'review.json')
                frozen = read_json(dest / 'inputs.json')
                if provenance.get('image') != image or selection.get('image_sha256') != image['sha256']:
                    raise StudioError('已采用图片字节/尺寸变化')
                old_fingerprint = provenance.get('input_fingerprint')
                if digest(frozen.get('inputs')) != old_fingerprint or frozen.get('fingerprint') != old_fingerprint:
                    raise StudioError('生产输入快照摘要不一致')
                if digest((dest / 'prompt.txt').read_text().rstrip('\n').encode()) != frozen['inputs']['prompt_sha256']:
                    raise StudioError('实际提示词与生产输入不一致')
                validate_review(review, image['sha256'], old_fingerprint)
                row.update(stage='selected', source='current' if old_fingerprint == fingerprint else 'stale', revision=revision)
                if selection.get('input_fingerprint') != fingerprint or old_fingerprint != fingerprint:
                    issue('illustration_stale', '来源段落、事实、标签或风格已变化')
                body = local(root, unit['path']).read_text(encoding='utf-8')
                blocks = [m.group(0) for m in MANAGED.finditer(body) if m.group(1) == fid]
                expected = os.path.relpath(dest / 'zh-CN.png', local(root, unit['path']).parent)
                expected_block = ('<!-- diagram: ' + fid + ' -->\n![' + brief['title'] + '](' + expected + ')\n\n' +
                                  '*图：' + brief.get('caption', brief['takeaway']) + '*\n<!-- /diagram: ' + fid + ' -->')
                if len(blocks) != 1 or blocks[0] != expected_block:
                    issue('illustration_placement', '正文图片、标题或图注与采用记录不一致')
                else: row['stage'] = 'placed'
                if image['width'] < 1400: issue('illustration_resolution', '宽度不足 1400 px')
                if publication and (scope is None or record.get('unit') in scope) and review.get('placement') != 'pass':
                    issue('illustration_reading_pending', '实际版面阅读检查尚未通过')
        except (StudioError, OSError, ValueError, KeyError, TypeError, struct.error) as exc:
            issue('illustration_invalid', str(exc))
        rows.append(row)
    return {'ok': not any(i['level'] == 'error' for i in issues), 'figures': rows, 'issues': issues,
            'legacy_remaining': sum(d.get('type') in ('mindmap', 'flowchart') for d in book.get('diagrams', [])),
            'network': '未访问', 'generation': '未执行'}

def command(root, args):
    root = Path(root).resolve()
    if args.action == 'status': return audit(root)
    if not args.figure: raise StudioError('需要 --figure')
    if args.action == 'pack':
        if not args.output: raise StudioError('需要 --output（书仓相对目录）')
        return pack(root, args.figure, args.output)
    if args.action == 'import':
        if not all((args.image, args.pack, args.revision, args.tool)): raise StudioError('需要 --image、--pack、--revision、--tool')
        return import_candidate(root, args.figure, args.image, args.pack, args.revision, args.tool, args.reference_used)
    if args.action == 'select':
        if not args.revision or not args.review: raise StudioError('需要 --revision、--review')
        return select(root, args.figure, args.revision, args.review)
    raise StudioError('未知插图动作')


def pdf_assets(root, unit, body, book):
    """Flatten registered raster paths inside a fixed-source export directory."""
    from urllib.parse import unquote
    root = Path(root).resolve()
    entries = []
    pattern = r"<!-- diagram: (FIG-\d+) -->\s*!\[([^]\n]*)\]\(([^)\n]+)\)"
    def replace(match):
        fid, alt, target = match.groups()
        if not any(d.get('id') == fid and d.get('unit') == unit['id'] and d.get('type') == 'illustration' for d in book.get('diagrams', [])):
            raise StudioError('未登记手绘插图：' + fid)
        source = local(root, unquote(target))
        png_info(source)
        out = root / ('diagram-' + fid + '.png')
        if out.exists(): raise StudioError('PDF 插图身份或文件重复：' + fid)
        shutil.copy2(source, out)
        entries.append((fid, out.name, unit['id'], unit.get('title', unit['id'])))
        return '![' + alt + '](' + out.name + '){width=100%}'
    return re.sub(pattern, replace, body), entries
