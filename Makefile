report:
	uv run modwire -d .modwire architecture src/modwire python

install-dev:
	uv tool uninstall modwire || true
	uv tool install --editable .
