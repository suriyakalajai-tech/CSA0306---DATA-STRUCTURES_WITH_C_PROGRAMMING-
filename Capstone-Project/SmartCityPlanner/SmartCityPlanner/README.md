# Smart City Navigation and Utility Network Planner

A local Flask + SQLite + Leaflet starter application for a Chennai-focused university capstone. It includes an administrator dashboard, interactive OpenStreetMap view, four analysis modules, saved analysis history and CSV export.

## Quick start (Windows)

1. Install **Python 3.10 or newer** from https://www.python.org/downloads/ and enable **Add Python to PATH**.
2. Extract this ZIP to a folder such as `E:\SmartCityPlanner`.
3. Open that folder in VS Code.
4. Open Terminal → New Terminal and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. Or skip activation and use `.venv\Scripts\python.exe -m pip install -r requirements.txt` followed by `.venv\Scripts\python.exe app.py`.

5. Open **http://127.0.0.1:5000** in your browser.

## First login

- Username: `admin`
- Password: `Admin@123`

Change the default password and `SECRET_KEY` before using beyond a local demonstration.

## Included modules

1. Urban accessibility: Dijkstra shortest path, alternative route candidate, graph connectivity and critical-node demonstration.
2. Utility optimizer: Kruskal minimum spanning tree and disjoint-set union with a clearly labelled shared-corridor cost assumption.
3. Conflict detection: Shapely geometric intersection and distance checks on sample utility geometries.
4. Resilience: Edmonds–Karp maximum flow and connected-component simulation.

## Important data limitations

This is a runnable academic demonstration, not a certified municipal GIS decision-support system. Seeded Chennai locality/facility points are a small illustrative sample. Utility geometries, capacities, costs, road graph, service thresholds and failure scenarios are simulated. The map uses OpenStreetMap tiles and requires internet access. OSM attribution is displayed. OSM data coverage varies and OSM data is subject to ODbL; comply with attribution and share-alike requirements when distributing derived databases.

For a production-quality city-scale implementation, import validated OSM road/facility data and authorized utility asset data, build a projected metric network (e.g. EPSG:32644 for Chennai), add an actual R-tree/STRtree candidate index, implement route approval/versioning, CSRF protection, rate limiting, secure account management, job queues, backup verification and full PDF/XLSX reporting. Do not present the sample outputs as real city measurements.

## Project structure

- `app.py` – Flask routes and application entry point
- `database.py` – SQLite schema and first-run demo seed
- `algorithms/graph.py` – custom Dijkstra, alternative route, Kruskal, components and Edmonds–Karp
- `templates/` – ten application pages including login
- `static/` – responsive dashboard styling and Leaflet interactions
- `instance/smartcity.db` – created automatically on first run
- `reports/`, `backups/` – reserved for report and backup outputs

## Troubleshooting

- **`py` is not recognized:** install Python and tick “Add python.exe to PATH”, then reopen VS Code.
- **Package installation fails:** check internet and rerun `python -m pip install -r requirements.txt`.
- **Port 5000 is busy:** change `port=5000` in the last line of `app.py` to `port=5001`.
- **Map is blank:** check internet access; Leaflet and OpenStreetMap tiles load from CDNs.
- **Reset demo database:** stop the server, delete `instance/smartcity.db`, and restart. This resets all local users and analysis history.

## Simplest Windows setup
You can also double-click `setup.bat` once to create the virtual environment and install dependencies, then double-click `start.bat` whenever you want to launch the website.
