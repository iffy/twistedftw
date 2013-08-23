
.PHONY: all test

all: test article_index.json


article_index.json: articles/* articles/*/* bin/mkindex.py
	python bin/mkindex.py > article_index.json

test: _tests
	python bin/run_files.py _tests

_tests: articles/* articles/*/* bin/extract-code-as-tests.py
	-rm -r _tests
	python bin/extract-code-as-tests.py articles _tests