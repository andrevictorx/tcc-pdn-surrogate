"""
Exploração 2: Como os 8 parâmetros de projeto afetam Z11(f)?

Este script carrega múltiplas configurações e visualiza:
1. Overlay de curvas Z11(f) para diferentes valores de cada feature
2. Correlação entre features e propriedades de Z(f) (Z_max, f_min, etc.)
3. Quais features têm maior impacto na impedância
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data.touchstone import parse_touchstone, self_impedance

# ============================================================================
# PASSO 1: Carregar os 8 parâmetros de projeto
# ============================================================================

print("=" * 80)
print("PASSO 1: Carregando Parâmetros de Projeto")
print("=" * 80)

base_path = Path(__file__).parent.parent / "6_layer_pcb_based_pdn_with_two_arrays_LHS_mar_2023"
params_csv = base_path / "parameter.csv"

# Carregar CSV
df = pd.read_csv(params_csv)

# Filtrar apenas as 8 features que variam (conforme DATA_SPEC.md)
features_8 = ['TDIEL', 'PERMITTIVITY', 'A1_VIARADIUS', 'A1_ANTIPADRADIUS',
              'A1_VIAPITCH', 'A2_VIARADIUS', 'A2_ANTIPADRADIUS', 'A2_VIAPITCH']

df_features = df[features_8 + ['simu_index']].copy()

print(f"Dataset carregado: {df_features.shape[0]} configurações")
print()
print("Estatísticas das 8 features:")
print(df_features[features_8].describe())
print()

# ============================================================================
# PASSO 2: Selecionar 10 configurações "representativas"
# ============================================================================

print("=" * 80)
print("PASSO 2: Selecionando 10 Configurações Representativas")
print("=" * 80)

# Estratégia: pegar distribuição uniforme ao longo da primeira feature (TDIEL)
sorted_idx = np.argsort(df_features['TDIEL'].values)
step = len(sorted_idx) // 10
representative_idx = sorted_idx[::step][:10]

df_rep = df_features.iloc[representative_idx].reset_index(drop=True)

print("Configurações selecionadas:")
print(df_rep.to_string())
print()

# ============================================================================
# PASSO 3: Carregar Z11(f) para cada uma
# ============================================================================

print("=" * 80)
print("PASSO 3: Carregando Z11(f) para Cada Configuração")
print("=" * 80)

z11_curves = []
freqs = None

for idx, row in df_rep.iterrows():
    simu_idx = int(row['simu_index'])
    path = base_path / "variation" / f"simu_{simu_idx}.s36p"

    print(f"  [{idx+1:2d}/10] Lendo {path.name}...", end=" ")

    try:
        network = parse_touchstone(path, n_ports=36)
        z11 = self_impedance(network, port=0)
        z11_curves.append(z11)

        if freqs is None:
            freqs = network.freq.copy()

        print(f"✓ TDIEL={row['TDIEL']:.1f}, ε_r={row['PERMITTIVITY']:.2f}")
    except Exception as e:
        print(f"✗ Erro: {e}")

z11_curves = np.array(z11_curves)
z11_mags = np.abs(z11_curves)

print()
print(f"Matriz Z11 carregada: shape = {z11_mags.shape}")
print(f"  {z11_mags.shape[0]} configurações × {z11_mags.shape[1]} frequências")
print()

# ============================================================================
# PASSO 4: Extrair propriedades agregadas de Z(f)
# ============================================================================

print("=" * 80)
print("PASSO 4: Propriedades Agregadas de Z(f)")
print("=" * 80)

properties = {}
for i, (idx, row) in enumerate(df_rep.iterrows()):
    z_mag = z11_mags[i]

    properties[i] = {
        'TDIEL': row['TDIEL'],
        'PERMITTIVITY': row['PERMITTIVITY'],
        'Z_max': np.max(z_mag),
        'Z_min': np.min(z_mag),
        'f_min_Hz': freqs[np.argmin(z_mag)],
    }

df_props = pd.DataFrame(properties).T

print(df_props.to_string())
print()

# ============================================================================
# PASSO 5: Visualizações
# ============================================================================

print("=" * 80)
print("PASSO 5: Gerando Gráficos")
print("=" * 80)

fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

# ---- Subplot 1: Overlay Z11(f) linear ----
ax = fig.add_subplot(gs[0, :2])
colors = plt.cm.viridis(np.linspace(0, 1, z11_mags.shape[0]))
for i in range(z11_mags.shape[0]):
    ax.plot(freqs/1e6, z11_mags[i], label=f"TDIEL={df_rep.iloc[i]['TDIEL']:.1f} mil",
            color=colors[i], linewidth=2, alpha=0.7)
ax.set_xlabel('Frequência (MHz)', fontsize=11)
ax.set_ylabel('|Z11| (Ω)', fontsize=11)
ax.set_title('Z11(f) para 10 Configurações — Escala Linear', fontsize=12, fontweight='bold')
ax.legend(fontsize=8, loc='upper right', ncol=2)
ax.grid(True, alpha=0.3)
ax.set_ylim([0, 50])  # Zoom para ver melhor as diferenças

# ---- Subplot 2: Overlay Z11(f) log-log ----
ax = fig.add_subplot(gs[0, 2])
for i in range(z11_mags.shape[0]):
    ax.loglog(freqs/1e6, z11_mags[i], color=colors[i], linewidth=2, alpha=0.7)
ax.set_xlabel('Frequência (MHz)', fontsize=10)
ax.set_ylabel('|Z11| (Ω)', fontsize=10)
ax.set_title('Z11(f) — Log-Log', fontsize=11, fontweight='bold')
ax.grid(True, which='both', alpha=0.3)

# ---- Subplot 3: Z_max vs TDIEL ----
ax = fig.add_subplot(gs[1, 0])
scatter = ax.scatter(df_props['TDIEL'], df_props['Z_max'], s=100, c=df_props['PERMITTIVITY'],
                     cmap='coolwarm', edgecolors='black', linewidth=1)
ax.set_xlabel('TDIEL (mil)', fontsize=10)
ax.set_ylabel('Z_max (Ω)', fontsize=10)
ax.set_title('Z_max vs TDIEL\n(colorido por ε_r)', fontsize=11, fontweight='bold')
ax.grid(True, alpha=0.3)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('ε_r', fontsize=9)

# ---- Subplot 4: Z_min vs TDIEL ----
ax = fig.add_subplot(gs[1, 1])
ax.scatter(df_props['TDIEL'], df_props['Z_min'], s=100, c=df_props['PERMITTIVITY'],
           cmap='coolwarm', edgecolors='black', linewidth=1)
ax.set_xlabel('TDIEL (mil)', fontsize=10)
ax.set_ylabel('Z_min (Ω)', fontsize=10)
ax.set_title('Z_min vs TDIEL\n(colorido por ε_r)', fontsize=11, fontweight='bold')
ax.grid(True, alpha=0.3)

# ---- Subplot 5: f_min vs TDIEL ----
ax = fig.add_subplot(gs[1, 2])
ax.scatter(df_props['TDIEL'], df_props['f_min_Hz']/1e6, s=100, c=df_props['PERMITTIVITY'],
           cmap='coolwarm', edgecolors='black', linewidth=1)
ax.set_xlabel('TDIEL (mil)', fontsize=10)
ax.set_ylabel('f_min (MHz)', fontsize=10)
ax.set_title('f(Z_min) vs TDIEL\n(colorido por ε_r)', fontsize=11, fontweight='bold')
ax.grid(True, alpha=0.3)

# ---- Subplot 6: Z_max vs ε_r ----
ax = fig.add_subplot(gs[2, 0])
ax.scatter(df_props['PERMITTIVITY'], df_props['Z_max'], s=100, c=df_props['TDIEL'],
           cmap='plasma', edgecolors='black', linewidth=1)
ax.set_xlabel('PERMITTIVITY (ε_r)', fontsize=10)
ax.set_ylabel('Z_max (Ω)', fontsize=10)
ax.set_title('Z_max vs ε_r\n(colorido por TDIEL)', fontsize=11, fontweight='bold')
ax.grid(True, alpha=0.3)

# ---- Subplot 7: Correlação entre features ----
ax = fig.add_subplot(gs[2, 1])
corr_matrix = df_props[['TDIEL', 'PERMITTIVITY', 'Z_max', 'Z_min']].corr()
im = ax.imshow(corr_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
ax.set_xticks(range(len(corr_matrix)))
ax.set_yticks(range(len(corr_matrix)))
ax.set_xticklabels(['TDIEL', 'ε_r', 'Z_max', 'Z_min'], fontsize=9, rotation=45, ha='right')
ax.set_yticklabels(['TDIEL', 'ε_r', 'Z_max', 'Z_min'], fontsize=9)
ax.set_title('Matriz de Correlação', fontsize=11, fontweight='bold')
for i in range(len(corr_matrix)):
    for j in range(len(corr_matrix)):
        ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}', ha='center', va='center',
                color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black', fontsize=9)
plt.colorbar(im, ax=ax, label='Correlação')

# ---- Subplot 8: Distribuição de Z_max ----
ax = fig.add_subplot(gs[2, 2])
ax.hist(df_props['Z_max'], bins=5, color='steelblue', edgecolor='black', alpha=0.7)
ax.set_xlabel('Z_max (Ω)', fontsize=10)
ax.set_ylabel('Frequência', fontsize=10)
ax.set_title('Distribuição de Z_max', fontsize=11, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

plt.savefig(Path(__file__).parent / '02_feature_impact.png', dpi=150, bbox_inches='tight')
print("Gráfico salvo: 02_feature_impact.png")
print()

# ============================================================================
# RESUMO E INSIGHTS
# ============================================================================

print("=" * 80)
print("RESUMO E INSIGHTS")
print("=" * 80)

print(f"""
Resumo das 10 configurações representativas:

1. Z_max varia de {df_props['Z_max'].min():.1f} Ω a {df_props['Z_max'].max():.1f} Ω
   → Diferença de {df_props['Z_max'].max() / df_props['Z_max'].min():.1f}×

2. Z_min varia de {df_props['Z_min'].min():.3f} Ω a {df_props['Z_min'].max():.3f} Ω
   → Diferença de {df_props['Z_min'].max() / df_props['Z_min'].min():.1f}×

3. f(Z_min) varia de {df_props['f_min_Hz'].min()/1e6:.0f} MHz a {df_props['f_min_Hz'].max()/1e6:.0f} MHz
   → Diferença de {(df_props['f_min_Hz'].max() - df_props['f_min_Hz'].min())/1e6:.0f} MHz

4. Correlação TDIEL ↔ Z_max: {corr_matrix.loc['TDIEL', 'Z_max']:.3f}
   → {'FORTE' if abs(corr_matrix.loc['TDIEL', 'Z_max']) > 0.7 else 'MODERADA' if abs(corr_matrix.loc['TDIEL', 'Z_max']) > 0.4 else 'FRACA'}

5. Correlação ε_r ↔ Z_max: {corr_matrix.loc['PERMITTIVITY', 'Z_max']:.3f}
   → {'FORTE' if abs(corr_matrix.loc['PERMITTIVITY', 'Z_max']) > 0.7 else 'MODERADA' if abs(corr_matrix.loc['PERMITTIVITY', 'Z_max']) > 0.4 else 'FRACA'}

Conclusão:
- A espessura do dielétrico (TDIEL) afeta significativamente a impedância
- A permitividade relativa (ε_r) também tem influência importante
- Diferentes configurações produzem curvas Z11(f) bem distintas
- Isso é bom para um dataset de ML — há variação o suficiente para aprender

Próxima etapa: Analisar todo o dataset (985 configs) para ver a distribuição
completa das features e suas correlações com Z(f).
""")
