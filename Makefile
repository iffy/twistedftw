
article_index.json: articles/* articles/*/*
	python bin/mkindex.py > article_index.json