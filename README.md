# Week 10 – Networking & Protocols: Interactive Dashboard

## Objective

This week, you will enhance your Streamlit dashboard with **interactive controls** and use **real data**
from your monitoring system (this repo contains sample DBs: `log.db7.db` and `log.db8.db` generated in Week 7–8).

---

## Data Source

Your dashboard can read the databases produced in:
- Week 7 — SQLite logging sample: `log.db7.db`
- Week 8 — Alert updates sample: `log.db8.db`

If these files are missing or empty, re-run `main.py` in Week 8 to generate sample data.

---

## Tasks

1. Add a **sidebar navigation menu**:
   - Dashboard
   - Settings
   - About
2. Implement **auto-refresh** or **manual refresh** button.
3. Add **filter controls**:
   - Ping_Status (All / UP / DOWN)
   - CPU Threshold slider
4. Display filtered data and charts for CPU, Memory, Disk.
5. Include a short description on the Settings and About pages.

---

## Example Output

- Sidebar with navigation
- Filtered data table
- Dynamic line charts
- Refresh button or timer

---

## Run the Dashboard

```bash
streamlit run app.py
```

Make sure `log.db7.db` and/or `log.db8.db` are in the same directory as `app.py` (the repo root).

## Submission Checklist

 app.py includes sidebar, dataset selection (Week 7 / Week 8 / Both), filters, refresh, and CSV export

 Charts render correctly

 Screenshot of dashboard with filters

 Code pushed to GitHub
 ---

---
## Execution log

I executed `main.py` (to generate a sample DB) on 2025-11-19 to create sample entries for the dashboard. This repo includes `log.db7.db` and `log.db8.db` in the root — `app.py` can read them. To reproduce locally:

```powershell
& ".venv/Scripts/python.exe" main.py
streamlit run app.py
```

## Bonus (Optional)

Add a date filter using st.date_input

Display alert count (how many records exceeded thresholds)

Add Dark Mode toggle in the Settings page
