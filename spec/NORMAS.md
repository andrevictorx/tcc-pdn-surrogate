# Spec: curvas-limite de emissão irradiada (camada normativa)

**Criado em:** 2026-10-24 · **Dados:** `data/normas/limites_emissao_irradiada.csv` · **Código:** `src/normas/limites.py`
**Relaciona-se com:** objetivo do TCC (margem normativa em dB, afirmação **ordinal**, nunca certificação)

## Fontes

| Norma | Edição | Tabela | Escopo |
|---|---|---|---|
| CISPR 32 | 2.0 (2015) | A.2 (classe A) e A.4 (classe B): emissão irradiada até 1 GHz | equipamentos multimídia |
| IEC 61000-6-3 | 3.0 (2020) | Tabela 3: emissão irradiada, porta de gabinete | norma genérica, ambiente residencial, comercial e de indústria leve |
| IEC 61000-6-4 | 3.0 (2018) | Tabela 3: emissão irradiada, porta de gabinete | norma genérica, ambiente industrial |

Os PDFs ficam fora do repositório (`.gitignore`), por direito autoral. Só os valores numéricos dos limites são
versionados, com a cláusula de origem de cada linha.

## Limites de 30 MHz a 1 GHz, detector de quase-pico, em dB(µV/m)

| Norma | Cláusula | Classe / ambiente | Instalação | Distância | 30–230 MHz | 230–1000 MHz |
|---|---|---|---|---|---|---|
| CISPR 32 | A4.1 | B | OATS/SAC | 10 m | 30 | 37 |
| CISPR 32 | A4.2 | B | OATS/SAC | 3 m | 40 | 47 |
| CISPR 32 | A4.3 | B | FAR | 10 m | 32 → 25 | 32 |
| CISPR 32 | A4.4 | B | FAR | 3 m | 42 → 35 | 42 |
| CISPR 32 | A2.1 | A | OATS/SAC | 10 m | 40 | 47 |
| CISPR 32 | A2.2 | A | OATS/SAC | 3 m | 50 | 57 |
| CISPR 32 | A2.3 | A | FAR | 10 m | 42 → 35 | 42 |
| CISPR 32 | A2.4 | A | FAR | 3 m | 52 → 45 | 52 |
| IEC 61000-6-3 | 3.1 | residencial | OATS/SAC | 10 m | 30 | 37 |
| IEC 61000-6-3 | 3.3 | residencial | FAR | 3 m | 42 → 35 | 42 |
| IEC 61000-6-4 | 3.1 | industrial | OATS/SAC | 10 m | 40 | 47 |
| IEC 61000-6-4 | 3.3 | industrial | FAR | 3 m | 52 → 45 | 52 |

OATS: área de teste aberta; SAC: câmara semianecoica; FAR: câmara totalmente anecoica. "42 → 35": o limite cai de 42
para 35 dB(µV/m) entre 30 e 230 MHz.

## Regras de leitura (requisitos gerais de emissão das IEC 61000-6-3:2020 e 6-4:2018)

1. Onde o limite varia numa faixa, ele muda **linearmente com o logaritmo da frequência**.
2. Na frequência de transição entre faixas (230 MHz), **vale o limite mais baixo**.
3. Uma única cláusula se aplica em toda a faixa: não se combinam linhas de instalações ou distâncias diferentes.

## Relações entre as normas (verificadas nos testes)

- **Classe B da CISPR 32 = IEC 61000-6-3** e **classe A = IEC 61000-6-4**, linha a linha, nas cláusulas comuns.
- **A classe A fica 10 dB acima da classe B** em toda a banda.
- **3 m fica 10 dB acima de 10 m.** As normas adotam 10 dB, e não $20\log_{10}(10/3) = 10{,}5$ dB.

## Escolha de referência para a camada normativa do TCC

| Papel | Linha | Por quê |
|---|---|---|
| **Principal** | CISPR 32 classe B, OATS/SAC a 10 m (A4.1) ≡ IEC 61000-6-3, 3.1 | a mais restritiva, a geométrica de referência das normas genéricas e plana por faixa, o que simplifica a margem |
| Sensibilidade | CISPR 32 classe A, A2.1 ≡ IEC 61000-6-4, 3.1 | ambiente industrial; mesma forma, 10 dB acima. **Não altera nenhum ranking**: a diferença é uma constante |

Como a diferença entre classe A e classe B é uma constante de 10 dB, a escolha da classe só desloca a margem e não
muda a ordenação de projetos. A escolha da instalação (FAR × OATS) muda a forma da curva entre 30 e 230 MHz e, por
isso, pode mudar rankings: deve ser reportada como sensibilidade, se for usada.

## O que esta spec não cobre

- **Emissão conduzida** e **irradiada acima de 1 GHz**: fora da banda simulada da SI/PI-Database (1 MHz–1 GHz).
- **O modelo $Z(f)$ → corrente de ruído → emissão irradiada em dB(µV/m)**, que é a outra metade da camada normativa e
  fica para o TCC II. A margem só tem sentido **ordinal**: compara projetos entre si, sob o mesmo modelo de excitação e
  de irradiação. Não substitui ensaio em laboratório acreditado nem declara conformidade.
