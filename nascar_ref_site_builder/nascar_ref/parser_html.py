"""Parses NR2003-exported race result HTML files (Practice / Qualifying /
Happy Hour / Race sessions, cautions, weather, penalties)."""
import re
import os
from bs4 import BeautifulSoup

FILENAME_RE = re.compile(r'.*?_(N[CXT]S)_(\d{4})_R(\d+)\.html?$', re.IGNORECASE)
ALLSTAR_RE = re.compile(
    r'.*?_(\d{4})_(?:AS|AllStar)(?:_?(.*?))?\.html?$', re.IGNORECASE
)
SERIES_MAP = {'NCS': 'cup', 'NXS': 'xfinity', 'NTS': 'truck'}


def parse_filename(path):
    m = FILENAME_RE.match(os.path.basename(path))
    if m:
        code, year, race_num = m.groups()
        series = SERIES_MAP.get(code.upper())
        if not series:
            return None
        return {'series': series, 'year': int(year), 'race_num': int(race_num)}

    m = ALLSTAR_RE.match(os.path.basename(path))
    if m:
        year = int(m.group(1))
        suffix = (m.group(2) or '').lower()
        if not suffix or suffix == 'race':
            allstar_type = 'Race'
            race_num = 801
        elif 'open' in suffix:
            allstar_type = 'Open'
            race_num = 800
        elif re.match(r'r?\d+$', suffix):
            n = int(re.match(r'r?(\d+)', suffix).group(1))
            allstar_type = f'AS {n}'
            race_num = 800 + n
        else:
            allstar_type = suffix.capitalize()
            race_num = 801
        return {'series': 'cup', 'year': year, 'race_num': race_num, 'is_allstar': True, 'allstar_type': allstar_type}

    return None


def _text(tag):
    return tag.get_text(strip=True) if tag else None


def _h3_value(soup, label):
    """Find an <H3> whose text starts with `label:` and return the remainder."""
    for h3 in soup.find_all('h3'):
        t = h3.get_text(' ', strip=True)
        if t.lower().startswith(label.lower() + ':'):
            return t.split(':', 1)[1].strip()
    return None


def parse_race_file(path):
    with open(path, 'r', encoding='latin-1', errors='replace') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    meta = parse_filename(path)
    if not meta:
        return None

    track = _h3_value(soup, 'Track')
    date = _h3_value(soup, 'Date')
    cautions = _h3_value(soup, 'Caution Flags')
    lead_changes = _h3_value(soup, 'Lead Changes')
    weather = _h3_value(soup, 'Weather')
    pitstop = _h3_value(soup, 'Pitstop Frequency')
    ai_strength = _h3_value(soup, 'AI Strength')

    # Walk the document in order, pairing each "Session: X" H3 with the table that follows it
    sessions = {}
    body_children = list(soup.body.children) if soup.body else []
    current_session = None
    for el in body_children:
        if getattr(el, 'name', None) == 'h3':
            t = el.get_text(' ', strip=True)
            if t.lower().startswith('session:'):
                current_session = t.split(':', 1)[1].strip()
        elif getattr(el, 'name', None) == 'table' and current_session:
            rows = el.find_all('tr')
            if not rows:
                continue
            headers = [_text(td) for td in rows[0].find_all('td')]
            data_rows = []
            for tr in rows[1:]:
                cells = [_text(td) for td in tr.find_all('td')]
                if not cells or all(c is None for c in cells):
                    continue
                # pad/truncate to header length
                cells = (cells + [None] * len(headers))[:len(headers)]
                data_rows.append(dict(zip(headers, cells)))
            sessions[current_session] = data_rows
            current_session = None  # each session table only follows its own header

    return {
        **meta,
        'track': track,
        'date': date,
        'cautions': cautions,
        'lead_changes': lead_changes,
        'weather': weather,
        'pitstop': pitstop,
        'ai_strength': ai_strength,
        'sessions': sessions,
        'is_allstar': meta.get('is_allstar', False),
        'allstar_type': meta.get('allstar_type'),
    }


def scan_results_dir(results_dir):
    races = []
    for fname in sorted(os.listdir(results_dir)):
        if not fname.lower().endswith(('.html', '.htm')):
            continue
        meta = parse_filename(fname)
        if not meta:
            continue
        full = os.path.join(results_dir, fname)
        try:
            race = parse_race_file(full)
            if race:
                races.append(race)
        except Exception as e:
            print(f'  ! failed to parse {fname}: {e}')
    return races
