# Modelo substituto informado por física para predição de impedância de PDN

Trabalho de Conclusão de Curso — Engenharia Elétrica, ênfase em sistemas
eletrônicos embarcados · Universidade Federal do Paraná.

**Autor:** André Victor Xavier Pires (GRR20212735)
**Orientador:** Prof. Dr. Leandro dos Santos Coelho (DELT / PPGEE — UFPR)
**Período:** TCC I (2026/2) · TCC II (2027/1) — **em andamento**

---

## O problema

A rede de distribuição de energia (*power delivery network*, PDN) de uma placa
multicamadas é um dos principais determinantes da conformidade eletromagnética
de um produto eletrônico: o par de planos de alimentação e referência se comporta
como cavidade ressonante, e os picos de impedância resultantes convertem ruído de
comutação em emissão irradiada.

Avaliar essa impedância exige hoje solvers eletromagnéticos cujo custo — dezenas
de minutos por configuração — inviabiliza a exploração do espaço de projeto
justamente na fase inicial de *layout*, quando as correções ainda são baratas.

## A proposta

Treinar um **modelo substituto** que prediga a curva de impedância `Z(f)` da PDN
diretamente dos parâmetros do empilhamento, em menos de 1 ms, **incorporando
restrições eletromagnéticas conhecidas em forma fechada à função de perda** —
comportamento capacitivo no regime quase-estático, monotonicidade até o nulo de
série e passividade.

A hipótese central é que essa informação física compensa a escassez de dados
(< 1000 amostras), regime em que modelos puramente orientados a dados tendem a
violar a física do problema. As hipóteses são enunciadas de forma refutável: um
resultado negativo é reportável.

---

## Estado atual

| Etapa | Estado |
|---|---|
| Proposta / plano de trabalho (Anexo I) | ✅ concluída — 40 páginas, 13 referências verificadas |
| Caracterização da base de dados | 🔄 verificada sobre amostra de 40 configurações |
| Pipeline de extração de impedância | 🔄 em implementação (`src/data/touchstone.py`) |
| Modelos de referência | ⬜ |
| Modelo informado por física | ⬜ |
| Otimização multiobjetivo | ⬜ |

---

## A base de dados

**SI/PI-Database v1.0**, Technische Universität Hamburg (TUHH). Subconjunto
principal: *6-Layer PCB based PDN with Two Via Arrays* (amostragem por hipercubo
latino).

| | |
|---|---|
| Configurações | **985** |
| Features (parâmetros que efetivamente variam) | **8** de 17 colunas |
| Alvo | curva `Z11(f)` — **334 pontos**, 1 MHz a 1 GHz, espaçamento linear de 3 MHz |
| Formato bruto | Touchstone `.s36p`, 36 portas, ~24 MB por arquivo |
| Volume | ~24 GB descompactados no subconjunto principal |

> ⚠️ **A base não está neste repositório.** É de acesso público mediante aceite
> dos termos de uso da TUHH e não pode ser redistribuída aqui. Consulte
> [`spec/DATA_SPEC.md`](spec/DATA_SPEC.md) para a origem, o esquema esperado e o
> procedimento de verificação de integridade.

Números anteriormente estimados (986 configurações, 13 features, alvo escalar)
foram **refutados por inspeção direta dos arquivos** — o histórico da correção
está registrado em [`spec/RESEARCH_BRIEF.md`](spec/RESEARCH_BRIEF.md).

---

## Estrutura

```
spec/         especificações — o QUÊ (fonte de verdade sobre dados e física)
design/       arquitetura — o COMO
src/          código de produção
tests/        testes automatizados
scripts/      utilitários e verificações reproduzíveis
notebooks/    exploração
experiments/  rastreamento de experimentos
proposta/     documento LaTeX da proposta de TCC
docs/         documentação de processo
```

**Ordem de leitura sugerida:** [`spec/RESEARCH_BRIEF.md`](spec/RESEARCH_BRIEF.md)
→ [`spec/SCOPE.md`](spec/SCOPE.md) → [`spec/DATA_SPEC.md`](spec/DATA_SPEC.md) →
[`spec/PHYSICS_SPEC.md`](spec/PHYSICS_SPEC.md) →
[`design/architecture.md`](design/architecture.md).

---

## Reproduzir

### Ambiente

```bash
conda env create -f environment.yml
conda activate tcc_pdn
pytest tests/ -v
```

### Verificar as âncoras físicas

Reproduz a medição que sustenta o termo de perda quase-estático — a inclinação
capacitiva medida vale −1,018 ± 0,008 contra −1 teórico:

```bash
python scripts/verify_physics_anchors.py --n 40 --seed 42
```

Requer a base da TUHH disponível localmente.

### Compilar o documento da proposta

```bash
cd proposta && make
```

Detalhes em [`proposta/README.md`](proposta/README.md); guia de edição em
[`docs/EDITAR_E_RECOMPILAR.md`](docs/EDITAR_E_RECOMPILAR.md).

---

## Método de trabalho

O projeto é conduzido por **desenvolvimento orientado a especificação**: `spec/`
define o quê, `design/` define o como, e o código vem depois. Quando a inspeção
dos dados contradiz uma premissa, a spec é corrigida e a correção fica
registrada — em vez de o documento ser silenciosamente reescrito.

Ferramentas de IA são usadas na condução do trabalho sob política explícita,
documentada em [`docs/AI_USAGE_POLICY.md`](docs/AI_USAGE_POLICY.md). Todo
resultado numérico afirmado é verificável por script neste repositório.

---

## Referências principais

- Schierholz, M. *et al.* **SI/PI-Database of PCB-Based Interconnects for
  Machine Learning Applications.** IEEE Access, 2021.
  [doi:10.1109/ACCESS.2021.3065252](https://doi.org/10.1109/ACCESS.2021.3065252)
- Hillebrecht, T. *et al.* **Generation and Application of a Very Large Dataset
  for Signal Integrity Via Array and Link Analysis.** IEEE Transactions on
  Electromagnetic Compatibility, 2024.
  [doi:10.1109/TEMC.2024.3450307](https://doi.org/10.1109/TEMC.2024.3450307)
- Raissi, M.; Perdikaris, P.; Karniadakis, G. E. **Physics-informed neural
  networks.** Journal of Computational Physics, 2019.
  [doi:10.1016/j.jcp.2018.10.045](https://doi.org/10.1016/j.jcp.2018.10.045)
- Torun, H. M. *et al.* **A Spectral Convolutional Net for Co-Optimization of
  Integrated Voltage Regulators and Embedded Inductors.** IEEE, 2020.

A lista completa está em [`proposta/referencias.bib`](proposta/referencias.bib).

---

## Licença

- **Código e documentação deste repositório:** MIT (ver [`LICENSE`](LICENSE)).
- **SI/PI-Database:** licenciada pela TUHH, **não incluída aqui**. Ao usá-la,
  cite os artigos originais e respeite os termos de uso da fonte.
- **Artigos de terceiros e o Manual de Normalização da UFPR** consultados durante
  o trabalho não são redistribuídos neste repositório.
