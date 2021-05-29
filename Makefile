.ONESHELL:
SHELL := /bin/bash
SRC = $(wildcard ./*.ipynb)

all: docs

nicHelper: $(SRC)
	nbdev_build_lib
	touch nicHelper

sync:
	nbdev_update_lib

docs_serve: docs
	cd docs && bundle exec jekyll serve

docs: $(SRC)
	nbdev_build_docs
	touch docs

test:
	nbdev_test_nbs

pypi: dist
	twine upload --repository pypi dist/*

dist: build
	nbdev_bump_version
	python setup.py sdist bdist_wheel

clean:
	rm -rf dist build build.bak
    
build: clean
	nbdev_build_lib
	nbdev_build_docs --mk_readme true
	nbdev_clean_nbs
