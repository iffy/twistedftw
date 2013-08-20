
article_index.json: articles/* articles/*/* bin/mkindex.py
	python bin/mkindex.py > article_index.json
