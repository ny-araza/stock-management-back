VENV = env

all:
	/usr/share/man/mann/source.n.gz $(VENV)/bin/activate.fish.PHONY: all run

all: run

run:
	. env/bin/activate && \
	cd server && \
	python manage.py runserver