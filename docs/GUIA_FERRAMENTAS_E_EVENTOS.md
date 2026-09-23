# Guia — ferramentas e eventos indicados pelo Prof. Leandro

**Data:** 2026-09-23 · **Origem:** e-mail do orientador de 22/09/2026, em resposta ao relatório da 1ª avaliação.

| Pedido do orientador | Onde está a resposta |
|---|---|
| versão Colab em arquivo único | `notebooks/TCC_PDN_Colab.ipynb` — §3 |
| tempo para ler e processar os dados | §4 |
| incluir métricas | `notebooks/05_resultados_salib.md` — §1 e §5 |
| inferência causal (causalml / DoWhy) | §2 |
| sensibilidade com SALib | §1 |
| SeMicro-PR e IEEE ICIT 2027 | §5 |
| próximas etapas | §6 |

> **Achado que atravessa tudo.** Rodar o SALib expôs um problema de integridade no PI-4: as
> simulações **1000–1499 não correspondem aos parâmetros do `parameter.csv`**. Com os 985
> dados, nenhum modelo passa de R² ≈ 0,11; com as 485 simulações confiáveis (`simu_index ≥ 1500`),
> o mesmo modelo atinge R² = 0,995. Detalhes em `spec/PHYSICS_SPEC.md` (R2, correção de
> 2026-09-23) e na figura `notebooks/05a_integridade_pi4.png`.

---

## 1. SALib — análise de sensibilidade

**O que é.** Biblioteca de análise de sensibilidade global: mede quanto da variância de uma
saída é explicada por cada entrada, isoladamente e em interação.

**A restrição que importa.** Cada método do SALib exige um desenho de amostragem próprio. Os
dados do TCC **já existem** e foram amostrados por hipercubo latino, então só servem os métodos
que aceitam amostra dada:

| Método | Aceita os dados atuais? | O que mede |
|---|---|---|
| **RBD-FAST** (`SALib.analyze.rbd_fast`) | ✅ sim | S1 — fração da variância explicada por cada entrada sozinha |
| **delta** (`SALib.analyze.delta`) | ✅ sim | δ — efeito sobre a *distribuição inteira*, não só a variância; também S1 |
| **PAWN** (`SALib.analyze.pawn`) | ✅ sim | estatística KS entre distribuição condicional e incondicional |
| **HDMR** (`SALib.analyze.hdmr`) | ✅ sim, com cautela | 1ª e 2ª ordem; **sobreajusta** com poucos dados — sempre conferir a coluna `select` |
| **Sobol** (`SALib.analyze.sobol`) | ❌ não | S1, ST (total) e S2; exige amostragem de **Saltelli** |
| **Morris** e **FAST** | ❌ não | exigem trajetórias / amostragem próprias |

**Como fazer Sobol mesmo assim.** Depois que existir o modelo substituto: gerar amostra de
Saltelli com `SALib.sample.sobol.sample`, avaliar no **modelo** (milissegundos) e analisar com
`sobol.analyze`. É o uso clássico de surrogate em sensibilidade — e dá ST e S2, que respondem
diretamente se há interações.

**Como rodar.** `./venv/bin/python notebooks/05_sensibilidade_salib.py` (80 s) — gera tabelas em
`notebooks/05_resultados_salib.md` e as figuras `05a_…` e `05b_…`. Ou a seção 6 do notebook Colab.

**Resultados no bloco confiável (485 configurações).**

| Saída | Soma S1 | Parâmetros dominantes (S1, RBD-FAST) |
|---|---|---|
| log\|Z\| em 1 MHz | 0,973 | TDIEL 0,924 · ε_r 0,070 |
| frequência do nulo de série | 0,961 | **ε_r 0,540 · A1 raio da via 0,332** · A1 passo 0,075 · TDIEL 0,020 |
| log\|Z\| no nulo | 0,786 | TDIEL 0,675 |
| log\|Z\| em 1 GHz | 0,687 | TDIEL 0,611 |

**Como ler.**
- **Soma S1 ≈ 1** → efeitos individuais explicam a saída; não há interação relevante. É o caso
  do regime capacitivo, coerente com a lei aditiva em log.
- **Soma S1 < 1** → sobra variância para interações ou comportamento que as 8 entradas não
  capturam. É o caso perto do nulo e em 1 GHz.
- **O nulo de série não depende da espessura do dielétrico** (S1 = 0,02). Leitura física a
  confirmar pelo autor: C ∝ ε_r/h e L_via ∝ h, logo o produto LC não depende de h.
- **O arranjo A2 tem influência nula**; o A1 domina junto ao nulo. A porta 0 fica no arranjo I —
  o que valida a porta escolhida no adaptador.

**Lição de método.** O HDMR sobre as 985 configurações deu soma 0,966 espalhada em 28 pares
com ≈ 0,03 cada — parecia "tudo é interação". A coluna `select` mostrou que **nenhum** par foi
significativo em nenhum dos 20 bootstraps, e a validação cruzada piorou ao permitir interações.
Era sobreajuste. Nenhum índice agregado sem teste de significância e inspeção.

---

## 2. Inferência causal — DoWhy e causalml

**Onde ela não acrescenta.** O PI-4 é um **experimento projetado**: as entradas foram atribuídas
pelo experimentador (hipercubo latino), não observadas. Não há confundimento, e o efeito de cada
parâmetro já é identificado pela própria análise de sensibilidade. O DoWhy confirma isso: a
identificação sai com conjunto de ajuste trivial.

**Onde ele acrescenta: testes de refutação.** Resultado real, efeito de log h sobre log|Z| em 1 MHz:

| Dados | Efeito estimado | Placebo | Causa comum aleatória | Subconjunto 70 % |
|---|---|---|---|---|
| bloco confiável (485) | **+0,956** (física: +1) | −0,000 | +0,956 | +0,956 |
| todas (985) | **+0,428** ❌ | −0,013 | +0,428 | +0,426 |

**A estimativa errada passa em todos os refutadores.** Os refutadores checam a robustez da
estimativa *dentro* dos dados; não checam se os dados descrevem o que dizem descrever. Quem pegou
o problema foi a validação física. Esse contraste é, em si, um bom argumento metodológico.

**Onde a inferência causal pode ser útil de verdade:** na **união de subconjuntos**. Juntando
PI-1, PI-2, PI-3 e PI-4, o subconjunto de origem passa a ser um confundidor (cada um tem sua
geometria, faixa de parâmetros e número de cavidades). Aí um grafo causal com `subconjunto_id`
e `n_cavidades` como causas comuns, e o ajuste pelo DoWhy, deixam de ser redundantes.

**causalml — não recomendado aqui.** Foi feito para *uplift* e efeitos heterogêneos de um
**tratamento** (tipicamente binário) em dados observacionais — marketing, medicina. Aqui não há
tratamento nem observação: há parâmetros contínuos de um experimento projetado; a heterogeneidade
de efeitos é coberta por Sobol (ST, S2) e SHAP sobre o modelo. Além disso, instalar o causalml
traz 305 MB de biblioteca CUDA e **conflita com o DoWhy** (um exige scipy < 1,16, o outro 1,18).
Se um dia for necessário, usar num ambiente separado ou no Colab.

⚠️ **Efeito colateral já ocorrido:** instalar o DoWhy rebaixou numpy (2,5 → 2,4) e scipy
(1,18 → 1,15) no `venv`. Os 36 testes continuam passando.

---

## 3. Notebook Colab — `notebooks/TCC_PDN_Colab.ipynb`

**Arquivo único**, sem dependência do repositório: leitura Touchstone, conversão S→Z, R1,
integridade, lei quase-estática, modelo de referência com métricas, SALib e DoWhy (opcional).
Entregue **já executado**, com todas as saídas e figuras gravadas — o orientador pode ler sem rodar.

**Para rodar no Colab.** Criar `MyDrive/TCC_PDN/` no Google Drive e colocar:

| Modo | O que subir | Tempo |
|---|---|---|
| `cache` (padrão) | `data/processed/pdn6_cache.npz` (1,2 MB) | ~1 min |
| `bruto` | a pasta do subconjunto (23 GB) | lento pelo Drive — usar `LIMITE = 200` |

⚠️ **Decisão sua antes de enviar:** o `pdn6_cache.npz` contém as curvas reduzidas da base da
TUHH. Compartilhar com o orientador, em Drive privado, para avaliação acadêmica, é uso razoável —
mas os termos da TUHH são seus para conferir. Alternativa: o orientador solicita acesso à base
pelo formulário do site. O notebook cita Schierholz *et al.* (2021) e declara o uso de IA
generativa (Portaria CNPq nº 2.664/2026, art. 9º, I, c).

**Testado:** executado do início ao fim no kernel do projeto, nos três caminhos — modo cache,
modo bruto (200 arquivos) e com o DoWhy ativado.

---

## 4. Tempo de processamento

Medido nesta máquina (16 núcleos, 8 processos de leitura):

| Etapa | Tempo |
|---|---|
| PI-4: ler 985 arquivos `.s36p` (23 GB) e extrair \|Z11(f)\| | 55,6 s |
| PI-1: ler 36 199 arquivos `.s2p` (2 GB) | 29,0 s |
| verificação física completa (`04_sensibilidade_fisica.py`, a partir do cache) | 19,2 s |
| integridade + SALib + modelo de referência (`05_sensibilidade_salib.py`) | 80 s |
| testes automatizados (36) | 11,9 s |
| **total, do Touchstone bruto ao último resultado** | **≈ 3 min 16 s** |
| notebook Colab, modo cache | ≈ 30 s de processamento |

A leitura é limitada por disco (arquivos ASCII de 24 MB). No Colab, a partir do Drive, a leitura
do bruto é várias vezes mais lenta — por isso o modo cache.

---

## 5. Eventos: SeMicro-PR 2026 e IEEE ICIT 2027

### Datas e formato

| | **SeMicro-PR 2026** | **IEEE ICIT 2027** |
|---|---|---|
| Local | Centro Politécnico, UFPR, Curitiba | UFSC, Florianópolis |
| Data | 4–6 nov. 2026 | 17–19 mar. 2027 (preliminar) ¹ |
| **Submissão** | **5 out. 2026 (12 dias)** | **regular: 12 out. 2026 (19 dias) · WiP: 25 out. 2026 (32 dias)** |
| Formato | até 4 p., PT ou EN, modelo Word/LaTeX | regular: 6 p. · WiP: 4 p., sem páginas extras · IEEE duas colunas, inglês |
| Resultado | 30 out. 2026 | 11 dez. 2026 |
| Publicação | anais, só se apresentado | IEEE Xplore, só se apresentado **presencialmente** |
| Escopo | microeletrônica ampla (CIs, embarcados, processamento de sinais, ferramentas de projeto, teste). PI/EMC de placa **não aparece explicitamente** — confirmar aderência | trilhas **T9** (IA e Informática Industrial) ou **T4** (Eletrônica para Ciência de Dados) |

¹ O cartaz traz 17–19 no cabeçalho e 15–17 no texto; o site confirma 17–19, ainda "preliminar".

### Custo do ICIT 2027

**Inscrição** (valores oficiais em reais, com desconto CAPES/CNPq para brasileiros):

| Categoria | Antecipada | Regular | Cobre artigo? |
|---|---|---|---|
| Membro IES | R$ 2.100 | R$ 2.500 | sim, 1 (até 2 com +R$ 800) |
| Membro IEEE | R$ 2.300 | R$ 2.700 | sim |
| Não membro | R$ 2.800 | R$ 3.200 | sim |
| **Estudante membro** | R$ 900 | R$ 1.100 | **não** |

A inscrição de autor inclui almoços, café, jantar de gala e anais. Página extra: R$ 400.
**Todo artigo aceito precisa de uma inscrição completa** — a de estudante não serve para isso.

**Deslocamento e estadia** (estimativas próprias, a conferir): ônibus Curitiba–Florianópolis,
≈ 300 km, R$ 200–400 ida e volta; 3 noites a R$ 150–350; jantares e transporte local
R$ 300–450. Subtotal: **R$ 1.000–1.900**.

| Cenário | Inscrição | Viagem | **Total** |
|---|---|---|---|
| A. você, não membro | R$ 2.800 | R$ 1.000–1.900 | **R$ 3.800–4.700** |
| B. você, membro IEEE + IES | R$ 2.100 + anuidade | R$ 1.000–1.900 | **R$ 3.100–4.000 + anuidade** |
| C. artigo coberto pela inscrição completa do orientador; você como estudante | R$ 900 | R$ 1.000–1.900 | **R$ 1.900–2.800** |

**Bolsa S&YP da IEEE IES — até US$ 1.500.** Prazo 15 jan. 2027. Na edição de 2026 eram 10 bolsas,
cobrindo transporte, inscrição e hotel até 3 estrelas; exigiam **ser membro IEEE e IES** como
estudante, pedido pelo sistema de submissão *após* o aceite e **um vídeo de exatamente 3 minutos**.
Condições de 2027 a confirmar. Se obtida, cobre praticamente todo o cenário B.

**Anuidade de estudante IEEE + IES:** varia por país — conferir em
`ieee.org/membership/join/dues` selecionando Brasil. É o que torna o cenário B e a bolsa possíveis.

**Apoio institucional:** verificar editais da UFPR e do PPGEE de auxílio à participação de
estudantes em eventos.

### SeMicro-PR

Em Curitiba, no seu campus: **custo de deslocamento zero**. Taxa de inscrição não localizada no
site — confirmar com a organização (GICS/UFPR).

### Riscos e cuidados

- **Prazo.** SeMicro em 12 dias e ICIT regular em 19. Um artigo de 6 páginas até 12/10 exige
  resultado de modelo que ainda não existe; o **WiP de 25/10** é o realista.
- **Fragmentação e divulgação prévia** (Portaria CNPq nº 2.664/2026, art. 9º, II, *e*, *f* e *u*):
  os dois textos precisam ter contribuições distintas, e o segundo deve declarar o primeiro.
  Divisão natural: **SeMicro** — verificação física da base e o achado de integridade;
  **ICIT WiP** — modelo substituto, SALib e primeiro resultado com restrições físicas.
- **Uso de IA** (art. 9º, I, *c*): declarar ferramenta e finalidade no texto. A IEEE tem política
  própria de declaração — conferir no *Author Center* antes de submeter.
- **Achado sobre a base da TUHH:** reportar aos mantenedores **antes** de publicar qualquer
  afirmação sobre a integridade dos dados deles. Eles podem ter versão corrigida, e é o
  procedimento correto.

---

## 6. Próximas etapas

1. **Reportar à TUHH** o descasamento das simulações 1000–1499 do PI-4 (formulário do site).
2. **Excluir `simu_index < 1500` do PI-4 no carregador**, com teste, até a resposta.
3. **Baixar PI-3** (8 camadas, LHS), reduzir à curva, apagar o bruto; depois **PI-2**.
   Detalhes em `spec/UNIAO_SUBCONJUNTOS.md`.
4. **Modelo substituto da curva inteira** (hoje o modelo de referência é por ponto de frequência)
   e **Sobol via substituto** com o SALib.
5. **Itens de EDA do e-mail anterior** ainda pendentes: correlação phik, sensibilidade da fase,
   agrupamento de decaps (PI-1) e balanceamento de `targetMet`.
6. **Artigos:** decidir com o orientador entre SeMicro-PR (5/10), ICIT regular (12/10) e ICIT WiP (25/10).
7. **Curvas-limite normativas** (CISPR 32 A/B, IEC 61000-6-3 e 6-4) — preparação da camada normativa.

---

## Fontes

- ICIT 2027: `icit2027.ieee-ies.org` — páginas *For Authors* e *Registration*, consultadas em 23/09/2026.
- Bolsa S&YP: página *Students* da ICIT 2026 (`icit2026.ieee-ies.org/students/`) e *IES Paper Travel
  Assistance* (`ieee-ies.org/membership/syp/travel`).
- SeMicro-PR 2026: `jpm.ufpr.br/chamada-de-trabalhos/`.
- SI/PI-Database: site da TUHH, consultado em 23/09/2026.
