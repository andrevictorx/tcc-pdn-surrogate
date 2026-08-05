# Documentos de TCC — build

Dois documentos em LaTeX, no modelo da UFPR, compartilhando classe, pacotes e
bibliografia:

| Documento | Fonte | Saída | Papel |
|---|---|---|---|
| **Plano de trabalho** | `plano.tex` + `plano/` | `Plano_de_Trabalho_TCC_Andre_Victor_Xavier_Pires_GRR20212735.pdf` (15 pág.) | **entrega à comissão de TCC** — segue estrita e exclusivamente a lista de itens do Anexo I |
| **Documento completo** | `main.tex` + `0-iniciais/` … | `Documento_completo_com_apendices.pdf` (49 pág.) | leitura pessoal e base do texto de TCC — referencial teórico, hipóteses, justificativa, apêndices |

No plano, o capítulo se chama *Descrição do projeto* (expressão do próprio Anexo)
e cada seção é um dos itens 2 a 9, na ordem em que o Anexo os enumera; o item 1
está na folha de rosto e o item 10 em REFERÊNCIAS. **O sumário é o checklist do
Anexo I.**

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
contadas mas não numeradas, como o Manual exige. O que a classe **não** faz e foi
acrescentado nos dois documentos: espaçamento **simples** no interior das tabelas e
na lista de referências, com linha em branco entre entradas, conforme o Manual e a
NBR 6023 — apenas o corpo do texto usa 1,5.

## Compilar

```bash
make            # PLANO DE TRABALHO -> o PDF da entrega
make completo   # DOCUMENTO COMPLETO, com os apêndices A e B
make tudo       # os dois
make clean      # remove intermediários
```

Os apêndices entram pela macro `\comapendices`, definida na linha de comando pelo
alvo `completo`. Ela liga os `\include` de apêndice no fim de `main.tex` e, via
`\seapendice{...}`, reativa os trechos de texto que os citam — de modo que a versão
sem apêndices não fica com referências penduradas.

> **Nota para quem clonou o repositório:** os apêndices A e B são material de
> consulta pessoal do autor e não integram o repositório público
> (`a1-engenharia/` e `a2-integridade/` estão no `.gitignore`). O `main.tex` testa a
> existência dos arquivos com `\IfFileExists`, de modo que `make completo` num clone
> compila normalmente, apenas sem os apêndices.

Sem `make`:

```bash
# plano de trabalho (entrega)
pdflatex plano && bibtex plano && pdflatex plano && pdflatex plano

# documento completo, com apêndices
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

Ambos os documentos declaram os dados de identificação exigidos — estudante,
matrícula, ênfase, orientador e coorientador com dados profissionais — em uma página
logo após a folha de rosto (`plano/identificacao.tex` e
`0-iniciais/identificacao.tex`).

No **plano**, os itens 2 a 9 são as seções, na ordem do Anexo, com os títulos
literais: mexer na ordem das seções quebra essa correspondência. No **documento
completo**, cuja estrutura segue o cap. 6 do Manual de Normalização, a página de
identificação traz um quadro mapeando cada item do Anexo para a seção
correspondente — ao renumerar seções, conferir o quadro.

## Estado

Plano de trabalho: 15 páginas, 13 referências. Documento completo: 49 páginas.
Referências verificadas via Crossref em 2026-08-01, **exceto** as cinco entradas de
norma técnica e livro acrescentadas em 2026-08-04 (CISPR 32, IEC 61000-6-3, IEC
61000-6-4, Paul 2006, Ott 2009), que não têm DOI indexado e cujo ano e edição devem
ser conferidos no catálogo do editor antes da entrega final.

Compilação dos dois sem erros, sem referências indefinidas e sem *warnings* do
LaTeX; um *overfull box* de 2,5 pt na lista de referências do documento completo.
