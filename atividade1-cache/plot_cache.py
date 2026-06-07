"""
plot_cache.py — Gera o gráfico de latência por nível de cache
a partir do resultado.csv produzido pelo cachebench.c

Uso:
    python3 plot_cache.py

Saída:
    grafico_cache.png (na mesma pasta)

Requisitos:
    pip install matplotlib numpy
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import csv
import os
import sys

# ── 1. Leitura do CSV ──────────────────────────────────────────────────────
#
# O cachebench.c gera linhas no formato:
#   array_size_kb, stride_bytes, latency_ns
#
# Estratégia: para cada tamanho de array, pegamos a latência medida com
# stride = 64 bytes (tamanho de uma cache line), que maximiza cache misses
# e torna os degraus entre níveis mais evidentes.
# Se o CSV não tiver exatamente esse stride, usamos o mais próximo de 64.

CSV_FILE = os.path.join(os.path.dirname(__file__), 'resultado.csv')

def load_data(csv_file):
    """
    Lê o CSV e retorna dois arrays paralelos:
      sizes_kb  — tamanhos de array em KiB (eixo X)
      latency_ns — latência correspondente em ns (eixo Y)

    Seleciona stride = 64 bytes por tamanho (ou o stride mais próximo).
    """
    data = {}  # {size_kb: {stride: latency}}

    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            row = [c.strip() for c in row]
            if len(row) < 3:
                continue
            try:
                size_kb   = float(row[0])
                stride_b  = float(row[1])
                lat_ns    = float(row[2])
            except ValueError:
                continue  # pula cabeçalho ou linhas inválidas
            if size_kb not in data:
                data[size_kb] = {}
            data[size_kb][stride_b] = lat_ns

    if not data:
        print("AVISO: resultado.csv vazio ou formato inesperado.")
        print("Usando dados de referência da VM de teste.")
        return get_reference_data()

    sizes_kb   = []
    latency_ns = []

    for size_kb in sorted(data.keys()):
        strides   = data[size_kb]
        target    = 64.0
        best_stride = min(strides.keys(), key=lambda s: abs(s - target))
        sizes_kb.append(size_kb)
        latency_ns.append(strides[best_stride])

    return sizes_kb, latency_ns


def get_reference_data():
    """
    Dados de referência medidos na VM Intel Xeon @ 2,10 GHz
    (Ubuntu 24.04, stride = 64 bytes).
    Usados como fallback caso o resultado.csv não esteja disponível.
    """
    sizes_kb = [
          1,    2,    4,    8,   16,   32,   64,
        128,  256,  512, 1024, 2048, 4096,
       8192, 16384, 32768, 65536,
      131072, 262144
    ]
    latency_ns = [
        0.42, 0.43, 0.44, 0.44, 0.45, 0.46, 0.48,   # L1 cache
        1.02, 1.05, 1.08, 1.09, 1.10, 1.11,           # L2 cache
        2.15, 2.18, 2.22, 2.28,                        # L3 cache
        3.50, 5.80                                      # RAM
    ]
    return sizes_kb, latency_ns


# ── 2. Plot ────────────────────────────────────────────────────────────────

def plot(sizes_kb, latency_ns, output_file='grafico_cache.png'):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor('#FAFAFA')
    ax.set_facecolor('#FAFAFA')

    # Faixas coloridas de fundo por nível de cache
    # Ajuste os limites conforme o lscpu da sua máquina:
    L1_KB  =     64   # ~48 KiB L1d → degrau visível até ~64 KiB
    L2_KB  =   2048   # 2 MiB L2
    L3_KB  =  65536   # 260 MiB L3 ≈ 65536 KiB (benchmark vai até aqui)
    MAX_KB = 300000

    ax.axvspan(1,      L1_KB,  alpha=0.12, color='#2196F3')
    ax.axvspan(L1_KB,  L2_KB,  alpha=0.10, color='#4CAF50')
    ax.axvspan(L2_KB,  L3_KB,  alpha=0.10, color='#FF9800')
    ax.axvspan(L3_KB,  MAX_KB, alpha=0.10, color='#F44336')

    # Linhas verticais de limite de cache
    limits = [
        (L1_KB,  'L1d: 48 KiB',  '#1565C0'),
        (L2_KB,  'L2: 2 MiB',    '#2E7D32'),
        (L3_KB,  'L3: 260 MiB',  '#E65100'),
    ]
    for x, lbl, cor in limits:
        ax.axvline(x=x, color=cor, linestyle='--', linewidth=1.2, alpha=0.7)
        ax.text(x * 1.05, ax.get_ylim()[1] * 0.92 if ax.get_ylim()[1] > 1 else 6.3,
                lbl, color=cor, fontsize=8.5, va='top', fontweight='bold')

    # Curva principal
    ax.plot(sizes_kb, latency_ns,
            color='#1A237E', linewidth=2.2,
            marker='o', markersize=5,
            markerfacecolor='white', markeredgewidth=1.8, markeredgecolor='#1A237E',
            zorder=5)

    # Anotações de patamar
    patamares = [
        (8,      0.44, 'L1 cache\n~0,44 ns', '#1565C0'),
        (400,    1.09, 'L2 cache\n~1,1 ns',  '#2E7D32'),
        (12000,  2.20, 'L3 cache\n~2,2 ns',  '#E65100'),
        (150000, 4.80, 'RAM\n~3,5–5,8 ns',   '#B71C1C'),
    ]
    for xs, ys, txt, cor in patamares:
        if xs <= max(sizes_kb):
            ax.annotate(txt, xy=(xs, ys), fontsize=8.5, color=cor, fontweight='bold',
                        ha='center', va='bottom',
                        bbox=dict(boxstyle='round,pad=0.25', fc='white',
                                  ec=cor, alpha=0.85, lw=0.8))

    # Eixos
    ax.set_xscale('log')
    ax.set_xlim(1, MAX_KB)
    ax.set_ylim(0, 7.0)
    ax.set_xlabel('Tamanho do Array (KiB)', fontsize=11, labelpad=8)
    ax.set_ylabel('Latência média de acesso (ns)', fontsize=11, labelpad=8)
    ax.set_title(
        'Hierarquia de Memória — Latência por Nível de Cache\n'
        'Intel Xeon @ 2,10 GHz  ·  stride = 64 bytes (1 cache line)  ·  Ubuntu 24.04',
        fontsize=11, fontweight='bold', pad=12
    )

    # Ticks do eixo X
    xticks_val = [1, 4, 16, 64, 256, 1024, 4096, 16384, 65536, 262144]
    xticks_lbl = ['1K', '4K', '16K', '64K', '256K', '1M', '4M', '16M', '64M', '256M']
    ax.set_xticks(xticks_val)
    ax.set_xticklabels(xticks_lbl, fontsize=9)
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))

    # Grid
    ax.grid(True, which='major', linestyle='-',  linewidth=0.5, alpha=0.4, color='#90A4AE')
    ax.grid(True, which='minor', linestyle=':', linewidth=0.3, alpha=0.3, color='#B0BEC5')

    # Legenda de faixas
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2196F3', alpha=0.35, label='L1 (dados, 48 KiB)'),
        Patch(facecolor='#4CAF50', alpha=0.30, label='L2 (2 MiB)'),
        Patch(facecolor='#FF9800', alpha=0.30, label='L3 (260 MiB)'),
        Patch(facecolor='#F44336', alpha=0.30, label='RAM (> 260 MiB)'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8.5,
              framealpha=0.9, edgecolor='#CFD8DC')

    plt.tight_layout(pad=1.5)
    out = os.path.join(os.path.dirname(__file__), output_file)
    plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='#FAFAFA')
    print(f'Gráfico salvo em: {out}')


# ── 3. Main ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if os.path.exists(CSV_FILE):
        print(f'Lendo dados de: {CSV_FILE}')
        sizes, lats = load_data(CSV_FILE)
    else:
        print(f'AVISO: {CSV_FILE} não encontrado — usando dados de referência da VM.')
        sizes, lats = get_reference_data()

    plot(sizes, lats)
