# Proposta de TCC — build

Documento em LaTeX da proposta, no modelo da UFPR.

## Origem e adaptações

Baseado no modelo do Prof. Carlos Maziero (PPGInf/UFPR),
<https://git.c3sl.ufpr.br/maziero/tese>. Adaptações feitas em `main.tex`:

- estrutura de **projeto** conforme o cap. 6 do *Manual de Normalização de
  Documentos Científicos* (UFPR/SiBi, 2024): folha de rosto → sumário →
  introdução (tema, problema, hipóteses, objetivos, justificativa) →
  desenvolvimento (referencial teórico, metodologia, recursos, cronograma) →
  referências;
- `\field{Engenharia Elétrica}` e descrição de TCC no lugar dos padrões do
  PPGInf;
- ambientes `alineas` e `subalineas` conforme itens 3.4.3 e 3.4.4 do Manual
  (letra minúscula + parêntese, recuo de 1,5 cm);
- ficha catalográfica e folha de aprovação omitidas — não se aplicam a projeto.

O modo `defesa` da classe já entrega espaçamento 1,5 e páginas pré-textuais
contadas mas não numeradas, como o Manual exige.

## Compilar

Duas saídas, a partir do mesmo fonte:

```bash
make            # ENTREGA  -> Plano_de_Trabalho_TCC_Andre_Victor_Xavier_Pires_GRR20212735.pdf
make pessoal    # PESSOAL  -> main_com_apendices.pdf (com os apêndices A e B)
make tudo       # as duas
make clean      # remove intermediários
```

A diferença é só a macro `\comapendices`, definida pela linha de comando no alvo
`pessoal`. Ela liga os dois `\include` de apêndice no fim de `main.tex` e, via
`\seapendice{...}`, reativa os trechos de texto que citam os apêndices — de modo
que a versão de entrega não fica com referências penduradas.

> **Nota para quem clonou o repositório:** os apêndices A e B são material de
> consulta pessoal do autor e não integram o repositório público
> (`a1-engenharia/` e `a2-integridade/` estão no `.gitignore`). O `main.tex`
> testa a existência dos arquivos com `\IfFileExists`, de modo que `make
> pessoal` num clone produz exatamente a versão de entrega, sem erro.

Sem `make`:

```bash
# entrega (sem apêndices)
pdflatex main && bibtex main && pdflatex main && pdflatex main

# pessoal (com apêndices)
pdflatex -jobname=main_ap "\def\comapendices{}\input{main}" && bibtex main_ap && \
pdflatex -jobname=main_ap "\def\comapendices{}\input{main}" && \
pdflatex -jobname=main_ap "\def\comapendices{}\input{main}"
```

## Dependências TeX

Compilado com TeX Live 2026 (TinyTeX). Pacotes além do básico:

```
collection-latexrecommended collection-fontsrecommended collection-langportuguese
newtx xstring multirow booktabs pdfpages wallpaper moreverb currfile
titlesec titletoc tocbibind enumitem setspace fancyhdr microtype algorithms
```

Instalar com `tlmgr install <pacote>`.

## Figura

`3-metodo/figuras/ancoras_fisicas.pdf` é **gerada**, não versionada à mão.
Para reproduzi-la e aos números que ela sustenta:

```bash
cd .. && python scripts/verify_physics_anchors.py --n 40 --seed 42
```

## Conformidade com o Anexo I

O documento atende aos itens exigidos pelo **Anexo I** das normas de TCC do
DELT/UFPR. A página `0-iniciais/identificacao.tex`, logo após a folha de rosto,
traz os dados de identificação (estudante, matrícula, ênfase, orientador,
coorientador) e um quadro que mapeia cada um dos dez itens obrigatórios para a
seção correspondente. Ao mexer na numeração de seções, conferir esse quadro.

## Estado

Entrega: 40 páginas · versão pessoal: 48 páginas · 13 referências, todas
verificadas via Crossref em 2026-08-01 · compilação sem erros, sem referências
indefinidas, sem *warnings* do LaTeX (1 *overfull box* de 2,5 pt na lista de
referências).
