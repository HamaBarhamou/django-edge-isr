.PHONY: fmt lint test all
fmt:
\tblack .
\truff check . --fix

lint:
\truff check .
\tblack --check .

test:
\tpython -m pytest -q

all: fmt lint test
