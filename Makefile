.PHONY: dev dev-backend dev-frontend help

dev:
	@./scripts/dev-all.sh

dev-backend:
	@cd backend && ./scripts/dev.sh

dev-frontend:
	@cd frontend && ./scripts/dev.sh

help:
	@echo "Usage:"
	@echo "  make dev            Start backend (:8000) and frontend (:5173)"
	@echo "  make dev-backend    Start backend only"
	@echo "  make dev-frontend   Start frontend only"
