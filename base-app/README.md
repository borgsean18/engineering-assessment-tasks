# Base Application: Project Controls Hub

A web application used by Turner & Townsend teams to monitor **cost, schedule,
risk, and benchmark** performance across a portfolio of construction projects. This is
the shared codebase every candidate receives. It ships pre-built and working; candidates
extend it with one scoped feature (see [`../briefs/`](../briefs/README.md)).

## Why this product

It mirrors Turner & Townsend's real domain (project controls + benchmarking), is rich enough
to support frontend, backend, and full-stack tasks, and is small enough to read in under an
hour. Every task reuses the same entities, API, and seed data so submissions are comparable.

## Pre-built (existing) features

These already work in the shipped repo. Candidate tasks build _on top of_ or _interact with_ them.

1. **Project portfolio** - list of projects with region, sector, status, and headline KPIs.
2. **Project detail** - cost baseline vs actuals-to-date, schedule milestones with RAG status.
3. **Cost trend** - monthly cost time-series (baseline, forecast, actual) rendered with Highcharts.
4. **Schedule milestones** - milestone list with planned/forecast/actual dates and RAG.
5. **Benchmark panel** - compares a project's unit metrics against peer-project medians.

## Domain model

See [`domain-model.md`](domain-model.md) for entities, relationships, and the ERD.

## Contracts (source of truth)

| Artifact           | File                                                   | Used by                                                 |
| ------------------ | ------------------------------------------------------ | ------------------------------------------------------- |
| API contract       | [`contracts/openapi.json`](contracts/openapi.json)     | Exported from FastAPI; drives generated Angular client. |
| Database schema    | [`contracts/schema.sql`](contracts/schema.sql)         | PostgreSQL DDL + reference for migrations.              |
| Seed data contract | [`contracts/seed-data.json`](contracts/seed-data.json) | Deterministic seed for reproducible task output.        |

These three artifacts are the **seed data + domain contract** referenced by every brief. They
make take-home outputs deterministic: given the same seed, every candidate's calculations and
charts should produce the same numbers, which makes review fast and objective.

## Repository layout (target)

See [`architecture.md`](architecture.md) for the full Nx workspace and FastAPI service layout,
local-run instructions, and the OpenAPI-first client generation flow.

## Prerequisites

Install these before cloning or running the app. Volta pins the JavaScript toolchain so every
developer and candidate uses the same Node and Yarn versions.

| Tool                                                      | Version | Notes                                                                                   |
| --------------------------------------------------------- | ------- | --------------------------------------------------------------------------------------- |
| [Volta](https://volta.sh)                                 | latest  | Manages Node.js and Yarn per project (`volta` field in `package.json`).                 |
| Node.js                                                   | 22.22.3 | Pinned by Volta; installed automatically on first `yarn` / `node` command in this repo. |
| Yarn                                                      | 4.5.0   | Pinned by Volta; matches `packageManager` in `package.json`.                            |
| [Docker](https://www.docker.com/products/docker-desktop/) | —       | Docker Desktop or Docker Engine + Compose v2 for API and Postgres.                      |
| [uv](https://docs.astral.sh/uv/)                          | latest  | Python package manager for the API (only if running outside Docker).                    |
| Python                                                    | 3.11+   | Installed automatically by uv when needed; only required outside Docker.                |

**Install Volta** (macOS/Linux):

```bash
curl https://get.volta.sh | bash
```

Restart your terminal, `cd` into this directory, and Volta will use the pinned Node and Yarn
versions. No separate `nvm` or global Yarn install is required.

## Running locally (summary)

```bash
# 1. Start API + Postgres (seeded deterministically) on http://localhost:8000
#    Source is bind-mounted; uvicorn --reload restarts on API code changes.
docker compose -f infra/docker-compose.yml up --build

# 2. Install JS deps and start the Angular app on http://localhost:4200
yarn install
yarn nx serve hub

# Optional: export OpenAPI from FastAPI and refresh typed client types
yarn api-client:generate
```

To run the API without Docker (SQLite):

```bash
cd apps/api
uv sync
uv run uvicorn app.main:app --reload   # http://localhost:8000, auto-seeds on startup
uv run pytest                          # backend test suite
uv run ruff check . && uv run ruff format --check . && uv run mypy app tests  # lint + typecheck
```

Or from the repo root (after `uv sync` in `apps/api`): `yarn api:lint`.

Full prerequisites, ports, and troubleshooting live in [`architecture.md`](architecture.md).

### Troubleshooting

| Symptom                                    | Likely cause                 | Fix                                                                       |
| ------------------------------------------ | ---------------------------- | ------------------------------------------------------------------------- |
| `ERR_CONNECTION_REFUSED` on `:8000`        | API not running              | Start Docker Compose **or** the SQLite `uvicorn` path above               |
| `could not translate host name "postgres"` | Compose stack incomplete     | `docker compose -f infra/docker-compose.yml down` then `up --build` again |
| Port already allocated on `5432`           | Another Postgres on the host | Compose publishes Postgres on host port **5433**                          |

Run API and frontend in **separate terminals** (don't chain commands on one line).

## Definition of "ready to ship to candidates"

- `docker compose -f infra/docker-compose.yml up` boots API + Postgres and seeds deterministically.
- `yarn nx serve hub` renders portfolio, project detail, cost trend, milestones, benchmark panel.
- Starter tests pass: `yarn nx test hub` (Vitest), `yarn nx e2e hub-e2e` (Cypress), `uv run pytest` (API).
- API lint and typecheck pass: `yarn api:lint` (Ruff + mypy).
- README setup works on a clean machine (Volta + Docker) in under 15 minutes.

## What ships in this repo

| Part                    | Where                                                              | Status                                                                                 |
| ----------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| FastAPI service + tests | [`apps/api/`](apps/api)                                            | Runnable; 13 pytest tests pass; serves all contract endpoints.                         |
| Angular 21 app          | [`apps/hub/`](apps/hub)                                            | Builds; portfolio + project detail with Signal Stores, Material, Tailwind, Highcharts. |
| Cypress e2e             | [`apps/hub-e2e/`](apps/hub-e2e)                                    | Starter portfolio-to-detail spec.                                                      |
| Shared libs             | [`libs/domain`](libs/domain), [`libs/api-client`](libs/api-client) | Domain models + typed API client.                                                      |
| Infra                   | [`infra/`](infra)                                                  | Docker Compose (api/postgres) + reference k8s manifests.                               |
