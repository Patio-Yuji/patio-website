"""
cast-data.js に記載されている画像・音声のうち、
ローカルのuploadsフォルダに存在しないものを
patio-patio.jp からダウンロードします
"""
import json, re, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).parent
UPLOADS = ROOT / 'uploads'
BASE_URL = 'https://patio-patio.jp/wp-content/uploads/'

text = (ROOT / 'js' / 'cast-data.js').read_text(encoding='utf-8', errors='replace')
data = json.loads(re.sub(r'^const CAST_DATA\s*=\s*', '', text).rstrip().rstrip(';'))

missing = set()
for c in data:
    for path in [c.get('image',''), *c.get('images',[]), *c.get('audios',[])]:
        if not path:
            continue
        local = UPLOADS / path.replace('uploads/', '', 1)
        if not local.exists():
            missing.add(path.replace('uploads/', '', 1))

print(f"不足ファイル: {len(missing)}件\n")

ok = skip = err = 0
for rel in sorted(missing):
    dest = UPLOADS / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = BASE_URL + rel
    try:
        parsed = urllib.parse.urlsplit(url)
        encoded = urllib.parse.urlunsplit(parsed._replace(path=urllib.parse.quote(parsed.path, safe='/')))
        req = urllib.request.Request(encoded, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r, open(dest, 'wb') as f:
            f.write(r.read())
        print(f'✅ {rel}')
        ok += 1
    except Exception as e:
        print(f'❌ {rel} ({e})')
        err += 1

print(f'\n完了: 成功={ok} エラー={err}')
