# Copyright (c) The TwistedFTW Team
# See LICENSE for details.

.PHONY: all test

all: test article_index.json

clean:
	find . -name "*.pyc" -exec rm {} \;
	-rm -rf _trial_temp
	-rm -rf _tests

article_index.json: articles/* articles/*/* bin/mkindex.py
	python bin/mkindex.py > article_index.json

test: _tests
	python bin/run_files.py _tests

_tests: articles/* articles/*/* bin/extract-code-as-tests.py
	-rm -r _tests
	python bin/extract-code-as-tests.py articles _tests