# Spec: definição operacional de |Z|max

**Decidido em:** 2026-10-24 · **Implementação:** `src/data/alvos.py` · **Relaciona-se com:** portão C10 de
`spec/CONSISTENCIA_DADOS.md`, item V13 de `spec/PLANO_VALIDACAO.md`

## Problema

$\lvert Z\rvert_{\max}$ é a impedância no extremo capacitivo da banda, 1 MHz. Nos subconjuntos multicamadas (PI-2, PI-3
e PI-4), o ponto de 1 MHz tem uma anomalia: parte real 7 a 13 vezes maior que a perda dielétrica, e $\lvert Z\rvert$ fora
da curva capacitiva em até mais de 10 % (C10). Usar o valor bruto põe essa anomalia no alvo dos modelos.

## Decisão

| Papel | Definição | Função |
|---|---|---|
| **Principal** | **Extrapolação capacitiva sem o ponto de 1 MHz.** $C$ é a mediana de $C_i = (1-(f_i/f_0)^2)/(-2\pi f_i\,\mathrm{Im}\{Z_i\})$ sobre os pontos da janela $f < f_0/3$, **exceto o primeiro**, com $f_0$ = 1º mínimo local. Então $\lvert Z\rvert_{\max} = (1-(f_{\rm ref}/f_0)^2)/(2\pi f_{\rm ref}C)$, com $f_{\rm ref} = 1$ MHz | `zmax_extrapolado` |
| Sensibilidade | $\lvert Z\rvert$ interpolado em log–log em **4,34 MHz**, o segundo ponto da grade do PI-1, que cai entre o 2º e o 3º ponto da grade dos demais | `zmax_4mhz` |

Toda métrica de modelo que use $\lvert Z\rvert_{\max}$ é reportada com a definição principal; a de sensibilidade é
reportada ao lado, em tabela própria.

## Por que a extrapolação é a principal

1. **Usa a lei validada.** A forma $\lvert Z\rvert = (1-(f/f_0)^2)/(2\pi f C)$ passou no V6 de `spec/PLANO_VALIDACAO.md`,
   com resíduo < 0,01 na inclinação, nos quatro subconjuntos.
2. **Mantém o significado físico e a comparação com a literatura.** O alvo continua sendo a impedância em 1 MHz, a mesma
   grandeza de Schierholz, Hassab e Schuster (2023).
3. **É comparável entre subconjuntos.** Em 4,34 MHz o PI-1 já está perto do nulo de série (mediana de 24 MHz), e o valor
   medido ali sai 3 % abaixo da curva capacitiva pura, por efeito do LC série. A extrapolação corrige esse efeito; o
   ponto fixo não. Isso importa na união dos subconjuntos.

## Medições que sustentam a decisão

| Subconjunto | Extrapolado / bruto em 1 MHz | Curvas com desvio > 5 % | ρ (extrapolado × 4,34 MHz) | Extrapolado em 4,34 MHz / medido |
|---|---|---|---|---|
| PI-4 | 0,982 | 1,1 % | 1,0000 | 1,001 |
| PI-3 | 0,974 | 24,4 % | 1,0000 | 1,004 |
| PI-2 | 0,978 | 25,5 % | 1,0000 | 1,001 |
| PI-1 | 0,997 | 0,0 % | 0,9999 | 1,030 |

**A escolha não muda nenhum ranking dentro de um subconjunto** (ρ ≥ 0,9999). Como a margem normativa do TCC é ordinal,
a decisão afeta os valores absolutos e a união dos subconjuntos, mas não a ordenação de projetos.

## Limitação

No PI-1, a janela sem o ponto de 1 MHz tem mediana de 2 pontos e, em alguns casos, 1. Quando sobra só um ponto, $C$
vem dele, ainda com a correção do LC série. Isso já é robusto: o PI-1 não tem a anomalia de 1 MHz (desvio mediano de
0,1 %).
