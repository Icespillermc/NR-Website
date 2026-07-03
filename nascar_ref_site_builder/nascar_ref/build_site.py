#!/usr/bin/env python3
"""Build a local, static 'racing reference' style website from your NR2003
sim race result HTML files and season workbook.

Usage:
    python build_site.py --results /path/to/race/htmls --workbook NASCAR_SIM.xlsx --out ./site

Then open ./site/index.html in your browser. No server required.
"""
import argparse
import sys
from parser_xlsx import parse_workbook
from parser_html import scan_results_dir
from generator import SiteBuilder


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--results', required=True, help='Folder containing your EEL_SIM_*.html race result files')
    ap.add_argument('--workbook', required=True, help='Path to your season/roster .xlsx workbook')
    ap.add_argument('--out', default='./site', help='Output folder for the generated website (default: ./site)')
    ap.add_argument('--name', default='Sim Racing Reference', help='Site title')
    ap.add_argument('--list-tracks', action='store_true',
                     help="Don't build the site -- just print every distinct raw track name "
                          "found in your race files (with how many races used it) and which "
                          "canonical track page it currently gets merged into. Useful for "
                          "spotting duplicates that still need an alias.")
    ap.add_argument('--list-drivers', action='store_true',
                     help="Don't build the site -- just print every distinct raw driver name "
                          "found in your race files that could NOT be matched to a Stats-sheet "
                          "driver, sorted by how often it appears. Useful for spotting typos "
                          "or drivers missing from the Stats sheet.")
    args = ap.parse_args()

    print(f'Reading workbook: {args.workbook}')
    xlsx_data = parse_workbook(args.workbook)
    print(f'  -> {len(xlsx_data["seasons"])} season sheets, {len(xlsx_data["career"])} drivers in career stats')

    print(f'Scanning race results in: {args.results}')
    races = scan_results_dir(args.results)
    print(f'  -> parsed {len(races)} race files')
    if not races:
        print('No race files matched the expected filename pattern (e.g. EEL_SIM_NCS_2034_R23.html). Aborting.')
        sys.exit(1)

    if args.list_tracks or args.list_drivers:
        builder = SiteBuilder(xlsx_data, races, args.out, site_name=args.name)
        if args.list_tracks:
            print_track_report(builder)
        if args.list_drivers:
            print_driver_report(builder)
        return

    print(f'Generating site into: {args.out}')
    builder = SiteBuilder(xlsx_data, races, args.out, site_name=args.name)
    builder.build()
    print(f'Done. {len(builder.all_drivers)} driver pages, {len(builder.all_teams)} team pages, {len(races)} race pages.')
    print(f'Open {args.out}/index.html in your browser to view the site.')


def print_track_report(builder):
    from collections import Counter
    from parser_xlsx import _clean  # noqa
    from generator import clean_name
    raw_counts = Counter(clean_name(r['track']) for r in builder.races if r.get('track'))
    print('\n--- Track name report (raw name -> canonical page) ---')
    groups = {}
    for raw, canon in sorted(builder.track_canon.items()):
        groups.setdefault(canon, []).append((raw, raw_counts.get(raw, 0)))
    for canon, members in sorted(groups.items()):
        print(f'\n{canon}  [{sum(c for _, c in members)} races]')
        for raw, c in sorted(members, key=lambda x: -x[1]):
            flag = '' if raw.upper() == canon.upper() else '  <-- merged'
            print(f'    {c:>4}  {raw}{flag}')
    print('\nIf two of the groups above are actually the same real track, tell me the exact')
    print('raw name strings and I will add them to TRACK_ALIASES in generator.py.')


def print_driver_report(builder):
    from collections import Counter
    unresolved = Counter()
    for name, apps in builder.driver_races.items():
        if name not in builder.career:
            unresolved[name] = len(apps)
    print('\n--- Drivers in race results NOT matched to the Stats sheet ---')
    for name, count in unresolved.most_common(60):
        print(f'    {count:>4}  {name}')
    if not unresolved:
        print('    (none -- every driver in your race files matched the Stats sheet)')


if __name__ == '__main__':
    main()
