all: ocemr.png ocemr.pdf

clean:
	rm ocemr.dot ocemr.png ocemr.pdf
ocemr.dot: ../models.py
	( cd ..; python modelviz.8.py ocemr > doc/ocemr.dot )
ocemr.png: ocemr.dot
	dot ocemr.dot -Tpng -o ocemr.png
ocemr.pdf: ocemr.dot
	dot ocemr.dot -Tpdf -o ocemr.pdf
