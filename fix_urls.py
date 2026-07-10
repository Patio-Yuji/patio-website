"""
画像・音声URLをWordPressサーバーからローカルuploadsフォルダへ一括置換
- profile/*.html → ../uploads/
- その他のファイル → uploads/
"""

from pathlib import Path

ROOT = Path(__file__).parent
OLD = "https://patio-patio.jp/wp-content/uploads/"

changed = 0

# profile/*.html は ../uploads/ （1階層上を参照）
for path in (ROOT / "profile").glob("*.html"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    new_text = text.replace(OLD, "../uploads/").replace("src=\"uploads/", "src=\"../uploads/").replace("src='uploads/", "src='../uploads/")
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print(f"✅ {path.name}")
        changed += 1

# cast-data.js・ルートHTMLは uploads/
for name in ["js/cast-data.js", "index.html", "profile.html", "company.html", "commission.html", "contact.html", "register.html"]:
    path = ROOT / name
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    new_text = text.replace(OLD, "uploads/")
    # cast-data.js内に混入した ../uploads/ も修正
    new_text = new_text.replace('"../uploads/', '"uploads/').replace("'../uploads/", "'uploads/")
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print(f"✅ {name}")
        changed += 1

print(f"\n完了: {changed} ファイルを修正しました")
