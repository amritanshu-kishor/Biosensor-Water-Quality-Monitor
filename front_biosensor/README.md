# Biosensor Water Quality Detector (Frontend)

Static **HTML + CSS + JavaScript** frontend for a 2-layer biosensor-based water quality detector:

- **Pre-analysis layer**: screening using **PPI** and **RI**
- **Advanced layer**: runs only if pre-analysis passes, using **TDS**, **pH**, **Turbidity** + **graphs**
- **Final output**: clear declaration of whether water is **Drinkable / Non-drinkable**

## Screens / Flow

1. Enter **PPI** and **RI** → click **Run pre-analysis**
2. If screening **passes**, Advanced layer unlocks
3. Click **Run advanced layer** to get TDS/pH/Turbidity + charts + final verdict

## Run locally

You can open `index.html` directly, but using a local server is recommended.

### Option A: VS Code / Cursor Live Server

- Install “Live Server”
- Right-click `index.html` → **Open with Live Server**

### Option B: Python (if installed)

From the project folder:

```bash
python -m http.server 5500
```

Then open `http://localhost:5500`.

## Files

- `index.html`: UI layout (pre-analysis + advanced layer)
- `styles.css`: modern dashboard styling
- `app.js`: logic (gating, demo sensor values, verdict, Chart.js graphs)

## Thresholds / Calibration

Update thresholds in `app.js` inside the `CONFIG` object:

- Pre-analysis ranges: `CONFIG.preAnalysis.ppi`, `CONFIG.preAnalysis.ri`
- Advanced thresholds: `CONFIG.advanced.tds`, `CONFIG.advanced.ph`, `CONFIG.advanced.turbidity`

## Backend integration (later)

This frontend can run in **demo mode** (no backend), or connect to the Flask backend in this repo.

In `app.js`, replace the demo generator in:

- `fetchLatestReading()` → call your API (example: `/api/latest`)

Expected JSON format:

```json
{
  "tds": 220,
  "ph": 7.2,
  "turbidity": 1.8
}
```

If you want realtime updates, you can also replace `simulateStream()` with WebSocket/SSE.

## Connect to the backend in this repo

1. Start backend:

```bash
cd smart_water_biosensor_backend
pip install -r requirements.txt
python main.py
```

2. Start frontend (any static server) and open the dashboard with an API base:

- Example: `index.html?api=http://127.0.0.1:5000`

The dashboard uses:

- `GET /water/generate` to create a new sample
- `GET /water/report/advanced` to read the latest values (pH, RI, TDS, turbidity, water level)

## Charts

Charts use **Chart.js** via CDN (no bundler needed).  
If you prefer no external CDNs, tell me and I’ll vendor a local copy.

## Project status

- Frontend UI + visuals: done
- Pre-analysis gating → advanced layer lock/unlock: done
- Advanced metrics + charts + final declaration: done
- Backend API wiring: pending (you’ll provide endpoints / payloads)
