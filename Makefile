format:
	black .
	isort .
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive -v .

run:
	fastapi dev main.py
