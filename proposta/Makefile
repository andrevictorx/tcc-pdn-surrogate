# Makefile — dois documentos a partir da mesma classe e da mesma bibliografia.
# Base: Carlos Maziero @UFPR, out 2017.
#
#   make            PLANO DE TRABALHO — a entrega à comissão de TCC.
#                   Segue estrita e exclusivamente a lista do Anexo I. ~14 pág.
#                   fonte: plano.tex + plano/
#
#   make completo   DOCUMENTO COMPLETO — leitura pessoal e base do texto de TCC.
#                   Referencial teórico, hipóteses, justificativa e apêndices.
#                   fonte: main.tex + 0-iniciais/ 1-intro/ ... a2-integridade/
#
#   make tudo       os dois
#   make clean      remove intermediários

PLANO=plano
MAIN=main
ENTREGA=Plano_de_Trabalho_TCC_Andre_Victor_Xavier_Pires_GRR20212735.pdf
COMPLETO=Documento_completo_com_apendices.pdf

# Sem .PHONY, o alvo "plano" seria confundido com o diretório plano/ e o make
# reportaria "up to date" sem compilar nada.
.PHONY: plano completo tudo bib clean purge

# ---- padrão: o plano de trabalho (entrega) -----------------------------------
plano:
	@pdflatex $(PLANO)
	@bibtex   $(PLANO)
	@pdflatex $(PLANO)
	@pdflatex $(PLANO)
	@mv $(PLANO).pdf $(ENTREGA)
	@echo "==> $(ENTREGA)  (PLANO DE TRABALHO — entrega à comissão)"

# ---- documento completo, com apêndices (leitura pessoal) ---------------------
# \comapendices liga os apêndices A e B; ver nota no preâmbulo de main.tex.
completo:
	@pdflatex -jobname=main_ap "\def\comapendices{}\input{$(MAIN)}"
	@bibtex   main_ap
	@pdflatex -jobname=main_ap "\def\comapendices{}\input{$(MAIN)}"
	@pdflatex -jobname=main_ap "\def\comapendices{}\input{$(MAIN)}"
	@mv main_ap.pdf $(COMPLETO)
	@echo "==> $(COMPLETO)  (documento completo — leitura pessoal)"

tudo: plano completo

bib:
	@bibtex $(PLANO)

clean:
	@find . -xdev -iname \*~    -print -delete
	@find . -xdev -iname \*.aux -print -delete
	-rm -f texput.log
	-rm -f $(PLANO).log $(PLANO).lot $(PLANO).lof $(PLANO).out
	-rm -f $(PLANO).toc $(PLANO).bbl $(PLANO).blg
	-rm -f $(MAIN).log $(MAIN).lot $(MAIN).lof $(MAIN).out
	-rm -f $(MAIN).toc $(MAIN).bbl $(MAIN).blg
	-rm -f $(MAIN).acr $(MAIN).smb
	-rm -f main_ap.log main_ap.lot main_ap.lof main_ap.out
	-rm -f main_ap.toc main_ap.bbl main_ap.blg

purge: clean
	@rm -f $(ENTREGA) $(COMPLETO) $(PLANO).pdf $(MAIN).pdf
	@rm -f main_com_apendices.pdf
