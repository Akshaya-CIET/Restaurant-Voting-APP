# Build the Docker image
build:
	@echo -e "Creating Docker images:"
	docker-compose build

# Run the Docker containers
runserver:
	@echo -e "Running Docker containers:"
	docker-compose up

# Run the Docker containers in detached mode
runserver-detached:
	docker-compose up -d

# Stop the Docker containers
down:
	docker-compose down

# Restart the Docker containers
restart:
	docker-compose restart

# Access the Django shell
shell:
	docker-compose run web python manage.py shell

# Apply database migrations
makemigrations:
	docker-compose run web python manage.py makemigrations

# Apply database migrations
migrate:
	docker-compose run web python manage.py migrate

setup: build migrate
	@echo "SETUP SUCCEEDED"
	@echo -e "Run 'make runserver' to start the Django development server and the node server."

# Collect static files
collectstatic:
	docker-compose run web python manage.py collectstatic --noinput

# Run tests
test:
	docker-compose run web python manage.py test

# Generate code coverage report
coverage:
	docker-compose run web coverage run --source='.' manage.py test
	docker-compose run web coverage report

# Clean up unused Docker resources
clean:
	docker system prune

createsuperuser:
	@echo -e "Creating super user"
	@docker-compose run --rm web ./manage.py createsuperuser

fix-black:
	@echo -e "Running black to fix linting"
	@docker-compose run --rm web black .

fix-imports:
	@echo -e "Running black to fix imports"
	@docker-compose run --rm web isort .

fix-linting: fix-black fix-imports
	@echo -e "Fixed linting"

.PHONY: build runserver runserver-detached down restart shell migrate collectstatic test coverage clean fix-black fix-imports fix-linting createsuperuser setup
