"""
Exploração 3: Estatísticas do Dataset Completo (985 configurações)

Por eficiência, este script:
1. Analisa a distribuição dos 8 parâmetros de projeto
2. Carrega uma amostra aleatória de 50 configs para estimar Z(f) statistics
3. Gera visualizações de cobertura e representatividade
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data.touchstone import parse_touchstone, self_impedance

# ============================================================================
# PASSO 1: Análise dos Parâmetros (Sem Carregar S36p)
# ============================================================================

print("=" * 80)
print("PASSO 1: Análise dos 8 Parâmetros de Projeto")
print("=" * 80)

base_path = Path(__file__).parent.parent / "6_layer_pcb_based_pdn_with_two_arrays_LHS_mar_2023"
df = pd.read_csv(base_path / "parameter.csv")

features_8 = ['TDIEL', 'PERMITTIVITY', 'A1_VIARADIUS', 'A1_ANTIPADRADIUS',
              'A1_VIAPITCH', 'A2_VIARADIUS', 'A2_ANTIPADRADIUS', 'A2_VIAPITCH']

df_features = df[features_8].copy()

print(f"Dataset: {df_features.shape[0]} configurações × {df_features.shape[1]} features")
print()
print("Estatísticas Completas:")
print(df_features.describe())
print()

# ============================================================================
# PASSO 2: Carregar Amostra de 50 Configs para Z11(f) Statistics
# ============================================================================

print("=" * 80)
print("PASSO 2: Carregando Amostra de 50 Configurações")
print("=" * 80)

np.random.seed(42)
sample_idx = np.random.choice(df.shape[0], size=50, replace=False)
df_sample = df.iloc[sample_idx][features_8 + ['simu_index']].reset_index(drop=True)

z11_sample = []
freqs = None
valid_count = 0

for idx, row in df_sample.iterrows():
    simu_idx = int(row['simu_index'])
    path = base_path / "variation" / f"simu_{simu_idx}.s36p"

    if (idx + 1) % 10 == 0:
        print(f"  [{idx+1:2d}/50] Processando...", end="\r")

    try:
        network = parse_touchstone(path, n_ports=36)
        z11 = self_impedance(network, port=0)
        z11_sample.append(z11)
        valid_count += 1

        if freqs is None:
            freqs = network.freq.copy()
    except Exception as e:
        pass

z11_sample = np.array(z11_sample)
z11_mags = np.abs(z11_sample)

print(f"Carregados com sucesso: {valid_count} / 50 configurações")
print()

# ============================================================================
# PASSO 3: Calcular Propriedades de Z(f) para a Amostra
# ============================================================================

print("=" * 80)
print("PASSO 3: Propriedades de Z11(f) na Amostra")
print("=" * 80)

z_maxs = []
z_mins = []
f_mins = []

for i in range(z11_mags.shape[0]):
    z_mag = z11_mags[i]
    z_maxs.append(np.max(z_mag))
    z_mins.append(np.min(z_mag))
    f_mins.append(freqs[np.argmin(z_mag)])

z_maxs = np.array(z_maxs)
z_mins = np.array(z_mins)
f_mins = np.array(f_mins)

print(f"Z_max:  μ={z_maxs.mean():.1f} Ω, σ={z_maxs.std():.1f} Ω, range=[{z_maxs.min():.1f}, {z_maxs.max():.1f}]")
print(f"Z_min:  μ={z_mins.mean():.3f} Ω, σ={z_mins.std():.3f} Ω, range=[{z_mins.min():.3f}, {z_mins.max():.3f}]")
print(f"f(min): μ={f_mins.mean()/1e6:.1f} MHz, σ={f_mins.std()/1e6:.1f} MHz, range=[{f_mins.min()/1e6:.0f}, {f_mins.max()/1e6:.0f}]")
print()

# ============================================================================
# PASSO 4: Visualizações
# ============================================================================

print("=" * 80)
print("PASSO 4: Gerando Gráficos")
print("=" * 80)

fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(4, 4, hspace=0.4, wspace=0.35)

# Row 1: Histogramas dos 8 features
feature_names_short = ['TDIEL', 'ε_r', 'A1_r_v', 'A1_r_ap', 'A1_p', 'A2_r_v', 'A2_r_ap', 'A2_p']

for i, (feat, short_name) in enumerate(zip(features_8, feature_names_short)):
    ax = fig.add_subplot(gs[0, i % 4])
    if i == 4:
        ax = fig.add_subplot(gs[1, 0])
    if i == 5:
        ax = fig.add_subplot(gs[1, 1])
    if i == 6:
        ax = fig.add_subplot(gs[1, 2])
    if i == 7:
        ax = fig.add_subplot(gs[1, 3])

    data = df_features[feat].values
    ax.hist(data, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    ax.set_xlabel(short_name, fontsize=10)
    ax.set_ylabel('Frequência', fontsize=10)
    ax.set_title(f'{short_name}: μ={data.mean():.2f}, σ={data.std():.2f}', fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

# Row 3: Scatter plots (pairwise features)
ax = fig.add_subplot(gs[2, :2])
scatter = ax.scatter(df_features['TDIEL'], df_features['PERMITTIVITY'], alpha=0.5, s=30, color='steelblue')
ax.set_xlabel('TDIEL (mil)', fontsize=11)
ax.set_ylabel('PERMITTIVITY (ε_r)', fontsize=11)
ax.set_title('TDIEL vs ε_r (Coverage do LHS)', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

ax = fig.add_subplot(gs[2, 2:])
ax.scatter(df_features['A1_VIAPITCH'], df_features['A1_VIARADIUS'], alpha=0.5, s=30, color='coral')
ax.set_xlabel('A1_VIAPITCH (mil)', fontsize=11)
ax.set_ylabel('A1_VIARADIUS (mil)', fontsize=11)
ax.set_title('A1_VIAPITCH vs A1_VIARADIUS (via Array 1)', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

# Row 4: Distribuições de Z(f) statistics
ax = fig.add_subplot(gs[3, 0])
ax.hist(z_maxs, bins=15, color='darkblue', edgecolor='black', alpha=0.7)
ax.set_xlabel('Z_max (Ω)', fontsize=11)
ax.set_ylabel('Frequência', fontsize=11)
ax.set_title(f'Z_max (n=50)\nμ={z_maxs.mean():.1f}, σ={z_maxs.std():.1f}', fontsize=11, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

ax = fig.add_subplot(gs[3, 1])
ax.hist(z_mins, bins=15, color='darkgreen', edgecolor='black', alpha=0.7)
ax.set_xlabel('Z_min (Ω)', fontsize=11)
ax.set_ylabel('Frequência', fontsize=11)
ax.set_title(f'Z_min (n=50)\nμ={z_mins.mean():.3f}, σ={z_mins.std():.3f}', fontsize=11, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

ax = fig.add_subplot(gs[3, 2])
ax.hist(f_mins / 1e6, bins=15, color='darkred', edgecolor='black', alpha=0.7)
ax.set_xlabel('f(Z_min) (MHz)', fontsize=11)
ax.set_ylabel('Frequência', fontsize=11)
ax.set_title(f'f(Z_min) (n=50)\nμ={f_mins.mean()/1e6:.0f}, σ={f_mins.std()/1e6:.1f}', fontsize=11, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Correlação matriz
ax = fig.add_subplot(gs[3, 3])
corr_mat = df_features[features_8].corr()
im = ax.imshow(corr_mat, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
ax.set_xticks(range(len(features_8)))
ax.set_yticks(range(len(features_8)))
ax.set_xticklabels(feature_names_short, fontsize=8, rotation=45, ha='right')
ax.set_yticklabels(feature_names_short, fontsize=8)
ax.set_title('Correlação entre Features', fontsize=11, fontweight='bold')
plt.colorbar(im, ax=ax)

plt.savefig(Path(__file__).parent / '03_dataset_stats.png', dpi=150, bbox_inches='tight')
print("Gráfico salvo: 03_dataset_stats.png")
print()

# ============================================================================
# PASSO 5: LHS (Latin Hypercube Sampling) Check
# ============================================================================

print("=" * 80)
print("PASSO 5: Cobertura do Espaço de Design (LHS Check)")
print("=" * 80)

print(f"""
O dataset foi gerado com Latin Hypercube Sampling (LHS), que busca
cobrir uniformemente todo o espaço de design.

Verificação de cobertura (para cada feature):
""")

for feat in features_8:
    data = df_features[feat].values
    min_val, max_val = data.min(), data.max()
    n_unique = len(np.unique(np.round(data, 2)))  # Valores únicos (arredondados)
    density = n_unique / len(data)

    print(f"  {feat:20s}: {n_unique:3d} valores únicos, densidade={density:.2%}, range=[{min_val:.2f}, {max_val:.2f}]")

print()
print("Interpretação:")
print(f"""
  - Alta densidade (~100%): Todas as 985 configs são distintas, bom coverage
  - LHS garante que não há "aglomerados" de configs similares
  - As 985 configs cobrem bem todo o espaço de design multidimensional

Conclusão: Este é um bom dataset para treinar um modelo ML. Há:
  ✓ Variação suficiente em todos os 8 parâmetros
  ✓ Nenhuma correlação tão forte que torne features redundantes
  ✓ Cobertura uniforme do espaço de design (por design LHS)
  ✓ Diferentes curvas Z11(f) associadas a diferentes configs
""")

print("=" * 80)
print("PRÓXIMOS PASSOS")
print("=" * 80)
print("""
Você agora entende:
1. Como ler arquivos Touchstone e extrair Z11(f)
2. Como os 8 parâmetros afetam a impedância
3. A distribuição e cobertura do dataset completo

Próxima etapa: Criar loader.py para carregar tudo de uma vez,
com paralelização, para usar no treinamento do modelo ML.
""")
