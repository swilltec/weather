# Weather App (React + TypeScript + Vite)

A weather dashboard with current conditions, 5-day forecast, geolocation, theming, and shadcn/ui components.

## Prerequisites
- Node.js **≥20.19** (or 22.x). Vite 7 and React Router 7 require this.  
- npm 10+ (ships with current Node).

## Setup
1) Install dependencies  
   ```bash
   npm install
   ```
2) Configure environment variables  
   Create a `.env` file in the project root:
   ```bash
   VITE_OPENWEATHER_API_KEY=your_api_key_here
   ```
   You can reuse the sample key already present in `.env` if it’s valid.

## Run
- Dev server:  
  ```bash
  npm run dev
  ```
  Then open the printed localhost URL (default `http://localhost:5173`).

- Production build:  
  ```bash
  npm run build
  npm run preview
  ```

## If you received a zip
1) Unzip `weather_app.zip` somewhere you can work (e.g., Desktop).  
2) Open a terminal and `cd` into the project folder:  
   ```bash
   cd /path/to/weather_app
   ```
3) Ensure `.env` exists in that folder with `VITE_OPENWEATHER_API_KEY=...` set.  
4) Install dependencies from the project root (same folder as `package.json`):  
   ```bash
   npm install
   ```
5) Start dev server:  
   ```bash
   npm run dev
   ```
   or build/preview with `npm run build && npm run preview`.

## Tech Stack
- React 19 + TypeScript + Vite 7
- React Router 7
- @tanstack/react-query for data fetching/caching
- Tailwind CSS 4 + shadcn/ui components
- OpenWeather API (current weather, 5-day forecast, geocoding)
