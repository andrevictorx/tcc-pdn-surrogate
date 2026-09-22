"""
Exploração 1: Como funciona o arquivo Touchstone e a conversão para impedância

Este script desconstrói a leitura de um arquivo .s36p:
1. O que é um arquivo Touchstone
2. Como ler S-parameters
3. Como converter S para Z (impedância)
4. Como visualizar a curva Z11(f)
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Importar o módulo de leitura Touchstone do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data.touchstone import parse_touchstone, s_to_z, self_impedance

# ============================================================================
# PASSO 1: Localizar um arquivo exemplo
# ============================================================================

base_path = Path(__file__).parent.parent / "6_layer_pcb_based_pdn_with_two_arrays_LHS_mar_2023"
example_file = base_path / "variation" / "simu_1000.s36p"

print("=" * 80)
print("PASSO 1: Arquivo Touchstone Exemplo")
print("=" * 80)
print(f"Caminho: {example_file}")
print(f"Tamanho: {example_file.stat().st_size / 1e6:.1f} MB")
print()

# ============================================================================
# PASSO 2: Ver o conteúdo bruto (primeiras 50 linhas)
# ============================================================================

print("=" * 80)
print("PASSO 2: Conteúdo Bruto do Arquivo (primeiras 30 linhas)")
print("=" * 80)

with open(example_file) as f:
    lines = [f.readline() for _ in range(30)]
    for i, line in enumerate(lines):
        print(f"{i+1:3d}: {line.rstrip()}")

print("\n[...arquivo continua...]")
print()

# ============================================================================
# PASSO 3: Entender o formato
# ============================================================================

print("=" * 80)
print("PASSO 3: O Que Significa?")
print("=" * 80)
print("""
Formato Touchstone v1.1:

1. Linhas começadas com '#' são metadados:
   # Hz S RI R 50.00

   Hz     = frequência em Hertz
   S      = parâmetros de espalhamento (S-parameters)
   RI     = formato Real-Imaginário (não logarítmico)
   R 50   = impedância de referência = 50 Ω

2. Parâmetros S (S-parameters):
   - Descrevem como ondas eletromagnéticas se comportam em um circuito
   - S11 = reflexão na porta 1
   - S12 = transmissão de porta 1 → porta 2
   - Adimensional (razão de amplitudes de onda)
   - Complexos (real + imaginário)

3. Formato das linhas de dados:
   Para cada frequência, temos P² elementos (P = número de portas):
   freq  Re(S11) Im(S11) Re(S12) Im(S12) ... Re(Spp) Im(Spp)

   Nosso arquivo tem 36 portas → 36² = 1296 parâmetros S por frequência
   + 1 frequência = 1297 números por linha (mas quebrados em múltiplas linhas)

4. Número de frequências:
   Com 334 frequências e 36 portas:
   Total de valores = 334 × (1 + 2 × 36²) = 334 × 2593 ≈ 865k números
""")
print()

# ============================================================================
# PASSO 4: Ler com parse_touchstone
# ============================================================================

print("=" * 80)
print("PASSO 4: Lendo com parse_touchstone()")
print("=" * 80)

network = parse_touchstone(example_file, n_ports=36)

print(f"Frequências carregadas: {network.n_freq} pontos")
print(f"Faixa de frequência: {network.freq[0]/1e6:.1f} MHz → {network.freq[-1]/1e9:.1f} GHz")
print(f"Espaçamento: {(network.freq[1] - network.freq[0])/1e6:.1f} MHz (linear)")
print()

print(f"Matriz S (S-parameters):")
print(f"  Shape: {network.s.shape}")
print(f"  Tipo: {network.s.dtype}")
print(f"  = {network.n_freq} frequências × {network.n_ports} portas × {network.n_ports} portas (matriz quadrada)")
print()

# ============================================================================
# PASSO 5: Entender um elemento S específico
# ============================================================================

print("=" * 80)
print("PASSO 5: Um Elemento S Específico")
print("=" * 80)

# Pega S11 (reflexão na porta 1) em várias frequências
s11 = network.s[:, 0, 0]

print(f"S11 (reflexão na porta 1):")
print(f"  Shape: {s11.shape} (1 valor por frequência)")
print()
print("Primeiras 5 valores de S11:")
for i in range(5):
    f = network.freq[i]
    s = s11[i]
    print(f"  f = {f/1e6:7.1f} MHz: S11 = {s.real:+.6f} {s.imag:+.6f}j")
print()

# ============================================================================
# PASSO 6: Converter S para Z (impedância)
# ============================================================================

print("=" * 80)
print("PASSO 6: Convertendo S → Z (Impedância)")
print("=" * 80)

z_matrix = s_to_z(network)

print(f"Matriz Z (impedância):")
print(f"  Shape: {z_matrix.shape}")
print(f"  Tipo: {z_matrix.dtype}")
print(f"  Unidade: Ohms (Ω)")
print()

print("A fórmula de conversão (Teoria de Circuitos):")
print("  Z = Z0 (I + S)(I - S)⁻¹")
print("  onde:")
print("    I = matriz identidade")
print("    Z0 = impedância de referência (50 Ω)")
print("    S = matriz de parâmetros de espalhamento")
print()

# ============================================================================
# PASSO 7: Extrair Z11(f) — autoimpedância na porta 1
# ============================================================================

print("=" * 80)
print("PASSO 7: Autoimpedância Z11(f)")
print("=" * 80)

z11 = self_impedance(network, port=0)

print(f"Z11 (autoimpedância da porta 1):")
print(f"  Shape: {z11.shape} (1 valor por frequência)")
print(f"  Tipo: {z11.dtype}")
print()

print("Primeiras 5 valores:")
for i in range(5):
    f = network.freq[i]
    z = z11[i]
    magnitude = np.abs(z)
    phase = np.angle(z, deg=True)
    print(f"  f = {f/1e6:7.1f} MHz: Z11 = {z.real:+8.3f} {z.imag:+8.3f}j Ω  " +
          f"(|Z| = {magnitude:8.3f} Ω, ∠ {phase:+7.1f}°)")
print()

print("Magnitude e fase de Z11:")
z11_mag = np.abs(z11)
z11_phase = np.angle(z11, deg=True)
print(f"  |Z11| mín = {z11_mag.min():.3f} Ω @ f = {network.freq[z11_mag.argmin()]/1e6:.1f} MHz")
print(f"  |Z11| máx = {z11_mag.max():.3f} Ω @ f = {network.freq[z11_mag.argmax()]/1e6:.1f} MHz")
print()

# ============================================================================
# PASSO 8: Verificar invariantes físicas
# ============================================================================

print("=" * 80)
print("PASSO 8: Invariantes Físicas (Verificações de Qualidade)")
print("=" * 80)

from src.data.touchstone import check_invariants

invariants = check_invariants(network)

print("Checksum físico (para garantir que os dados fazem sentido):")
for name, passed in invariants.items():
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status}: {name}")
print()

# ============================================================================
# PASSO 9: Plotar Z11(f)
# ============================================================================

print("=" * 80)
print("PASSO 9: Visualização Gráfica")
print("=" * 80)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Subplot 1: |Z11| em escala linear
ax = axes[0, 0]
ax.plot(network.freq / 1e6, z11_mag, linewidth=2, color='navy')
ax.set_xlabel('Frequência (MHz)', fontsize=11)
ax.set_ylabel('|Z11| (Ω)', fontsize=11)
ax.set_title('Magnitude de Z11 — Escala Linear', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

# Subplot 2: |Z11| em escala log-log
ax = axes[0, 1]
ax.loglog(network.freq / 1e6, z11_mag, linewidth=2, color='darkgreen')
ax.set_xlabel('Frequência (MHz)', fontsize=11)
ax.set_ylabel('|Z11| (Ω)', fontsize=11)
ax.set_title('Magnitude de Z11 — Escala Log-Log', fontsize=12, fontweight='bold')
ax.grid(True, which='both', alpha=0.3)

# Subplot 3: Fase de Z11
ax = axes[1, 0]
ax.plot(network.freq / 1e6, z11_phase, linewidth=2, color='darkred')
ax.set_xlabel('Frequência (MHz)', fontsize=11)
ax.set_ylabel('∠Z11 (graus)', fontsize=11)
ax.set_title('Fase de Z11', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

# Subplot 4: Componentes real e imaginária
ax = axes[1, 1]
ax.plot(network.freq / 1e6, z11.real, linewidth=2, label='Re{Z11}', color='blue')
ax.plot(network.freq / 1e6, z11.imag, linewidth=2, label='Im{Z11}', color='red')
ax.set_xlabel('Frequência (MHz)', fontsize=11)
ax.set_ylabel('Impedância (Ω)', fontsize=11)
ax.set_title('Componentes Real e Imaginária de Z11', fontsize=12, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(Path(__file__).parent / '01_z11_analysis.png', dpi=150, bbox_inches='tight')
print("Gráfico salvo: 01_z11_analysis.png")
print()

# ============================================================================
# PASSO 10: Características Principais (Ressonâncias, Anti-ressonâncias)
# ============================================================================

print("=" * 80)
print("PASSO 10: Características Principais de Z11(f)")
print("=" * 80)

# Encontrar mínimo (anti-ressonância, "null of series")
idx_min = z11_mag.argmin()
f_min = network.freq[idx_min]
z_min = z11_mag[idx_min]

print(f"Mínimo de |Z11| (nulo de série / anti-ressonância):")
print(f"  Frequência: {f_min/1e6:.1f} MHz")
print(f"  Magnitude: {z_min:.3f} Ω")
print()

# Verificar inclinação em baixa frequência (deve ser -1 para capacitivo puro)
from src.data.touchstone import low_frequency_slope

slope = low_frequency_slope(network.freq, z11_mag)
print(f"Inclinação log-log de |Z11| em baixa frequência (< 25 MHz):")
print(f"  Slope = {slope:.3f}")
print(f"  Esperado: ≈ -1.0 para comportamento capacitivo puro")
print(f"  Status: {'✓ PASS' if -1.05 < slope < -0.95 else '✗ Fora do esperado'}")
print()

print("=" * 80)
print("RESUMO")
print("=" * 80)
print(f"""
Você acaba de:
1. Ler um arquivo Touchstone (.s36p) com 36 portas e 334 frequências
2. Entender que ele contém S-parameters (parâmetros de espalhamento)
3. Converter S-parameters em matriz Z (impedância) usando álgebra linear
4. Extrair Z11(f) — a autoimpedância da PDN vista por uma porta
5. Visualizar a curva característica de uma PDN:
   - Comportamento capacitivo em baixa freq (Z ∝ 1/f)
   - Nulo de série ("anti-ressonância") por volta de {f_min/1e6:.0f} MHz
   - Resposta complexa em frequência maior

Próxima etapa: Repetir para todos os 985 arquivos e comparar como os
parâmetros de projeto (TDIEL, ε_r, raio de vias, etc.) afetam Z11(f).
""")
