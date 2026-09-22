# Relatório de Progresso — Primeira Avaliação de TCC I

**Aluno:** André Victor Xavier Pires (GRR20212735)
**Orientador:** Prof. Dr. Leandro dos Santos Coelho
**Data:** 22 de setembro de 2026
**Título:** Predição de margem de conformidade eletromagnética de PDNs em PCBs multicamadas por modelo substituto informado por física

---

## 1. Resumo executivo

- O **plano de trabalho foi entregue** (11 páginas, conforme Anexo I das normas do DELT).
- A **infraestrutura de dados está construída e validada**: 1.341 linhas de código Python, **36 testes automatizados passando**.
- **Dois subconjuntos da base de dados** foram processados integralmente: 985 e 36.199 configurações (25 GB de arquivos Touchstone).
- **Cinco hipóteses físicas foram testadas** sobre os dados reais: três confirmadas, uma reformulada e uma refutada.
- O **primeiro marco do cronograma (setembro/2026) está cumprido** com antecedência.

---

## 2. Revisão bibliográfica

**Acervo:** 15 artigos coletados; 9 lidos integralmente e fichados em documento de análise metodológica (`referencias/ANALISE_METODOLOGICA.md`, 375 linhas).

**Resultados práticos da revisão:**

- **Identificação do artigo que projetou a base de dados usada no TCC** — Schierholz, Hassab e Schuster (*IEEE Trans. CPMT*, vol. 13, n. 10, out. 2023). A Tabela I desse artigo reproduz, valor a valor, os parâmetros fixos do conjunto de dados utilizado. Isso fornece a justificativa publicada de por que 8 dos 17 parâmetros variam e 9 são constantes.
- **Delimitação do espaço ocupado pela pesquisa.** Hillebrecht et al. (*IEEE Trans. EMC*, dez. 2024) declaram explicitamente que a predição do comportamento eletromagnético em toda a faixa de frequência é um problema em aberto que exige métodos informados por física. Garbuglia et al. (*IEEE Trans. EMC*, dez. 2023) declaram como trabalho futuro exatamente os dois itens que este TCC executa: estender a modelagem a variáveis de projeto adicionais e impor propriedades físicas às predições.
- **Referências indicadas pelo orientador** (e-mail de set/2026) já incorporadas ao acervo e fichadas, incluindo a Tabela I do artigo relacional de 2025, que lista os subconjuntos disponíveis para as próximas etapas.

---

## 3. Infraestrutura de dados (código)

**Módulos implementados** (`src/data/`):

| Arquivo | Linhas | Função |
|---|---|---|
| `touchstone.py` | 231 | Leitura de arquivos Touchstone, conversão S → Z, verificação de invariantes físicas |
| `loader.py` | 346 | Carregamento paralelo e genérico de qualquer subconjunto de PDN |
| `subsets.py` | 98 | Adaptador que descreve cada subconjunto (portas, features, geometria) |
| `grid.py` | 81 | Interpolação para grade de frequência comum entre subconjuntos |

**Testes:** `tests/test_touchstone.py` (227 linhas) e `tests/test_subsets.py` (222 linhas) — **36 testes, 100% aprovados**, executados em 16 segundos. Cobrem casos analíticos, invariantes físicas e verificações de forma e tipo.

**Desempenho:** carregamento das 985 configurações do subconjunto de referência (23 GB) em aproximadamente 30 segundos, com processamento paralelo em 8 núcleos.

---

## 4. Resultados experimentais

### 4.1 Verificação das hipóteses físicas

Cada restrição física foi testada sobre os dados antes de ser incorporada ao modelo — princípio metodológico adotado desde o plano de trabalho.

| Hipótese | Resultado | Situação |
|---|---|---|
| **R1** — comportamento capacitivo abaixo do nulo de série (inclinação log-log = −1) | −1,0197 ± 0,0062 (985 configs) e −1,0001 ± 0,0113 (36.199 configs) — **100% de conformidade nas duas topologias** | Confirmada |
| **R2** — escala da capacitância (lei de placas paralelas) | Vale para **66,3%** do conjunto, com expoentes +0,952 e −0,974 contra +1 e −1 teóricos (**R² = 0,973**) | Reformulada |
| **R3** — monotonicidade até o nulo de série | Confirmada no subconjunto de referência | Confirmada |
| **R4** — passividade | Obrigatória por construção | Confirmada |
| **R5** — localização dos modos de cavidade | Modos previstos **não são observáveis** na autoimpedância | **Refutada** |

**Interpretação de R2:** o fator ≈ 2,1 encontrado corresponde à porta acoplada a duas cavidades em paralelo. A escala absoluta, porém, **não transfere entre topologias** (razão 2,13 num subconjunto contra 0,46 no outro), o que confirma a decisão de projeto — já registrada no plano de trabalho — de formular o termo de perda apenas sobre a derivada logarítmica, que é invariante a fator multiplicativo.

### 4.2 Reprodução de resultado publicado

O ranking de sensibilidade dos parâmetros medido sobre as 985 configurações **reproduz exatamente a ordem publicada** na Fig. 11 de Schierholz et al. (2023) nas duas primeiras posições (espessura do dielétrico e permissividade relativa), obtida por metodologia estatística independente da usada pelos autores.

### 4.3 Validação do pipeline contra referência externa

No subconjunto de 36.199 configurações, o banco de capacitores de desacoplamento é uma grandeza conhecida de forma independente. Ajustando a capacitância extraída contra as contribuições conhecidas:

```
C_extraída = α · C_placa + β · C_decaps
β = 1,065        R² = 0,996        (n = 300)
```

O coeficiente do banco de decaps é recuperado em **1,065** contra 1,000 esperado — validação de ponta a ponta da leitura Touchstone, da conversão S → Z e da extração de capacitância.

### 4.4 Correções de engenharia identificadas por medição

- **Erro de janela de medição detectado e corrigido.** A regra de extração calibrada no primeiro subconjunto reprovava 91% das configurações do segundo, por motivo puramente metodológico (os capacitores deslocam o nulo de série para dentro da janela de medição). A regra passou a ser adaptativa por configuração: conformidade de **9% → 100%**.
- **Tolerância de reciprocidade recalibrada.** A tolerância especificada originalmente (1×10⁻⁶) reprovava todas as configurações; a assimetria medida é da ordem de 10⁻⁵, compatível com ruído numérico do solver. Corrigida para 1×10⁻⁴, com a medição registrada.
- **Alinhamento dos dados verificado.** Teste de permutação confirma que parâmetros e curvas estão corretamente pareados (R² real de 0,197 contra 0,002 com rótulos embaralhados).

---

## 5. Documentação produzida

- **6 especificações técnicas** (`spec/`, 1.189 linhas): escopo, roteiro, dados, física, união de subconjuntos e brief de pesquisa.
- **Documento de arquitetura** (`design/architecture.md`, 383 linhas).
- **Análise metodológica da literatura** (`referencias/ANALISE_METODOLOGICA.md`, 375 linhas) — tabela comparativa de protocolo experimental, métricas e resultados dos trabalhos correlatos.
- **Apresentação de 27 slides** (`docs/apresentacao_exploracao_dados.pptx`) com a exploração completa dos dados, no template oficial da UFPR.
- **4 scripts de análise** com figuras geradas (`notebooks/`).

---

## 6. Situação do cronograma

| Marco | Prazo | Situação |
|---|---|---|
| Pipeline validado contra propriedades analíticas conhecidas | set/2026 | **Cumprido** |
| Quatro subconjuntos reunidos e melhor modelo de referência com R² > 0,80 | nov/2026 | Em andamento (2 de 4 subconjuntos processados) |
| Modelo informado por física superando a ablação | abr/2027 | TCC II |
| Fronteira de Pareto conferida por simulação | jun/2027 | TCC II |

**Atividades do cronograma em execução no momento:** revisão bibliográfica (ago–out), pipeline de extração e validação (ago–out) e reunião dos subconjuntos e das normas (set–nov).

---

## 7. Próximos passos até novembro

1. **Incorporar dois subconjuntos adicionais** — identificados na Tabela I do artigo relacional de 2025: 8 camadas (10.000 configurações, hipercubo latino) e 4 camadas (9.999 configurações). Com 3, 5 e 7 cavidades na mesma família geométrica, o número de cavidades passa a ser um atributo observável, o que permite testar a hipótese que explicaria o desvio de escala de R2.
2. **Análise exploratória complementar**, conforme orientação recebida por e-mail: correlações de Pearson e phik (Spearman já executada), correlações sobre a fase, balanceamento de classes e agrupamento de capacitores por proximidade à porta.
3. **Modelos de referência sob protocolo único** — processos gaussianos e rede neural, com partição registrada e curva de aprendizado.
4. **Tabulação das curvas-limite normativas** (CISPR 32 classes A e B; IEC 61000-6-3 e 6-4), preparando a camada normativa do TCC II.

---

## 8. Arquivos para análise

| Arquivo | Conteúdo |
|---|---|
| `proposta/Plano_de_Trabalho_...pdf` | Plano de trabalho entregue (11 páginas) |
| `docs/apresentacao_exploracao_dados.pptx` | Apresentação com todos os resultados (27 slides) |
| `spec/PHYSICS_SPEC.md` | Hipóteses físicas, evidências e registro da refutação |
| `spec/UNIAO_SUBCONJUNTOS.md` | Especificação da união dos subconjuntos |
| `referencias/ANALISE_METODOLOGICA.md` | Análise metodológica dos trabalhos correlatos |
| `src/` e `tests/` | Código-fonte e testes automatizados |
| `notebooks/` | Scripts de análise e figuras |

---

*Repositório completo disponível para inspeção. A base de dados original (SI/PI-Database, TUHH) não é redistribuída, conforme os termos de uso.*
