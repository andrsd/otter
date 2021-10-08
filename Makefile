CONDABASE=$(shell conda info --base)
DIST=`pwd`/dist/
FRAMEWORKS=$(DIST)/Otter.app/Contents/Frameworks

all:
	@echo ""

create-venv:
	@python -m venv venv

init:
	@pip install -e .
	@pip install -r requirements/test.txt

syntax-check check-syntax:
	@flake8 otter tests setup.py

test:
	@pytest .

coverage:
	@coverage run --source=otter -m pytest
	@coverage html

icon.icns:
	@mkdir -p icon.iconset
	@sips -z 512 512 otter/assets/icons/otter.png --out icon.iconset/icon_512x512.png
	@iconutil -c icns icon.iconset
	@rm -rf icon.iconset

app: icon.icns
	@python setup.py py2app
	@cp $(CONDABASE)/lib/libffi.7.dylib $(FRAMEWORKS)
