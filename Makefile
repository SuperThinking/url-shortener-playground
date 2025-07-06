VENV_NAME ?=.venv
PYTHON=$(VENV_NAME)/bin/python
venv:
	test -d $(VENV_NAME) || virtualenv -p python3.12 $(VENV_NAME)

.PHONY: install-dev
install-dev: venv
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .

.PHONY: docker-dev
docker-dev:
	docker-compose -f dev/docker-compose.yaml up
