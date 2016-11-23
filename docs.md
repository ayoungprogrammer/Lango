# Docs

Pip Installs
```
sphinx-autobuild==0.6.0
sphinx-rtd-theme==0.1.9
sphinxcontrib-napoleon==0.5.0
```

Generate docs
```
sphinx-apidoc -f -e -o docs lango
cd docs
make html
```

## Development

```
python setup.py develop
```