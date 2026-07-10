"""
全プロフィールHTMLからimages・audios・経歴を抽出してcast-data.jsを一括更新
"""
import json, re
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).parent

# cast-data.js 読み込み
text = (ROOT / 'js' / 'cast-data.js').read_text(encoding='utf-8')
cast_data = json.loads(re.sub(r'^const CAST_DATA\s*=\s*', '', text).rstrip().rstrip(';'))

class ProfileParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.audios = []
        self.career_cols = []  # [左カラム文字列, 右カラム文字列]
        self._in_main_img = False
        self._in_career_body = False
        self._in_career_list = False
        self._in_career_name = False
        self._in_career_text = False
        self._in_li = False
        self._current_col_lines = []
        self._current_block_lines = []
        self._cols_raw = []  # 各staff-career__listのブロックリスト

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get('class', '')
        if 'staff-profile__mainimg' in cls:
            self._in_main_img = True
        if self._in_main_img and tag == 'img' and 'js-main-target' in cls:
            src = attrs.get('src', '')
            if src:
                self.images.append(src)
        if tag == 'audio':
            src = attrs.get('src', '')
            if src:
                self.audios.append(src)
        if 'staff-career__body' in cls:
            self._in_career_body = True
        if self._in_career_body and 'staff-career__list' in cls:
            self._in_career_list = True
            self._current_col_lines = []
        if self._in_career_list and 'staff-career__name' in cls:
            self._in_career_name = True
        if self._in_career_list and 'staff-career__text' in cls:
            self._in_career_text = True
        if self._in_career_text and tag == 'li':
            self._in_li = True

    def handle_endtag(self, tag):
        if tag == 'div':
            if self._in_career_list:
                self._in_career_list = False
                self._cols_raw.append('\n'.join(self._current_col_lines).strip())
                self._current_col_lines = []
            elif self._in_career_body:
                self._in_career_body = False
        if self._in_career_name and tag == 'p':
            self._in_career_name = False
        if self._in_career_text and tag == 'ul':
            self._in_career_text = False
        if self._in_li and tag == 'li':
            self._in_li = False

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
        if self._in_career_name:
            self._current_col_lines.append(f'【見出し】{data}')
        elif self._in_li:
            self._current_col_lines.append(f'・{data}')

def parse_profile(path):
    p = ProfileParser()
    try:
        p.feed(path.read_text(encoding='utf-8', errors='replace'))
    except Exception:
        pass
    cols = p._cols_raw
    return {
        'images': p.images,
        'audios': p.audios,
        'careerLeft': cols[0] if len(cols) > 0 else '',
        'careerRight': cols[1] if len(cols) > 1 else '',
    }

updated = 0
for cast in cast_data:
    pid = cast.get('id')
    html_path = ROOT / 'profile' / f'{pid}.html'
    if not html_path.exists():
        continue
    data = parse_profile(html_path)
    # imagesが未設定 or 1枚のみの場合に補完
    if not cast.get('images') or len(cast.get('images', [])) <= 1:
        if data['images']:
            cast['images'] = data['images']
            cast['image'] = data['images'][0]
    # audiosが未設定の場合に補完
    if not cast.get('audios') and data['audios']:
        cast['audios'] = data['audios']
        cast['audio'] = data['audios'][0]
    # 経歴が未設定の場合に補完
    if not cast.get('careerLeft') and data['careerLeft']:
        cast['careerLeft'] = data['careerLeft']
    if not cast.get('careerRight') and data['careerRight']:
        cast['careerRight'] = data['careerRight']
    updated += 1
    print(f'✅ {cast["name"]} (id={pid}): 写真{len(cast.get("images",[]))}枚')

# cast-data.js 書き出し
out = 'const CAST_DATA = ' + json.dumps(cast_data, ensure_ascii=False, indent=2) + ';\n'
(ROOT / 'js' / 'cast-data.js').write_text(out, encoding='utf-8')
print(f'\n完了: {updated}名のデータを更新しました → js/cast-data.js')
