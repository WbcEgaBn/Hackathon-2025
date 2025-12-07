# Colorado Springs Legistar Agenda PDF Scraper

This Python script automatically downloads **all Agenda PDFs** from the Colorado Springs Legistar calendar ([https://coloradosprings.legistar.com/Calendar.aspx](https://coloradosprings.legistar.com/Calendar.aspx)) and saves them to a local directory.

---

## Features

- Automatically navigates the Legistar calendar, including **all pages**.
- Opens each **meeting detail page** to find Agenda PDFs.
- Downloads all PDFs labeled **“Agenda”**.
- Saves PDFs to a local folder (`~/Downloads/legistar_agendas` by default).
- Handles dynamic JavaScript content using **Selenium**.
- Skips meetings that are **not viewable by the public**.
- Avoids downloading duplicate files.

---

## Requirements

- Python 3.8+  
- Google Chrome (or Chromium)  
- Python packages:

```bash
pip install selenium requests beautifulsoup4 webdriver-manager
