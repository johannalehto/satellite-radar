# Satellites Radar

FastAPI backend for reading a satellite catalog from MongoDB and returning satellites visible from
a given observer location. The repository also contains currently a small static debug UI for manually testing
the radar endpoint.

## Prerequisites

- Python 3.12
- Poetry
- Make
- MongoDB credentials for the satellite catalog database
- Docker
- Fly CLI (`flyctl`) for deployment

## First-Time Setup

Install Python dependencies:

```bash
poetry install
```

Create a local `.env` file from the example if you want to run the API directly with Poetry or
`docker run` against the shared Atlas database:

```bash
cp .env.example .env
```

Then replace the MongoDB credentials in `.env`:

```bash
MONGO_USERNAME=replace-with-mongo-username
MONGO_PASSWORD=replace-with-mongo-password
MONGO_HOST=cluster0.afeh5pj.mongodb.net
MONGO_DBNAME=satellites_db
```

`MONGO_HOST` and `MONGO_DBNAME` have defaults, but `MONGO_USERNAME` and `MONGO_PASSWORD`
are required for the API to read the satellite catalog.

## Local Development

Run the FastAPI app locally:

```bash
make run-local
```

This runs:

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Useful local URLs:

- FastAPI docs: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Radar endpoint: `http://127.0.0.1:8000/satellite_radar/get_visible_satellites/{lat}/{lon}`
- Example radar request: `http://127.0.0.1:8000/satellite_radar/get_visible_satellites/35.3112/139.5341`

## Debug UI

The debug UI is a static HTML page in `debug/satellites-now.html`. It is not served by the FastAPI
app.

To run it locally:

```bash
make run-debug-ui
```

This runs:

```bash
python -m http.server 3000 --directory debug
```

Open:

```text
http://localhost:3000/satellites-now.html
```

When opened locally, the debug page calls:

```text
http://127.0.0.1:8000
```

When deployed, it calls:

```text
https://satellite-radar.fly.dev
```

## Testing And Formatting

Run the full test suite:

```bash
make test
```

Run lint and formatting checks:

```bash
make lint
```

Format and auto-fix lint issues:

```bash
make format
```

CI also runs:

```bash
poetry run pre-commit run --all-files
poetry run pytest --cov --cov-report=term-missing --cov-report=xml
```

## Docker

The root `Dockerfile` builds the FastAPI API image.

There are two Docker workflows:

- `docker compose` runs the API with a local MongoDB container.
- `docker build` / `docker run --env-file .env` runs only the API container against the configured
  MongoDB credentials in `.env`.

### Docker Compose With Local MongoDB

Start the API and local MongoDB:

```bash
make start
```

This starts:

- FastAPI app: `http://127.0.0.1:8000`
- MongoDB: `127.0.0.1:27017`

Docker Compose sets the app connection string to:

```text
mongodb://satellites-local:satellites-local-password@mongo:27017/satellites_db?authSource=admin
```

These are local-only Docker Compose credentials. They are not used by Atlas or Fly.

The local MongoDB starts empty. Populate the local `satellite_catalog` collection from CelesTrak:

```bash
make update-catalog-local
```

Then test the radar endpoint:

```text
http://127.0.0.1:8000/satellite_radar/get_visible_satellites/35.3112/139.5341
```

Stop the containers:

```bash
make down
```

### Docker Image With `.env`

Build the API image:

```bash
docker build -t satellite-radar .
```

Run the API image with local environment variables:

```bash
docker run --env-file .env -p 8000:8000 satellite-radar
```

Then open:

```text
http://127.0.0.1:8000/docs
```

The debug UI has a separate Dockerfile in `debug/Dockerfile`. It copies `satellites-now.html`
into the [Nginx Docker image](https://hub.docker.com/_/nginx#what-is-nginx) and is used for the deployed
debug UI app.

## Deployment

Production deployment is handled by the manual GitHub Actions workflow:

```text
.github/workflows/deploy.yml
```

The workflow requires the GitHub secret:

```text
FLY_API_TOKEN
```

It deploys three things:

1. API app: `satellite-radar`
   ```bash
   flyctl deploy --remote-only -a satellite-radar -c fly.api.toml
   ```

2. Debug UI app: `satellites-debug-ui`
   ```bash
   flyctl deploy --remote-only -a satellites-debug-ui -c debug/fly.toml debug
   ```

3. Scheduled catalog updater machine: `satellite-catalog-updater`
   ```bash
   flyctl machine run . -a satellite-catalog-updater --schedule daily --restart no -- python -m app.satellite_catalog.updater
   ```

Fly builds Docker images from this repository:

- API and updater use the root `Dockerfile`
- Debug UI uses `debug/Dockerfile`

Manual deployment can also be run with:

```bash
make deploy-api
make deploy-debug-ui
```

These run:

```bash
flyctl deploy --remote-only -a satellite-radar -c fly.api.toml
flyctl deploy --remote-only -a satellites-debug-ui -c debug/fly.toml debug
```

To recreate the scheduled updater machine manually:

```bash
make deploy-scheduled-updater
```

## Troubleshooting

If the radar endpoint returns an empty list, the catalog may be empty, MongoDB may contain no usable
TLE documents, or no satellites may be visible for the requested location and time.

If the debug UI works locally but not in production, make sure the `satellites-debug-ui` app was
deployed. Deploying only the API does not update the static debug HTML.

If MongoDB access fails when running with Poetry or `docker run --env-file .env`, verify `.env`
contains valid `MONGO_USERNAME` and `MONGO_PASSWORD`.

If Docker Compose returns an empty radar response, run `make update-catalog-local` to populate the
local MongoDB catalog.
