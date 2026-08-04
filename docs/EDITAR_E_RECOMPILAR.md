# Como editar o TCC e recompilar o PDF

Guia prático para mexer no documento sem depender de ajuda. Tudo acontece dentro
de `proposta/`.

```bash
cd ~/Downloads/TCC/proposta
```

---

## 1. Onde fica cada coisa

O `main.tex` quase não tem texto: ele só **monta** o documento. O conteúdo está
em arquivos separados, um por capítulo.

| Quero mexer em… | Arquivo |
|---|---|
| Título, autor, orientador, palavras-chave | `main.tex` (bloco "metadados", linhas ~47–70) |
| **Matrícula, ênfase, coorientador, quadro do Anexo I** | `0-iniciais/identificacao.tex` |
| Resumo (português) | `0-iniciais/resumo.tex` |
| Abstract (inglês) | `0-iniciais/abstract.tex` |
| Lista de siglas | `0-iniciais/abreviaturas.tex` |
| Lista de símbolos | `0-iniciais/simbolos.tex` |
| **Cap. 1 — Introdução, objetivos, público alvo, contribuição** | `1-intro/texto.tex` |
| **Cap. 2 — Referencial teórico** | `2-fundam/texto.tex` |
| **Cap. 3 — Metodologia** | `3-metodo/texto.tex` |
| **Cap. 4 — Recursos, cronograma, resultados** | `4-recursos/texto.tex` |
| Referências bibliográficas | `referencias.bib` |
| Apêndice A — engenharia de software | `a1-engenharia/texto.tex` |
| Apêndice B — integridade e uso de IA | `a2-integridade/texto.tex` |

Abra qualquer um deles num editor de texto comum (VS Code, gedit, nano). São
arquivos de texto puro.

---

## 2. Recompilar

```bash
make            # versão de ENTREGA (sem apêndices)
make pessoal    # versão PESSOAL (com apêndices A e B)
make tudo       # as duas de uma vez
```

Saídas:

- `Plano_de_Trabalho_TCC_Andre_Victor_Xavier_Pires_GRR20212735.pdf` — **é este
  que vai para o professor**
- `main_com_apendices.pdf` — sua cópia com os apêndices

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

## 3. Como os apêndices entram e saem

O mesmo fonte gera as duas versões. O mecanismo tem duas partes:

1. No fim do `main.tex`:

   ```latex
   \ifdefined\comapendices
     \appendix
     \include{a1-engenharia/texto}
     \include{a2-integridade/texto}
   \fi
   ```

   `make pessoal` define `\comapendices` na linha de comando; `make` normal não
   define, e os apêndices simplesmente não entram.

2. Trechos de texto que **citam** os apêndices ficam envolvidos por
   `\seapendice{...}`. Exemplo em `1-intro/texto.tex`:

   ```latex
   ...testado e versionado\seapendice{, segundo as práticas relatadas no
   Apêndice~\ref{ap:engenharia}}, com registro explícito...
   ```

   Na versão de entrega, o miolo desaparece e a frase fica "…testado e
   versionado, com registro explícito…". Isso evita que a entrega saia com
   referências apontando para um apêndice inexistente (aquele `??` feio).

3. Os dois arquivos de apêndice (`a1-engenharia/`, `a2-integridade/`) estão no
   `.gitignore`: eles existem **só na sua máquina** e não vão para o repositório
   público. O `main.tex` verifica se os arquivos existem antes de incluí-los, de
   modo que quem clonar o repositório e rodar `make pessoal` recebe a versão de
   entrega, sem erro de compilação.

   > **Cuidado:** como não estão versionados, os apêndices **não têm backup**. Se
   > formatar a máquina, você os perde. Vale guardar uma cópia à parte.

**Se você escrever uma frase nova que cite um apêndice, envolva com
`\seapendice{}`** — senão a versão de entrega sai quebrada. Para conferir:

```bash
make && /usr/bin/grep -c "??" main.log     # tem que dar 0
```

---

## 4. Receitas comuns

### Trocar uma informação de identificação

Abra `0-iniciais/identificacao.tex`. É uma tabela; cada linha tem o formato
`\textbf{Rótulo} & valor \\`. Exemplo, se o professor decidir formalizar o
coorientador:

```latex
\textbf{Coorientador} & Prof.\ Dr.\ Bruno Pohlot Ricobom --- Departamento de
Engenharia Elétrica, UFPR \\
```

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

Em `4-recursos/texto.tex`, as tabelas de cronograma usam `\mes` para pintar a
célula:

```latex
Revisão bibliográfica sistemática   & \mes & \mes & \mes &      &      \\
```

Cada `&` separa uma coluna (ago, set, out, nov, dez). Célula vazia = sem
atividade. O número de colunas tem que bater com o cabeçalho.

### Acrescentar uma sigla

Em `0-iniciais/abreviaturas.tex`, mantendo a ordem alfabética:

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
/usr/bin/grep -n -A5 "^!" main.log       # primeiro erro fatal
/usr/bin/grep -c "Undefined" main.log    # referências/comandos indefinidos
```

> Use `/usr/bin/grep` com caminho completo neste ambiente: existe uma função de
> shell chamada `grep` que ignora arquivos listados no `.gitignore` — e o
> `main.log` é um deles, então o `grep` normal não acha nada dentro dele.

**Caracteres que precisam de escape no LaTeX:** `& % $ # _ { }` viram
`\& \% \$ \# \_ \{ \}`. O `~` e o `^` precisam de `\textasciitilde{}` e
`\textasciicircum{}`.

---

## 6. Antes de enviar para o professor

```bash
make clean && make
/usr/bin/grep -c "Undefined" main.log    # 0
/usr/bin/grep -c "??" main.log           # 0
pdfinfo Plano_de_Trabalho_*.pdf | grep Pages
```

Depois abra o PDF e confira a olho:

- página de identificação: matrícula, ênfase e coorientador corretos;
- quadro do Anexo I: cada item aponta para uma seção que realmente existe (se
  você mexeu na ordem das seções, os números mudam sozinhos, mas vale conferir);
- sumário coerente;
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
(New Project → Upload Project → zip da pasta) e compilar com pdfLaTeX. Nesse
caso o Overleaf não roda o `Makefile`, então a versão gerada será a de
**entrega** (sem apêndices) — que é justamente a que você precisa enviar.
