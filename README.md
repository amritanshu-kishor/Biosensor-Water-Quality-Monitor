# Biosensor-Water-Quality-Monitor
A compact project using biosensors to detect contaminants in water and convert signals into measurable data. Integrated with a microcontroller and visualization tools, it enables real‑time monitoring, alerts for unsafe conditions, and supports sustainable water management in both domestic and industrial settings.

## Folders

- `smart_water_biosensor_backend/`: Flask API (Swagger at `/apidocs/`)
- `front_biosensor/`: Static frontend dashboard (Chart.js) + About page

## Quick run (local)

Backend:

```bash
cd smart_water_biosensor_backend
pip install -r requirements.txt
python main.py
```

Frontend:

- Open `front_biosensor/index.html` via a local server and add `?api=http://127.0.0.1:5000` to use realtime samples.
- Or run without the query param to use demo data.
