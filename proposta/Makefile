# Makefile básico, sugestões são bem-vindas...
# Carlos Maziero @UFPR, out 2017
# Adaptado: duas saídas — entrega (sem apêndices) e pessoal (com apêndices).

MAIN=main
ENTREGA=Plano_de_Trabalho_TCC_Andre_Victor_Xavier_Pires_GRR20212735.pdf
PESSOAL=main_com_apendices.pdf

# padrão: versão de ENTREGA para a UFPR, sem apêndices
main: $(MAIN).tex
	@pdflatex $(MAIN)
	@bibtex   $(MAIN)
	@pdflatex $(MAIN)
	@pdflatex $(MAIN)
	@mv $(MAIN).pdf $(ENTREGA)
	@echo "==> $(ENTREGA) (versão de entrega, sem apêndices)"

# versão PESSOAL: define \comapendices, que liga os apêndices A e B
pessoal:
	@pdflatex -jobname=main_ap "\def\comapendices{}\input{$(MAIN)}"
	@bibtex   main_ap
	@pdflatex -jobname=main_ap "\def\comapendices{}\input{$(MAIN)}"
	@pdflatex -jobname=main_ap "\def\comapendices{}\input{$(MAIN)}"
	@mv main_ap.pdf $(PESSOAL)
	@echo "==> $(PESSOAL) (versão pessoal, com apêndices)"

# gera as duas
tudo: main pessoal

bib:
	@bibtex $(MAIN)

# dessa forma somente os arquivos removidos são listados na saída
clean:
	@find . -xdev -iname \*~    -print -delete
	@find . -xdev -iname \*.aux -print -delete
	-rm -f texput.log
	-rm -f $(MAIN).log $(MAIN).lot $(MAIN).lof
	-rm -f $(MAIN).toc $(MAIN).bbl $(MAIN).blg
	-rm -f $(MAIN).acr $(MAIN).smb
	-rm -f main_ap.log main_ap.lot main_ap.lof
	-rm -f main_ap.toc main_ap.bbl main_ap.blg main_ap.out

purge: clean
	@rm -f $(ENTREGA) $(PESSOAL) $(MAIN).pdf
