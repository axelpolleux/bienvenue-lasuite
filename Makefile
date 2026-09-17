.DEFAULT_GOAL := help

# ANSI color codes
BLUE   := \033[36m
GREEN  := \033[32m
YELLOW := \033[33m
RESET  := \033[0m
BOLD   := \033[1m

.PHONY: help up start down stop restart ps status logs logs-backend logs-frontend logs-keycloak build migrate seed reset test-backend test-frontend test clean

help:
	@echo "$(BOLD)Bienvenue La Suite - Docker Management Commands$(RESET)"
	@echo ""
	@echo "$(YELLOW)Usage:$(RESET)"
	@echo "  make $(GREEN)<target>$(RESET)"
	@echo ""
	@echo "$(YELLOW)Available Targets:$(RESET)"
	@echo "  $(GREEN)up$(RESET) / $(GREEN)start$(RESET)       Build and start all containers in background"
	@echo "  $(GREEN)down$(RESET) / $(GREEN)stop$(RESET)      Stop and remove all containers"
	@echo "  $(GREEN)restart$(RESET)          Restart all containers"
	@echo "  $(GREEN)ps$(RESET) / $(GREEN)status$(RESET)       Show container status"
	@echo "  $(GREEN)build$(RESET)            Build or rebuild all services"
	@echo "  $(GREEN)logs$(RESET)             Follow logs for all containers"
	@echo "  $(GREEN)logs-backend$(RESET)     Follow backend container logs"
	@echo "  $(GREEN)logs-frontend$(RESET)    Follow frontend container logs"
	@echo "  $(GREEN)logs-keycloak$(RESET)    Follow Keycloak container logs"
	@echo "  $(GREEN)migrate$(RESET)          Run Django database migrations"
	@echo "  $(GREEN)seed$(RESET)             Seed demo database data"
	@echo "  $(GREEN)reset$(RESET)            Reset onboarding tasks and signature to 0% (e.g. make reset or make reset AGENT=alex.martin@gouv.fr)"
	@echo "  $(GREEN)test-backend$(RESET)     Run Django backend tests"
	@echo "  $(GREEN)test-frontend$(RESET)    Run frontend production build test"
	@echo "  $(GREEN)test$(RESET)             Run both backend and frontend tests"
	@echo "  $(GREEN)clean$(RESET)            Stop containers and remove volumes"
	@echo ""

up:
	docker compose up -d --build

start: up

down:
	docker compose down

stop: down

restart:
	docker compose restart

ps:
	docker compose ps

status: ps

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

logs-keycloak:
	docker compose logs -f keycloak

build:
	docker compose build

migrate:
	docker compose exec backend python manage.py migrate

seed:
	docker compose exec backend python manage.py seed_demo_data

reset:
	docker compose exec backend python manage.py reset_onboarding $(if $(AGENT),--agent $(AGENT),)


test-backend:
	docker compose exec backend python manage.py test

test-frontend:
	docker compose exec frontend npm run build

test: test-backend test-frontend

clean:
	docker compose down -v
