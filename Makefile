.PHONY: build validate

build:
	./scripts/build.sh

validate:
	python3 scripts/validate_layout.py

