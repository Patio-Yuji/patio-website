"""
貴理子・月脚めぐみの画像データをcast-data.jsで修正
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).parent
path = ROOT / 'js' / 'cast-data.js'
text = path.read_text(encoding='utf-8', errors='replace')
data = json.loads(re.sub(r'^const CAST_DATA\s*=\s*', '', text).rstrip().rstrip(';'))

for c in data:
    # 貴理子：02-2.jpgを先頭に追加
    if c['name'] == '貴理子':
        imgs = c.get('images', [])
        first = 'uploads/2026/04/貴理子02-2.jpg'
        if first not in imgs:
            imgs.insert(0, first)
            c['images'] = imgs
        c['image'] = first
        print(f"✅ 貴理子: {c['images']}")

    # 月脚めぐみ：サムネイルを09-2に修正
    if c['name'] == '月脚 めぐみ' or '月脚' in c.get('name', ''):
        correct = 'uploads/2022/03/月脚めぐみ09-2.jpg'
        c['image'] = correct
        imgs = c.get('images', [])
        if correct not in imgs:
            imgs.insert(0, correct)
        else:
            imgs.remove(correct)
            imgs.insert(0, correct)
        c['images'] = imgs
        print(f"✅ {c['name']}: {c['images']}")

out = 'const CAST_DATA = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n'
path.write_text(out, encoding='utf-8')
print('\n完了: cast-data.js を更新しました')
