report:
	uv run modwire -d .modwire architecture health src/modwire python

install-dev:
	uv tool uninstall modwire-cli || true
	uv tool install --editable ../modwire-cli
