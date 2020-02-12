# Deploy as binary app


## Setup environment

```
$ virtualenv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```


## Mac OS X: Build icns

```
$ mkdir icon.iconset
$ sips -z 512 512 otter.png --out icon.iconset/icon_512x512.png
$ iconutil -c icns icon.iconset
$ rm -rf icon.iconset
```

## Build the bundle

```
$ python setup.py py2app
```

## Fix the install manually

```
$ cp /path/to/libffi.6.dylib /path/to/Otter.app/Contents/Frameworks/
```

Note: libffi.6.dylib can sit either on the system or in miniconda dir


## NOTES

- if package dependencies change, generate a new `requirements.txt` by running:

    $ pip freeze > requirements.txt

## Resources

- [0] https://py2app.readthedocs.io/en/latest/
- [1] https://www.metachris.com/2015/11/create-standalone-mac-os-x-applications-with-python-and-py2app/
