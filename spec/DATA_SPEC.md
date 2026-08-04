# Spec: Extração de impedância a partir de arquivos Touchstone

**Versão:** 2.0
**Data:** 2026-08-01
**Substitui:** premissas de dados em `RESEARCH_BRIEF.md` v1.0 (ver seção "Correções")
**Status:** parcialmente implementado e verificado sobre 40 configurações

---

## Correções sobre a v1.0

A v1.0 deste projeto assumia fatos que a inspeção direta dos arquivos refutou.
Registrados aqui para que não sejam reintroduzidos:

| Premissa v1.0 | Fato verificado |
|---|---|
| 13 features de entrada | **8** parâmetros variam; 9 dos 17 são constantes |
| alvo = escalar `Z_max` | alvo = **curva** `Z11(f)` com 334 pontos; `Z_max` é derivado |
| dataset "986 configs" | **985** configurações (986 linhas do CSV incluem o cabeçalho) |
| — | espaçamento em frequência é **linear** (3 MHz), não logarítmico |
| — | 24 GB descompactados; 24 MB por arquivo `.s36p` |
| âncora modal utilizável | modos **não observáveis** em `Z11` nesta banda (ver `PHYSICS_SPEC.md`) |

---

## Escopo

Converter os arquivos Touchstone do subconjunto *6-Layer PCB based PDN with Two
Via Arrays* em um conjunto tabular pronto para treinamento.

## Entradas

| Item | Formato | Observação |
|---|---|---|
| `parameter.csv` | CSV, 985 linhas + cabeçalho | 17 colunas + `simu_index` |
| `variation/simu_<idx>.s36p` | Touchstone v1.1 | `# Hz S RI R 50.00`, 36 portas, 334 frequências |

**Unidades.** Dimensões geométricas em **mil** (1 mil = 25,4 µm). Hipótese
sustentada por dois indícios (ver `PHYSICS_SPEC.md`), pendente de confirmação
junto aos mantenedores da base. Todo código deve converter para SI na fronteira
de entrada e operar exclusivamente em SI internamente.

### Parâmetros que variam (as 8 features)

| Coluna | Grandeza | Mín | Máx | Níveis |
|---|---|---|---|---|
| `TDIEL` | espessura do dielétrico | 3,12 | 78,99 | 984 |
| `PERMITTIVITY` | ε_r | 2,50 | 4,50 | 984 |
| `A1_VIARADIUS` | raio da via, arranjo 1 | 10 | 20 | 11 |
| `A1_ANTIPADRADIUS` | raio do antipad, arranjo 1 | 20 | 39 | 20 |
| `A1_VIAPITCH` | passo do arranjo 1 | 80 | 120 | 9 |
| `A2_VIARADIUS` | raio da via, arranjo 2 | 10 | 20 | 11 |
| `A2_ANTIPADRADIUS` | raio do antipad, arranjo 2 | 20 | 39 | 20 |
| `A2_VIAPITCH` | passo do arranjo 2 | 80 | 120 | 9 |

### Parâmetros constantes (não são features — não alimentar o modelo)

`TMET` = 1 mil · `XWIDTH` = 5800 mil · `YWIDTH` = 4000 mil ·
`CONDUCTIVITY` = 5,8e7 S/m · `LOSSTANGENT` = 0,01 ·
`A1_XCENTER` = 2900 · `A1_YCENTER` = 2000 · `A2_XCENTER` = 3900 ·
`A2_YCENTER` = 3000

> Qualquer conclusão do trabalho está condicionada a esses valores fixos e não
> pode ser extrapolada para outros.

## Saídas

| Artefato | Formato | Conteúdo |
|---|---|---|
| `data/processed/pdn6.parquet` | Parquet | 985 × (8 features + metadados) |
| `data/processed/pdn6_z.npy` | `float32[985, 334]` | `log10 |Z11(f)|` |
| `data/processed/pdn6_freq.npy` | `float64[334]` | grade de frequência em Hz |
| `data/processed/manifest.json` | JSON | sementes, checksums, versão do código |

## Contratos de função

```
parse_touchstone(path, n_ports) -> (freq: float64[nf], S: complex128[nf, P, P])
```
- `freq` estritamente crescente, em Hz
- `S` adimensional
- **erro** se o número de valores não for divisível por `1 + 2·P²`

```
s_to_z(S, z0=50.0) -> Z: complex128[nf, P, P]
```
- `Z = sqrt(Z0) (I + S)(I - S)⁻¹ sqrt(Z0)`, em ohms
- implementar por `solve`, nunca por `inv` explícita

## Invariantes verificáveis

| # | Invariante | Tolerância |
|---|---|---|
| I1 | `S` simétrica (reciprocidade) | `atol=1e-6` |
| I2 | valores singulares de `S` ≤ 1 (passividade) | `atol=1e-6` |
| I3 | `Re{Z_ii} ≥ 0` ∀ f, ∀ i (passividade) | `atol=1e-9` |
| I4 | `freq` estritamente crescente | exato |
| I5 | `nf == 334`, `P == 36` | exato |
| I6 | inclinação log-log de `|Z11|` abaixo de 25 MHz ∈ [−1,05; −0,95] | ver PHYSICS_SPEC |

## Critérios de aceitação

- [ ] as 985 configurações são processadas sem exceção
- [ ] I1–I6 verificadas em amostra aleatória de ≥ 40 configurações com semente fixa
- [ ] tempo total da passagem única < 10 min em CPU
- [ ] volume do artefato processado < 100 MB (redução ≥ 200×)
- [ ] reexecução com a mesma semente produz arquivos byte-idênticos

## Riscos

1. **Unidades** — mitigado por I6 e por verificação de ordem de grandeza da
   capacitância; confirmação pendente com os mantenedores.
2. **Subamostragem da primeira década** — 4 pontos entre 1 e 10 MHz contra >300
   entre 100 MHz e 1 GHz. Toda métrica de erro deve ser **ponderada por década**.
3. **Volume** — não carregar a base bruta inteira em memória; processar por
   streaming, um arquivo por vez.
