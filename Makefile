.DEFAULT_GOAL := help

.PHONY: help format lint

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_-]+:.*## / {printf "%-10s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

format: ## Format the codebase with Ruff
	uv run ruff format .

lint: ## Lint the codebase with Ruff
	uv run ruff check .
