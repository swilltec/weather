Selenium smoke test for the frontend (search, favorites, theme toggle).

### Prerequisites
- Python 3.10+
- Google Chrome installed
- Frontend running locally (e.g. `cd frontend && npm install && npm run dev -- --host --port 5173`)

### Install deps
```bash
pip install -r "testing code/requirements.txt"
```

### Configure
- `BASE_URL` (default: `http://localhost:5173/`)
- `TEST_CITY` (default: `London`)
- `HEADLESS` set to `0` to see the browser, otherwise runs headless

### Run
```bash
python "testing code/selenium_smoke.py"
```
