# Como editar o TCC e recompilar o PDF

Guia prático para mexer no documento sem depender de ajuda. Tudo acontece dentro
de `proposta/`.

```bash
cd ~/Downloads/TCC/proposta
```

---

## 1. São dois documentos

A pasta contém **dois** documentos que compartilham a mesma classe LaTeX, os
mesmos pacotes e a mesma bibliografia:

| Documento | Fonte | Saída | Para quê |
|---|---|---|---|
| **Plano de trabalho** (15 pág.) | `plano.tex` + `plano/` | `Plano_de_Trabalho_TCC_Andre_Victor_Xavier_Pires_GRR20212735.pdf` | **a entrega à comissão** — segue estritamente a lista do Anexo I |
| **Documento completo** (49 pág.) | `main.tex` + `0-iniciais/` … `a2-integridade/` | `Documento_completo_com_apendices.pdf` | leitura pessoal e base do texto de TCC — tem referencial teórico, hipóteses, justificativa e apêndices |

O `plano.tex` e o `main.tex` quase não têm texto: eles só **montam** o documento.
O conteúdo está em arquivos separados.

### Plano de trabalho — onde fica cada coisa

| Quero mexer em… | Arquivo |
|---|---|
| Título, autor, orientador, **coorientador** | `plano.tex` (bloco "metadados") |
| **Matrícula, ênfase, dados do coorientador** | `plano/identificacao.tex` |
| **Todo o conteúdo** (itens 2 a 9 do Anexo I) | `plano/conteudo.tex` |
| Referências bibliográficas | `referencias.bib` (compartilhado) |

O `plano/conteudo.tex` é um arquivo único, com as oito seções na ordem do Anexo I
e um cabeçalho de comentário no topo mapeando seção → item do Anexo.

### Documento completo — onde fica cada coisa

| Quero mexer em… | Arquivo |
|---|---|
| Título, autor, orientador, coorientador | `main.tex` (bloco "metadados") |
| Matrícula, ênfase, quadro do Anexo I | `0-iniciais/identificacao.tex` |
| Resumo / Abstract | `0-iniciais/resumo.tex`, `0-iniciais/abstract.tex` |
| Listas de siglas e símbolos | `0-iniciais/abreviaturas.tex`, `0-iniciais/simbolos.tex` |
| Cap. 1 — Introdução, objetivos, público alvo, contribuição | `1-intro/texto.tex` |
| Cap. 2 — Referencial teórico | `2-fundam/texto.tex` |
| Cap. 3 — Metodologia | `3-metodo/texto.tex` |
| Cap. 4 — Recursos, cronograma, resultados | `4-recursos/texto.tex` |
| Apêndices A e B | `a1-engenharia/texto.tex`, `a2-integridade/texto.tex` |

Abra qualquer um deles num editor de texto comum (VS Code, gedit, nano). São
arquivos de texto puro.

> ⚠️ **Os dois documentos têm objetivos diferentes.** O plano adotou o objetivo
> novo — predizer a **margem de conformidade em dB** contra a curva-limite de uma
> norma escolhida. O documento completo ainda carrega o objetivo anterior, de
> predizer só a impedância. Ao atualizá-lo, comece pelo `1-intro/texto.tex` e pelo
> `\title{}` do `main.tex`.

---

## 2. Recompilar

```bash
make            # PLANO DE TRABALHO -> o PDF da entrega
make completo   # DOCUMENTO COMPLETO, com apêndices
make tudo       # os dois
```

Se algo ficar estranho (numeração errada, referência aparecendo como `??`),
limpe os arquivos intermediários e refaça:

```bash
make clean && make
```

**Por que quatro passadas?** O LaTeX descobre os números de página e de seção na
primeira passada, grava num arquivo `.aux`, e só na segunda consegue montar
sumário e referências cruzadas corretamente. O `bibtex` no meio é quem monta a
lista de referências. O `make` já faz tudo na ordem certa.

---

## 3. Como os apêndices entram e saem (documento completo)

Os apêndices A e B pertencem só ao documento completo, e ainda assim de forma
condicional. O mecanismo tem três partes:

1. No fim do `main.tex`:

   ```latex
   \ifapendices
     \appendix
     \include{a1-engenharia/texto}
     \include{a2-integridade/texto}
   \fi
   ```

   `make completo` define `\comapendices` na linha de comando, e o `main.tex`
   liga `\ifapendices` se — e só se — os arquivos existirem no disco.

2. Trechos de texto que **citam** os apêndices ficam envolvidos por
   `\seapendice{...}`. Exemplo em `1-intro/texto.tex`:

   ```latex
   ...testado e versionado\seapendice{, segundo as práticas relatadas no
   Apêndice~\ref{ap:engenharia}}, com registro explícito...
   ```

   Sem os apêndices, o miolo desaparece e a frase fica "…testado e versionado, com
   registro explícito…". Isso evita referências apontando para um apêndice
   inexistente (aquele `??` feio).

3. Os dois diretórios de apêndice (`a1-engenharia/`, `a2-integridade/`) estão no
   `.gitignore`: existem **só na sua máquina** e não vão para o repositório
   público. Quem clonar o repositório e rodar `make completo` recebe o documento
   sem apêndices, sem erro de compilação.

   > **Cuidado:** como não estão versionados, os apêndices **não têm backup**. Se
   > formatar a máquina, você os perde. Vale guardar uma cópia à parte.

**Se você escrever uma frase nova que cite um apêndice, envolva com
`\seapendice{}`** — senão a versão sem apêndices sai quebrada. Para conferir:

```bash
make completo && /usr/bin/grep -c "??" main_ap.log     # tem que dar 0
```

---

## 4. Receitas comuns

### Trocar uma informação de identificação

Abra `plano/identificacao.tex` (ou `0-iniciais/identificacao.tex`, no documento
completo). É uma tabela; cada linha tem o formato `\textbf{Rótulo} & valor \\`:

```latex
\textbf{Coorientador} & Prof.\ Dr.\ Bruno Pohlot Ricobom \\[0.4em]
\textbf{\quad Vínculo} & Departamento de Engenharia Elétrica, UFPR \\
```

O nome do coorientador aparece **também** na folha de rosto, via
`\coadvisor{...}` no `plano.tex` — se mudar em um lugar, mude nos dois.

### Remover o coorientador

Três lugares: a linha `\coadvisor{...}` no `plano.tex` (comente ou apague), as
quatro linhas do coorientador em `plano/identificacao.tex`, e o §1.5.1 (Recursos
humanos) em `plano/conteudo.tex`.

### Acrescentar um parágrafo

Escreva direto no `.tex` do capítulo. Parágrafo novo = **uma linha em branco**
antes. Não use `\\` para separar parágrafos.

### Acrescentar uma seção

```latex
\section{Nome da seção}
\label{sec:nome_curto}

Texto...
```

O `\label` é o que permite citar depois com `Seção~\ref{sec:nome_curto}`. O `~`
é um espaço que não quebra linha — sempre use antes de `\ref`.

### Acrescentar uma referência bibliográfica

1. Cole a entrada BibTeX em `referencias.bib`:

   ```bibtex
   @article{sobrenome2025,
     author  = {Sobrenome, Nome and Outro, Fulano},
     title   = {Título do artigo},
     journal = {IEEE Transactions on Electromagnetic Compatibility},
     volume  = {67}, number = {2}, pages = {123--134}, year = {2025},
     doi     = {10.1109/TEMC.2025.1234567}
   }
   ```

2. Cite no texto com `\citep{sobrenome2025}` (entre parênteses) ou
   `\citet{sobrenome2025}` (o autor vira sujeito da frase: "Sobrenome et al.
   (2025) mostraram que…").
3. Rode `make` — precisa das passadas do bibtex para a referência aparecer.

**Só aparece na lista quem é citado no texto.** Entrada no `.bib` sem `\cite`
correspondente é ignorada.

### Marcar um mês no cronograma

No fim de `plano/conteudo.tex`, a tabela de cronograma usa `\mes` para pintar a
célula:

```latex
Revisão bibliográfica sistemática  & \mes & \mes & \mes & & & & & & & \\
```

Cada `&` separa uma coluna. São **dez**: ago–dez de 2026/2, depois mar–jul de
2027/1. Célula vazia = sem atividade. O número de `&` tem que bater com o
cabeçalho, senão o LaTeX reclama de "extra alignment tab".

### Acrescentar uma sigla

Só o documento completo tem lista de siglas. Em `0-iniciais/abreviaturas.tex`,
mantendo a ordem alfabética:

```latex
FEM & \textit{Finite Element Method} (método dos elementos finitos)\\
```

---

## 5. Erros que vão acontecer

| Sintoma | Causa quase sempre |
|---|---|
| `! Undefined control sequence` | comando escrito errado, ex. `\textbf` virou `\textbfg` |
| `! Missing $ inserted` | usou `_` ou `^` fora de modo matemático — escreva `\_` ou coloque entre `$...$` |
| `! LaTeX Error: File ... not found` | nome de arquivo errado no `\include` |
| Referência sai como `??` | falta rodar de novo (`make`), ou o `\label` não existe |
| Citação sai como `(?)` | a chave não existe em `referencias.bib`, ou faltou o bibtex |
| Compilação trava pedindo entrada | erro no meio do caminho: digite `X` e Enter para sair, corrija, rode de novo |

Para achar o erro no log:

```bash
/usr/bin/grep -n -A5 "^!" plano.log       # primeiro erro fatal
/usr/bin/grep -c "Undefined" plano.log    # referências/comandos indefinidos
```

O log do plano é `plano.log`; o do documento completo, `main_ap.log`.

> Use `/usr/bin/grep` com caminho completo neste ambiente: existe uma função de
> shell chamada `grep` que ignora arquivos listados no `.gitignore` — e os `.log`
> são ignorados, então o `grep` normal não acha nada dentro deles.

**Caracteres que precisam de escape no LaTeX:** `& % $ # _ { }` viram
`\& \% \$ \# \_ \{ \}`. O `~` e o `^` precisam de `\textasciitilde{}` e
`\textasciicircum{}`.

---

## 6. Antes de enviar para o professor

```bash
make clean && make
/usr/bin/grep -c "Undefined" plano.log    # 0
/usr/bin/grep -c "??" plano.log           # 0
pdfinfo Plano_de_Trabalho_*.pdf | grep Pages   # deve dar 15
```

Depois abra o PDF e confira a olho:

- página de identificação: matrícula, ênfase e dados do coorientador corretos;
- **sumário**: as oito seções têm de ser, na ordem, os itens 2 a 9 do Anexo I —
  Introdução, Objetivos, Público alvo, Metodologia, Recursos, Resultados,
  Contribuição, Cronograma. O sumário é o checklist da comissão;
- lista de referências completa, sem `(?)`.

---

## 7. Se precisar instalar o LaTeX em outra máquina

O ambiente atual usa **TinyTeX** (`~/.TinyTeX`). Para reproduzir:

```bash
# instalar TinyTeX
wget -qO- "https://yihui.org/tinytex/install-bin-unix.sh" | sh

# pacotes usados por este documento
tlmgr install collection-latexrecommended collection-fontsrecommended \
  collection-langportuguese newtx xstring multirow booktabs pdfpages \
  wallpaper moreverb currfile titlesec titletoc tocbibind enumitem \
  setspace fancyhdr microtype algorithms pdflscape
```

Alternativa sem instalar nada: subir a pasta `proposta/` no **Overleaf**
(New Project → Upload Project → zip da pasta) e compilar com pdfLaTeX. O Overleaf
não roda o `Makefile`, então defina `plano.tex` como documento principal
(Menu → Main document) para gerar a entrega.
