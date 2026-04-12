# hello-faststream

Simple Producer/Consumer application created to familiarize with faststream, observability stack and deployment with kubernetes.

We will be using the following stack:

- Faststream
- Msgspec for serializtion/deserialization
- NATS as message broker
- Postgres as database
- Socketify for healthchecks
- Loki for logs
- Prometheus for metrics
- Tempo for stack traces
- Grafana for dashboards
- Kubernets configuration files

## Running Locally

The project uses a Dev Container — open it in VS Code to have NATS, Postgres, and the observability stack start automatically.

```bash
# Install dependencies
uv sync

# Configure environment variables
cp .env.example .env

# Run the consumer worker (terminal 1)
uv run --env-file .env faststream run hello_faststream.producer_worker:app

# Run the producer worker (terminal 2)
uv run --env-file .env faststream run hello_faststream.consumer_worker:app
```
