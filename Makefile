.PHONY: test demo eval search

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

demo:
	PYTHONPATH=src python -m seed.cli demo

eval:
	PYTHONPATH=src python -m seed.cli eval-demo

search:
	PYTHONPATH=src python -m seed.cli search-demo
