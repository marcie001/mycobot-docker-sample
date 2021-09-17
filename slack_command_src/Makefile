SHELL := /bin/bash

init-venv:
	python3 -m venv venv

save-dep:
	source venv/bin/activate && pip freeze > requirements.txt

install-dep:
	source venv/bin/activate && pip install -r requirements.txt

run:
	source venv/bin/activate && python main.py
