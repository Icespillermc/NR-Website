import os
import re
import json
import html as htmlmod
import shutil
from collections import defaultdict, Counter
from jinja2 import Environment, FileSystemLoader

SERIES_LABELS = {'cup': 'Cup Series', 'xfinity': 'Xfinity Series', 'truck': 'Truck Series'}
SERIES_ORDER = ['cup', 'xfinity', 'truck']

SERIES_LOGO = {
    'cup': 'static/download (2).png',
    'xfinity': 'static/XFINITY-Series-Logo-scaled.jpg',
    'truck': 'static/nascar-camping-world-truck-seires-logo.jpg',
}

HERE = os.path.dirname(os.path.abspath(__file__))

# Known real-world track renames -- extend this if your universe has others.
TRACK_ALIASES = {
    'INFINEON RACEWAY': 'Sonoma Raceway',
    'SONOMA RACEWAY': 'Sonoma Raceway',
    'CALIFORNIA SPEEDWAY': 'Auto Club Speedway',
    'AUTO CLUB SPEEDWAY': 'Auto Club Speedway',
    'LOWES MOTOR SPEEDWAY': 'Charlotte Motor Speedway',
    "LOWE'S MOTOR SPEEDWAY": 'Charlotte Motor Speedway',
    'CHARLOTTE MOTOR SPEEDWAY': 'Charlotte Motor Speedway',
    'NORTH CAROLINA SPEEDWAY': 'Rockingham Speedway',
    'ROCKINGHAM SPEEDWAY': 'Rockingham Speedway',
    'PHOENIX INTERNATIONAL RACEWAY': 'Phoenix Raceway',
    'PHOENIX RACEWAY': 'Phoenix Raceway',
    'RICHMOND INTERNATIONAL RACEWAY': 'Richmond Raceway',
    'RICHMOND RACEWAY': 'Richmond Raceway',
    'CHICAGOLAND SPEEDWAY': 'Chicagoland Speedway',
    'JOLIET SPEEDWAY': 'Chicagoland Speedway',
    'ROAD AMERICA 2011': 'Road America',
    'WATKINS GLEN INTERNATIONAL': 'Watkins Glen International',
    'DAYTONA ROAD COURSE 2008': 'Daytona Road Course',
    'YAS MARINA CIRCUIT': 'Yas Marina Circuit',
    'YAS MARINA CIRCUIT NIGHT': 'Yas Marina Circuit',
    'ARMORY DIGITAL SUPERSPEEDWAY': 'Armory Digital Superspeedway',
    'ARMORY DIGITAL SUPERSPEEDWAY 2017': 'Armory Digital Superspeedway',
}

_TRACK_SUFFIX_WORDS = {'INTERNATIONAL', 'MOTOR', 'MOTORS', 'SPEEDWAY', 'RACEWAY', 'FAIRGROUNDS',
                        'PARK', 'CIRCUIT', 'MOTORSPORTS', 'COMPLEX', 'SUPERSPEEDWAY', 'SPDWY'}

_TRACK_VERSION_WORDS = {'NIGHT', 'DAY', 'WKC', 'WKD'}

TRACK_LENGTHS = {
    'Daytona International Speedway': 2.5,
    'Daytona Road Course': 3.56,
    'Talladega Superspeedway': 2.66,
    'Auto Club Speedway': 2.0,
    'Michigan International Speedway': 2.0,
    'Pocono Raceway': 2.5,
    'Indianapolis Motor Speedway': 2.5,
    'Charlotte Motor Speedway': 1.5,
    'Atlanta Motor Speedway': 1.54,
    'Texas Motor Speedway': 1.5,
    'Homestead-Miami Speedway': 1.5,
    'Kansas Speedway': 1.5,
    'Las Vegas Motor Speedway': 1.5,
    'Chicago Motor Speedway': 1.029,
    'Chicagoland Speedway': 1.5,
    'Kentucky Speedway': 1.5,
    'Nashville Superspeedway': 1.333,
    'Gateway Motorsports Park': 1.25,
    'World Wide Technology Raceway': 1.25,
    'Dover Motor Speedway': 1.0,
    'Dover Downs International Speedway': 1.0,
    'Phoenix Raceway': 1.0,
    'Phoenix International Raceway': 1.0,
    'New Hampshire Motor Speedway': 1.058,
    'Loudon': 1.058,
    'Richmond Raceway': 0.75,
    'Richmond International Raceway': 0.75,
    'Bristol Motor Speedway': 0.533,
    'Martinsville Speedway': 0.526,
    'North Wilkesboro Speedway': 0.625,
    'Rockingham Speedway': 1.017,
    'North Carolina Speedway': 1.017,
    'Darlington Raceway': 1.366,
    'Sonoma Raceway': 1.99,
    'Infineon Raceway': 1.99,
    'Watkins Glen International': 2.45,
    'Watkins Glen': 2.45,
    'Road America': 4.048,
    'Road Atlanta': 2.54,
    'Mid-Ohio Sports Car Course': 2.258,
    'Iowa Speedway': 0.875,
    'Iowa': 0.875,
    'Memphis Motorsports Park': 0.75,
    'Evergreen Speedway': 0.646,
    'Nazareth Speedway': 1.0,
    'South Boston Speedway': 0.4,
    'Myrtle Beach Speedway': 0.538,
    'Hickory Motor Speedway': 0.363,
    'Orange County Speedway': 0.375,
    'Tucson Raceway Park': 0.375,
    'Milwaukee Mile': 1.0,
    'Pikes Peak International Raceway': 1.0,
    'Kentucky Motor Speedway': 0.437,
    'Louisville Motor Speedway': 0.437,
    'Flemington Speedway': 0.625,
    'Thompson Speedway': 0.625,
    'Waterford Speedbowl': 0.375,
    'Stafford Motor Speedway': 0.5,
    'Seekonk Speedway': 0.333,
    'Riverhead Raceway': 0.25,
    'Laguna Seca Raceway': 1.9,
    'Lime Rock Park': 1.53,
    'Mosport Park': 2.459,
    'Mosport': 2.459,
    'Mount Panorama Circuit': 3.861,
    'Yas Marina Circuit': 3.451,
    'Circuit de la Sarthe': 8.469,
    'Brands Hatch': 2.433,
    'Silverstone Circuit': 3.66,
    'Suzuka Circuit': 3.608,
    'Sebring International Raceway': 3.701,
    'Armory Digital Superspeedway': 2.0,
    'Willow Springs Raceway': 2.5,
    'Irwindale Speedway': 0.5,
    'ISM Raceway': 1.0,
    'Portland International Raceway': 1.964,
    'Circuit Of The Americas': 3.426,
    'COTA': 3.426,
    'Twin Ring Motegi': 1.549,
    'Calder Thunderdome': 1.18,
    'Chicago Street Circuit': 2.2,
    'Canadian Tire Motorsport Park': 2.459,
    'New Jersey Motorsports Park': 2.25,
    'Iowa Speedway #2': 0.875,
    'Gateway': 1.25,
    'Gateway International Raceway': 1.25,
    'Roval': 2.28,
    'Charlotte Roval': 2.28,
    'Dover International Speedway': 1.0,
    'Eldora Speedway': 0.5,
    'Mid-Ohio': 2.258,
    'Mount Panorama-Bathurst': 3.861,
    'Bahrain International Circuit': 3.363,
    'Autodromo Hermanos Rodriguez': 2.674,
    'Autódromo Hermanos Rodríguez': 2.674,
    'Concord Motorsport Park': 0.375,
    'Kyalami': 2.814,
    'Lowe\'s Dirt Track 2012': 0.25,
    'Lowes Dirt Track 2012': 0.25,
    'Miami Hard Rock Stadium Circuit': 2.0,
    'Nashville SS DAY WKC': 1.333,
    'Saint Petersburg 13': 1.8,
    'St. Petersburg 13': 1.8,
    'Sydney Motorsport Park SuperNight': 2.0,
    'The Chili Bowl': 0.2,
    'Twin Ring Motegi': 1.549,
    'BTCC Brands Hatch': 2.433,
}

TRACK_LOCATIONS = {
    'Daytona International Speedway': 'Daytona Beach, FL',
    'Daytona Road Course': 'Daytona Beach, FL',
    'Talladega Superspeedway': 'Talladega, AL',
    'Auto Club Speedway': 'Fontana, CA',
    'Michigan International Speedway': 'Brooklyn, MI',
    'Pocono Raceway': 'Long Pond, PA',
    'Indianapolis Motor Speedway': 'Speedway, IN',
    'Charlotte Motor Speedway': 'Concord, NC',
    'Charlotte Roval': 'Concord, NC',
    'Roval': 'Concord, NC',
    'Atlanta Motor Speedway': 'Hampton, GA',
    'Texas Motor Speedway': 'Fort Worth, TX',
    'Homestead-Miami Speedway': 'Homestead, FL',
    'Kansas Speedway': 'Kansas City, KS',
    'Las Vegas Motor Speedway': 'Las Vegas, NV',
    'Chicago Motor Speedway': 'Cicero, IL',
    'Chicagoland Speedway': 'Joliet, IL',
    'Kentucky Speedway': 'Sparta, KY',
    'Nashville Superspeedway': 'Lebanon, TN',
    'Gateway Motorsports Park': 'Madison, IL',
    'World Wide Technology Raceway': 'Madison, IL',
    'Gateway': 'Madison, IL',
    'Gateway International Raceway': 'Madison, IL',
    'Dover Motor Speedway': 'Dover, DE',
    'Dover International Speedway': 'Dover, DE',
    'Dover Downs International Speedway': 'Dover, DE',
    'Phoenix Raceway': 'Avondale, AZ',
    'Phoenix International Raceway': 'Avondale, AZ',
    'ISM Raceway': 'Avondale, AZ',
    'New Hampshire Motor Speedway': 'Loudon, NH',
    'Loudon': 'Loudon, NH',
    'Richmond Raceway': 'Richmond, VA',
    'Richmond International Raceway': 'Richmond, VA',
    'Bristol Motor Speedway': 'Bristol, TN',
    'Martinsville Speedway': 'Martinsville, VA',
    'North Wilkesboro Speedway': 'North Wilkesboro, NC',
    'Rockingham Speedway': 'Rockingham, NC',
    'North Carolina Speedway': 'Rockingham, NC',
    'Darlington Raceway': 'Darlington, SC',
    'Sonoma Raceway': 'Sonoma, CA',
    'Infineon Raceway': 'Sonoma, CA',
    'Watkins Glen International': 'Watkins Glen, NY',
    'Watkins Glen': 'Watkins Glen, NY',
    'Road America': 'Elkhart Lake, WI',
    'Road Atlanta': 'Braselton, GA',
    'Mid-Ohio Sports Car Course': 'Lexington, OH',
    'Iowa Speedway': 'Newton, IA',
    'Iowa': 'Newton, IA',
    'Memphis Motorsports Park': 'Millington, TN',
    'Evergreen Speedway': 'Monroe, WA',
    'Nazareth Speedway': 'Nazareth, PA',
    'South Boston Speedway': 'South Boston, VA',
    'Myrtle Beach Speedway': 'Myrtle Beach, SC',
    'Hickory Motor Speedway': 'Hickory, NC',
    'Orange County Speedway': 'Rougemont, NC',
    'Tucson Raceway Park': 'Tucson, AZ',
    'Milwaukee Mile': 'West Allis, WI',
    'Pikes Peak International Raceway': 'Fountain, CO',
    'Kentucky Motor Speedway': 'Whitesville, KY',
    'Louisville Motor Speedway': 'Louisville, KY',
    'Flemington Speedway': 'Flemington, NJ',
    'Thompson Speedway': 'Thompson, CT',
    'Waterford Speedbowl': 'Waterford, CT',
    'Stafford Motor Speedway': 'Stafford, CT',
    'Seekonk Speedway': 'Seekonk, MA',
    'Riverhead Raceway': 'Riverhead, NY',
    'Laguna Seca Raceway': 'Monterey, CA',
    'Lime Rock Park': 'Lakeville, CT',
    'Mosport Park': 'Bowmanville, Ontario, Canada',
    'Mosport': 'Bowmanville, Ontario, Canada',
    'Canadian Tire Motorsport Park': 'Bowmanville, Ontario, Canada',
    'Mount Panorama Circuit': 'Bathurst, New South Wales, Australia',
    'Yas Marina Circuit': 'Abu Dhabi, United Arab Emirates',
    'Circuit de la Sarthe': 'Le Mans, France',
    'Brands Hatch': 'Kent, England, UK',
    'Silverstone Circuit': 'Silverstone, England, UK',
    'Suzuka Circuit': 'Suzuka, Japan',
    'Sebring International Raceway': 'Sebring, FL',
    'Armory Digital Superspeedway': 'Digital, USA',
    'Willow Springs Raceway': 'Rosamond, CA',
    'Irwindale Speedway': 'Irwindale, CA',
    'Portland International Raceway': 'Portland, OR',
    'Circuit Of The Americas': 'Austin, TX',
    'COTA': 'Austin, TX',
    'Twin Ring Motegi': 'Motegi, Japan',
    'Calder Thunderdome': 'Melbourne, Victoria, Australia',
    'Chicago Street Circuit': 'Chicago, IL',
    'New Jersey Motorsports Park': 'Millville, NJ',
    'Iowa Speedway #2': 'Newton, IA',
    'Eldora Speedway': 'Rossburg, OH',
    'Mid-Ohio': 'Lexington, OH',
    'Mount Panorama-Bathurst': 'Bathurst, New South Wales, Australia',
    'Bahrain International Circuit': 'Sakhir, Bahrain',
    'Autodromo Hermanos Rodriguez': 'Mexico City, Mexico',
    'Autódromo Hermanos Rodríguez': 'Mexico City, Mexico',
    'Concord Motorsport Park': 'Concord, NC',
    'Kyalami': 'Midrand, South Africa',
    "Lowe's Dirt Track 2012": 'Concord, NC',
    'Lowes Dirt Track 2012': 'Concord, NC',
    'Miami Hard Rock Stadium Circuit': 'Miami Gardens, FL',
    'Nashville SS DAY WKC': 'Lebanon, TN',
    'Saint Petersburg 13': 'St. Petersburg, FL',
    'St. Petersburg 13': 'St. Petersburg, FL',
    'Sydney Motorsport Park SuperNight': 'Sydney, New South Wales, Australia',
    'The Chili Bowl': 'Tulsa, OK',
    'BTCC Brands Hatch': 'Kent, England, UK',
}


def _track_core(name_upper):
    n = re.sub(r'[^A-Z0-9 ]', ' ', name_upper)
    n = re.sub(r'\s{2,}', ' ', n).strip()
    # Remove trailing version qualifiers iteratively
    while True:
        old = n
        n = re.sub(r'\s+\d{4}\s*$', '', n)            # trailing year (4 digits)
        n = re.sub(r'\s*\([^)]*\)\s*$', '', n)          # trailing parenthetical qualifiers
        n = re.sub(r'\s+(NIGHT|DAY|WKC)\s*$', '', n)    # trailing version word
        if n == old:
            break
    tokens = [t for t in n.split() if t not in _TRACK_SUFFIX_WORDS]
    return ' '.join(tokens) or name_upper


# Known misspellings/typos in the source data -- add more as you find them.
# Keyed by the name lowercased with punctuation stripped.
NAME_FIXES = {
    'bj mcloed': 'BJ McLeod',
    'jeffery earnhardt': 'Jeffrey Earnhardt',
    'truex': 'Ryan Truex',
    'earnhardt': 'Jeffrey Earnhardt',
    'k busch': 'Kyle Busch',
}

TEAM_FIXES = {
    'jtg daurtghy racing': 'JTG Daugherty Racing',
    'jtg daugherty': 'JTG Daugherty Racing',
    'jtg daughrety racing': 'JTG Daugherty Racing',
    'jtg daughtery racing': 'JTG Daugherty Racing',
    'hendrick': 'Hendrick Motorsports',
    'stewart haas racing': 'Stewart-Haas Racing',
    'tony stewart racing': 'Stewart-Haas Racing',
    'dgr crosley racing': 'DGR-Crosley',
}

TEAM_DISPLAY = {
    'Stewart-Haas Racing': 'Stewart-Haas Racing/Tony Stewart Racing',
}

MANUFACTURER_ABBREV = {'CHEVY': 'Chevrolet', 'DODGE': 'Dodge', 'TOYOTA': 'Toyota', 'FORD': 'Ford'}



MANUFACTURER_MAP = {
    'hendrick motorsports': 'Chevrolet',
    'richard childress racing': 'Chevrolet',
    'childress racing': 'Chevrolet',
    'jr motorsports': 'Chevrolet',
    'jtg daugherty racing': 'Chevrolet',
    'spire motorsports': 'Chevrolet',
    'kaulig racing': 'Chevrolet',
    'trackhouse racing': 'Chevrolet',
    'dgm racing': 'Chevrolet',
    'gms racing': 'Chevrolet',
    'b j mcleod motorsports': 'Chevrolet',
    'bj mcleod motorsports': 'Chevrolet',
    'our motorsports': 'Chevrolet',
    'youngs motorsports': 'Chevrolet',
    'ss greenlight racing': 'Chevrolet',
    'ss racing': 'Chevrolet',
    'mcm racing': 'Chevrolet',
    'nurtec racing': 'Chevrolet',
    'joe gibbs racing': 'Toyota',
    '23xi racing': 'Toyota',
    'leavine family racing': 'Toyota',
    'kyle busch motorsports': 'Toyota',
    'team penske': 'Ford',
    'stewart-haas racing': 'Ford',
    'wood brothers racing': 'Ford',
    'rfk racing': 'Ford',
    'front row motorsports': 'Ford',
    'roush fenway keselowski racing': 'Ford',
    'rick ware racing': 'Ford',
    'nascar technical institute': 'Chevrolet',
}

def manufacturer_for(team_name):
    cn = clean_team_name(team_name).lower()
    if cn in MANUFACTURER_MAP:
        return MANUFACTURER_MAP[cn]
    for keyword, make in [('chevrolet', 'Chevrolet'), ('chevy', 'Chevrolet'), ('ford', 'Ford'), ('toyota', 'Toyota'), ('dodge', 'Dodge')]:
        if keyword in cn:
            return make
    return None


MANUFACTURER_NAMES_LOWER = {'chevrolet', 'ford', 'toyota', 'dodge'}

def is_manufacturer_name(name):
    cn = clean_team_name(name).strip().lower()
    return cn in MANUFACTURER_NAMES_LOWER


def format_track_name(name):
    """Convert all-caps track names to Title Case. Leave already-formatted names alone."""
    if not name:
        return name
    if name != name.upper():
        return name
    SPECIAL_TOKENS = {'II', 'III', 'IV', 'WKC', 'NTT', 'ISM', 'IMS', 'IRP', 'NSCS'}
    n = name.title()
    # Fix known patterns
    n = n.replace(' Of ', ' of ').replace(' At ', ' at ').replace(' And ', ' and ')
    # Fix special tokens that should stay uppercase
    result = []
    for tok in n.split():
        if tok.upper() in SPECIAL_TOKENS:
            result.append(tok.upper())
        else:
            result.append(tok)
    return ' '.join(result)


def clean_team_name(name):
    if not name:
        return name
    n = clean_name(name)
    fix_key = re.sub(r'[-]', ' ', n.lower())
    fix_key = re.sub(r'[^a-z ]', '', fix_key)
    fix_key = re.sub(r'\s+', ' ', fix_key).strip()
    if fix_key in TEAM_FIXES:
        n = TEAM_FIXES[fix_key]
    return n


def clean_name(name):
    """Strip rookie/parenthetical tags like (R) or (##), stray asterisks, and
    leading/trailing hyphens left over from spreadsheet formatting quirks.
    Also corrects known misspellings via NAME_FIXES."""
    if not name:
        return name
    n = str(name).strip()
    n = re.sub(r'\([^)]*\)', '', n)          # remove any (...) tag, e.g. (R), (##)
    n = n.replace('*', '').replace(',', '').replace('.', '')
    n = re.sub(r'^[\s\-]+|[\s\-]+$', '', n)  # strip leading/trailing hyphens & whitespace
    n = re.sub(r'\s+', ' ', n).strip()
    fix_key = re.sub(r'[^a-z ]', '', n.lower()).strip()
    fix_key = re.sub(r'\s+', ' ', fix_key)
    if fix_key in NAME_FIXES:
        n = NAME_FIXES[fix_key]
    return n


def split_driver_names(s):
    """A roster cell can list a shared ride as 'Driver A/Driver B/Driver C' --
    split that into individual clean driver names."""
    if not s:
        return []
    return [clean_name(p) for p in str(s).split('/') if clean_name(p)]


def slugify(name):
    if not name:
        return 'unknown'
    s = clean_name(name)
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return s or 'unknown'


def esc(v):
    if v is None:
        return ''
    return htmlmod.escape(str(v))


def fnum(v, decimals=None):
    if v is None:
        return '-'
    try:
        f = float(v)
    except (ValueError, TypeError):
        return esc(v)
    if decimals is not None:
        return f"{f:.{decimals}f}"
    if f == int(f):
        return str(int(f))
    return f"{f:.2f}"


def badge(series):
    return f'<span class="badge {series}">{SERIES_LABELS.get(series, series)}</span>'


def table_html(headers, rows, row_classes=None, aligns=None, row_attrs=None, table_id=None):
    """rows: list of list of pre-escaped cell strings (in header order)."""
    aligns = aligns or {}
    idattr = f' id="{table_id}"' if table_id else ''
    out = [f'<table class="data"{idattr}><thead><tr>']
    for i, h in enumerate(headers):
        cls = ' class="num"' if aligns.get(i) == 'num' else ''
        out.append(f'<th{cls}>{esc(h)}</th>')
    out.append('</tr></thead><tbody>')
    for ri, row in enumerate(rows):
        rc = (row_classes[ri] if row_classes else '')
        ra = (row_attrs[ri] if row_attrs else '')
        out.append(f'<tr class="{rc}" {ra}>')
        for i, cell in enumerate(row):
            cls = ' class="num"' if aligns.get(i) == 'num' else ''
            out.append(f'<td{cls}>{cell}</td>')
        out.append('</tr>')
    out.append('</tbody></table>')
    return ''.join(out)


class SiteBuilder:
    def __init__(self, xlsx_data, races, out_dir, site_name='Sim Racing Reference'):
        self.career = {clean_name(k): v for k, v in xlsx_data['career'].items() if '/' not in k}
        self.seasons = xlsx_data['seasons']
        self.races = races
        self.out_dir = out_dir
        self.site_name = site_name
        self.env = Environment(loader=FileSystemLoader(os.path.join(HERE, 'templates')))
        self.base_tpl = self.env.get_template('base.html')

        self.driver_slugs = {}
        self.team_slugs = {}
        bfy = os.path.join(HERE, 'driver_birth_years.json')
        self.birth_years = json.load(open(bfy)) if os.path.exists(bfy) else {}
        # Add placeholder birth years for any driver without one
        for d in self.career:
            if d not in self.birth_years:
                self.birth_years[d] = 0
        # Rebuild the JSON so all drivers appear with placeholder years for manual editing
        if self.birth_years:
            with open(bfy, 'w') as f:
                json.dump(dict(sorted(self.birth_years.items())), f, indent=2)
        self._build_indexes()

    @staticmethod
    def _compute_points(finish, led, start):
        """Compute points using the custom system:
        1st=45, 2nd=39, then -1 per position,
        +1 for most laps led, +1 for leading at least 1 lap, +1 for pole."""
        try:
            fin = int(finish)
        except (ValueError, TypeError):
            return 0.0
        if fin == 1:
            base = 45
        elif fin == 2:
            base = 39
        else:
            base = max(0, 41 - fin)
        led_raw = str(led or '').strip()
        has_star = '*' in led_raw
        if has_star:
            base += 1
        num_str = led_raw.rstrip('*').strip()
        if num_str and num_str != '-':
            try:
                if int(num_str) > 0:
                    base += 1
            except ValueError:
                pass
        elif has_star and not num_str:
            base += 1
        try:
            st = int(start)
            if st == 1:
                base += 1
        except (ValueError, TypeError):
            pass
        return float(base)

    # ---------------------------------------------------------- indexing
    def _roster_lookup(self, series, year):
        """car# -> {'team':..., 'driver':...}, for a given series/year."""
        season = self.seasons.get(year, {})
        roster = season.get('roster', {}).get(series, [])
        lookup = {}
        stripped = {}  # alias: leading-zero-stripped key → original key
        for r in roster:
            if r['car']:
                key = str(r['car']).lstrip('#') or '0'
                lookup[key] = r
                alias = key.lstrip('0') or '0'
                if alias != key:
                    stripped[alias] = key
        # Add stripped aliases only when they don't collide with an existing entry.
        # This matches "08" → "8" (HTML) when no bare "8" roster entry exists,
        # while keeping "02" and "2" separate when both are present.
        for alias, original in stripped.items():
            if alias not in lookup:
                lookup[alias] = lookup[original]
        return lookup

    @staticmethod
    def _lastname(n):
        n = clean_name(n)
        parts = n.replace('.', '').replace(',', '').split()
        # drop generational suffixes so "Martin Truex Jr." matches "M. Truex"
        while parts and parts[-1].lower() in ('jr', 'sr', 'ii', 'iii', 'iv'):
            parts.pop()
        return parts[-1].lower() if parts else ''

    def _normalize_driver_name(self, race_name, roster_entry):
        """If the race file only recorded an initials-style name (common in
        older seasons before full names were supported), substitute the
        roster's full name when the last name matches."""
        race_name = clean_name(race_name)
        if not roster_entry:
            return race_name
        roster_name = clean_name(roster_entry['driver'] or '')
        if not roster_name:
            return race_name
        # Skip roster normalization if the roster name is a compound
        # (e.g. "Cole Custer/Kyle Larson" shared ride) – the race file
        # will have the actual driver's single name, not the compound string.
        if '/' in roster_name:
            return race_name
        if self._lastname(race_name) and self._lastname(race_name) == self._lastname(roster_name):
            return roster_name
        return race_name

    def _resolve_to_career(self, name):
        """Match a name against the Stats-sheet driver list: exact match first,
        then an unambiguous last-name match, then first-initial match.
        Returns None if it can't be resolved to a single Stats-sheet driver."""
        cn = clean_name(name)
        if not cn:
            return None
        if cn in self.career:
            return cn
        candidates = self.career_by_lastname.get(self._lastname(cn), [])
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            parts = cn.split()
            if len(parts) >= 2 and len(parts[0]) == 1 and parts[0][0].isalpha():
                initial = parts[0][0].upper()
                match = [c for c in candidates if c.startswith(initial)]
                if len(match) == 1:
                    return match[0]
        return None

    def _build_track_canon_map(self):
        raw_tracks = [clean_name(r['track']) for r in self.races if r.get('track')]
        counts = Counter(raw_tracks)
        groups = defaultdict(list)
        for raw in sorted(set(raw_tracks)):
            key = self._track_group_key(raw)
            groups[key].append(raw)
        canon_map = {}
        for key, members in groups.items():
            # Prefer a TRACK_ALIASES target if the key or any clean member matches
            alias_target = key if key in TRACK_ALIASES.values() else None
            if not alias_target:
                for m in members:
                    mc = re.sub(r'\s+', ' ', re.sub(r'[^A-Z0-9 ]', ' ', m.upper())).strip()
                    if mc in TRACK_ALIASES:
                        alias_target = TRACK_ALIASES[mc]
                        break
            canonical = alias_target or sorted(members, key=lambda m: (-counts[m], -len(m)))[0]
            for m in members:
                canon_map[m] = canonical
        return canon_map

    @staticmethod
    def _track_group_key(raw):
        """Normalize a track name for grouping: strip version suffixes (year,
        Night, parentheticals) first so they don't block TRACK_ALIASES matching,
        then fall back to core word stripping."""
        up = raw.upper()
        pre = up
        while True:
            old = pre
            pre = re.sub(r'\s+\d{4}\s*$', '', pre)
            pre = re.sub(r'\s*\([^)]*\)\s*$', '', pre)
            pre = re.sub(r'\s+(NIGHT|DAY|WKC)\s*$', '', pre)
            if pre == old:
                break
        # Strip non-alphanum so trademark symbols don't block TRACK_ALIASES
        pre_clean = re.sub(r'[^A-Z0-9 ]', ' ', pre)
        pre_clean = re.sub(r'\s+', ' ', pre_clean).strip()
        alias = TRACK_ALIASES.get(pre_clean)
        if alias:
            return alias
        return _track_core(up)

    def _build_indexes(self):
        self._allstar_race_keys = {(r['series'], r['year'], r['race_num']) for r in self.races if r.get('is_allstar')}
        self.driver_races = defaultdict(list)   # driver name -> [race appearance dict]
        self.team_races = defaultdict(list)     # team name -> [race appearance dict]
        self.driver_teams = defaultdict(set)     # driver -> set of team names (from races + rosters)
        self.team_drivers = defaultdict(set)
        self.track_races = defaultdict(list)     # canonical track name -> [race appearance-ish dict]
        # track -> driver -> series -> {wins, top5, poles, laps_led, finish_sum, finish_n}
        self.track_driver_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'top5': 0, 'poles': 0, 'laps_led': 0, 'finish_sum': 0, 'finish_n': 0, 'starts': 0})))

        self.career_by_lastname = defaultdict(list)
        for cname in self.career.keys():
            self.career_by_lastname[self._lastname(cname)].append(cname)

        self.track_canon = self._build_track_canon_map()

        roster_cache = {}

        def lookup_for(series, year):
            key = (series, year)
            if key not in roster_cache:
                roster_cache[key] = self._roster_lookup(series, year)
            return roster_cache[key]

        # ---- pass 1: best-effort per-row resolution (car+roster, then Stats sheet) ----
        raw_race_rows = []   # one entry per Race-session row across all races
        raw_qual_rows = []   # one entry per pole (first row) of each race's Qualifying session
        for race in sorted(self.races, key=lambda r: (r['year'], r['series'], r['race_num'])):
            lookup = lookup_for(race['series'], race['year'])
            raw_track = clean_name(race['track']) if race['track'] else race['track']
            track = self.track_canon.get(raw_track, raw_track)

            race_rows = race['sessions'].get('Race', [])
            for row in race_rows:
                drv_raw = (row.get('DRIVER') or '').strip()
                if not drv_raw:
                    continue
                car_raw = (row.get('#') or '').strip()
                car_norm = car_raw or '0'
                roster_entry = lookup.get(car_norm)
                team = clean_team_name(roster_entry['team']) if roster_entry else None
                drv_stage1 = self._normalize_driver_name(drv_raw, roster_entry)
                drv_resolved = self._resolve_to_career(drv_stage1)
                raw_race_rows.append({
                    'series': race['series'], 'year': race['year'], 'race_num': race['race_num'],
                    'track': track, 'date': race['date'], 'car_norm': car_norm,
                    'finish': row.get('F'), 'start': row.get('S'), 'car': car_raw,
                    'laps': row.get('LAPS'), 'led': row.get('LED'), 'points': row.get('POINTS'),
                    'status': row.get('STATUS'), 'team': team,
                    'drv_stage1': drv_stage1, 'drv_resolved': drv_resolved,
                })

            qual_rows = race['sessions'].get('Qualifying', [])
            if qual_rows:
                q = qual_rows[0]
                q_drv_raw = (q.get('DRIVER') or '').strip()
                if q_drv_raw:
                    car_raw = (q.get('#') or '').strip()
                    car_norm = car_raw or '0'
                    roster_entry = lookup.get(car_norm)
                    q_stage1 = self._normalize_driver_name(q_drv_raw, roster_entry)
                    q_resolved = self._resolve_to_career(q_stage1)
                    raw_qual_rows.append({
                        'series': race['series'], 'year': race['year'], 'car_norm': car_norm,
                        'drv_stage1': q_stage1, 'drv_resolved': q_resolved,
                    })

        # ---- build a per-(series, year, car#) "who actually drove this car" map from
        # whichever rows WERE resolved to a Stats-sheet driver, so races where the same
        # driver's name printed as a bare initial/last-name can still be merged in ----
        car_owner_votes = defaultdict(Counter)
        for r in raw_race_rows:
            if r['drv_resolved']:
                car_owner_votes[(r['series'], r['year'], r['car_norm'])][r['drv_resolved']] += 1
        car_owner = {k: v.most_common(1)[0][0] for k, v in car_owner_votes.items()}

        def finalize(r):
            if r['drv_resolved']:
                return r['drv_resolved']
            fallback = car_owner.get((r['series'], r['year'], r['car_norm']))
            return fallback or r['drv_stage1']

        # ---- pass 2: build appearances, race results index, track winners, poles ----
        races_by_key_tmp = defaultdict(list)
        for r in raw_race_rows:
            races_by_key_tmp[(r['series'], r['year'], r['race_num'])].append(r)

        self.driver_race_stats = defaultdict(lambda: defaultdict(lambda: {
            'starts': 0, 'wins': 0, 'top5': 0, 'top10': 0, 'poles': 0,
            'points': 0.0, 'finish_sum': 0.0, 'finish_n': 0, 'start_sum': 0.0, 'start_n': 0,
        }))  # driver -> series -> stat dict ('total' key holds the combined total)
        self.rookie_drivers = defaultdict(set)    # (series, year) -> set of rookie driver names
        self.rookie_of_year = {}                   # (series, year) -> resolved driver name or None

        for (series, year, race_num), rows in races_by_key_tmp.items():
            track = rows[0]['track']
            date = rows[0]['date']
            best_finish = None
            winner_drv = None
            for r in rows:
                drv = finalize(r)
                team = r['team']
                try:
                    fin = int(r['finish'])
                except (ValueError, TypeError):
                    fin = None
                try:
                    st = int(r['start'])
                except (ValueError, TypeError):
                    st = None
                pts = self._compute_points(r['finish'], r['led'], r['start'])

                appearance = {
                    'series': series, 'year': year, 'race_num': race_num,
                    'track': track, 'date': date,
                    'finish': r['finish'], 'start': r['start'], 'car': r['car'],
                    'laps': r['laps'], 'led': r['led'], 'points': pts,
                    'status': r['status'], 'team': team, 'driver': drv,
                }
                self.driver_races[drv].append(appearance)
                if team:
                    self.team_races[team].append(appearance)
                    self.driver_teams[drv].add(team)
                    self.team_drivers[team].add(drv)
                if (series, year, race_num) not in self._allstar_race_keys:
                    for bucket in (self.driver_race_stats[drv]['total'], self.driver_race_stats[drv][series]):
                        bucket['starts'] += 1
                        bucket['points'] += pts
                        if fin is not None:
                            bucket['finish_sum'] += fin
                            bucket['finish_n'] += 1
                            if fin == 1:
                                bucket['wins'] += 1
                            if fin <= 5:
                                bucket['top5'] += 1
                            if fin <= 10:
                                bucket['top10'] += 1
                        if st is not None:
                            bucket['start_sum'] += st
                            bucket['start_n'] += 1

                # Track-level driver stats
                for t_bucket in ('total', series):
                    tds = self.track_driver_stats[track][drv][t_bucket]
                    tds['starts'] += 1
                    if fin is not None:
                        tds['finish_sum'] += fin
                        tds['finish_n'] += 1
                        if fin == 1:
                            tds['wins'] += 1
                        if fin <= 5:
                            tds['top5'] += 1
                    if st == 1:
                        tds['poles'] += 1
                    led_raw = str(r['led'] or '').strip()
                    led_num = led_raw.rstrip('*').strip()
                    if led_num and led_num != '-':
                        try:
                            tds['laps_led'] += int(led_num.replace(',', ''))
                        except (ValueError, TypeError):
                            pass

                if fin is not None and (best_finish is None or fin < best_finish):
                    best_finish = fin
                    winner_drv = drv

            self.track_races[track].append({
                'series': series, 'year': year, 'race_num': race_num,
                'winner': winner_drv if rows else None, 'date': date,
            })

        for q in raw_qual_rows:
            if q['drv_resolved']:
                drv = q['drv_resolved']
            else:
                drv = car_owner.get((q['series'], q['year'], q['car_norm'])) or q['drv_stage1']
            for bucket_key in ('total', q['series']):
                self.driver_race_stats[drv][bucket_key]['poles'] += 1

        # also pull team/driver associations from season rosters (covers drivers who
        # appear in the roster but whose race file might use a slightly different name).
        # Shared-ride roster cells like "Driver A/Driver B" are split into individuals
        # and resolved against the Stats sheet wherever unambiguous.
        for year, season in self.seasons.items():
            for series, roster in season.get('roster', {}).items():
                for r in roster:
                    if r['driver'] and r['team']:
                        team_clean = clean_team_name(r['team'])
                        for indiv in split_driver_names(r['driver']):
                            resolved = self._resolve_to_career(indiv) or indiv
                            self.driver_teams[resolved].add(team_clean)
                            self.team_drivers[team_clean].add(resolved)

        # Build rookie lookups from rosters and standings (drivers with (R) in their name)
        for year, season in self.seasons.items():
            for series, roster in season.get('roster', {}).items():
                for r in roster:
                    raw_name = str(r.get('driver', ''))
                    if '(R)' in raw_name:
                        for indiv in split_driver_names(raw_name):
                            resolved = self._resolve_to_career(indiv) or indiv
                            self.rookie_drivers[(series, year)].add(resolved)
            for series in SERIES_ORDER:
                standings = season.get('driver_standings', {}).get(series, [])
                for rec in standings:
                    raw_name = str(rec.get('Driver') or rec.get('NAME') or '')
                    if '(R)' in raw_name:
                        drv = clean_name(raw_name)
                        resolved = self._resolve_to_career(drv) or drv
                        self.rookie_drivers[(series, year)].add(resolved)

        # Build Rookie of the Year lookup from awards data
        for year, season in self.seasons.items():
            awards = season.get('awards', {})
            for series in SERIES_ORDER:
                rook_raw = awards.get(series, {}).get('Rookie of the Year')
                if rook_raw:
                    roty = clean_name(rook_raw)
                    roty = self._resolve_to_career(roty) or roty
                    self.rookie_of_year[(series, int(year))] = roty

        # driver pages are only built for drivers who appear on the Stats sheet
        self.driver_slugs = {name: slugify(name) for name in self.career.keys()}
        for t in self.team_drivers.keys():
            self.team_slugs[t] = slugify(t)

        self.all_drivers = sorted(self.driver_slugs.keys())
        self.all_teams = sorted(self.team_slugs.keys())

        # races indexed by series/year/race_num for quick lookup + season/standings
        self.races_by_key = {(r['series'], r['year'], r['race_num']): r for r in self.races}
        self.years_by_series = defaultdict(set)
        for r in self.races:
            self.years_by_series[r['series']].add(r['year'])
        self.track_slugs = {t: slugify(t) for t in self.track_races.keys()}

    def _champion_for(self, series, year):
        """Return the champion driver name for a series/year, or None."""
        standings = self.seasons.get(year, {}).get('driver_standings', {}).get(series, [])
        if standings:
            drv = clean_name(standings[0].get('Driver') or standings[0].get('NAME'))
            return self._resolve_to_career(drv) or drv
        return None

    def _season_finish(self, driver, series, year):
        """Return the final championship position for a driver in a series/year, or None."""
        standings = self.seasons.get(year, {}).get('driver_standings', {}).get(series, [])
        for rec in standings:
            drv = clean_name(rec.get('Driver') or rec.get('NAME'))
            drv = self._resolve_to_career(drv) or drv
            if drv == driver:
                try:
                    return int(re.sub(r'\D', '', str(rec.get('Pos.', ''))))
                except (ValueError, TypeError):
                    return None
        return None

    def _computed_stats_for(self, name):
        """Career stats computed directly from parsed race results (not the workbook)."""
        raw = self.driver_race_stats.get(name)
        if not raw:
            return None

        def finish_stat(bucket):
            out = dict(bucket)
            out['avg_f'] = (bucket['finish_sum'] / bucket['finish_n']) if bucket['finish_n'] else None
            out['avg_s'] = (bucket['start_sum'] / bucket['start_n']) if bucket['start_n'] else None
            return out

        result = {'total': finish_stat(raw.get('total', {})) if raw.get('total') else None}
        for series in SERIES_ORDER:
            result[series] = finish_stat(raw[series]) if raw.get(series) else {'starts': 0}
        return result

    # ---------------------------------------------------------- rendering plumbing
    def _write(self, rel_path, title, content_html):
        depth = rel_path.count('/')
        base = '../' * depth
        html_out = self.base_tpl.render(title=title, content=content_html, base=base, site_name=self.site_name)
        full = os.path.join(self.out_dir, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            f.write(html_out)

    def link(self, rel_path, depth_from):
        return ('../' * depth_from) + rel_path

    def _team_link(self, team_name, depth=1):
        cn = clean_team_name(team_name)
        tslug = self.team_slugs.get(cn)
        if tslug:
            return f'<a href="{"../"*depth}teams/{tslug}.html">{esc(cn)}</a>'
        return esc(cn) if cn else ''

    # ---------------------------------------------------------- pages
    def build(self):
        os.makedirs(self.out_dir, exist_ok=True)
        shutil.copytree(os.path.join(HERE, 'static'), os.path.join(self.out_dir, 'static'), dirs_exist_ok=True)
        self._build_home()
        for series in SERIES_ORDER:
            self._build_series_index(series)
            for year in sorted(self.years_by_series.get(series, [])):
                self._build_season_page(series, year)
                self._build_standings_page(series, year)
                for (s, y, rn), race in self.races_by_key.items():
                    if s == series and y == year:
                        self._build_race_page(race)
        self._build_records()
        self._build_allstar_page()
        self._build_drivers_index()
        self._build_driver_stats_page()
        for slug in sorted(set(self.driver_slugs.values())):
            self._build_driver_page(slug)
        self._build_teams_index()
        self._build_team_stats_page()
        for slug in sorted(set(self.team_slugs.values())):
            self._build_team_page(slug)
        self._build_tracks_index()
        for slug in sorted(set(self.track_slugs.values())):
            self._build_track_page(slug)
        self._generate_search_data()
        self._build_driver_compare_page()

    def _tab_image_html(self, name):
        tab_dir = os.path.join(HERE, 'static', 'tab-images')
        for ext in ('jpg', 'jpeg', 'png', 'webp', 'avif'):
            path = os.path.join(tab_dir, f'{name}.{ext}')
            if os.path.exists(path):
                return f'<img src="static/tab-images/{name}.{ext}" alt="" style="width:100%;object-fit:contain;border-radius:4px;margin-bottom:10px;display:block;background:#f0f0f0">'
        return ''

    def _build_home(self):
        rows = []
        for series in SERIES_ORDER:
            years = sorted(self.years_by_series.get(series, []))
            if not years:
                continue
            latest = years[-1]
            n_races = sum(1 for r in self.races if r['series'] == series and not r.get('is_allstar'))
            logo = SERIES_LOGO.get(series)
            logo_html = f'<img src="{logo}" alt="{SERIES_LABELS[series]}" style="max-width:100%;height:auto;max-height:80px;display:block;margin:0 auto 8px">' if logo else ''
            rows.append(f'''<div class="card">
                {logo_html}
                <h3>{badge(series)}</h3>
                <div class="stat-row"><span>Seasons on file</span><span>{years[0]}&ndash;{latest}</span></div>
                <div class="stat-row"><span>Races on file</span><span>{n_races}</span></div>
                <p><a href="seasons/{series}/index.html">Browse seasons &rarr;</a></p>
            </div>''')

        content = f'''
        <div class="hero"><div class="wrap">
          <h1 style="color:blue">Sim Racing Reference</h1>
          <p>Race results, driver careers, team histories, and season standings for the NR2003 sim universe &mdash; built from {sum(1 for r in self.races if not r.get('is_allstar'))} race files.</p>
        </div></div>
        <div class="wrap" style="padding-top:24px">
        <div class="grid">{''.join(rows)}</div>
        <div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(280px,1fr))">
          <div class="panel"><h2>Drivers</h2><div class="body">
            {self._tab_image_html('drivers')}
            <p>{len(self.all_drivers)} drivers on record.</p>
            <p><a href="drivers/index.html">Browse drivers &rarr;</a><br><a href="drivers/stats.html">Career stats &rarr;</a></p>
          </div></div>
          <div class="panel"><h2>Teams</h2><div class="body">
            {self._tab_image_html('teams')}
            <p>{len(self.all_teams)} teams on record.</p>
            <p><a href="teams/index.html">Browse teams &rarr;</a><br><a href="teams/stats.html">Career stats &rarr;</a></p>
          </div></div>
          <div class="panel"><h2>Tracks</h2><div class="body">
            {self._tab_image_html('tracks')}
            <p>{len(self.track_slugs)} tracks on record.</p>
            <p><a href="tracks/index.html">Browse tracks &rarr;</a></p>
          </div></div>
        </div>
        </div>
        '''
        self._write('index.html', 'Home', content)

    def _build_series_index(self, series):
        years = sorted(self.years_by_series.get(series, []))
        links = ''.join(f'<a href="{y}/index.html">{y}</a>' for y in years)
        logo = SERIES_LOGO.get(series)
        logo_html = f'<img src="../../{logo}" alt="{SERIES_LABELS[series]}" style="max-width:100%;height:auto;max-height:80px;display:block;margin:0 auto 16px">' if logo else ''
        champ_rows = []
        for year in reversed(years):
            n_races = sum(1 for r in self.races if r['series'] == series and r['year'] == year and not r.get('is_allstar'))
            year_link = f'<a href="{year}/index.html">{year}</a>'
            awards = self.seasons.get(year, {}).get('awards', {}).get(series, {})

            # driver champion
            champ = self._champion_for(series, year)
            if not champ:
                continue
            dslug = self.driver_slugs.get(champ)
            champ_cell = f'<a href="../../drivers/{dslug}.html">{esc(champ)}</a>' if dslug else esc(champ)

            # champion's team(s) that season
            lookup = self._roster_lookup(series, year)
            champ_teams = set()
            for entry in lookup.values():
                for indiv in split_driver_names(entry['driver']):
                    resolved = self._resolve_to_career(indiv) or indiv
                    if resolved == champ:
                        champ_teams.add(clean_team_name(entry['team']))
            team_cell = ', '.join(f'<a href="../../teams/{self.team_slugs.get(t, slugify(t))}.html">{esc(t)}</a>' for t in sorted(champ_teams)) or '-'

            # owner champion (from awards or team_points)
            owner_champ_cell = '-'
            owner_raw = awards.get('Team Champion')
            if owner_raw:
                tp_team = clean_team_name(owner_raw)
                tslug = self.team_slugs.get(tp_team)
                owner_champ_cell = f'<a href="../../teams/{tslug}.html">{esc(tp_team)}</a>' if tslug else esc(tp_team)
            else:
                team_pts = self.seasons.get(year, {}).get('team_points', {}).get(series, [])
                if team_pts and team_pts[0]:
                    tp_team = clean_team_name(team_pts[0].get('team', ''))
                    if tp_team:
                        tslug = self.team_slugs.get(tp_team)
                        owner_champ_cell = f'<a href="../../teams/{tslug}.html">{esc(tp_team)}</a>' if tslug else esc(tp_team)

            # manufacturer champion (from awards or computed from team_points)
            mfg_champ_cell = '-'
            mfg_raw = awards.get('Manufactuer Champion')
            if mfg_raw:
                mfg_raw = MANUFACTURER_ABBREV.get(mfg_raw.upper().strip(), mfg_raw)
                mfg_champ_cell = esc(mfg_raw)
            else:
                team_pts = self.seasons.get(year, {}).get('team_points', {}).get(series, [])
                if team_pts:
                    mfg_scores = defaultdict(float)
                    for tp in team_pts:
                        mfg = manufacturer_for(tp.get('team', ''))
                        if mfg:
                            mfg_scores[mfg] += float(tp.get('points', 0))
                    if mfg_scores:
                        mfg_champ = max(mfg_scores, key=mfg_scores.get)
                        mfg_champ_cell = esc(mfg_champ)

            # rookie of the year (from awards or fallback to (R) in standings)
            rook_cell = '-'
            rook_raw = awards.get('Rookie of the Year')
            if rook_raw:
                rooki = clean_name(rook_raw)
                rooki = self._resolve_to_career(rooki) or rooki
                rslug = self.driver_slugs.get(rooki)
                rook_cell = f'<a href="../../drivers/{rslug}.html">{esc(rooki)}</a>' if rslug else esc(rooki)
            else:
                raw_standings = self.seasons.get(year, {}).get('driver_standings', {}).get(series, [])
                for rec in raw_standings:
                    raw_name = rec.get('Driver') or rec.get('NAME') or ''
                    if '(R)' in raw_name.upper() or '(R)' in raw_name:
                        rooki = clean_name(raw_name)
                        rooki = self._resolve_to_career(rooki) or rooki
                        rslug = self.driver_slugs.get(rooki)
                        rook_cell = f'<a href="../../drivers/{rslug}.html">{esc(rooki)}</a>' if rslug else esc(rooki)
                        break

            champ_rows.append([year_link, champ_cell, team_cell, owner_champ_cell, mfg_champ_cell, rook_cell, str(n_races)])
        champ_tbl = ''
        if champ_rows:
            ch_headers = ['Year', 'Champion', "Champion's Team", 'Owner Champion', 'Mfg Champion', 'Rookie of the Year', 'Races']
            champ_tbl = f'<div class="panel"><h2>Season Champions</h2><div class="body">{table_html(ch_headers, champ_rows, aligns={0: "num", 6: "num"}, table_id="champion-table")}</div></div>'
        content = f'''
        <div class="breadcrumb"><a href="../../index.html">Home</a> / {SERIES_LABELS[series]}</div>
        {logo_html}
        <h1 class="page-title">{SERIES_LABELS[series]}</h1>
        <p class="subtitle">Select a season to view the schedule, race results, and standings.</p>
        {champ_tbl}
        <div class="season-index">{links}</div>
        '''
        self._write(f'seasons/{series}/index.html', f'{SERIES_LABELS[series]}', content)

    def _schedule_rows_html(self, series, year):
        season = self.seasons.get(year, {})
        schedule = season.get('schedule', {}).get(series, [])
        seen_rns = {e['race_num'] for e in schedule}
        # Add races from parsed files that are not in workbook schedule
        all_rns = sorted({r['race_num'] for r in self.races if r['series'] == series and r['year'] == year})
        for rn in all_rns:
            if rn not in seen_rns:
                race = self.races_by_key.get((series, year, rn))
                if race and not race.get('is_allstar'):
                    # Create dummy workbook entry
                    schedule.append({'race_num': rn, 'track': race['track']})
        schedule.sort(key=lambda e: e['race_num'])
        rows = []
        cls = []
        for entry in schedule:
            rn = entry['race_num']
            race = self.races_by_key.get((series, year, rn))
            if race and race.get('is_allstar'):
                continue
            if race:
                canon_track = format_track_name(self.track_canon.get(clean_name(race['track']), clean_name(race['track'])))
                link = f'<a class="plain" href="../../../races/{series}/{year}/R{rn}.html">{esc(canon_track)}</a>'
                race_rows = race['sessions'].get('Race', [])
                cars = str(len(race_rows)) if race_rows else '-'

                # Total laps (max LAPS from any driver)
                laps = '-'
                if race_rows:
                    max_laps = 0
                    for row in race_rows:
                        try:
                            l = int(row.get('LAPS', 0))
                            if l > max_laps:
                                max_laps = l
                        except (ValueError, TypeError):
                            pass
                    laps = str(max_laps) if max_laps > 0 else '-'

                # Track miles
                raw_track = clean_name(race['track'])
                canon_for_len = self.track_canon.get(raw_track, raw_track)
                track_len = TRACK_LENGTHS.get(canon_for_len, None)
                if track_len is None:
                    track_len = TRACK_LENGTHS.get(canon_track, None)
                miles = '-'
                if track_len and laps != '-':
                    try:
                        miles = f'{track_len * max_laps:.1f}'
                    except (ValueError, TypeError):
                        pass

                # Pole winner (P=1 from Qualifying)
                pole = '-'
                q_rows = race['sessions'].get('Qualifying', [])
                if q_rows:
                    for qr in q_rows:
                        if qr.get('P') == '1' or qr.get('P') == 1:
                            pole_name = qr.get('DRIVER', '')
                            if pole_name:
                                lookup = self._roster_lookup(series, year)
                                car_norm = (qr.get('#') or '').strip() or '0'
                                roster_entry = lookup.get(car_norm)
                                pole_name = self._normalize_driver_name(pole_name, roster_entry)
                                pole_name = self._resolve_to_career(pole_name) or pole_name
                                pslug = self.driver_slugs.get(pole_name)
                                pole = f'<a href="../../../drivers/{pslug}.html">{esc(pole_name)}</a>' if pslug else esc(pole_name)
                            break

                winner = ''
                if race_rows:
                    lookup = self._roster_lookup(series, year)
                    first = race_rows[0]
                    car_norm = (first.get('#') or '').strip() or '0'
                    roster_entry = lookup.get(car_norm)
                    winner_name = self._normalize_driver_name(first.get('DRIVER'), roster_entry)
                    winner_name = self._resolve_to_career(winner_name) or winner_name
                    wslug = self.driver_slugs.get(winner_name)
                    winner = f'<a href="../../../drivers/{wslug}.html">{esc(winner_name)}</a>' if wslug else esc(winner_name)
                    winner = f'<span class="hl-winner">{winner}</span>'
                status = 'On file'
            else:
                link = esc(format_track_name(entry['track']))
                cars = '-'
                laps = '-'
                miles = '-'
                pole = '-'
                winner = '-'
                status = '<span style="color:#a89f8c">No file</span>'
            rows.append([str(rn), link, cars, laps, miles, pole, winner, status])
            cls.append('')
        return rows

    def _build_season_page(self, series, year):
        rows = self._schedule_rows_html(series, year)
        tbl = table_html(['#', 'Track', 'Cars', 'Laps', 'Miles', 'Pole', 'Winner', 'Status'], rows, aligns={0: 'num', 2: 'num', 3: 'num', 4: 'num'})

        roster = self.seasons.get(year, {}).get('roster', {}).get(series, [])
        roster_rows = []
        seen = set()
        for entry in roster:
            for indiv in split_driver_names(entry.get('driver', '')):
                indiv = self._resolve_to_career(indiv) or indiv
                dedup_key = (entry.get('car', ''), indiv)
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)
                dslug = self.driver_slugs.get(indiv)
                drv_cell = f'<a href="../../../drivers/{dslug}.html">{esc(indiv)}</a>' if dslug else esc(indiv)
                team_clean = clean_team_name(entry.get('team', ''))
                tslug = self.team_slugs.get(team_clean)
                team_cell = f'<a href="../../../teams/{tslug}.html">{esc(team_clean)}</a>' if tslug else esc(team_clean)
                drv_display = drv_cell
                if indiv in self.rookie_drivers.get((series, year), set()):
                    drv_display += ' (R)'
                roster_rows.append([esc(entry.get('car', '')), drv_display, team_cell])
        roster_tbl = ''
        if roster_rows:
            roster_tbl = f'<div class="panel"><h2>Roster</h2><div class="body">{table_html(["#", "Driver", "Team"], roster_rows, aligns={0: "num"})}</div></div>'

        content = f'''
        <div class="breadcrumb"><a href="../../../index.html">Home</a> / <a href="../index.html">{SERIES_LABELS[series]}</a> / {year}</div>
        <h1 class="page-title">{year} {SERIES_LABELS[series]}</h1>
        <p class="subtitle"><a href="../../../standings/{series}/{year}.html">View {year} points standings &rarr;</a></p>
        <div class="panel"><h2>Schedule &amp; Results</h2><div class="body">{tbl}</div></div>
        {roster_tbl}
        '''
        self._write(f'seasons/{series}/{year}/index.html', f'{year} {SERIES_LABELS[series]}', content)

    def _standings_rows_from_sheet(self, series, year):
        season = self.seasons.get(year, {})
        data = season.get('driver_standings', {}).get(series, [])
        rows = []
        row_classes = []
        for rec in data:
            drv_clean = clean_name(rec.get('Driver') or rec.get('NAME'))
            drv_clean = self._resolve_to_career(drv_clean) or drv_clean
            slug = self.driver_slugs.get(drv_clean)
            drv_link = f'<a href="../../drivers/{slug}.html">{esc(drv_clean)}</a>' if slug else esc(drv_clean)
            if drv_clean in self.rookie_drivers.get((series, year), set()):
                drv_link += ' (R)'
            team_raw = clean_team_name(rec.get('Team')) if rec.get('Team') else None
            t_cell = esc(team_raw) if team_raw else ''
            if team_raw:
                tslug = self.team_slugs.get(team_raw)
                if tslug:
                    t_cell = f'<a href="../../teams/{tslug}.html">{esc(team_raw)}</a>'
            rows.append([
                esc(rec.get('Pos.')), esc(rec.get('#')), drv_link, t_cell,
                esc(rec.get('ST')), esc(rec.get('W')), esc(rec.get('T5')), esc(rec.get('T10')),
                fnum(rec.get('AvFP'), 1), esc(rec.get('P')), fnum(rec.get('AvSP'), 1), esc(rec.get('PTS')),
            ])
            cls = 'roty' if drv_clean == self.rookie_of_year.get((series, year)) else ''
            row_classes.append(cls)
        return rows, row_classes

    def _standings_rows_computed(self, series, year):
        lookup = self._roster_lookup(series, year)
        totals = defaultdict(lambda: {'pts': 0.0, 'starts': 0, 'wins': 0, 'top5': 0, 'top10': 0, 'car': None, 'team': None})
        for r in self.races:
            if r['series'] != series or r['year'] != year or r.get('is_allstar'):
                continue
            for row in r['sessions'].get('Race', []):
                drv_raw = (row.get('DRIVER') or '').strip()
                if not drv_raw:
                    continue
                car_norm = (row.get('#') or '').strip() or '0'
                roster_entry = lookup.get(car_norm)
                drv = self._normalize_driver_name(drv_raw, roster_entry)
                drv = self._resolve_to_career(drv) or drv
                pts = self._compute_points(row.get('F'), row.get('LED'), row.get('S'))
                try:
                    fin = int(row.get('F'))
                except (ValueError, TypeError):
                    fin = 99
                t = totals[drv]
                t['pts'] += pts
                t['starts'] += 1
                t['wins'] += 1 if fin == 1 else 0
                t['top5'] += 1 if fin <= 5 else 0
                t['top10'] += 1 if fin <= 10 else 0
                t['car'] = row.get('#')
        ordered = sorted(totals.items(), key=lambda kv: -kv[1]['pts'])
        rows = []
        row_classes = []
        for pos, (drv, t) in enumerate(ordered, start=1):
            slug = self.driver_slugs.get(drv)
            drv_link = f'<a href="../../drivers/{slug}.html">{esc(drv)}</a>' if slug else esc(drv)
            if drv in self.rookie_drivers.get((series, year), set()):
                drv_link += ' (R)'
            rows.append([str(pos), esc(t['car']), drv_link, '', str(t['starts']), str(t['wins']),
                         str(t['top5']), str(t['top10']), '-', '-', '-', fnum(t['pts'])])
            cls = 'roty' if drv == self.rookie_of_year.get((series, year)) else ''
            row_classes.append(cls)
        return rows, row_classes

    def _driver_standings_chart_svg(self, name):
        """Return SVG bar chart of driver's final standing position per season."""
        entries = []
        for year, season in self.seasons.items():
            for series in SERIES_ORDER:
                standings = season.get('driver_standings', {}).get(series, [])
                for rec in standings:
                    drv = clean_name(rec.get('Driver') or rec.get('NAME'))
                    drv = self._resolve_to_career(drv) or drv
                    if drv == name:
                        try:
                            pos = int(re.sub(r'\D', '', str(rec.get('Pos.', ''))))
                        except (ValueError, TypeError):
                            pos = None
                        if pos is not None:
                            entries.append((int(year), series, pos, rec.get('PTS', '')))
        entries.sort(key=lambda e: (e[0], SERIES_ORDER.index(e[1]) if e[1] in SERIES_ORDER else 99))
        if len(entries) < 2:
            return ''
        max_pos = max(e[2] for e in entries)
        bar_colors = {'cup': '#000000', 'xfinity': '#b32127', 'truck': '#2b5fa8'}
        h = 300
        ml, mt, mr, mb = 50, 25, 140, 50
        n = len(entries)
        base_pw = 1200 - ml - mr
        bar_w = max(8, min(50, base_pw // n - 4))
        content_w = ml + mr + n * (bar_w + 4)
        w = max(1000, content_w)
        pw, ph = w - ml - mr, h - mt - mb
        total_bars_w = n * (bar_w + 4)
        offset_x = ml + (pw - total_bars_w) // 2

        bars = []
        for i, (yr, series, pos, pts) in enumerate(entries):
            x = offset_x + i * (bar_w + 4)
            bar_h = (pos / max_pos) * ph
            y = mt + ph - bar_h
            color = bar_colors.get(series, '#746c5c')
            bars.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" fill="{color}" rx="2" opacity="0.85"/>')
            bars.append(f'<text x="{x + bar_w / 2}" y="{y - 6}" text-anchor="middle" fill="#1c1a16" font-size="11" font-weight="700">{pos}</text>')
            bars.append(f'<text x="{x + bar_w / 2}" y="{h - mb + 14}" text-anchor="middle" fill="#746c5c" font-size="10">{yr}</text>')
            slug = self.team_slugs.get(entries[i][1])  # not needed
            label = entries[i][1]
            bars.append(f'<a href="../standings/{series}/{yr}.html"><text x="{x + bar_w / 2}" y="{h - mb + 28}" text-anchor="middle" fill="{bar_colors.get(series, "#746c5c")}" font-size="9" font-weight="600">{SERIES_LABELS[series].split()[0]}</text></a>')

        y_ticks = 5
        y_axis = []
        for i in range(y_ticks + 1):
            val = int(max_pos * i / y_ticks)
            y = mt + ph - (val / max_pos) * ph
            y_axis.append(f'<text x="{ml - 8}" y="{y + 4}" text-anchor="end" fill="#746c5c" font-size="11">{val if val > 0 else ""}</text>')
            y_axis.append(f'<line x1="{ml}" y1="{y}" x2="{ml + pw}" y2="{y}" stroke="#d9d0bb" stroke-width="0.5" stroke-dasharray="3,3"/>')

        svg = f'''<svg viewBox="0 0 {w} {h}" style="width:{w}px;max-width:none;display:block;margin:0;background:#fff;border-radius:4px;overflow:visible;font-family:-apple-system,sans-serif">
  <text x="{ml}" y="{mt - 14}" fill="#1c1a16" font-size="13" font-weight="700">Season Standings Finish</text>
  {''.join(y_axis)}
  {''.join(bars)}
</svg>'''
        return svg

    def _team_standings_chart_svg(self, team_name):
        """Return SVG bar chart showing the team's finish in team standings per season."""
        entries = []
        for year, season in self.seasons.items():
            for series in SERIES_ORDER:
                team_pts = season.get('team_points', {}).get(series, [])
                for idx, entry in enumerate(team_pts):
                    raw_team = entry.get('team', '')
                    if clean_team_name(raw_team) == team_name:
                        pos = idx + 1
                        entries.append((int(year), series, pos))
        entries.sort(key=lambda e: (e[0], SERIES_ORDER.index(e[1]) if e[1] in SERIES_ORDER else 99))
        if len(entries) < 2:
            return ''
        max_pos = max(e[2] for e in entries)
        bar_colors = {'cup': '#000000', 'xfinity': '#b32127', 'truck': '#2b5fa8'}
        h = 300
        ml, mt, mr, mb = 50, 25, 100, 50
        n = len(entries)
        base_pw = 1200 - ml - mr
        bar_w = max(8, min(50, base_pw // n - 4))
        content_w = ml + mr + n * (bar_w + 4)
        w = max(1000, content_w)
        pw, ph = w - ml - mr, h - mt - mb
        total_bars_w = n * (bar_w + 4)
        offset_x = ml + (pw - total_bars_w) // 2
        bars = []
        for i, (yr, series, pos) in enumerate(entries):
            x = offset_x + i * (bar_w + 4)
            bar_h = (pos / max_pos) * ph
            y = mt + ph - bar_h
            color = bar_colors.get(series, '#746c5c')
            bars.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" fill="{color}" rx="2" opacity="0.85"/>')
            bars.append(f'<text x="{x + bar_w / 2}" y="{y - 6}" text-anchor="middle" fill="#1c1a16" font-size="11" font-weight="700">{pos}</text>')
            bars.append(f'<text x="{x + bar_w / 2}" y="{h - mb + 14}" text-anchor="middle" fill="#746c5c" font-size="10">{yr}</text>')
            bars.append(f'<a href="../standings/{series}/{yr}.html"><text x="{x + bar_w / 2}" y="{h - mb + 28}" text-anchor="middle" fill="{bar_colors.get(series, "#746c5c")}" font-size="9" font-weight="600">{SERIES_LABELS[series].split()[0]}</text></a>')
        y_ticks = 5
        y_axis = []
        for i in range(y_ticks + 1):
            val = int(max_pos * i / y_ticks)
            y = mt + ph - (val / max_pos) * ph
            y_axis.append(f'<text x="{ml - 8}" y="{y + 4}" text-anchor="end" fill="#746c5c" font-size="11">{val if val > 0 else ""}</text>')
            y_axis.append(f'<line x1="{ml}" y1="{y}" x2="{ml + pw}" y2="{y}" stroke="#d9c0bb" stroke-width="0.5" stroke-dasharray="3,3"/>')
        svg = f'''<svg viewBox="0 0 {w} {h}" style="width:{w}px;max-width:none;display:block;margin:0;background:#fff;border-radius:4px;overflow:visible;font-family:-apple-system,sans-serif">
  <text x="{ml}" y="{mt - 14}" fill="#1c1a16" font-size="13" font-weight="700">Team Standings Finish</text>
  {''.join(y_axis)}
  {''.join(bars)}
</svg>'''
        return svg

    def _build_records(self):
        def _is_points_race(a):
            return (a['series'], a['year'], a['race_num']) not in self._allstar_race_keys

        drv_wins = defaultdict(lambda: defaultdict(int))
        for drv, apps in self.driver_races.items():
            for a in apps:
                if a['finish'] == '1' and _is_points_race(a):
                    drv_wins[a['series']][drv] += 1
                    drv_wins['total'][drv] += 1

        team_wins = defaultdict(lambda: defaultdict(int))
        for drv, apps in self.driver_races.items():
            for a in apps:
                if a['finish'] == '1' and a.get('team') and _is_points_race(a):
                    team_wins[a['series']][a['team']] += 1
                    team_wins['total'][a['team']] += 1

        champ_counts = defaultdict(lambda: defaultdict(int))
        for year, season in self.seasons.items():
            for series in SERIES_ORDER:
                champ = self._champion_for(series, year)
                if champ:
                    champ_counts[series][champ] += 1
                    champ_counts['total'][champ] += 1

        season_wins = defaultdict(lambda: defaultdict(int))
        for drv, apps in self.driver_races.items():
            for a in apps:
                if a['finish'] == '1' and a['series'] in SERIES_ORDER and _is_points_race(a):
                    season_wins[(a['series'], a['year'])][drv] += 1

        season_avg = defaultdict(lambda: defaultdict(lambda: {'s': 0, 'n': 0}))
        for drv, apps in self.driver_races.items():
            for a in apps:
                if a['series'] not in SERIES_ORDER:
                    continue
                try:
                    f = int(a['finish'])
                except:
                    continue
                season_avg[(a['series'], a['year'])][drv]['s'] += f
                season_avg[(a['series'], a['year'])][drv]['n'] += 1

        season_race_count = defaultdict(int)
        for r in self.races:
            if r['series'] in SERIES_ORDER and not r.get('is_allstar'):
                season_race_count[(r['series'], r['year'])] += 1

        def top_with_ties(items):
            items = list(items)
            if not items:
                return []
            mv = max(v for _, v in items)
            return sorted([(k, v) for k, v in items if v == mv], key=lambda x: (-x[1], x[0]))

        def link_drv(d):
            s = self.driver_slugs.get(d)
            return f'<a href="../drivers/{s}.html">{esc(d)}</a>' if s else esc(d)

        def link_team(t):
            s = self.team_slugs.get(t)
            return f'<a href="../teams/{s}.html">{esc(t)}</a>' if s else esc(t)

        def badge_or_label(sk):
            return badge(sk) if sk in SERIES_ORDER else '<span class="badge overall">Overall</span>'

        def race_cell(yr, s, rn, label=None):
            if label is None:
                label = f'R{rn}'
            return f'<a href="../races/{s}/{yr}/R{rn}.html">{label}</a>'

        def series_abbr(s):
            return SERIES_LABELS.get(s, s).split()[0]

        # --- compute win streaks/droughts/winless-streaks per series ---
        def races_sorted(drv, series=None):
            rs = [a for a in self.driver_races.get(drv, []) if (a['series'], a['year'], a['race_num']) not in self._allstar_race_keys]
            if series:
                rs = [a for a in rs if a['series'] == series]
            rs.sort(key=lambda a: (a['year'], SERIES_ORDER.index(a['series']) if a['series'] in SERIES_ORDER else 99, a['race_num']))
            return rs

        def win_streak_detailed(races):
            cur = best = 0
            cur_races = []
            best_races = []
            for a in races:
                if a['finish'] == '1':
                    cur += 1
                    cur_races.append((a['year'], a['series'], a['race_num']))
                    if cur > best:
                        best = cur
                        best_races = list(cur_races)
                else:
                    cur = 0
                    cur_races = []
            return best, best_races

        def win_drought_detailed(races):
            poses = [(i, a['year'], a['series'], a['race_num']) for i, a in enumerate(races) if a['finish'] == '1']
            if len(poses) < 2:
                return 0, None, None
            best_gap = -1
            best_pair = None
            for j in range(len(poses) - 1):
                gap = poses[j+1][0] - poses[j][0] - 1
                if gap > best_gap:
                    best_gap = gap
                    best_pair = ((poses[j][1], poses[j][2], poses[j][3]), (poses[j+1][1], poses[j+1][2], poses[j+1][3]))
            if best_pair is None:
                return 0, None, None
            return best_gap, best_pair[0], best_pair[1]

        def winless_streak_detailed(races):
            cur = best = 0
            cur_start = None
            best_start = None
            for a in races:
                if a['finish'] != '1':
                    if cur == 0:
                        cur_start = (a['year'], a['series'], a['race_num'])
                    cur += 1
                    if cur > best:
                        best = cur
                        best_start = cur_start
                else:
                    cur = 0
                    cur_start = None
            return best, best_start

        streak_data = {}      # (series_key, drv) -> int
        streak_detail = {}    # (series_key, drv) -> [(year, series, race_num), ...]
        drought_data = {}     # (series_key, drv) -> int
        drought_detail = {}   # (series_key, drv) -> ((y1,s1,rn1), (y2,s2,rn2))
        winless_data = {}   # (series_key, drv) -> int
        winless_detail = {} # (series_key, drv) -> (year, series, race_num) start of streak
        for drv in self.driver_races:
            for sk in SERIES_ORDER + ['total']:
                rs = races_sorted(drv, sk if sk != 'total' else None)
                sv, sraces = win_streak_detailed(rs)
                if sv >= 1:
                    streak_data[(sk, drv)] = sv
                    streak_detail[(sk, drv)] = sraces
                dv, win_a, win_b = win_drought_detailed(rs)
                if dv > 0:
                    drought_data[(sk, drv)] = dv
                    drought_detail[(sk, drv)] = (win_a, win_b)
                wl, wl_start = winless_streak_detailed(rs)
                if wl > 0:
                    winless_data[(sk, drv)] = wl
                    winless_detail[(sk, drv)] = wl_start

        # --- collect records per series ---
        series_keys = SERIES_ORDER + ['overall']

        def for_series(sk, data_map):
            """Return top-with-ties entries for a series key from a {(sk, drv): val} map."""
            if sk == 'overall':
                relevant = {drv: v for (s, drv), v in data_map.items() if s == 'total'}
            else:
                relevant = {drv: v for (s, drv), v in data_map.items() if s == sk}
            return top_with_ties(relevant.items())

        rec_sections = []
        jump_links = []

        def _sid(title):
            return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

        def add_section(title, col_headers, sk_to_rows):
            rows = []
            for sk in series_keys:
                r = sk_to_rows.get(sk, [])
                rows.extend(r)
            if rows:
                sid = _sid(title)
                jump_links.append(f'<a href="#{sid}">{esc(title)}</a>')
                rec_sections.append(f'<div class="panel"><h2 id="{sid}">{esc(title)}</h2><div class="body">{table_html(col_headers, rows)}</div></div>')

        # 1. Most Championships (Drivers)
        champ_sk_rows = {}
        for sk in series_keys:
            mk = 'total' if sk == 'overall' else sk
            entries = top_with_ties(champ_counts[mk].items())
            if entries:
                rows = [[badge_or_label(sk), link_drv(d), str(v)] for d, v in entries]
                champ_sk_rows[sk] = rows
        add_section('Most Championships (Drivers)', ['Series', 'Driver', 'Titles'], champ_sk_rows)

        # 2. Most Wins (Drivers)
        dw_sk_rows = {}
        for sk in series_keys:
            mk = 'total' if sk == 'overall' else sk
            entries = top_with_ties(drv_wins[mk].items())
            if entries:
                rows = [[badge_or_label(sk), link_drv(d), str(v)] for d, v in entries]
                dw_sk_rows[sk] = rows
        add_section('Most Wins (Drivers)', ['Series', 'Driver', 'Wins'], dw_sk_rows)

        # 3. Most Wins (Teams)
        tw_sk_rows = {}
        for sk in series_keys:
            mk = 'total' if sk == 'overall' else sk
            entries = top_with_ties(team_wins[mk].items())
            if entries:
                rows = [[badge_or_label(sk), link_team(t), str(v)] for t, v in entries]
                tw_sk_rows[sk] = rows
        add_section('Most Wins (Teams)', ['Series', 'Team', 'Wins'], tw_sk_rows)

        # 4. Most Wins in a Single Season
        sw_sk_rows = {}
        overall_sw = defaultdict(int)  # (year, drv) -> total wins across all series
        for (s, yr), drivers in season_wins.items():
            for drv, cnt in drivers.items():
                overall_sw[(yr, drv)] += cnt
        for sk in series_keys:
            all_sw = []
            if sk == 'overall':
                for (yr, drv), cnt in overall_sw.items():
                    all_sw.append((cnt, drv, yr))
            else:
                for (s, yr), drivers in season_wins.items():
                    if s == sk:
                        for drv, cnt in drivers.items():
                            all_sw.append((cnt, drv, yr))
            if all_sw:
                mv = max(c for c, _, _ in all_sw)
                entries = [(c, d, y) for c, d, y in all_sw if c == mv]
                rows = [[badge_or_label(sk), str(yr), link_drv(d), str(c)] for c, d, yr in entries]
                sw_sk_rows[sk] = rows
        add_section('Most Wins in a Single Season', ['Series', 'Year', 'Driver', 'Wins'], sw_sk_rows)

        # 5. Best Avg Finish
        av_sk_rows = {}
        for sk in series_keys:
            all_av = []
            if sk == 'overall':
                overall_avg = defaultdict(lambda: defaultdict(lambda: {'s': 0, 'n': 0}))
                for (s, yr), drivers in season_avg.items():
                    for drv, st in drivers.items():
                        overall_avg[yr][drv]['s'] += st['s']
                        overall_avg[yr][drv]['n'] += st['n']
                total_races_by_year = defaultdict(int)
                for (s, yr), cnt in season_race_count.items():
                    total_races_by_year[yr] += cnt
                for yr, drivers in overall_avg.items():
                    total_races = total_races_by_year.get(yr, 0)
                    min_starts = int(total_races * 0.9)
                    for drv, st in drivers.items():
                        if st['n'] >= min_starts:
                            avg = st['s'] / st['n']
                            all_av.append((avg, drv, yr, st['n']))
            else:
                for (s, yr), drivers in season_avg.items():
                    if s == sk:
                        total_races = season_race_count.get((s, yr), 0)
                        min_starts = int(total_races * 0.9)
                        for drv, st in drivers.items():
                            if st['n'] >= min_starts:
                                avg = st['s'] / st['n']
                                all_av.append((avg, drv, yr, st['n']))
            if all_av:
                mv = min(a for a, _, _, _ in all_av)
                entries = [(a, d, y, n) for a, d, y, n in all_av if a == mv]
                rows = [[badge_or_label(sk), str(yr), link_drv(d), f'{a:.2f}', str(n)] for a, d, yr, n in entries]
                av_sk_rows[sk] = rows
        add_section('Best Avg Finish in a Season (min 90% of races)', ['Series', 'Year', 'Driver', 'Avg F', 'Starts'], av_sk_rows)

        # 6. Most Wins by a Rookie
        ry_sk_rows = {}
        for sk in series_keys:
            all_ry = []
            for yr in self.seasons:
                for series in SERIES_ORDER:
                    if sk != 'overall' and series != sk:
                        continue
                    rookies = self.rookie_drivers.get((series, int(yr)), set())
                    for drv in rookies:
                        if sk == 'overall':
                            wcnt = sum(1 for a in self.driver_races.get(drv, [])
                                       if a['finish'] == '1' and a['year'] == int(yr)
                                       and (a['series'], a['year'], a['race_num']) not in self._allstar_race_keys)
                        else:
                            wcnt = sum(1 for a in self.driver_races.get(drv, [])
                                       if a['finish'] == '1' and a['series'] == series and a['year'] == int(yr)
                                       and (a['series'], a['year'], a['race_num']) not in self._allstar_race_keys)
                        if wcnt:
                            all_ry.append((wcnt, drv, yr))
            if all_ry:
                mv = max(c for c, _, _ in all_ry)
                entries = [(c, d, y) for c, d, y in all_ry if c == mv]
                rows = [[badge_or_label(sk), link_drv(d), str(yr), str(c)] for c, d, yr in entries]
                ry_sk_rows[sk] = rows
        add_section('Most Wins by a Rookie', ['Series', 'Driver', 'Year', 'Wins'], ry_sk_rows)

        # 7. Win Streak
        st_sk_rows = {}
        for sk in series_keys:
            entries = for_series(sk, streak_data)
            if entries:
                rows = []
                for d, v in entries:
                    mk = 'total' if sk == 'overall' else sk
                    sraces = streak_detail.get((mk, d), [])
                    cells = []
                    for yr, s, rn in sraces:
                        label = f'{series_abbr(s)} R{rn}' if mk == 'total' else f'R{rn}'
                        cells.append(race_cell(yr, s, rn, label))
                    detail_cell = ', '.join(cells)
                    rows.append([badge_or_label(sk), link_drv(d), str(v), detail_cell])
                st_sk_rows[sk] = rows
        add_section('Longest Win Streak', ['Series', 'Driver', 'Consecutive Wins', 'Races in Streak'], st_sk_rows)

        # 8. Win Drought (most races between wins)
        dr_sk_rows = {}
        for sk in series_keys:
            entries = for_series(sk, drought_data)
            if entries:
                rows = []
                for d, v in entries:
                    mk = 'total' if sk == 'overall' else sk
                    win_a, win_b = drought_detail.get((mk, d), (None, None))
                    if win_a and win_b:
                        yr_a, s_a, rn_a = win_a
                        yr_b, s_b, rn_b = win_b
                        def _dl(yr, s, rn):
                            label = f'{series_abbr(s)} R{rn}' if mk == 'total' else f'R{rn}'
                            return race_cell(yr, s, rn, label)
                        detail_cell = f'{_dl(yr_a, s_a, rn_a)} &rarr; {_dl(yr_b, s_b, rn_b)}'
                    else:
                        detail_cell = ''
                    rows.append([badge_or_label(sk), link_drv(d), str(v), detail_cell])
                dr_sk_rows[sk] = rows
        add_section('Longest Win Drought (Races Between Wins)', ['Series', 'Driver', 'Races', 'Between'], dr_sk_rows)

        # 9. Most Races Without a Win (longest winless streak still active or broken)
        wl_sk_rows = {}
        for sk in series_keys:
            entries = for_series(sk, winless_data)
            if entries:
                rows = []
                for d, v in entries:
                    mk = 'total' if sk == 'overall' else sk
                    wl_info = winless_detail.get((mk, d))
                    if wl_info:
                        yr, s, rn = wl_info
                        label = f'{series_abbr(s)} R{rn}' if mk == 'total' else f'R{rn}'
                        detail_cell = f'Since {race_cell(yr, s, rn, label)}'
                    else:
                        detail_cell = ''
                    rows.append([badge_or_label(sk), link_drv(d), str(v), detail_cell])
                wl_sk_rows[sk] = rows
        add_section('Most Races Without a Win', ['Series', 'Driver', 'Races', 'Streak Start'], wl_sk_rows)

        def _parse_led(val):
            if not val:
                return 0
            try:
                return int(re.sub(r'[^0-9]', '', str(val)))
            except (ValueError, TypeError):
                return 0

        # 10. Most Laps Led in a Single Race
        llr_sk_rows = {}
        for sk in series_keys:
            best = {}
            for drv, apps in self.driver_races.items():
                for a in apps:
                    if sk != 'overall' and a['series'] != sk:
                        continue
                    led = _parse_led(a['led'])
                    if led <= 0:
                        continue
                    prev = best.get(drv, (0,))
                    if led > prev[0]:
                        best[drv] = (led, a['year'], a['series'], a['race_num'])
            if best:
                mv = max(v[0] for v in best.values())
                entries = [(d, v) for d, v in best.items() if v[0] == mv]
                rows = []
                for d, (ld, yr, s, rn) in entries:
                    label = f'{series_abbr(s)} R{rn}' if sk == 'overall' else f'R{rn}'
                    rows.append([badge_or_label(sk), link_drv(d), str(ld), race_cell(yr, s, rn, label)])
                llr_sk_rows[sk] = rows
        add_section('Most Laps Led in a Single Race', ['Series', 'Driver', 'Laps Led', 'Race'], llr_sk_rows)

        # 11. Most Laps Led in a Season
        lls_sk_rows = {}
        for sk in series_keys:
            season_totals = defaultdict(int)
            for drv, apps in self.driver_races.items():
                for a in apps:
                    if sk != 'overall' and a['series'] != sk:
                        continue
                    led = _parse_led(a['led'])
                    season_totals[(drv, a['year'])] += led
            if season_totals:
                drv_best = {}
                for (drv, yr), total in season_totals.items():
                    if total <= 0:
                        continue
                    prev = drv_best.get(drv, (0,))
                    if total > prev[0]:
                        drv_best[drv] = (total, yr)
                mv = max(v[0] for v in drv_best.values())
                entries = [(d, v) for d, v in drv_best.items() if v[0] == mv]
                rows = [[badge_or_label(sk), link_drv(d), str(yr), str(t)] for d, (t, yr) in entries]
                lls_sk_rows[sk] = rows
        add_section('Most Laps Led in a Season', ['Series', 'Driver', 'Year', 'Laps Led'], lls_sk_rows)

        jump_bar = f'<div class="jump-bar">{" &middot; ".join(jump_links)}</div>' if jump_links else ''
        sections_html = '\n'.join(rec_sections)

        content = f'''
        <div class="breadcrumb"><a href="../index.html">Home</a> / Records</div>
        <h1 class="page-title">Records</h1>
        {jump_bar}
        {sections_html}
        '''
        self._write('records/index.html', 'Records', content)

    def _build_allstar_page(self):
        as_races = [r for r in self.races if r.get('is_allstar')]
        as_races.sort(key=lambda r: (r['year'], r['race_num']))

        # Races tab
        race_rows = []
        for r in as_races:
            raw_canon = self.track_canon.get(clean_name(r['track']), clean_name(r['track']))
            track_slug = self.track_slugs.get(raw_canon)
            canon_track = format_track_name(raw_canon)
            track_cell = f'<a href="../tracks/{track_slug}.html">{esc(canon_track)}</a>' if track_slug else esc(canon_track)
            race_link = f'<a href="../races/cup/{r["year"]}/R{r["race_num"]}.html">Results</a>'
            winner = '-'
            race_sesh = r['sessions'].get('Race', [])
            if race_sesh:
                first = race_sesh[0]
                lookup = self._roster_lookup(r['series'], r['year'])
                car_norm = (first.get('#') or '').strip() or '0'
                roster_entry = lookup.get(car_norm)
                w = self._normalize_driver_name(first.get('DRIVER'), roster_entry)
                w = self._resolve_to_career(w) or w
                wslug = self.driver_slugs.get(w)
                winner = f'<a href="../drivers/{wslug}.html">{esc(w)}</a>' if wslug else esc(w)
            as_type = r.get('allstar_type', 'Race')
            race_rows.append([str(r['year']), esc(as_type), track_cell, winner, race_link])
        races_tbl = table_html(['Year', 'Type', 'Track', 'Winner', ''], race_rows, aligns={0: 'num'})
        races_html = f'<div class="panel allstar-tab-content" id="as-races"><h2>All-Star Races</h2><div class="body">{races_tbl}</div></div>'

        # Stats tab: count AS race appearances and wins by driver
        as_driver_stats = defaultdict(lambda: {'apps': 0, 'wins': 0})
        seen_year = set()
        for r in as_races:
            at = r.get('allstar_type', 'Race')
            if at == 'Open':
                continue
            race_sesh = r['sessions'].get('Race', [])
            for row in race_sesh:
                drv_raw = (row.get('DRIVER') or '').strip()
                if not drv_raw:
                    continue
                lookup = self._roster_lookup(r['series'], r['year'])
                car_norm = (row.get('#') or '').strip() or '0'
                roster_entry = lookup.get(car_norm)
                drv = self._normalize_driver_name(drv_raw, roster_entry)
                drv = self._resolve_to_career(drv) or drv
                if (drv, r['year']) not in seen_year:
                    seen_year.add((drv, r['year']))
                    as_driver_stats[drv]['apps'] += 1
                if row.get('F') == '1':
                    as_driver_stats[drv]['wins'] += 1

        sorted_drivers = sorted(as_driver_stats.items(), key=lambda kv: (-kv[1]['wins'], -kv[1]['apps'], kv[0]))
        stat_rows = []
        for drv, st in sorted_drivers:
            slug = self.driver_slugs.get(drv)
            link = f'<a href="../drivers/{slug}.html">{esc(drv)}</a>' if slug else esc(drv)
            stat_rows.append([link, str(st['apps']), str(st['wins'])])
        stats_tbl = table_html(['Driver', 'Appearances', 'Wins'], stat_rows, aligns={1: 'num', 2: 'num'})
        stats_html = f'<div class="panel allstar-tab-content" id="as-stats" style="display:none"><h2>All-Star Driver Stats</h2><div class="body">{stats_tbl}</div></div>'

        tab_script = '''
        <script>
        (function(){
          var btns = document.querySelectorAll('.as-tab-btn');
          var panels = {races: document.getElementById('as-races'), stats: document.getElementById('as-stats')};
          btns.forEach(function(b){
            b.addEventListener('click', function(){
              btns.forEach(function(x){ x.classList.remove('active'); });
              b.classList.add('active');
              Object.keys(panels).forEach(function(k){
                panels[k].style.display = k === b.getAttribute('data-tab') ? '' : 'none';
              });
            });
          });
        })();
        </script>
        '''
        filter_bar = '<div class="filter-bar stats-tab-bar"><button type="button" class="filter-btn as-tab-btn active" data-tab="races">Races</button><button type="button" class="filter-btn as-tab-btn" data-tab="stats">Stats</button></div>'

        content = f'''
        <div class="breadcrumb"><a href="../index.html">Home</a> / All-Star</div>
        <h1 class="page-title">All-Star</h1>
        {filter_bar}
        {races_html}
        {stats_html}
        {tab_script}
        '''
        self._write('allstar/index.html', 'All-Star', content)

    def _build_standings_page(self, series, year):
        rows_from_sheet, sheet_classes = self._standings_rows_from_sheet(series, year)
        note = ''
        if rows_from_sheet:
            rows, row_classes = rows_from_sheet, sheet_classes
        else:
            rows, row_classes = self._standings_rows_computed(series, year)
            note = '<p class="subtitle">Season in progress &mdash; standings computed live from race files on hand.</p>'
        row_classes = [('win' if i == 0 else '') + (' ' + rc if rc else '') for i, rc in enumerate(row_classes)]
        tbl = table_html(['Pos', '#', 'Driver', 'Team', 'St', 'W', 'T5', 'T10', 'Avg F', 'Poles', 'Avg S', 'Pts'],
                          rows, row_classes=row_classes,
                          aligns={0: 'num', 1: 'num', 4: 'num', 5: 'num', 6: 'num', 7: 'num', 8: 'num', 9: 'num', 10: 'num', 11: 'num'})

        team_pts = self.seasons.get(year, {}).get('team_points', {}).get(series, [])
        # Separate real teams from manufacturer-only entries
        real_teams = [tp for tp in team_pts if not is_manufacturer_name(tp.get('team', ''))]
        mfg_only = [tp for tp in team_pts if is_manufacturer_name(tp.get('team', ''))]
        team_tbl = ''
        if real_teams:
            trows = []
            for i, tp in enumerate(real_teams):
                t_cell = esc(tp['team'])
                tslug = self.team_slugs.get(clean_team_name(tp['team']))
                if tslug:
                    t_cell = f'<a href="../../teams/{tslug}.html">{esc(tp["team"])}</a>'
                trows.append([str(i + 1), t_cell, fnum(tp['points'])])
            team_tbl = f'<div class="panel"><h2>Team (Owner) Points</h2><div class="body">{table_html(["Pos", "Team", "Points"], trows, aligns={0: "num", 2: "num"})}</div></div>'

        mfg_pts = defaultdict(int)
        for tp in team_pts:
            mfg = manufacturer_for(tp.get('team', ''))
            if mfg:
                mfg_pts[mfg] += float(tp.get('points', 0))
        mfg_tbl = ''
        if mfg_pts:
            mrows = [[str(i + 1), esc(m), fnum(p)] for i, (m, p) in enumerate(sorted(mfg_pts.items(), key=lambda kv: -kv[1]))]
            mfg_tbl = f'<div class="panel"><h2>Manufacturer Points</h2><div class="body">{table_html(["Pos", "Manufacturer", "Points"], mrows, aligns={0: "num", 2: "num"})}</div></div>'

        content = f'''
        <div class="breadcrumb"><a href="../../index.html">Home</a> / <a href="../../seasons/{series}/index.html">{SERIES_LABELS[series]}</a> / {year} Standings</div>
        <h1 class="page-title">{year} {SERIES_LABELS[series]} Standings</h1>
        {note}
        <div class="panel"><h2>Driver Points</h2><div class="body">{tbl}</div></div>
        {team_tbl}
        {mfg_tbl}
        '''
        self._write(f'standings/{series}/{year}.html', f'{year} {SERIES_LABELS[series]} Standings', content)

    def _session_table_html(self, race, session_name, depth, roster_lookup):
        rows_data = race['sessions'].get(session_name, [])
        if not rows_data:
            return '<p style="color:#a89f8c">No data recorded.</p>'
        headers = list(rows_data[0].keys())
        rows = []
        row_classes = []
        for row in rows_data:
            cells = []
            for h in headers:
                v = row.get(h)
                if h == 'DRIVER' and v:
                    car_norm = (row.get('#') or '').strip() or '0'
                    roster_entry = roster_lookup.get(car_norm)
                    display_name = self._normalize_driver_name(v.strip(), roster_entry)
                    display_name = self._resolve_to_career(display_name) or display_name
                    slug = self.driver_slugs.get(display_name)
                    drv_cell = f'<a href="{"../"*depth}drivers/{slug}.html">{esc(display_name)}</a>' if slug else esc(display_name)
                    team = roster_entry['team'] if roster_entry else None
                    if team:
                        drv_cell += f' <span class="team-tag">{self._team_link(team, depth)}</span>'
                    cells.append(drv_cell)
                else:
                    cells.append(esc(v))
            rows.append(cells)
            fin = row.get('F')
            row_classes.append('win' if fin == '1' else '')
        num_cols = {i for i, h in enumerate(headers) if h in ('F', 'S', 'ST', 'P', '#', 'LAPS', 'LED', 'POINTS', 'INTERVAL', 'TIME')}
        aligns = {i: 'num' for i in num_cols}
        return table_html(headers, rows, row_classes=row_classes, aligns=aligns)

    def _build_race_page(self, race):
        series, year, rn = race['series'], race['year'], race['race_num']
        depth = 3  # races/<series>/<year>/Rn.html
        roster_lookup = self._roster_lookup(series, year)
        session_order = ['Race', 'Qualifying', 'Happy Hour', 'Practice']
        panels = []
        for s in session_order:
            if s in race['sessions']:
                panels.append(f'<div class="panel"><h2>{esc(s)}</h2><div class="body">{self._session_table_html(race, s, depth, roster_lookup)}</div></div>')

        meta_bits = []
        if race.get('date'):
            meta_bits.append(f'<span><b>Date</b> {esc(race["date"])}</span>')
        if race.get('cautions'):
            meta_bits.append(f'<span><b>Cautions</b> {esc(race["cautions"])}</span>')
        if race.get('lead_changes'):
            meta_bits.append(f'<span><b>Lead Changes</b> {esc(race["lead_changes"])}</span>')
        if race.get('weather'):
            meta_bits.append(f'<span><b>Weather</b> {esc(race["weather"])}</span>')
        if race.get('pitstop'):
            meta_bits.append(f'<span><b>Pit Frequency</b> {esc(race["pitstop"])}</span>')
        if race.get('ai_strength'):
            meta_bits.append(f'<span><b>AI Strength</b> {esc(race["ai_strength"])}</span>')

        prev_link = next_link = ''
        if self.races_by_key.get((series, year, rn - 1)):
            prev_link = f'<a href="R{rn-1}.html">&larr; Race {rn-1}</a>'
        if self.races_by_key.get((series, year, rn + 1)):
            next_link = f'<a href="R{rn+1}.html">Race {rn+1} &rarr;</a>'

        raw_canon = self.track_canon.get(clean_name(race['track']), clean_name(race['track']))
        track_slug = self.track_slugs.get(raw_canon)
        canon_track = format_track_name(raw_canon)
        track_heading = f'<a class="plain" href="../../../tracks/{track_slug}.html">{esc(canon_track)}</a>' if track_slug else esc(canon_track)
        allstar_badge = ' <span class="badge allstar">All-Star</span>' if race.get('is_allstar') else ''
        content = f'''
        <div class="breadcrumb"><a href="../../../index.html">Home</a> / <a href="../../../seasons/{series}/index.html">{SERIES_LABELS[series]}</a> / <a href="../../../seasons/{series}/{year}/index.html">{year}</a> / Race {rn}</div>
        <h1 class="page-title">{track_heading}</h1>
        <p class="subtitle">{badge(series)} &middot; {year} &middot; Race {rn}{allstar_badge}</p>
        <div class="meta-strip">{''.join(meta_bits)}</div>
        <p>{prev_link} &nbsp; {next_link}</p>
        {''.join(panels)}
        '''
        self._write(f'races/{series}/{year}/R{rn}.html', f'{canon_track} ({year})', content)

    def _build_drivers_index(self):
        cards = []
        for d in self.all_drivers:
            slug = self.driver_slugs[d]
            teams = ', '.join(sorted(self.driver_teams.get(d, []))[:2])
            n_races = len(self.driver_races.get(d, []))
            cards.append(f'<div class="card"><h3><a class="plain" href="{slug}.html">{esc(d)}</a></h3>'
                         f'<div class="stat-row"><span>Races on file</span><span>{n_races}</span></div>'
                         f'<div class="stat-row"><span>{esc(teams) if teams else "&nbsp;"}</span></div></div>')
        content = f'''
        <div class="breadcrumb"><a href="../index.html">Home</a> / Drivers</div>
        <h1 class="page-title">Drivers</h1>
        <p class="subtitle">{len(self.all_drivers)} drivers on record. <a href="stats.html">Career stats &rarr;</a></p>
        <div class="grid">{''.join(cards)}</div>
        '''
        self._write('drivers/index.html', 'Drivers', content)

    def _build_driver_stats_page(self):
        n_drivers = 0
        for d in self.all_drivers:
            raw_t = self.driver_race_stats.get(d, {}).get('total', {})
            if raw_t.get('starts'):
                n_drivers += 1

        champ_by_series = defaultdict(lambda: defaultdict(int))
        for series in SERIES_ORDER:
            for year in sorted(self.years_by_series.get(series, [])):
                champ = self._champion_for(series, year)
                if champ:
                    champ_by_series[champ][series] += 1

        def _make_table(series_key, label):
            rows = []
            for d in self.all_drivers:
                raw = self.driver_race_stats.get(d, {}).get(series_key, {})
                if not raw.get('starts'):
                    continue
                slug = self.driver_slugs[d]
                avg = f'{raw["finish_sum"] / raw["finish_n"]:.1f}' if raw.get('finish_n') else '-'
                champs = sum(champ_by_series.get(d, {}).values()) if series_key == 'total' else champ_by_series.get(d, {}).get(series_key, 0)
                rows.append([
                    f'<a href="{slug}.html">{esc(d)}</a>',
                    fnum(raw['starts']), fnum(raw['wins']), fnum(raw['top5']), fnum(raw['top10']),
                    avg, fnum(raw['poles']), fnum(raw['points']), fnum(champs),
                ])
            rows.sort(key=lambda r: int(r[1]) if r[1] != '0' else 0, reverse=True)
            return table_html(['Driver', 'Starts', 'Wins', 'Top 5', 'Top 10', 'Avg Finish', 'Poles', 'Points', 'Championships'],
                              rows, aligns={i: 'num' for i in range(1, 9)})

        filter_btns = ''.join(f'<button type="button" class="filter-btn{(" active" if k == "total" else "")}" data-filter="{k}">{l}</button>'
                              for k, l in [('total', 'All'), ('cup', 'Cup'), ('xfinity', 'Xfinity'), ('truck', 'Truck')])
        containers_parts = []
        for k, l in [('total', 'All'), ('cup', 'Cup'), ('xfinity', 'Xfinity'), ('truck', 'Truck')]:
            style = ' style="display:none"' if k != 'total' else ''
            containers_parts.append(f'<div class="stats-container" data-series="{k}"{style}>{_make_table(k, l)}</div>')
        containers = ''.join(containers_parts)

        filter_script = '''
        <script>
        (function(){
          var btns = document.querySelectorAll('.stats-tab-bar .filter-btn');
          var containers = document.querySelectorAll('.stats-container');
          btns.forEach(function(btn){
            btn.addEventListener('click', function(){
              btns.forEach(function(b){ b.classList.remove('active'); });
              btn.classList.add('active');
              var f = btn.getAttribute('data-filter');
              containers.forEach(function(el){
                el.style.display = el.getAttribute('data-series') === f ? '' : 'none';
              });
            });
          });
        })();
        </script>
        '''

        content = f'''
        <div class="breadcrumb"><a href="../index.html">Home</a> / <a href="index.html">Drivers</a> / Career Stats</div>
        <h1 class="page-title">Driver Career Stats</h1>
        <p class="subtitle">{n_drivers} drivers with at least one start.</p>
        <div class="filter-bar stats-tab-bar">{filter_btns}</div>
        {containers}
        {filter_script}
        '''
        self._write('drivers/stats.html', 'Driver Stats', content)

    def _driver_photo_html(self, slug, name):
        photo_dir = os.path.join(HERE, 'static', 'driver-photos')
        for ext in ('jpg', 'jpeg', 'png', 'webp', 'avif'):
            path = os.path.join(photo_dir, f'{slug}.{ext}')
            if os.path.exists(path):
                return f'<img src="../static/driver-photos/{slug}.{ext}" alt="{esc(name)}" class="driver-photo">'
        return ''

    def _team_logo_html(self, slug, name):
        logo_dir = os.path.join(HERE, 'static', 'team-logos')
        for ext in ('jpg', 'jpeg', 'png', 'webp', 'avif'):
            path = os.path.join(logo_dir, f'{slug}.{ext}')
            if os.path.exists(path):
                return f'<img src="../static/team-logos/{slug}.{ext}" alt="{esc(name)}" class="driver-photo">'
        return ''

    def _track_image_html(self, slug, name):
        img_dir = os.path.join(HERE, 'static', 'track-images')
        for ext in ('jpg', 'jpeg', 'png', 'webp', 'avif'):
            path = os.path.join(img_dir, f'{slug}.{ext}')
            if os.path.exists(path):
                return f'<img src="../static/track-images/{slug}.{ext}" alt="{esc(name)}" class="driver-photo">'
        return ''

    def _build_driver_page(self, slug):
        name = next((d for d, s in self.driver_slugs.items() if s == slug), slug)
        photo_html = self._driver_photo_html(slug, name)
        stats = self._computed_stats_for(name)
        by = self.birth_years.get(name)
        birth_info = f'<p class="subtitle">Born: {by}</p>' if by else ''
        stat_boxes = ''
        career_panel = ''
        if stats and stats.get('total'):
            t = stats['total']
            stat_boxes = f'''
            <div class="stat-strip">
              <div class="stat-box"><div class="n">{fnum(t.get("starts"))}</div><div class="l">Starts</div></div>
              <div class="stat-box"><div class="n">{fnum(t.get("wins"))}</div><div class="l">Wins</div></div>
              <div class="stat-box"><div class="n">{fnum(t.get("top5"))}</div><div class="l">Top 5s</div></div>
              <div class="stat-box"><div class="n">{fnum(t.get("top10"))}</div><div class="l">Top 10s</div></div>
              <div class="stat-box"><div class="n">{fnum(t.get("poles"))}</div><div class="l">Poles</div></div>
              <div class="stat-box"><div class="n">{fnum(t.get("avg_f"), 1)}</div><div class="l">Avg Finish</div></div>
            </div>'''
            by_series_rows = []
            for series in SERIES_ORDER:
                s = stats.get(series) or {}
                if s.get('starts'):
                    by_series_rows.append([SERIES_LABELS[series], fnum(s.get('starts')), fnum(s.get('wins')),
                                            fnum(s.get('top5')), fnum(s.get('top10')), fnum(s.get('avg_f'), 1),
                                            fnum(s.get('poles')), fnum(s.get('points'))])
            by_series_tbl = table_html(['Series', 'Starts', 'Wins', 'Top 5', 'Top 10', 'Avg F', 'Poles', 'Points'],
                                        by_series_rows, aligns={i: 'num' for i in range(1, 8)})
            career_panel = (f'<div class="panel"><h2>Career Stats by Series</h2>'
                             f'<p style="padding:10px 14px 0;color:var(--muted);font-size:12px">'
                             f'Computed directly from race result files on hand (not the workbook).</p>'
                             f'<div class="body">{by_series_tbl}</div></div>')

        standings_chart_svg = self._driver_standings_chart_svg(name)
        standings_chart_html = f'<div class="panel" id="driver-standings-history"><h2>Season Standings History</h2><div class="body"><div style="overflow-x:auto">{standings_chart_svg}</div></div></div>' if standings_chart_svg else ''

        teams = sorted(self.driver_teams.get(name, []))
        team_links = ', '.join(f'<a href="../teams/{self.team_slugs.get(t, slugify(t))}.html">{esc(t)}</a>' for t in teams)

        # ---- team history from season rosters ----
        drv_race_counts = defaultdict(int)
        for a in self.driver_races.get(name, []):
            if (a['series'], a['year'], a['race_num']) in self._allstar_race_keys:
                continue
            t = a.get('team')
            if t:
                drv_race_counts[(a['year'], a['series'], t)] += 1
        team_history_rows = []
        for year in sorted(self.seasons.keys(), reverse=True):
            season = self.seasons[year]
            for series, roster in season.get('roster', {}).items():
                for r in roster:
                    for indiv in split_driver_names(r['driver']):
                        resolved = self._resolve_to_career(indiv) or indiv
                        if resolved == name:
                            tname = clean_team_name(r['team'])
                            tslug = self.team_slugs.get(tname)
                            tlink = f'<a href="../teams/{tslug}.html">{esc(tname)}</a>' if tslug else esc(tname)
                            drv_display = tlink
                            if resolved in self.rookie_drivers.get((series, year), set()):
                                drv_display += ' (R)'
                            cnt = drv_race_counts.get((year, series, tname), 0)
                            age = (int(year) - by) if by else None
                            age_str = f' (age {age})' if age else ''
                            pos = self._season_finish(name, series, year)
                            pos_str = f'<b>{pos}</b>' if pos else '-'
                            team_history_rows.append([str(year) + age_str, badge(series), esc(r['car']), drv_display, str(cnt), pos_str])
        team_history_tbl = ''
        if team_history_rows:
            team_history_tbl = f'<div class="panel" id="driver-team-history"><h2>Team History</h2><div class="body">{table_html(["Year", "Series", "#", "Team", "Races", "Fin"], team_history_rows, aligns={0: "num", 2: "num", 4: "num", 5: "num"})}</div></div>'

        def _series_key(s):
            try:
                return SERIES_ORDER.index(s)
            except ValueError:
                return 999
        appearances = sorted(self.driver_races.get(name, []), key=lambda a: (a['year'], _series_key(a['series']), a['race_num']), reverse=True)
        series_present = sorted({a['series'] for a in appearances}, key=_series_key)
        years_present = sorted({a['year'] for a in appearances}, reverse=True)
        rows = []
        points_races = 0
        row_classes = []
        row_attrs = []
        for a in appearances:
            is_as = (a['series'], a['year'], a['race_num']) in self._allstar_race_keys
            if not is_as:
                points_races += 1
            track_cell = f'<a href="../races/{a["series"]}/{a["year"]}/R{a["race_num"]}.html">{esc(format_track_name(a["track"]))}</a>'
            if is_as:
                track_cell += ' <span class="badge allstar">AS</span>'
            rows.append([
                str(a['year']), badge(a['series']),
                track_cell,
                esc(a.get('start')), esc(a.get('finish')), esc(a.get('car')),
                self._team_link(a.get('team')) if a.get('team') else '-',
                esc(a.get('led')), esc(a.get('points')), esc(a.get('status')),
            ])
            row_classes.append('win' if a.get('finish') == '1' else '')
            row_attrs.append(f'data-series="{a["series"]}" data-year="{a["year"]}"')
        log_tbl = table_html(['Year', 'Series', 'Track', 'St', 'Fin', '#', 'Team', 'Led', 'Pts', 'Status'],
                              rows, row_classes=row_classes, row_attrs=row_attrs,
                              aligns={0: 'num', 3: 'num', 4: 'num', 5: 'num', 7: 'num', 8: 'num'}, table_id='race-log')

        filter_html = ''
        if len(series_present) > 1 or len(years_present) > 1:
            parts = []
            if len(series_present) > 1:
                btns = ['<button type="button" class="filter-btn active" data-filter-type="series" data-filter-value="all">All</button>']
                for s in series_present:
                    btns.append(f'<button type="button" class="filter-btn" data-filter-type="series" data-filter-value="{s}">{SERIES_LABELS[s]}</button>')
                parts.append('<span class="filter-group">' + ''.join(btns) + '</span>')
            if len(years_present) > 1:
                opts = ['<option value="all">All Years</option>']
                for y in years_present:
                    opts.append(f'<option value="{y}">{y}</option>')
                parts.append('<span class="filter-group"><select class="filter-select" data-filter-type="year">' + ''.join(opts) + '</select></span>')
            filter_html = '<div class="filter-bar">' + ' '.join(parts) + '</div>'

        filter_script = '''
        <script>
        (function(){
          var panel = document.getElementById('race-log-panel');
          if (!panel) return;
          var rows = panel.querySelectorAll('#race-log tbody tr');
          var yearSel = panel.querySelector('[data-filter-type="year"]');
          function applyFilters() {
            var seriesVal = 'all';
            panel.querySelectorAll('.filter-btn.active').forEach(function(b){
              if (b.getAttribute('data-filter-type') === 'series') seriesVal = b.getAttribute('data-filter-value');
            });
            var yearVal = yearSel ? yearSel.value : 'all';
            rows.forEach(function(r){
              r.style.display =
                (seriesVal === 'all' || r.getAttribute('data-series') === seriesVal) &&
                (yearVal === 'all' || r.getAttribute('data-year') === yearVal) ? '' : 'none';
            });
          }
          panel.querySelectorAll('.filter-btn').forEach(function(btn){
            btn.addEventListener('click', function(){
              var type = btn.getAttribute('data-filter-type');
              panel.querySelectorAll('.filter-btn[data-filter-type="' + type + '"]').forEach(function(b){
                b.classList.remove('active');
              });
              btn.classList.add('active');
              applyFilters();
            });
          });
          if (yearSel) { yearSel.addEventListener('change', applyFilters); }
        })();
        </script>
        '''

        jump_links = []
        if standings_chart_html:
            jump_links.append('<a href="#driver-standings-history">Standings</a>')
        jump_links.append('<a href="#driver-stats">Career Stats</a>')
        if team_history_tbl:
            jump_links.append('<a href="#driver-team-history">Team History</a>')
        jump_links.append('<a href="#race-log-panel">Race Log</a>')
        jump = f'<div class="jump-bar">{" ".join(jump_links)}</div>'

        title_row = f'<div class="driver-title-row">{photo_html}<div><h1 class="page-title" style="margin-top:0">{esc(name)}</h1><p class="subtitle">{("Teams: " + team_links) if team_links else ""}</p>{birth_info}</div></div>'

        content = f'''
        <div class="breadcrumb"><a href="../index.html">Home</a> / <a href="index.html">Drivers</a> / {esc(name)}</div>
        {title_row}
        {jump}
        {stat_boxes}
        {standings_chart_html}
        <div id="driver-stats">{career_panel}</div>
        {team_history_tbl}
        <div class="panel" id="race-log-panel"><h2>Race Log ({points_races} races on file)</h2>{filter_html}<div class="body">{log_tbl}</div></div>
        {filter_script if filter_html else ''}
        '''
        self._write(f'drivers/{slug}.html', name, content)

    def _build_teams_index(self):
        cards = []
        for t in self.all_teams:
            slug = self.team_slugs[t]
            n_races = len(self.team_races.get(t, []))
            drivers = ', '.join(sorted(self.team_drivers.get(t, []))[:3])
            cards.append(f'<div class="card"><h3><a class="plain" href="{slug}.html">{esc(t)}</a></h3>'
                         f'<div class="stat-row"><span>Races on file</span><span>{n_races}</span></div>'
                         f'<div class="stat-row"><span>{esc(drivers)}</span></div></div>')
        content = f'''
        <div class="breadcrumb"><a href="../index.html">Home</a> / Teams</div>
        <h1 class="page-title">Teams</h1>
        <p class="subtitle">{len(self.all_teams)} teams on record. <a href="stats.html">Career stats &rarr;</a></p>
        <div class="grid">{''.join(cards)}</div>
        '''
        self._write('teams/index.html', 'Teams', content)

    def _build_team_stats_page(self):
        team_champs_by_series = defaultdict(lambda: defaultdict(int))
        for series in SERIES_ORDER:
            for year in sorted(self.years_by_series.get(series, [])):
                champ = self._champion_for(series, year)
                if champ:
                    lookup = self._roster_lookup(series, year)
                    for entry in lookup.values():
                        for indiv in split_driver_names(entry['driver']):
                            resolved = self._resolve_to_career(indiv) or indiv
                            if resolved == champ:
                                team_clean = clean_team_name(entry['team'])
                                team_champs_by_series[team_clean][series] += 1
                                break

        def _make_table(series_key, label):
            rows = []
            for t in self.all_teams:
                if series_key == 'total':
                    apps = self.team_races.get(t, [])
                else:
                    apps = [a for a in self.team_races.get(t, []) if a['series'] == series_key]
                if not apps:
                    continue
                slug = self.team_slugs[t]
                starts = len(apps)
                wins = sum(1 for a in apps if str(a.get('finish')) == '1')
                top5 = sum(1 for a in apps if str(a.get('finish')).isdigit() and int(a['finish']) <= 5)
                top10 = sum(1 for a in apps if str(a.get('finish')).isdigit() and int(a['finish']) <= 10)
                champs = sum(team_champs_by_series.get(t, {}).values()) if series_key == 'total' else team_champs_by_series.get(t, {}).get(series_key, 0)
                rows.append([
                    f'<a href="{slug}.html">{esc(t)}</a>',
                    fnum(starts), fnum(wins), fnum(top5), fnum(top10),
                    fnum(champs),
                ])
            rows.sort(key=lambda r: int(r[1]) if r[1] != '0' else 0, reverse=True)
            return table_html(['Team', 'Starts', 'Wins', 'Top 5', 'Top 10', 'Championships'],
                              rows, aligns={i: 'num' for i in range(1, 6)})

        filter_btns = ''.join(f'<button type="button" class="filter-btn{(" active" if k == "total" else "")}" data-filter="{k}">{l}</button>'
                              for k, l in [('total', 'All'), ('cup', 'Cup'), ('xfinity', 'Xfinity'), ('truck', 'Truck')])
        containers_parts = []
        for k, l in [('total', 'All'), ('cup', 'Cup'), ('xfinity', 'Xfinity'), ('truck', 'Truck')]:
            style = ' style="display:none"' if k != 'total' else ''
            containers_parts.append(f'<div class="stats-container" data-series="{k}"{style}>{_make_table(k, l)}</div>')
        containers = ''.join(containers_parts)

        filter_script = '''
        <script>
        (function(){
          var btns = document.querySelectorAll('.stats-tab-bar .filter-btn');
          var containers = document.querySelectorAll('.stats-container');
          btns.forEach(function(btn){
            btn.addEventListener('click', function(){
              btns.forEach(function(b){ b.classList.remove('active'); });
              btn.classList.add('active');
              var f = btn.getAttribute('data-filter');
              containers.forEach(function(el){
                el.style.display = el.getAttribute('data-series') === f ? '' : 'none';
              });
            });
          });
        })();
        </script>
        '''

        content = f'''
        <div class="breadcrumb"><a href="../index.html">Home</a> / <a href="index.html">Teams</a> / Career Stats</div>
        <h1 class="page-title">Team Career Stats</h1>
        <p class="subtitle">Team stats across all series.</p>
        <div class="filter-bar stats-tab-bar">{filter_btns}</div>
        {containers}
        {filter_script}
        '''
        self._write('teams/stats.html', 'Team Stats', content)

    def _build_team_page(self, slug):
        name = next((t for t, s in self.team_slugs.items() if s == slug), slug)
        # roster history by year (points races only)
        team_race_counts = defaultdict(int)
        for a in self.team_races.get(name, []):
            if (a['series'], a['year'], a['race_num']) in self._allstar_race_keys:
                continue
            d = a.get('driver')
            if d:
                team_race_counts[(a['year'], a['series'], d)] += 1
        history = defaultdict(list)
        for year, season in self.seasons.items():
            for series, roster in season.get('roster', {}).items():
                for r in roster:
                    if clean_team_name(r['team']) == name:
                        history[year].append((series, r['car'], r['driver']))
        rows = []
        for year in sorted(history.keys(), reverse=True):
            for series, car, driver in sorted(history[year], key=lambda x: SERIES_ORDER.index(x[0]) if x[0] in SERIES_ORDER else 99):
                for indiv in split_driver_names(driver):
                    indiv = self._resolve_to_career(indiv) or indiv
                    dslug = self.driver_slugs.get(indiv)
                    drv_link = f'<a href="../drivers/{dslug}.html">{esc(indiv)}</a>' if dslug else esc(indiv)
                    drv_display = drv_link
                    if indiv in self.rookie_drivers.get((series, year), set()):
                        drv_display += ' (R)'
                    cnt = team_race_counts.get((year, series, indiv), 0)
                    pos = self._season_finish(indiv, series, year)
                    pos_str = f'<b>{pos}</b>' if pos else '-'
                    rows.append([str(year), badge(series), esc(car), drv_display, str(cnt), pos_str])
        roster_tbl = table_html(['Year', 'Series', '#', 'Driver', 'Races', 'Fin'], rows, aligns={0: 'num', 2: 'num', 4: 'num', 5: 'num'})

        # ---- team stats (points races only) ----
        def _filter_points(apps):
            return [a for a in apps if (a['series'], a['year'], a['race_num']) not in self._allstar_race_keys]

        def _team_stats(apps):
            pts = _filter_points(apps)
            starts = len(pts)
            wins = sum(1 for a in pts if str(a.get('finish')) == '1')
            top5 = sum(1 for a in pts if str(a.get('finish')).isdigit() and int(a['finish']) <= 5)
            top10 = sum(1 for a in pts if str(a.get('finish')).isdigit() and int(a['finish']) <= 10)
            return starts, wins, top5, top10

        appearances = self.team_races.get(name, [])
        t_starts, t_wins, t_top5, t_top10 = _team_stats(appearances)
        # championships: any series/year where a driver from this team was champion that season
        t_champs = []
        for s in SERIES_ORDER:
            for year in sorted(self.years_by_series.get(s, [])):
                champ = self._champion_for(s, year)
                if champ:
                    lookup = self._roster_lookup(s, year)
                    champ_on_team = False
                    for entry in lookup.values():
                        for indiv in split_driver_names(entry['driver']):
                            resolved = self._resolve_to_career(indiv) or indiv
                            if resolved == champ and clean_team_name(entry['team']) == name:
                                champ_on_team = True
                                break
                        if champ_on_team:
                            break
                    if champ_on_team:
                        dslug = self.driver_slugs.get(champ)
                        drv_link = f'<a href="../drivers/{dslug}.html">{esc(champ)}</a>' if dslug else esc(champ)
                        t_champs.append(f'{year} {badge(s)} {drv_link}')

        # per-series stats table
        series_stats_rows = []
        for s in SERIES_ORDER:
            s_apps = [a for a in appearances if a['series'] == s]
            if s_apps:
                ss, sw, s5, s10 = _team_stats(s_apps)
                series_stats_rows.append([badge(s), fnum(ss), fnum(sw), fnum(s5), fnum(s10)])
        series_stats_rows.append([f'<b>Total</b>', fnum(t_starts), fnum(t_wins), fnum(t_top5), fnum(t_top10)])
        by_series_tbl = table_html(['Series', 'Starts', 'Wins', 'Top 5', 'Top 10'], series_stats_rows,
                                    aligns={1: 'num', 2: 'num', 3: 'num', 4: 'num'})

        stat_boxes = f'''
        <div class="stat-strip">
          <div class="stat-box"><div class="n">{fnum(t_starts)}</div><div class="l">Starts</div></div>
          <div class="stat-box"><div class="n">{fnum(t_wins)}</div><div class="l">Wins</div></div>
          <div class="stat-box"><div class="n">{fnum(t_top5)}</div><div class="l">Top 5s</div></div>
          <div class="stat-box"><div class="n">{fnum(t_top10)}</div><div class="l">Top 10s</div></div>
          <div class="stat-box"><div class="n">{fnum(len(t_champs))}</div><div class="l">Championships</div></div>
        </div>
        <div class="panel" id="stats-by-series"><h2>Stats by Series</h2><div class="body">{by_series_tbl}</div></div>'''
        champs_html = ''
        if t_champs:
            champs_html = f'<div class="panel" id="champs"><h2>Championships</h2><div class="body"><p style="margin:0">{"<br>".join(t_champs)}</p></div></div>'

        def _team_series_key(s):
            try:
                return SERIES_ORDER.index(s)
            except ValueError:
                return 999
        appearances_sorted = sorted(appearances, key=lambda a: (a['year'], _team_series_key(a['series']), a['race_num']), reverse=True)
        series_present = sorted({a['series'] for a in appearances_sorted}, key=_team_series_key)
        years_present = sorted({a['year'] for a in appearances_sorted}, reverse=True)
        team_points_races = 0
        race_rows = []
        row_classes = []
        row_attrs = []
        for a in appearances_sorted:
            is_as = (a['series'], a['year'], a['race_num']) in self._allstar_race_keys
            if not is_as:
                team_points_races += 1
            drv = a.get('driver')
            dslug = self.driver_slugs.get(drv)
            drv_cell = f'<a href="../drivers/{dslug}.html">{esc(drv)}</a>' if dslug else esc(drv)
            track_cell = f'<a href="../races/{a["series"]}/{a["year"]}/R{a["race_num"]}.html">{esc(format_track_name(a["track"]))}</a>'
            if is_as:
                track_cell += ' <span class="badge allstar">AS</span>'
            race_rows.append([str(a['year']), badge(a['series']),
                               track_cell,
                               drv_cell, esc(a.get('car')), esc(a.get('finish')), esc(a.get('points'))])
            row_classes.append('win' if a.get('finish') == '1' else '')
            row_attrs.append(f'data-series="{a["series"]}" data-year="{a["year"]}"')
        race_tbl = table_html(['Year', 'Series', 'Track', 'Driver', '#', 'Fin', 'Pts'], race_rows,
                               row_classes=row_classes, row_attrs=row_attrs,
                               aligns={0: 'num', 4: 'num', 5: 'num', 6: 'num'}, table_id='team-race-log')

        filter_html = ''
        if len(series_present) > 1 or len(years_present) > 1:
            parts = []
            if len(series_present) > 1:
                btns = ['<button type="button" class="filter-btn active" data-filter-type="series" data-filter-value="all">All</button>']
                for s in series_present:
                    btns.append(f'<button type="button" class="filter-btn" data-filter-type="series" data-filter-value="{s}">{SERIES_LABELS[s]}</button>')
                parts.append('<span class="filter-group">' + ''.join(btns) + '</span>')
            if len(years_present) > 1:
                opts = ['<option value="all">All Years</option>']
                for y in years_present:
                    opts.append(f'<option value="{y}">{y}</option>')
                parts.append('<span class="filter-group"><select class="filter-select" data-filter-type="year">' + ''.join(opts) + '</select></span>')
            filter_html = '<div class="filter-bar">' + ' '.join(parts) + '</div>'

        filter_script = '''
        <script>
        (function(){
          var panel = document.getElementById('results');
          if (!panel) return;
          var rows = panel.querySelectorAll('#team-race-log tbody tr');
          var yearSel = panel.querySelector('[data-filter-type="year"]');
          function applyFilters() {
            var seriesVal = 'all';
            panel.querySelectorAll('.filter-btn.active').forEach(function(b){
              if (b.getAttribute('data-filter-type') === 'series') seriesVal = b.getAttribute('data-filter-value');
            });
            var yearVal = yearSel ? yearSel.value : 'all';
            rows.forEach(function(r){
              r.style.display =
                (seriesVal === 'all' || r.getAttribute('data-series') === seriesVal) &&
                (yearVal === 'all' || r.getAttribute('data-year') === yearVal) ? '' : 'none';
            });
          }
          panel.querySelectorAll('.filter-btn').forEach(function(btn){
            btn.addEventListener('click', function(){
              var type = btn.getAttribute('data-filter-type');
              panel.querySelectorAll('.filter-btn[data-filter-type="' + type + '"]').forEach(function(b){
                b.classList.remove('active');
              });
              btn.classList.add('active');
              applyFilters();
            });
          });
          if (yearSel) { yearSel.addEventListener('change', applyFilters); }
        })();
        </script>
        '''

        display_name = TEAM_DISPLAY.get(name, name)
        logo_html = self._team_logo_html(slug, name)

        standings_chart_svg = self._team_standings_chart_svg(name)
        standings_chart_html = f'<div class="panel" id="team-standings-history"><h2>Season Standings History</h2><div class="body"><div style="overflow-x:auto">{standings_chart_svg}</div></div></div>' if standings_chart_svg else ''

        jump_links = ['<a href="#stats-by-series">Stats by Series</a>']
        if standings_chart_html:
            jump_links.append('<a href="#team-standings-history">Standings</a>')
        jump_links.append('<a href="#roster">Roster History</a>')
        if champs_html:
            jump_links.append('<a href="#champs">Championships</a>')
        jump_links.append('<a href="#results">Race Results</a>')
        jump = f'<div class="jump-bar">{" ".join(jump_links)}</div>'

        title_row = f'<div class="driver-title-row">{logo_html}<div><h1 class="page-title" style="margin-top:0">{esc(display_name)}</h1></div></div>' if logo_html else f'<h1 class="page-title">{esc(display_name)}</h1>'

        content = f'''
        <div class="breadcrumb"><a href="../index.html">Home</a> / <a href="index.html">Teams</a> / {esc(display_name)}</div>
        {title_row}
        {jump}
        {stat_boxes}
        {standings_chart_html}
        <div class="panel" id="roster"><h2>Roster History</h2><div class="body">{roster_tbl}</div></div>
        {champs_html}
        <div class="panel" id="results"><h2>Race Results ({team_points_races} on file)</h2>{filter_html}<div class="body">{race_tbl}</div></div>
        {filter_script if filter_html else ''}
        '''
        self._write(f'teams/{slug}.html', name, content)

    def _build_tracks_index(self):
        cards = []
        for t in sorted(self.track_races.keys()):
            slug = self.track_slugs[t]
            n = len(self.track_races[t])
            cards.append(f'<div class="card"><h3><a class="plain" href="{slug}.html">{esc(format_track_name(t))}</a></h3>'
                         f'<div class="stat-row"><span>Races on file</span><span>{n}</span></div></div>')
        content = f'''
        <div class="breadcrumb"><a href="../index.html">Home</a> / Tracks</div>
        <h1 class="page-title">Tracks</h1>
        <p class="subtitle">{len(self.track_races)} tracks on record.</p>
        <div class="grid">{''.join(cards)}</div>
        '''
        self._write('tracks/index.html', 'Tracks', content)

    def _build_track_page(self, slug):
        name = next((t for t, s in self.track_slugs.items() if s == slug), slug)
        def _series_key(s):
            try:
                return SERIES_ORDER.index(s)
            except ValueError:
                return 999
        appearances = sorted(self.track_races.get(name, []),
                              key=lambda a: (a['year'], _series_key(a['series']), a['race_num']), reverse=True)
        series_present = sorted({a['series'] for a in appearances}, key=_series_key)
        rows = []
        row_attrs = []
        for a in appearances:
            winner = esc(a.get('winner')) if a.get('winner') else '-'
            wslug = self.driver_slugs.get(a.get('winner')) if a.get('winner') else None
            if wslug:
                winner = f'<a href="../drivers/{wslug}.html">{winner}</a>'
            is_as = (a['series'], a['year'], a['race_num']) in self._allstar_race_keys
            race_cell = f'<a href="../races/{a["series"]}/{a["year"]}/R{a["race_num"]}.html">Race {a["race_num"]}</a>'
            if is_as:
                race_cell += ' <span class="badge allstar">AS</span>'
            rows.append([str(a['year']), badge(a['series']),
                         race_cell,
                         winner])
            row_attrs.append(f'data-series="{a["series"]}"')
        display_name = format_track_name(name)
        track_img = self._track_image_html(slug, name)
        track_points = sum(1 for a in appearances if (a['series'], a['year'], a['race_num']) not in self._allstar_race_keys)
        track_total = len(appearances)
        first_year = min(a['year'] for a in appearances) if appearances else '-'
        track_len = TRACK_LENGTHS.get(display_name) or TRACK_LENGTHS.get(name)
        track_len_str = f'{track_len} mi' if track_len else '-'
        location = TRACK_LOCATIONS.get(display_name) or TRACK_LOCATIONS.get(name)
        tbl = table_html(['Year', 'Series', 'Race', 'Winner'], rows, aligns={0: 'num'}, row_attrs=row_attrs, table_id='track-race-log')
        title_row = f'<div class="driver-title-row">{track_img}<div><h1 class="page-title" style="margin-top:0">{esc(display_name)}</h1></div></div>' if track_img else f'<h1 class="page-title">{esc(display_name)}</h1>'

        stat_boxes = f'''
        <div class="stat-strip">
          <div class="stat-box"><div class="n">{track_total}</div><div class="l">Total Races</div></div>
          <div class="stat-box"><div class="n">{track_points}</div><div class="l">Points Races</div></div>
          <div class="stat-box"><div class="n">{first_year}</div><div class="l">First Race</div></div>
          <div class="stat-box"><div class="n">{track_len_str}</div><div class="l">Length</div></div>
          <div class="stat-box"><div class="n">{esc(location) if location else '-'}</div><div class="l">Location</div></div>
        </div>
        '''

        # --- Track records: best per-category per-series ---
        tds = self.track_driver_stats.get(name, {})
        series_keys = [('total', 'Overall')] + [(s, SERIES_LABELS.get(s, s)) for s in SERIES_ORDER[::-1] if s in series_present]
        # only show series that have at least one driver with a start
        series_keys = [(sk, sl) for sk, sl in series_keys if any(d.get(sk, {}).get('starts', 0) for d in tds.values())]
        record_sections = []
        for sk, slabel in series_keys:
            candidates = [(drv, stats[sk]) for drv, stats in tds.items() if stats[sk]['starts'] > 0]
            if not candidates:
                continue
            # Compute best avg finish (need min 3 starts)
            for c in candidates:
                d, s = c
                if s['finish_n'] >= 3:
                    s['avg_f'] = round(s['finish_sum'] / s['finish_n'], 1)
                else:
                    s['avg_f'] = None
            best_win_drv, best_win_s = max(candidates, key=lambda x: x[1]['wins'])
            best_led_drv, best_led_s = max(candidates, key=lambda x: x[1]['laps_led'])
            best_t5_drv, best_t5_s = max(candidates, key=lambda x: x[1]['top5'])
            best_pole_drv, best_pole_s = max(candidates, key=lambda x: x[1]['poles'])
            # best avg finish among those with 3+ starts
            avg_cands = [(d, s) for d, s in candidates if s['avg_f'] is not None]
            best_avg_drv, best_avg_s = min(avg_cands, key=lambda x: x[1]['avg_f']) if avg_cands else ('-', None)
            def _link(d):
                s = self.driver_slugs.get(d)
                return f'<a href="../drivers/{s}.html">{esc(d)}</a>' if s else esc(d)
            rows = []
            rows.append(['Most Wins', str(best_win_s['wins']), _link(best_win_drv)])
            rows.append(['Most Laps Led', str(best_led_s['laps_led']), _link(best_led_drv)])
            rows.append(['Most Top 5s', str(best_t5_s['top5']), _link(best_t5_drv)])
            rows.append(['Most Poles', str(best_pole_s['poles']), _link(best_pole_drv)])
            rows.append(['Best Avg Finish', str(best_avg_s['avg_f']) if best_avg_s else '-', _link(best_avg_drv) if best_avg_drv != '-' else '-'])
            record_sections.append(f'<div style="margin-top:12px">{badge(sk) if sk != "total" else """<span class="badge overall">Overall</span>"""}</div>' + table_html(['Category', 'Record', 'Driver'], rows))
        records_html = ''.join(f'<div class="body">{s}</div>' for s in record_sections) if record_sections else ''
        if records_html:
            records_html = f'<div class="panel"><h2>Track Records</h2>{records_html}</div>'

        filter_html = ''
        if len(series_present) > 1:
            btns = ['<button type="button" class="filter-btn active" data-filter-type="series" data-filter-value="all">All</button>']
            for s in series_present:
                btns.append(f'<button type="button" class="filter-btn" data-filter-type="series" data-filter-value="{s}">{SERIES_LABELS[s]}</button>')
            filter_html = '<div class="filter-bar"><span class="filter-group">' + ''.join(btns) + '</span></div>'

        filter_script = '''
        <script>
        (function(){
          var panel = document.getElementById('track-race-log-panel');
          if (!panel) return;
          var rows = panel.querySelectorAll('#track-race-log tbody tr');
          function applyFilters() {
            var seriesVal = 'all';
            panel.querySelectorAll('.filter-btn.active').forEach(function(b){
              if (b.getAttribute('data-filter-type') === 'series') seriesVal = b.getAttribute('data-filter-value');
            });
            rows.forEach(function(r){
              r.style.display = (seriesVal === 'all' || r.getAttribute('data-series') === seriesVal) ? '' : 'none';
            });
          }
          panel.querySelectorAll('.filter-btn').forEach(function(btn){
            btn.addEventListener('click', function(){
              var type = btn.getAttribute('data-filter-type');
              panel.querySelectorAll('.filter-btn[data-filter-type="' + type + '"]').forEach(function(b){
                b.classList.remove('active');
              });
              btn.classList.add('active');
              applyFilters();
            });
          });
        })();
        </script>
        ''' if filter_html else ''

        content = f'''
        <div class="breadcrumb"><a href="../index.html">Home</a> / <a href="index.html">Tracks</a> / {esc(display_name)}</div>
        {title_row}
        {stat_boxes}
        {records_html}
        <div class="panel" id="track-race-log-panel"><h2>Race History</h2>{filter_html}<div class="body">{tbl}</div></div>
        {filter_script}
        '''
        self._write(f'tracks/{slug}.html', name, content)

    def _generate_search_data(self):
        data = {
            'drivers': [{'name': d, 'slug': self.driver_slugs[d]} for d in self.all_drivers],
            'teams': [{'name': t, 'slug': self.team_slugs[t]} for t in self.all_teams],
            'tracks': [{'name': format_track_name(t), 'slug': self.track_slugs[t]} for t in sorted(self.track_races.keys())],
            'pages': [{'name': 'Records', 'slug': 'records/index'}, {'name': 'All-Star', 'slug': 'allstar/index'}],
        }
        js = 'var SEARCH_DATA = ' + json.dumps(data) + ';'
        path = os.path.join(self.out_dir, 'static', 'search-data.js')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(js)

    def _build_driver_compare_page(self):
        drv_list = []
        for d in self.all_drivers:
            raw = self.driver_race_stats.get(d, {}).get('total', {})
            if not raw.get('starts'):
                continue
            by_series = {}
            for s in SERIES_ORDER:
                sraw = self.driver_race_stats.get(d, {}).get(s, {})
                if sraw.get('starts'):
                    avg_f = round(sraw['finish_sum'] / sraw['finish_n'], 1) if sraw.get('finish_n') else None
                    by_series[s] = {
                        'starts': sraw['starts'], 'wins': sraw['wins'], 'top5': sraw['top5'],
                        'top10': sraw['top10'], 'avg_f': avg_f, 'poles': sraw['poles'], 'points': round(sraw['points'], 1),
                    }
            t = raw
            avg_f = round(t['finish_sum'] / t['finish_n'], 1) if t.get('finish_n') else None
            drv_list.append({
                'name': d, 'slug': self.driver_slugs[d],
                'total': {'starts': t['starts'], 'wins': t['wins'], 'top5': t['top5'],
                          'top10': t['top10'], 'avg_f': avg_f, 'poles': t['poles'], 'points': round(t['points'], 1)},
                'by_series': by_series,
            })
        drv_json = json.dumps(drv_list)
        content = f'''
        <div class="breadcrumb"><a href="../index.html">Home</a> / <a href="index.html">Drivers</a> / Compare</div>
        <h1 class="page-title">Compare Drivers</h1>
        <p class="subtitle">Select up to 3 drivers to compare their career stats side by side.</p>
        <div id="compare-app">
          <div class="filter-bar" style="padding:0 0 16px">
            <select id="compare-select" class="filter-select" style="min-width:280px" multiple size="1">
              <option value="">-- Choose a driver --</option>
            </select>
            <button type="button" class="filter-btn" id="compare-btn">Compare</button>
          </div>
          <div id="compare-results"></div>
        </div>
        <script>
        var DRIVERS = {drv_json};
        var COMPARE_SERIES = {{'cup':'Cup','xfinity':'Xfinity','truck':'Truck'}};
        </script>
        <script src="../static/compare.js"></script>
        '''
        self._write('drivers/compare.html', 'Compare Drivers', content)
