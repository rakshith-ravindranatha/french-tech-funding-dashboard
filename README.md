# 🇫🇷 French Tech Fundraising Dashboard 2026

An interactive dashboard tracking French startup fundraising rounds in 2026, sourced from [Eldorado.co](https://eldorado.co/blog/analyses-des-lev%C3%A9es-de-fonds).

**Live site →** https://rakshith-ravindranatha.github.io/french-tech-funding-dashboard

---

## Features

- **Monthly bar chart** — click a bar to filter by month
- **Multi-filter** — sector, stage, region, free-text search
- **Company cards** — colour-coded by sector
- **Detail modal** — description, investors, stage, region
- **Jobs tab** — direct links to Welcome to the Jungle & LinkedIn

## Project Structure

```
├── index.html                  # Dashboard UI (loads data dynamically)
├── data/
│   └── companies.json          # Company data — update this monthly
├── scripts/
│   └── scrape_eldorado.py      # Helper to pull new months from Eldorado
└── .github/
    └── workflows/
        └── deploy.yml          # Auto-deploy to GitHub Pages on push
```

## Adding a New Month

1. Run the scraper (optional first pass):
   ```bash
   pip install requests beautifulsoup4
   python scripts/scrape_eldorado.py
   ```
2. Open `data/companies.json` and enrich new entries (sector, region, description, investors).
3. Update `MONTH_META` in `index.html` with the new month's totals from Eldorado.
4. Commit and push — GitHub Actions deploys automatically.

## Data Source

All fundraising data is sourced from [Eldorado.co](https://eldorado.co) monthly analyses. The dashboard currently covers **January – May 2026** (35 featured companies).

## Tech Stack

- Vanilla HTML/CSS/JS — zero build step
- [Chart.js](https://www.chartjs.org/) for the monthly chart
- GitHub Pages for hosting
- GitHub Actions for CI/CD
