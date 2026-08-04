# Política de uso de IA e integridade acadêmica

**Versão:** 1.0 · **Data:** 2026-08-01
**Vinculado a:** Apêndice B da proposta (`proposta/a2-integridade/texto.tex`)

Este documento é a versão operacional da política declarada na proposta. O texto
da proposta é o que a banca lê; este é o que se executa no dia a dia.

---

## Princípio

**Responsabilidade não delegável.** O autor responde por cada afirmação, número,
referência e linha de código, independentemente do instrumento usado para
produzi-los. Uma ferramenta de assistência não transfere responsabilidade, assim
como um compilador ou um solver eletromagnético não transferem.

Consequência prática: **nada entra no trabalho sem verificação independente.**

---

## Fronteira

| Admitido | Vedado |
|---|---|
| revisão de redação (clareza, coesão, gramática) | texto corrido incorporado sem reescrita e verificação integral |
| implementação de código sob spec escrita pelo autor | formulação do problema, das hipóteses ou do desenho experimental |
| explicação de conceitos e de artigos lidos | referências obtidas sem verificação na fonte primária |
| sugestão de estrutura e organização | interpretação de resultados e redação de conclusões |
| automação de tarefas repetitivas de verificação | qualquer número não derivado de execução reprodutível |

O critério que separa as colunas: a ferramenta contribui para a **substância
intelectual** ou apenas para **forma e execução**?

---

## Os dois modos de falha que mais importam

### 1. Referência fabricada

Modelos de linguagem produzem citações sintaticamente perfeitas e inexistentes:
autores plausíveis, periódicos reais, DOIs que não resolvem.

**Procedimento obrigatório.** Toda entrada de `referencias.bib` é confirmada na
fonte primária antes de ser citada. Verificação via Crossref:

```bash
curl -s -G "https://api.crossref.org/works" \
  --data-urlencode "query.bibliographic=<título e autores>" \
  --data-urlencode "rows=1" | python3 -m json.tool
```

Conferir: título, **todos** os autores, veículo, ano, volume, páginas, DOI.
Registrar a data da verificação no cabeçalho do `.bib`.

Status atual: as 15 entradas de `proposta/referencias.bib` foram verificadas
via Crossref em 2026-08-01. Uma entrada sem DOI (`lundberg2017`, NeurIPS) foi
confirmada manualmente.

### 2. Alucinação numérica

**Nenhum valor no texto pode ter origem em estimativa de ferramenta assistiva.**
Todo número reportado provém de execução registrada, rastreável a commit e
identificador de execução.

Exemplo de rastreabilidade — os números da Seção 3.4 da proposta:

```bash
python scripts/verify_physics_anchors.py --n 40 --seed 42
```

produz `-1.018 ± 0.008`, mediana da razão `2.12`, `r = 0.64` — exatamente os
valores citados. Registro em `experiments/physics_anchors.json`.

---

## O terceiro modo de falha: estatística plausível e errada

Este não é específico de IA, mas foi o que efetivamente ocorreu neste projeto e
por isso vale mais que os outros dois.

Uma análise preliminar reportou "erro mediano de casamento modal de 3,1%, 83%
abaixo de 10%" e a conclusão de que a restrição modal estava validada. Estava
errada: o detector localizava ondulação numérica, e com 15 modos na banda
qualquer frequência dista poucos por cento de algum deles. A estatística media a
densidade do espectro, não concordância física.

**O erro só apareceu ao plotar e olhar.**

**Regra decorrente, obrigatória:** nenhuma estatística agregada sustenta uma
conclusão antes de inspeção gráfica. Vale para métricas de modelo tanto quanto
para verificação física. Ver `spec/PHYSICS_SPEC.md`, seção "Registro de
refutação".

---

## Verificação de originalidade

| Momento | Ferramenta | Escopo |
|---|---|---|
| durante a escrita | Grammarly | por capítulo |
| fim de cada semestre | Copyleaks | documento integral |
| capítulos de alta densidade de citação | Quetext | verificação cruzada |
| documento final | Plag.pt | integral, português |
| trechos pontuais | DupliChecker, PaperRater | ad hoc |

**Interpretação dos relatórios.** Similaridade em referências, nomes de normas e
terminologia consagrada é esperada. Trecho de texto corrido com mais de 25
palavras consecutivas em similaridade: reescrever ou converter em citação direta
com fonte, página e recuo (NBR 10520).

**Limitação reconhecida.** Detectores identificam correspondência textual, não
plágio de ideias; detectores de texto gerado por IA têm taxas de erro que
desaconselham uso como evidência isolada. A garantia de integridade neste
trabalho não se apoia em detecção a posteriori, mas na **rastreabilidade
positiva**: código versionado, execuções registradas, números reproduzíveis.

Relatórios arquivados em `docs/relatorios_originalidade/`, disponíveis ao
orientador e à banca.

---

## Checklist antes de cada entrega

- [ ] toda referência verificada em fonte primária, data registrada
- [ ] todo número rastreável a uma execução registrada
- [ ] toda estatística agregada inspecionada graficamente
- [ ] `pytest` verde
- [ ] verificação de originalidade executada e arquivada
- [ ] declaração de uso de IA presente e atualizada
