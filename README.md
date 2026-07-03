# NR2003 Sim Racing Reference

A static reference website built from NR2003 race result HTML files and a season workbook.

## Quick Start

```bash
pip install -r requirements.txt
cd nascar_ref_site_builder/nascar_ref
python build_site.py --results ../../results --workbook "../../NASCAR SIM.xlsx"
```

Open `./site/index.html` in your browser.

## Deploy to GitHub Pages

Push to the `main` branch — the GitHub Action in `.github/workflows/deploy.yml`
automatically builds and deploys the site.
