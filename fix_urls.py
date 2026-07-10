"""
画像・音声URLをWordPressサーバーからローカルuploadsフォルダへ一括置換
https://patio-patio.jp/wp-content/uploads/ → uploads/
"""

from pathlib import Path

ROOT = Path(__file__).parent
OLD = "https://patio-patio.jp/wp-content/uploads/"
NEW = "uploads/"  # profile/内のHTMLからも ../uploads/ ではなくルート相対で統一

targets = []
# cast-data.js
targets.append(ROOT / "js" / "cast-data.js")
# profile/*.html
targets += list((ROOT / "profile").glob("*.html"))
# その他のHTML
for name in ["index.html", "profile.html", "company.html", "commission.html", "contact.html", "register.html"]:
    targets.append(ROOT / name)

changed = 0
for path in targets:
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    if OLD in text:
        path.write_text(text.replace(OLD, NEW), encoding="utf-8")
        print(f"✅ 置換済み: {path.name}")
        changed += 1
    else:
        print(f"－ スキップ: {path.name}")

print(f"\n完了: {changed} ファイルを置換しました")
