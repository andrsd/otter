CONDABASE=$(shell conda info --base)
DIST=`pwd`/dist/
FRAMEWORKS=$(DIST)/Otter.app/Contents/Frameworks
SRC=otter

all:
	@echo ""

create-venv:
	@python -m venv venv

init:
	@pip install -e .
	@pip install -r requirements/test.txt

syntax-check check-syntax:
	@flake8 $(SRC) tests setup.py

test:
	@PYTEST_QT_API=pyqt5 pytest .

coverage:
	@PYTEST_QT_API=pyqt5 coverage run --source=$(SRC) -m pytest -v -s
	@coverage html

icon.icns:
	@mkdir -p icon.iconset
	@sips -z 512 512 $(SRC)/assets/icons/otter.png --out icon.iconset/icon_512x512.png
	@iconutil -c icns icon.iconset
	@rm -rf icon.iconset

app: icon.icns
	@python setup.py py2app
	@cp $(CONDABASE)/lib/libffi.7.dylib $(FRAMEWORKS)
