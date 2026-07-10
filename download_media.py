"""
パティオ新サイト用メディアダウンロードスクリプト
patio-patio.jp から写真・音声ファイルを一括ダウンロードします
保存先: patio-website/uploads/ フォルダ
"""

import os
import re
import urllib.request
import urllib.parse
from pathlib import Path

# 保存先フォルダ
OUTPUT_DIR = Path(__file__).parent / "uploads"

# HTMLファイルとcast-data.jsからURLを抽出
SOURCE_FILES = [
    Path(__file__).parent / "js" / "cast-data.js",
    Path(__file__).parent / "profile",
    Path(__file__).parent / "profile2",
    Path(__file__).parent / "profile3",
]

def collect_urls():
    urls = set()
    pattern = re.compile(r'https://patio-patio\.jp/wp-content/uploads/[^\s"\'<>]+')

    for source in SOURCE_FILES:
        if source.is_file():
            urls.update(pattern.findall(source.read_text(encoding="utf-8", errors="ignore")))
        elif source.is_dir():
            for f in source.glob("*.html"):
                urls.update(pattern.findall(f.read_text(encoding="utf-8", errors="ignore")))
    return sorted(urls)

def download(urls):
    total = len(urls)
    ok = 0
    skip = 0
    err = 0

    for i, url in enumerate(urls, 1):
        # URLからローカルパスを生成
        rel = url.replace("https://patio-patio.jp/wp-content/uploads/", "")
        dest = OUTPUT_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)

        if dest.exists():
            print(f"[{i}/{total}] スキップ（既存）: {rel}")
            skip += 1
            continue

        try:
            # 日本語ファイル名をURLエンコード
            parsed = urllib.parse.urlsplit(url)
            encoded_path = urllib.parse.quote(parsed.path, safe="/")
            encoded_url = urllib.parse.urlunsplit(parsed._replace(path=encoded_path))
            req = urllib.request.Request(encoded_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
                f.write(r.read())
            print(f"[{i}/{total}] ✅ {rel}")
            ok += 1
        except Exception as e:
            print(f"[{i}/{total}] ❌ エラー: {rel} ({e})")
            err += 1

    print(f"\n完了: 成功={ok} スキップ={skip} エラー={err} / 合計={total}")

if __name__ == "__main__":
    urls = collect_urls()
    print(f"{len(urls)} 件のファイルをダウンロードします → {OUTPUT_DIR}\n")
    download(urls)
