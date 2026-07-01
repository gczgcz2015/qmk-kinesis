.PHONY: build validate wiring-svg

build:
	./scripts/build.sh

validate:
	python3 scripts/validate_layout.py

wiring-svg:
	python3 scripts/generate_wiring_svg.py
