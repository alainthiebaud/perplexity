all: facture.pdf

facture.pdf: facture_template.tex logo.png
	pdflatex -interaction=nonstopmode -halt-on-error facture_template.tex

clean:
	rm -f *.aux *.log *.out *.toc *.pdf
