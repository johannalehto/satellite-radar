# Satellite Catalog Updater (satellite-catalog-updater)

This Fly.io app updates satellite position data in MongoDB once per day using precomputed TLE data from Celestrak.

It is part of a larger system, where:
- `satellites-api-core` serves client requests
- `satellite-catalog-updater` handles backend satellite calculations and data refresh

---

## 🔧 How it works

- A scheduled Fly Machine runs `run_updater.py` once daily
- The task uses [CelesTrak](https://celestrak.org/) data to calculate satellite positions
- Results are upserted into the `satellite_catalog` collection in MongoDB
- The job includes a buffer of one hour (i.e. covering 25 hours of positions) to ensure data is always ahead of time

---

## 🔁 Scheduling

This app runs as a scheduled task via `fly machine run`:

```bash
fly machine run . -a satellite-catalog-updater \
  --schedule daily \
  --restart no \
  -- \
  python app/satellite_catalog/updater.py
```
Fly handles launching, running, and shutting down the Machine each day.


---

## 🗂 Project structure

```bash
app/
  satellite_catalog/
    updater.py        Script triggering `run_update() `

Dockerfile             Shared with `satellites-api-core`
fly.updater.toml          Config for the updater-specific Fly app
```

---

## 📦 Deployment
This updater app uses the same Dockerfile as the main API. The actual behavior is controlled via the command passed to fly machine run.

If in the future the satellite catalog is split into a microservice, it will:

- Run its own Dockerfile with a baked-in CMD

- Optionally expose a /satellite-catalog endpoint directly

- Own its data update lifecycle fully

---

## ➡️ Future improvements
- Move satellite-catalog to a standalone microservice

- Add optional HTTP API for direct position queries

- Replace Fly Machine scheduler with GitHub Actions or a queue if scaling
