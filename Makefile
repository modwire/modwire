.PHONY: killer-proof locust test

killer-proof:
	uv run python -m pytest

locust:
	uv run --with locust python scripts/run_locust_chaos.py --force --users 50 --spawn-rate 10 --run-time 45s

test: killer-proof
