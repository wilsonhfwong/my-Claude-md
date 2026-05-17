.PHONY: install dev worker eval agent test lint format

install:
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload --port 8000

worker:
	arq app.workers.WorkerSettings

eval:
	python -m eval.run

agent:
	python -m agent.loop

test:
	pytest -q

lint:
	ruff check . && ruff format --check .

format:
	ruff format . && ruff check --fix .
