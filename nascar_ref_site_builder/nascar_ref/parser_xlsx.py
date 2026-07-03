"""Parses the NASCAR_SIM.xlsx workbook: career stats, season rosters,
team points standings, driver season standings, and schedules."""
import pandas as pd
import math

SERIES_CODES = {'TRUCK:': 'truck', 'XFINITY:': 'xfinity', 'CUP:': 'cup'}
SERIES_LABELS = {'truck': 'Truck Series', 'xfinity': 'Xfinity Series', 'cup': 'Cup Series'}
BOGUS_DRIVERS = {'Xfinity Winner', 'Truck Winner', 'Cup Winner', 'Winner'}


def _clean(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    s = str(v).strip()
    if s and s.lower() != 'nan':
        # openpyxl reads integer 0 as float 0.0; strip trailing .0 for clean car numbers
        if s.endswith('.0') and s.count('.') == 1:
            s = s[:-2]
        return s
    return None


def _is_int(v):
    try:
        int(v)
        return True
    except (ValueError, TypeError):
        return False


def parse_stats_sheet(xl):
    """Career totals per driver: total + per series."""
    df = xl.parse('Stats', header=None)
    groups = {'total': 1, 'cup': 11, 'xfinity': 21, 'truck': 31}
    fields = ['starts', 'wins', 'win_pct', 'top5', 'top10', 'avg_f', 'poles', 'avg_s', 'points']
    drivers = {}
    for i in range(2, len(df)):
        name = _clean(df.iat[i, 0])
        if not name or name.lower() in ('driver', 'name', 'total', 'totals'):
            continue
        rec = {}
        for key, start_col in groups.items():
            block = {}
            for j, f in enumerate(fields):
                block[f] = df.iat[i, start_col + j]
            rec[key] = block
        drivers[name] = rec
    return drivers


def _find_label_cols(header_row, label):
    return [i for i, v in enumerate(header_row) if _clean(v) == label]


def parse_season_sheet(xl, year):
    df = xl.parse(str(year), header=None)
    header = df.iloc[0].tolist()
    result = {'schedule': {}, 'roster': {}, 'team_points': {}, 'driver_standings': {}}

    # --- Schedule: columns 1,2,3 = TRUCK/XFINITY/CUP track names, col0 = weekend No. ---
    series_col = {'truck': 1, 'xfinity': 2, 'cup': 3}
    counters = {'truck': 0, 'xfinity': 0, 'cup': 0}
    for i in range(1, len(df)):
        weekend_no = df.iat[i, 0]
        numeric_weekend = _is_int(weekend_no)
        for series, col in series_col.items():
            track = _clean(df.iat[i, col])
            if not track:
                continue
            if not numeric_weekend:
                continue  # exhibition (All-Star etc.) -- not a numbered points race
            counters[series] += 1
            race_num = counters[series]
            result['schedule'].setdefault(series, []).append({
                'race_num': race_num,
                'track': track,
                'weekend_no': weekend_no,
            })

    # --- Rosters: find "TRUCK:"/"XFINITY:"/"CUP:" followed by #, NAME, TEAM ---
    for i, cell in enumerate(header):
        label = _clean(cell)
        if label in SERIES_CODES and i + 3 < len(header):
            if [_clean(header[i + 1]), _clean(header[i + 2]), _clean(header[i + 3])] == ['#', 'NAME', 'TEAM']:
                series = SERIES_CODES[label]
                roster = []
                blank_streak = 0
                for r in range(1, len(df)):
                    car = _clean(df.iat[r, i + 1])
                    drv = _clean(df.iat[r, i + 2])
                    team = _clean(df.iat[r, i + 3])
                    if not drv and not team:
                        blank_streak += 1
                        if roster and blank_streak >= 1:
                            break  # end of this roster table -- don't sweep up tables stacked below
                        continue
                    blank_streak = 0
                    if drv and team and drv not in BOGUS_DRIVERS and 'winner' not in drv.lower():
                        roster.append({'car': car, 'driver': drv, 'team': team})
                if series not in result['roster']:
                    result['roster'][series] = roster

    # --- Team points: "TRUCK:"/"XFINITY:"/"CUP:" followed by TEAM, PTS ---
    for i, cell in enumerate(header):
        label = _clean(cell)
        if label in SERIES_CODES and i + 2 < len(header):
            if [_clean(header[i + 1]), _clean(header[i + 2])] == ['TEAM', 'PTS']:
                series = SERIES_CODES[label]
                pts = []
                for r in range(1, len(df)):
                    team = _clean(df.iat[r, i + 1])
                    p = df.iat[r, i + 2]
                    if team and _clean(p) is not None:
                        try:
                            p = float(p)
                        except (ValueError, TypeError):
                            continue
                        pts.append({'team': team, 'points': p})
                if pts and series not in result['team_points']:
                    result['team_points'][series] = sorted(pts, key=lambda x: -x['points'])

    # --- Driver season standings: "TRUCK:"/"XFINITY:"/"CUP:" followed by "Pos." ---
    for i, cell in enumerate(header):
        label = _clean(cell)
        if label in SERIES_CODES and i + 1 < len(header) and _clean(header[i + 1]) == 'Pos.':
            series = SERIES_CODES[label]
            # collect the column names of this block until a blank / next label
            col_names = []
            j = i + 1
            while j < len(header):
                name = _clean(header[j])
                if name is None:
                    break
                if name in SERIES_CODES and j != i + 1:
                    break
                col_names.append((j, name))
                j += 1
            rows = []
            for r in range(1, len(df)):
                pos_val = df.iat[r, col_names[0][0]]
                if _clean(pos_val) is None:
                    continue
                rec = {}
                for col_idx, name in col_names:
                    rec[name] = df.iat[r, col_idx]
                drv_name = _clean(rec.get('Driver')) or _clean(rec.get('NAME'))
                if not drv_name:
                    continue
                rows.append(rec)
            if rows and series not in result['driver_standings']:
                result['driver_standings'][series] = rows

    # --- Awards: scan rows for <SERIES> AWARDS followed by individual awards ---
    # Label column varies between years (col 1 for 2020-2029, col 2 for 2030+)
    result['awards'] = {'truck': {}, 'xfinity': {}, 'cup': {}}
    current_series = None
    for r in range(1, len(df)):
        label = None
        val = None
        for j in range(len(df.columns) - 1):
            cj = _clean(df.iat[r, j])
            if cj:
                if cj.endswith(' AWARDS'):
                    label = cj
                    val = _clean(df.iat[r, j + 1])
                    break
                if current_series and cj.startswith('-') and cj.endswith('-'):
                    label = cj
                    val = _clean(df.iat[r, j + 1])
                    break
        if label and label.endswith(' AWARDS'):
            prefix = label.split()[0]  # 'TRUCK', 'XFINITY', 'CUP'
            code = prefix + ':'
            current_series = SERIES_CODES.get(code)
            if current_series is None:
                # e.g. 'OVERALL' or unknown → stop collecting
                current_series = None
        elif current_series and label:
            if label.startswith('-') and label.endswith('-'):
                award_key = label.strip('-')
                result['awards'][current_series][award_key] = val
            else:
                # non-award row encountered while collecting → end block
                current_series = None
        else:
            # blank col-1 breaks the chain
            if current_series and label is None:
                current_series = None

    return result


def parse_workbook(path):
    xl = pd.ExcelFile(path)
    career = parse_stats_sheet(xl)
    year_sheets = [s for s in xl.sheet_names if s.isdigit()]
    seasons = {}
    for y in year_sheets:
        seasons[int(y)] = parse_season_sheet(xl, y)
    return {'career': career, 'seasons': seasons}
