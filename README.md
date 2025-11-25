# Week 10 – Networking & Protocols: Interactive Dashboard

## Objective

This week, you will enhance your Streamlit dashboard with **interactive controls** and use **real data**
from your monitoring system. This repository now includes two sample databases (Week 7 and Week 8): `log.db7.db` and `log.db8.db`.

---

## Data Source

Your dashboard can read the databases produced in:
- Week 7 — SQLite logging sample: `log.db7.db`
- Week 8 — Alert updates sample: `log.db8.db`

If these files are missing or you want to generate fresh data, there's a small helper script included — `generate_sample_dbs.py` — that creates both `log.db7.db` and `log.db8.db` in the repository root.

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

Make sure `log.db7.db` and/or `log.db8.db` are in the same directory as `app.py` (the repo root). This repository already contains the sample DB files so the app should work out-of-the-box.

---

## Screenshot (example)

Below is a sample screenshot (assets/screenshots/dashboard_screenshot.svg) showing the Dashboard page with filters and charts. Use it as a reference when capturing your own screenshot for submission.

![Dashboard example](assets/screenshots/dashboard_screenshot.svg)

### Where you should take your own screenshot

1. Run the app locally:

```powershell
# (Optional) regenerate the sample DBs
# Windows PowerShell example (use your Python executable path):
C:/path/to/python.exe generate_sample_dbs.py

# run the dashboard
streamlit run app.py
```

2. In the sidebar select:
   - Dataset: Week 7 or Week 8 (or Both)
   - Set Ping status (All / UP / DOWN)
   - Set a CPU threshold (e.g., 10%)
   - (Optionally) enable Auto refresh or press Refresh

3. Make sure the Dashboard page is selected from the sidebar so the top metrics, charts (Resource Usage), and the filtered table are visible.

4. Capture a screenshot that clearly shows:
   - The sidebar with the chosen filters
   - The top metrics (Records, Avg CPU/Memory/Disk)
   - The Resource Usage chart
   - Part of the Filtered Records table

5. Save the screenshot as PNG or JPG and include it in your submission (for example, place it in `assets/screenshots/your_screenshot.png`).

When uploading to your course/learning platform, attach the saved image file and include the GitHub repo link.

## Submission Checklist

 app.py includes sidebar, dataset selection (Week 7 / Week 8 / Both), filters, refresh, and CSV export

 Charts render correctly

 Screenshot of dashboard with filters

 Code pushed to GitHub
 ---

---
## Execution log

This repo already contains `log.db7.db` and `log.db8.db` in the root — `app.py` can read them. To (re)generate locally:

```powershell
# (re)generate sample DBs using the included generator
C:/path/to/python.exe generate_sample_dbs.py

# start the Streamlit app
streamlit run app.py
```

## Bonus (Optional)

Add a date filter using st.date_input

Display alert count (how many records exceeded thresholds)

Add Dark Mode toggle in the Settings page
