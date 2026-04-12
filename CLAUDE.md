# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A learning project exploring FastStream, NATS messaging, observability, and Kubernetes deployment. It implements a producer/consumer pipeline for sensor telemetry data.

## Environment

The project uses a Dev Container (Docker Compose). All infrastructure services start automatically with the container:

| Service  | Docker DNS (from container)  | Host (forwarded port)   | Purpose                        |
|----------|------------------------------|-------------------------|--------------------------------|
| NATS     | `nats://nats:4222`           | `nats://localhost:4222` | Message broker                 |
| NUI      | `http://nui:8080`            | http://localhost:8080   | NATS web UI                    |
| NATS Mon | `http://nats:8222`           | http://localhost:8222   | NATS HTTP monitoring           |
| Postgres | `postgres:5432`              | `localhost:5432`        | Database (`hello_faststream`)  |
| pgAdmin  | `http://pgadmin:80`          | http://localhost:5050   | Postgres web UI                |
| Grafana  | `http://lgtm:3000`           | http://localhost:3000   | Dashboards (LGTM Stack)        |

Python version is managed via `.python-version` (3.14). Dependencies are managed with `uv`.

## Common Commands

```bash
# Install / sync dependencies
uv sync

# Copy and configure environment variables
cp .env.example .env

# Run the consumer worker (subscribes to sensors.raw, publishes to sensors.processed)
uv run --env-file .env faststream run hello_faststream.consumer_worker:app

# Run the producer worker (generates fake telemetry, publishes to sensors.raw)
uv run --env-file .env faststream run hello_faststream.producer_worker:app
```

Environment variables are loaded from `.env` (see `.env.example`). Both workers require `NATS_URL`.

## Architecture

The app is split into two independent FastStream workers that communicate over NATS subjects:

```
producer_worker  →  [sensors.raw]  →  consumer_worker  →  [sensors.processed]
```

- **`producer_worker.py`** — Generates `RawSensorData` (timestamp + random Decimal reading) every 2 seconds and publishes to `sensors.raw`.
- **`consumer_worker.py`** — Subscribes to `sensors.raw`, applies a 2x adjustment, and republishes as `ProcessedSensorData` to `sensors.processed`.
- **`schema.py`** — Defines `RawSensorData` and `ProcessedSensorData` as `msgspec.Struct` types. msgspec is used (instead of Pydantic) for low-latency serialization/deserialization at the NATS boundary.

Each worker creates its own `NatsBroker` and `FastStream` app instance. Lifecycle hooks (`on_startup`, `on_shutdown`, `after_startup`) handle initialization and cleanup logic.

## Planned Stack (in progress)

The README describes future additions not yet implemented: Postgres integration (asyncpg is already a dependency), health checks (socketify), observability (Loki, Prometheus, Tempo already running via LGTM), and Kubernetes manifests.
