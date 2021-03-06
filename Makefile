init::
	python -m pip install --upgrade pip
	python -m pip install pip-tools pre_commit black isort
	python -m pre_commit install
	python -m piptools sync requirements/requirements.txt


issue-db:
	python -m issues.cli

black:
	black .

black-check:
	black --check .

flake8:
	flake8 .

isort:
	isort --profile black .

lint: black-check flake8

reqs:
	python -m piptools compile requirements/requirements.in
	python -m piptools compile requirements/dev-requirements.in

sync:
	 python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt

run:
	datasette --inspect-file data/dataset-issue.json data/dataset-issue.sqlite3
