VENV = .env
PYTHON = $(CURDIR)/$(VENV)/bin/python
PIP = $(CURDIR)/$(VENV)/bin/pip

.PHONY: all install run clean

all: run

$(VENV):
	python3 -m venv $(VENV)

install: $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

run: $(VENV)
	cd server && $(PYTHON) manage.py runserver

clean:
	rm -rf $(VENV)