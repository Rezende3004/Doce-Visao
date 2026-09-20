.PHONY: install dev lint test coverage migrate run-backend run-frontend docker-up docker-down seed

install:
	pip install -e ".[dev]"

dev: install
	alembic upgrade head

lint:
	ruff check backend/ frontend/
	ruff format --check backend/ frontend/

format:
	ruff check --fix backend/ frontend/
	ruff format backend/ frontend/

test:
	pytest backend/tests -v

coverage:
	pytest backend/tests --cov=backend/app --cov-report=term-missing

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(msg)"

run-backend:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	streamlit run frontend/app.py --server.port 8501

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

seed:
	python scripts/generate_sample_data.py
