.PHONY: install build clean run

# Variables
APP_NAME=ghost
VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
PYINSTALLER=$(VENV)/bin/pyinstaller

# Default target
all: install build

# Create virtual environment and install dependencies
install:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	$(PIP) install pyinstaller

# Build the executable
build:
	$(PYINSTALLER) \
		--name $(APP_NAME) \
		--onefile \
		--add-data "src/*:src" \
		--hidden-import=openai \
		--hidden-import=typer \
		--hidden-import=rich \
		--hidden-import=dotenv \
		src/main.py

# Clean build artifacts
clean:
	rm -rf build dist
	rm -f $(APP_NAME).spec
	rm -rf __pycache__

# Run the application in development mode
run:
	$(PYTHON) src/main.py

# Create a distribution package
dist: clean build
	mkdir -p dist/$(APP_NAME)
	cp dist/$(APP_NAME) dist/$(APP_NAME)/
	cp README.md dist/$(APP_NAME)/
	cp .env.example dist/$(APP_NAME)/
	cd dist && tar -czf $(APP_NAME).tar.gz $(APP_NAME)
	rm -rf dist/$(APP_NAME) 