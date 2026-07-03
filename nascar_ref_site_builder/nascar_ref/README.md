# Sim Racing Reference — Local Site Builder

Turns your NR2003 race result HTML files + season workbook into a local,
click-through "Racing-Reference" style website: driver pages, team pages,
season schedules, race pages, and points standings. No server required —
it's just static HTML files you open in a browser.

## What you need

- Python 3.9+ installed on your machine
- Your folder of race result files (e.g. `EEL_SIM_NCS_2034_R23.html`)
- Your `NASCAR_SIM.xlsx` roster/season workbook

## Setup (one time)

Open a terminal in this folder and run:

```
pip install pandas openpyxl beautifulsoup4 jinja2
```

## Build the site

```
cd C:\Users\eelbo\Desktop\Ethan\NR Website\nascar_ref_site_builder\nascar_ref
python build_site.py --results "C:\Users\eelbo\Desktop\Ethan\NR Website\results" --workbook "C:\Users\eelbo\Desktop\Ethan\NR Website\NASCAR SIM.xlsx" --out ./site
```

- `--results` — the folder containing all your `EEL_SIM_*.html` result files (they can all be in one flat folder)
- `--workbook` — path to your season/roster spreadsheet
- `--out` — where to generate the site (default `./site`)

When it finishes, open `site/index.html` in your browser (double-click it).
Every driver, team, season, race, and standings page is linked together.

## Re-running it

Any time you add new race result files or update the spreadsheet, just
re-run the same command. It regenerates the whole site fresh each time
(safe to delete the `site` folder and rebuild).

## How it works / what it reads

- **Race files**: parses the Practice / Qualifying / Happy Hour / Race
  tables, plus cautions, lead changes, weather, pit frequency, AI strength,
  and penalties for each race weekend. The series and season are read from
  the filename (`NCS`=Cup, `NXS`=Xfinity, `NTS`=Truck), and the race number
  is matched against your workbook's schedule for that series/season.
- **Workbook**: reads the `Stats` sheet for career totals, and each year
  sheet (`2020`, `2021`, ...) for that season's schedule, rosters (car
  number → driver → team), final driver points standings, and team (owner)
  points. If a season's official standings table isn't filled in yet
  (season still in progress), the site instead computes live, unofficial
  standings by summing points straight from whatever race files you have
  on hand for that season, and labels it as such.
- Driver and team pages cross-reference the race files, so team assignment
  per race is looked up by matching each race's car number against that
  season's roster table.

## Known limitations / things you might want to tweak

- Team assignment is season-long (from the roster table), so it won't
  reflect a mid-season driver swap for the same car number unless you edit
  the roster table in the spreadsheet to reflect it.
- A few "career stats" rows in your `Stats` sheet appear to be shared-ride
  combo entries (e.g. `Blaney/Keselowski/Buescher`) — these get their own
  (harmless) driver page since they're just treated as another name.
- The `Hub` sheet (win-lists, championship history, all-star records, etc.)
  isn't used yet — the site is built from `Stats` + the year sheets + your
  race files. Happy to wire more of it in if you want those pages too.
- If a race file is missing for a scheduled race, the schedule page just
  shows "No file" for it instead of a link.

## Files in this folder

- `build_site.py` — the command you run
- `parser_xlsx.py` — reads the workbook
- `parser_html.py` — reads the race result HTML files
- `generator.py` — builds all the HTML pages
- `templates/`, `static/` — page shell and stylesheet
