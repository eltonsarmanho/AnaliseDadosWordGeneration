#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIO VISUAL COMPLETO - TDE WORDGEN FASE 3
Interface visual interativa para análise de dados do Teste de Escrita (TDE)

Baseado na metodologia dos relatórios de vocabulário com adaptações específicas
para os dados e métricas do Teste de Escrita.

Autor: Sistema de Análise WordGen
Data: 2024
"""

import os
import re

import io
import base64
import pathlib
import argparse
from typing import List, Tuple, Dict
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configurações matplotlib para compatibilidade
plt.switch_backend("Agg")
sns.set_theme(style="whitegrid")

# ======================
# Configurações de Paths
# ======================
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.parent.resolve()  # Sair de TDE/Fase3/Modules/
DATA_DIR = BASE_DIR / "Data"
DASHBOARD_DIR = BASE_DIR / "Dashboard"
FIG_DIR = DATA_DIR / "figures"

# Arquivos de dados TDE - ALTERADO PARA TDE_longitudinal.csv
CSV_TABELA_TDE = DASHBOARD_DIR / "TDE_longitudinal.csv"
HTML_OUT = DATA_DIR / "relatorio_visual_TDE_fase3.html"
MAPPING_FILE = DATA_DIR / "RespostaTED.json"

# Configurações matplotlib
plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 120,
    "axes.grid": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ======================
# Benchmarks Educacionais TDE
# ======================

# Benchmarks específicos para Teste de Escrita baseados na literatura
TDE_BENCHMARKS = {
    "hattie_2009": {
        "threshold": 0.4,
        "description": "Hattie (2009) - Impacto visível na aprendizagem",
        "context": "Meta-análise de intervenções educacionais"
    },
    "writing_cohen_1988": {
        "threshold": 0.5,
        "description": "Cohen (1988) - Effect size médio para escrita",
        "context": "Benchmark clássico para estudos de escrita"
    },
    "literacy_interventions": {
        "threshold": 0.35,
        "description": "Intervenções de Letramento - Threshold mínimo",
        "context": "Meta-análises de programas de alfabetização"
    },
    "writing_instruction": {
        "threshold": 0.6,
        "description": "Ensino de Escrita - Programas efetivos",
        "context": "Graham & Perin (2007) - Writing instruction"
    }
}

# ======================
# Funções Utilitárias
# ======================

def fig_to_base64(fig) -> str:
    """Converte uma figura matplotlib para string Base64."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=120)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"

def interpretar_magnitude(es: float) -> str:
    """Interpreta a magnitude do effect size."""
    abs_es = abs(es)
    if abs_es < 0.15:
        return "Trivial"
    elif abs_es < 0.35:
        return "Pequeno"
    elif abs_es < 0.65:
        return "Moderado"
    elif abs_es < 1.0:
        return "Grande"
    else:
        return "Muito Grande"

def categorizar_mudanca_cohen_tde(delta: float, baseline_sd: float) -> str:
    """Categoriza mudanças usando thresholds de Cohen adaptados para TDE."""
    if not np.isfinite(baseline_sd) or baseline_sd <= 0:
        return "Sem Mudança Prática (±0.2 SD)"

    pequeno = 0.2 * baseline_sd
    medio = 0.5 * baseline_sd  
    grande = 0.8 * baseline_sd

    if delta >= grande:
        return "Melhora Grande (≥0.8 SD)"
    elif delta >= medio:
        return "Melhora Média (0.5-0.8 SD)"
    elif delta >= pequeno:
        return "Melhora Pequena (0.2-0.5 SD)"
    elif delta > -pequeno:
        return "Sem Mudança Prática (±0.2 SD)"
    elif delta > -medio:
        return "Piora Pequena (-0.5 a -0.2 SD)"
    elif delta > -grande:
        return "Piora Média (-0.8 a -0.5 SD)"
    else:
        return "Piora Grande (<-0.8 SD)"

def _ensure_fig_dir():
    """Garante que o diretório de figuras existe."""
    os.makedirs(FIG_DIR, exist_ok=True)

# ======================
# Carregamento e Preparação dos Dados
# ======================

def obter_escolas_disponiveis_tde():
    """Obtém a lista de escolas disponíveis nos dados TDE da Fase 3"""
    try:
        df = pd.read_csv(str(CSV_TABELA_TDE))
        # Filtrar apenas Fase 3
        df = df[df['Fase'] == 3]
    except:
        # Fallback se não conseguir ler
        return ["Todas"]
    
    escolas = sorted(df['Escola'].dropna().unique().tolist())
    return ["Todas"] + escolas

def carregar_dados_tde(csv_path: str = None, escola_filtro: str = None) -> Tuple[pd.DataFrame, Dict]:
    """Carrega e prepara os dados TDE da tabela longitudinal - Fase 3."""
    if csv_path is None:
        csv_path = str(CSV_TABELA_TDE)
    
    print("📊 CARREGANDO DADOS TDE FASE 3...")
    
    # Carregar dados
    try:
        if csv_path.endswith('.xlsx'):
            df = pd.read_excel(csv_path)
        else:
            try:
                df = pd.read_csv(csv_path, encoding='utf-8')
            except:
                df = pd.read_csv(csv_path, encoding='latin-1')
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        raise
    
    print(f"   Total de registros carregados: {len(df)}")
    
    # FILTRAR APENAS FASE 3
    df = df[df['Fase'] == 3].copy()
    print(f"   Registros da Fase 3: {len(df)}")
    
    # Aplicar filtro de escola se especificado
    if escola_filtro and escola_filtro != "Todas":
        df = df[df['Escola'] == escola_filtro].copy()
        print(f"   Filtro escola '{escola_filtro}': {len(df)} registros")
    
    # Calcular Delta_Score se não existir
    if 'Delta_Score' not in df.columns:
        df['Delta_Score'] = df['Score_Pos'] - df['Score_Pre']
    
    # Verificar colunas essenciais
    colunas_essenciais = ['Score_Pre', 'Score_Pos', 'Escola', 'Turma']
    missing_cols = [col for col in colunas_essenciais if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas essenciais ausentes: {missing_cols}")
    
    # Limpeza básica
    df = df.dropna(subset=['Score_Pre', 'Score_Pos'])
    
    # Criar novos grupos baseados no ano extraído da turma
    df['Ano'] = df['Turma'].str.extract(r'(\d+)(?:º|°|\s+(?:ano|ANO))', flags=re.IGNORECASE)[0]
    df['GrupoTDE_Novo'] = df['Ano'].map({
        '6': '6º ano',
        '7': '7º ano', 
        '8': '8º ano',
        '9': '9º ano'
    })
    
    # Filtrar apenas registros com anos válidos
    df = df.dropna(subset=['GrupoTDE_Novo'])
    
    # Metadados
    meta = {
        "n_total": len(df),
        "n_6ano": len(df[df['GrupoTDE_Novo'] == '6º ano']),
        "n_7ano": len(df[df['GrupoTDE_Novo'] == '7º ano']),
        "n_8ano": len(df[df['GrupoTDE_Novo'] == '8º ano']),
        "n_9ano": len(df[df['GrupoTDE_Novo'] == '9º ano']),
        "escolas": df['Escola'].unique().tolist(),
        "escola_filtro": escola_filtro
    }
    
    print(f"   Registros após limpeza: {len(df)}")
    print(f"   Grupos: 6º={meta['n_6ano']}, 7º={meta['n_7ano']}, 8º={meta['n_8ano']}, 9º={meta['n_9ano']}")
    
    return df, meta

def calcular_indicadores_tde(df: pd.DataFrame, grupo_filtro: str = None) -> Dict[str, float]:
    """Calcula indicadores estatísticos específicos para TDE."""
    
    # Aplicar filtro de grupo se especificado
    if grupo_filtro:
        df = df[df['GrupoTDE_Novo'] == grupo_filtro]
    
    if len(df) == 0:
        return {
            "n": 0,
            "mean_pre": 0.0,
            "std_pre": 0.0,
            "mean_pos": 0.0,
            "std_pos": 0.0,
            "mean_delta": 0.0,
            "std_delta": 0.0,
            "percent_improved": 0.0,
            "percent_worsened": 0.0,
            "percent_unchanged": 0.0,
            "cohen_d_global": np.nan
        }
    
    pre_scores = df['Score_Pre']
    pos_scores = df['Score_Pos'] 
    deltas = df['Delta_Score']
    
    n = len(df)
    
    # Estatísticas básicas
    mean_pre = float(pre_scores.mean())
    std_pre = float(pre_scores.std(ddof=1)) if n > 1 else 0.0
    mean_pos = float(pos_scores.mean())
    std_pos = float(pos_scores.std(ddof=1)) if n > 1 else 0.0
    mean_delta = float(deltas.mean())
    std_delta = float(deltas.std(ddof=1)) if n > 1 else 0.0
    
    # Percentuais de mudança
    improved = (deltas > 0).mean() * 100.0
    worsened = (deltas < 0).mean() * 100.0  
    unchanged = (deltas == 0).mean() * 100.0
    
    # Effect size global (Delta médio / SD do pré-teste)
    cohen_d = mean_delta / std_pre if std_pre > 1e-12 else np.nan
    
    return {
        "n": n,
        "mean_pre": mean_pre,
        "std_pre": std_pre,
        "mean_pos": mean_pos,
        "std_pos": std_pos,
        "mean_delta": mean_delta,
        "std_delta": std_delta,
        "percent_improved": improved,
        "percent_worsened": worsened,
        "percent_unchanged": unchanged,
        "cohen_d_global": cohen_d
    }

# ======================
# Funções de Análise de Palavras
# ======================

def extrair_palavras_tde(df: pd.DataFrame) -> pd.DataFrame:
    """Extrai dados das palavras TDE para análise."""
    palavras_data = []
    
    # Padrão das colunas no TDE_longitudinal.csv: Q{num}_Pre e Q{num}_Pos
    colunas = df.columns.tolist()
    
    # Extrair informações das questões (Q1 a Q40)
    for col in colunas:
        if col.startswith('Q') and '_Pre' in col:
            # Extrair número da questão
            questao_num = col.replace('_Pre', '')
            
            # Colunas correspondentes
            col_pre = f"{questao_num}_Pre"
            col_pos = f"{questao_num}_Pos"
            
            # Verificar se ambas as colunas existem
            if col_pre in colunas and col_pos in colunas:
                palavras_data.append({
                    'Questao': questao_num,
                    'Palavra': f"Palavra {questao_num}",  # Nome genérico
                    'Col_Pre': col_pre,
                    'Col_Pos': col_pos
                })
    
    return pd.DataFrame(palavras_data)

def analisar_palavras_tde(df: pd.DataFrame, grupo_filtro: str = None) -> pd.DataFrame:
    """Analisa performance das palavras TDE por grupo."""
    
    # Filtrar por grupo se especificado
    if grupo_filtro:
        df = df[df['GrupoTDE_Novo'] == grupo_filtro]
    
    if len(df) == 0:
        return pd.DataFrame()
    
    # Extrair informações das palavras
    palavras_info = extrair_palavras_tde(df)
    
    if len(palavras_info) == 0:
        return pd.DataFrame()
    
    resultados = []
    
    for _, palavra_info in palavras_info.iterrows():
        questao = palavra_info['Questao']
        palavra = palavra_info['Palavra']
        col_pre = palavra_info['Col_Pre']
        col_pos = palavra_info['Col_Pos']
        
        # Dados válidos (não nulos)
        mask_valido = df[col_pre].notna() & df[col_pos].notna()
        dados_validos = df[mask_valido]
        
        if len(dados_validos) == 0:
            continue
        
        # Calcular estatísticas
        acertos_pre = dados_validos[col_pre].sum()
        acertos_pos = dados_validos[col_pos].sum()
        total_tentativas = len(dados_validos)
        
        taxa_acerto_pre = acertos_pre / total_tentativas if total_tentativas > 0 else 0
        taxa_acerto_pos = acertos_pos / total_tentativas if total_tentativas > 0 else 0
        
        melhora = taxa_acerto_pos - taxa_acerto_pre
        melhora_percentual = melhora * 100
        
        # Percentual de erros
        perc_erro_pre = (1 - taxa_acerto_pre) * 100
        perc_erro_pos = (1 - taxa_acerto_pos) * 100
        
        resultados.append({
            'Questao': questao,
            'Palavra': palavra,
            'Total_Tentativas': total_tentativas,
            'Acertos_Pre': acertos_pre,
            'Acertos_Pos': acertos_pos,
            'Taxa_Acerto_Pre': taxa_acerto_pre,
            'Taxa_Acerto_Pos': taxa_acerto_pos,
            'Melhora': melhora,
            'Melhora_Percentual': melhora_percentual,
            'Perc_Erro_Pre': perc_erro_pre,
            'Perc_Erro_Pos': perc_erro_pos
        })
    
    return pd.DataFrame(resultados)

# ======================
# Geração de Gráficos
# ======================

def gerar_grafico_prepos_tde(df: pd.DataFrame) -> str:
    """Gera gráficos de comparação de scores e distribuição de mudanças por ano (4 gráficos em 2x2)."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    grupos = ['6º ano', '7º ano', '8º ano', '9º ano']
    cores = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
    
    # 1. Médias de scores por grupo
    ax = axes[0, 0]
    means_pre = []
    means_pos = []
    stds_pre = []
    stds_pos = []
    
    for grupo in grupos:
        data = df[df['GrupoTDE_Novo'] == grupo]
        if len(data) > 0:
            means_pre.append(data['Score_Pre'].mean())
            means_pos.append(data['Score_Pos'].mean())
            stds_pre.append(data['Score_Pre'].std())
            stds_pos.append(data['Score_Pos'].std())
        else:
            means_pre.append(0)
            means_pos.append(0)
            stds_pre.append(0)
            stds_pos.append(0)
    
    x = np.arange(len(grupos))
    width = 0.35
    grupos_curtos = grupos  # Usar os nomes já curtos
    
    ax.bar(x - width/2, means_pre, width, yerr=stds_pre, label='Pré-teste', alpha=0.8, color='#3498db')
    ax.bar(x + width/2, means_pos, width, yerr=stds_pos, label='Pós-teste', alpha=0.8, color='#e74c3c')
    
    ax.set_xlabel('Anos', fontsize=12)
    ax.set_ylabel('Score Médio', fontsize=12)
    ax.set_title('Comparação de Médias por Ano', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(grupos_curtos)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Boxplot de deltas (mudanças)
    ax = axes[0, 1]
    deltas_data = []
    for grupo in grupos:
        data = df[df['GrupoTDE_Novo'] == grupo]
        if len(data) > 0:
            deltas_data.append(data['Delta_Score'])
        else:
            deltas_data.append([0])  # Dados vazios
    
    bp = ax.boxplot(deltas_data, tick_labels=grupos_curtos, patch_artist=True)
    
    for patch, cor in zip(bp['boxes'], cores):
        patch.set_facecolor(cor)
        patch.set_alpha(0.7)
    
    ax.set_ylabel('Mudança (Delta Score)', fontsize=12)
    ax.set_title('Distribuição de Mudanças por Ano', fontsize=14, fontweight='bold')
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=2)
    ax.grid(True, alpha=0.3)
    
    # 3. Tamanhos de amostra
    ax = axes[1, 0]
    sizes = [len(df[df['GrupoTDE_Novo'] == grupo]) for grupo in grupos]
    bars = ax.bar(grupos_curtos, sizes, color=cores, alpha=0.8)
    
    for bar, size in zip(bars, sizes):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{size}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    ax.set_ylabel('Número de Estudantes', fontsize=12)
    ax.set_title('Tamanho das Amostras', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 4. Cohen's d por grupo
    ax = axes[1, 1]
    cohens_d = []
    for grupo in grupos:
        data = df[df['GrupoTDE_Novo'] == grupo]
        if len(data) > 1:
            pre_scores = data['Score_Pre']
            pos_scores = data['Score_Pos']
            deltas = data['Delta_Score']
            
            # Cohen's d = delta médio / desvio padrão do pré-teste
            pooled_std = pre_scores.std()
            d = deltas.mean() / pooled_std if pooled_std > 0 else 0
            cohens_d.append(d)
        else:
            cohens_d.append(0)
    
    bars = ax.bar(grupos_curtos, cohens_d, color=cores, alpha=0.8)
    
    # Linhas de referência Cohen
    ax.axhline(y=0.2, color='green', linestyle='--', alpha=0.7, label='Pequeno (0.2)')
    ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.7, label='Médio (0.5)')
    ax.axhline(y=0.8, color='red', linestyle='--', alpha=0.7, label='Grande (0.8)')
    
    # Linha de referência Hattie (específica para educação)
    ax.axhline(y=0.4, color='purple', linestyle=':', alpha=0.7, label='Hattie: Bom (0.4)')
    
    for bar, d in zip(bars, cohens_d):
        height = bar.get_height()
        y_text = height + 0.02 if height > 0 else height - 0.05
        ax.text(bar.get_x() + bar.get_width()/2., y_text,
                f'{d:.3f}', ha='center', va='bottom' if height > 0 else 'top', 
                fontweight='bold', fontsize=11)
    
    ax.set_ylabel("Cohen's d", fontsize=12)
    ax.set_title("Effect Size por Grupo", fontsize=14, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig_to_base64(fig)

def gerar_grafico_palavras_top_tde(df: pd.DataFrame) -> str:
    """Gera gráfico das palavras com maior melhora TDE por ano."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Analisar palavras por grupo
    palavras_geral = analisar_palavras_tde(df)
    palavras_6ano = analisar_palavras_tde(df, "6º ano")
    palavras_7ano = analisar_palavras_tde(df, "7º ano")
    palavras_8ano = analisar_palavras_tde(df, "8º ano")
    palavras_9ano = analisar_palavras_tde(df, "9º ano")
    
    if len(palavras_geral) == 0:
        # Gráfico vazio se não há dados
        for ax in axes:
            ax.text(0.5, 0.5, 'Dados insuficientes', ha='center', va='center', 
                    transform=ax.transAxes, fontsize=16)
        return fig_to_base64(fig)
    
    # 1. Top 20 palavras - melhora geral
    ax = axes[0]
    top_20 = palavras_geral.nlargest(20, 'Melhora')
    y_pos = np.arange(len(top_20))
    
    bars = ax.barh(y_pos, top_20['Melhora_Percentual'], color='#3498db', alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([p[:15] + '...' if len(p) > 15 else p for p in top_20['Palavra']])
    ax.set_xlabel('Melhora na Taxa de Acerto (%)', fontsize=12)
    ax.set_title('Top 20 Palavras TDE - Melhora Geral', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, valor in zip(bars, top_20['Melhora_Percentual']):
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{valor:.1f}%', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # 2. Comparação entre anos - Top 15
    ax = axes[1]
    top_15_questoes = palavras_geral.nlargest(15, 'Melhora')['Questao']
    
    melhoras_6ano = []
    melhoras_7ano = []
    melhoras_8ano = []
    melhoras_9ano = []
    palavras_nomes = []
    
    for questao in top_15_questoes:
        palavra = palavras_geral[palavras_geral['Questao'] == questao]['Palavra'].iloc[0]
        palavras_nomes.append(palavra[:10] + '...' if len(palavra) > 10 else palavra)
        
        # Buscar melhora para cada ano
        melhora_6 = palavras_6ano[palavras_6ano['Questao'] == questao]['Melhora_Percentual']
        melhora_7 = palavras_7ano[palavras_7ano['Questao'] == questao]['Melhora_Percentual']
        melhora_8 = palavras_8ano[palavras_8ano['Questao'] == questao]['Melhora_Percentual']
        melhora_9 = palavras_9ano[palavras_9ano['Questao'] == questao]['Melhora_Percentual']
        
        melhoras_6ano.append(melhora_6.iloc[0] if len(melhora_6) > 0 else 0)
        melhoras_7ano.append(melhora_7.iloc[0] if len(melhora_7) > 0 else 0)
        melhoras_8ano.append(melhora_8.iloc[0] if len(melhora_8) > 0 else 0)
        melhoras_9ano.append(melhora_9.iloc[0] if len(melhora_9) > 0 else 0)
    
    x = np.arange(len(palavras_nomes))
    width = 0.2
    
    ax.bar(x - 1.5*width, melhoras_6ano, width, label='6º ano', color='#3498db', alpha=0.7)
    ax.bar(x - 0.5*width, melhoras_7ano, width, label='7º ano', color='#2ecc71', alpha=0.7)
    ax.bar(x + 0.5*width, melhoras_8ano, width, label='8º ano', color='#e74c3c', alpha=0.7)
    ax.bar(x + 1.5*width, melhoras_9ano, width, label='9º ano', color='#f39c12', alpha=0.7)
    
    ax.set_xlabel('Palavras', fontsize=12)
    ax.set_ylabel('Melhora (%)', fontsize=12)
    ax.set_title('Comparação de Melhora TDE por Ano - Top 15', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(palavras_nomes, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Linha de referência em zero
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5, linewidth=1)
    
    plt.tight_layout()
    return fig_to_base64(fig)

def gerar_grafico_comparacao_intergrupos_tde(df: pd.DataFrame) -> str:
    """Gera comparação detalhada entre anos (4 gráficos de densidade separados)."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    grupos = ['6º ano', '7º ano', '8º ano', '9º ano']
    cores = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
    
    # 1. Distribuição de densidade - 6º ANO (superior esquerdo)
    ax = axes[0, 0]
    data_pre_6 = df[df['GrupoTDE_Novo'] == grupos[0]]['Score_Pre']
    data_pos_6 = df[df['GrupoTDE_Novo'] == grupos[0]]['Score_Pos']
    
    if len(data_pre_6) > 0:
        ax.hist(data_pre_6, alpha=0.5, label='Pré-teste', color=cores[0], bins=12, density=True)
        ax.hist(data_pos_6, alpha=0.7, label='Pós-teste', color=cores[0], bins=12, density=True, hatch='//')
        
        # Adicionar médias como linhas verticais
        mean_pre_6 = data_pre_6.mean()
        mean_pos_6 = data_pos_6.mean()
        ax.axvline(mean_pre_6, color=cores[0], linestyle='--', alpha=0.6, linewidth=2)
        ax.axvline(mean_pos_6, color=cores[0], linestyle='-', alpha=0.8, linewidth=2)
        
        # Texto com médias
        ax.text(0.05, 0.95, f'Médias:\nPré: {mean_pre_6:.1f}\nPós: {mean_pos_6:.1f}', 
                transform=ax.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                verticalalignment='top', fontsize=10)
    else:
        ax.text(0.5, 0.5, 'Dados insuficientes', ha='center', va='center', 
                transform=ax.transAxes, fontsize=14)
    
    ax.set_xlabel('Scores TDE', fontsize=12)
    ax.set_ylabel('Densidade', fontsize=12)
    ax.set_title('6º ano\nDistribuição de Densidade', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Distribuição de densidade - 7º ANO (superior direito)
    ax = axes[0, 1]
    data_pre_7 = df[df['GrupoTDE_Novo'] == grupos[1]]['Score_Pre']
    data_pos_7 = df[df['GrupoTDE_Novo'] == grupos[1]]['Score_Pos']
    
    if len(data_pre_7) > 0:
        ax.hist(data_pre_7, alpha=0.5, label='Pré-teste', color=cores[1], bins=12, density=True)
        ax.hist(data_pos_7, alpha=0.7, label='Pós-teste', color=cores[1], bins=12, density=True, hatch='//')
        
        # Adicionar médias como linhas verticais
        mean_pre_7 = data_pre_7.mean()
        mean_pos_7 = data_pos_7.mean()
        ax.axvline(mean_pre_7, color=cores[1], linestyle='--', alpha=0.6, linewidth=2)
        ax.axvline(mean_pos_7, color=cores[1], linestyle='-', alpha=0.8, linewidth=2)
        
        # Texto com médias
        ax.text(0.05, 0.95, f'Médias:\nPré: {mean_pre_7:.1f}\nPós: {mean_pos_7:.1f}', 
                transform=ax.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                verticalalignment='top', fontsize=10)
    else:
        ax.text(0.5, 0.5, 'Dados insuficientes', ha='center', va='center', 
                transform=ax.transAxes, fontsize=14)
    
    ax.set_xlabel('Scores TDE', fontsize=12)
    ax.set_ylabel('Densidade', fontsize=12)
    ax.set_title('7º ano\nDistribuição de Densidade', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Distribuição de densidade - 8º ANO (inferior esquerdo)
    ax = axes[1, 0]
    data_pre_8 = df[df['GrupoTDE_Novo'] == grupos[2]]['Score_Pre']
    data_pos_8 = df[df['GrupoTDE_Novo'] == grupos[2]]['Score_Pos']
    
    if len(data_pre_8) > 0:
        ax.hist(data_pre_8, alpha=0.5, label='Pré-teste', color=cores[2], bins=12, density=True)
        ax.hist(data_pos_8, alpha=0.7, label='Pós-teste', color=cores[2], bins=12, density=True, hatch='//')
        
        # Adicionar médias como linhas verticais
        mean_pre_8 = data_pre_8.mean()
        mean_pos_8 = data_pos_8.mean()
        ax.axvline(mean_pre_8, color=cores[2], linestyle='--', alpha=0.6, linewidth=2)
        ax.axvline(mean_pos_8, color=cores[2], linestyle='-', alpha=0.8, linewidth=2)
        
        # Texto com médias
        ax.text(0.05, 0.95, f'Médias:\nPré: {mean_pre_8:.1f}\nPós: {mean_pos_8:.1f}', 
                transform=ax.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                verticalalignment='top', fontsize=10)
    else:
        ax.text(0.5, 0.5, 'Dados insuficientes', ha='center', va='center', 
                transform=ax.transAxes, fontsize=14)
    
    ax.set_xlabel('Scores TDE', fontsize=12)
    ax.set_ylabel('Densidade', fontsize=12)
    ax.set_title('8º ano\nDistribuição de Densidade', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. Distribuição de densidade - 9º ANO (inferior direito)
    ax = axes[1, 1]
    data_pre_9 = df[df['GrupoTDE_Novo'] == grupos[3]]['Score_Pre']
    data_pos_9 = df[df['GrupoTDE_Novo'] == grupos[3]]['Score_Pos']
    
    if len(data_pre_9) > 0:
        ax.hist(data_pre_9, alpha=0.5, label='Pré-teste', color=cores[3], bins=12, density=True)
        ax.hist(data_pos_9, alpha=0.7, label='Pós-teste', color=cores[3], bins=12, density=True, hatch='//')
        
        # Adicionar médias como linhas verticais
        mean_pre_9 = data_pre_9.mean()
        mean_pos_9 = data_pos_9.mean()
        ax.axvline(mean_pre_9, color=cores[3], linestyle='--', alpha=0.6, linewidth=2)
        ax.axvline(mean_pos_9, color=cores[3], linestyle='-', alpha=0.8, linewidth=2)
        
        # Texto com médias
        ax.text(0.05, 0.95, f'Médias:\nPré: {mean_pre_9:.1f}\nPós: {mean_pos_9:.1f}', 
                transform=ax.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                verticalalignment='top', fontsize=10)
    else:
        ax.text(0.5, 0.5, 'Dados insuficientes', ha='center', va='center', 
                transform=ax.transAxes, fontsize=14)
    
    ax.set_xlabel('Scores TDE', fontsize=12)
    ax.set_ylabel('Densidade', fontsize=12)
    ax.set_title('9º ano\nDistribuição de Densidade', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig_to_base64(fig)
    
    # Adicionar valores nas barras
    for i, (mel, pio, ig) in enumerate(zip(melhorou, piorou, igual)):
        if mel > 0:
            ax.text(i - width, mel + 2, f'{mel:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
        if pio > 0:
            ax.text(i, pio + 2, f'{pio:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
        if ig > 0:
            ax.text(i + width, ig + 2, f'{ig:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Configurar eixos
    ax.set_xlabel('Grupos', fontsize=12)
    ax.set_ylabel('Percentual (%)', fontsize=12)
    ax.set_title('Distribuição de Resultados TDE', fontsize=14, fontweight='bold', pad=20)
    
    # Configurar eixo Y fixo de 0% a 100%
    ax.set_ylim(0, 100)
    
    # Configurar xticks - apenas nomes dos grupos (A e B)
    grupos_simples = ['A (6°/7°)', 'B (8°/9°)']  # Nomes simples dos grupos
    ax.set_xticks(x)
    ax.set_xticklabels(grupos_simples, fontsize=12, fontweight='bold')
    
    # Posicionar legenda no canto superior direito, fora da área dos dados
    ax.legend(loc='upper right', bbox_to_anchor=(1.0, 0.98), fontsize=10, 
              frameon=True, fancybox=True, shadow=True)
    
    # Grid mais sutil
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Configurar yticks de 0% a 100% com intervalos de 10%
    yticks = np.arange(0, 101, 10)  # 0%, 10%, 20%, ..., 100%
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{int(y)}%' for y in yticks], fontsize=10)
    
    plt.tight_layout()
    return fig_to_base64(fig)

def gerar_grafico_heatmap_erros_tde(df: pd.DataFrame, tipo_teste: str = "pos") -> str:
    """Gera heatmap do percentual de erros por palavra e ano TDE."""
    
    # Analisar palavras por grupo
    palavras_geral = analisar_palavras_tde(df)
    palavras_6ano = analisar_palavras_tde(df, "6º ano")
    palavras_7ano = analisar_palavras_tde(df, "7º ano")
    palavras_8ano = analisar_palavras_tde(df, "8º ano")
    palavras_9ano = analisar_palavras_tde(df, "9º ano")
    
    if len(palavras_geral) == 0:
        fig, ax = plt.subplots(figsize=(8, 12))
        ax.text(0.5, 0.5, 'Dados insuficientes', ha='center', va='center', 
                transform=ax.transAxes, fontsize=16)
        return fig_to_base64(fig)
    
    # Selecionar top 20 palavras com maior melhora geral
    top_20_questoes = palavras_geral.nlargest(20, 'Melhora')['Questao']
    
    # Preparar dados para heatmap
    heatmap_data = []
    palavras_labels = []
    
    coluna_erro = 'Perc_Erro_Pos' if tipo_teste == "pos" else 'Perc_Erro_Pre'
    
    for questao in top_20_questoes:
        palavra = palavras_geral[palavras_geral['Questao'] == questao]['Palavra'].iloc[0]
        palavras_labels.append(palavra[:12] + '...' if len(palavra) > 12 else palavra)
        
        # Erros para cada ano
        erro_6 = palavras_6ano[palavras_6ano['Questao'] == questao][coluna_erro]
        erro_7 = palavras_7ano[palavras_7ano['Questao'] == questao][coluna_erro]
        erro_8 = palavras_8ano[palavras_8ano['Questao'] == questao][coluna_erro]
        erro_9 = palavras_9ano[palavras_9ano['Questao'] == questao][coluna_erro]
        
        erro_6_val = erro_6.iloc[0] if len(erro_6) > 0 else 0
        erro_7_val = erro_7.iloc[0] if len(erro_7) > 0 else 0
        erro_8_val = erro_8.iloc[0] if len(erro_8) > 0 else 0
        erro_9_val = erro_9.iloc[0] if len(erro_9) > 0 else 0
        
        heatmap_data.append([erro_6_val, erro_7_val, erro_8_val, erro_9_val])
    
    heatmap_array = np.array(heatmap_data)
    
    fig, ax = plt.subplots(figsize=(8, 12))
    
    im = ax.imshow(heatmap_array, cmap='Reds', aspect='auto')
    
    # Configurar eixos
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(['6º ano', '7º ano', '8º ano', '9º ano'])
    ax.set_yticks(range(len(palavras_labels)))
    ax.set_yticklabels(palavras_labels)
    
    teste_nome = "Pós-teste" if tipo_teste == "pos" else "Pré-teste"
    ax.set_title(f'Percentual de Erros TDE por Palavra e Grupo\n({teste_nome} - Top 20 palavras)', 
                 fontweight='bold', fontsize=14)
    
    # Adicionar valores
    for i in range(len(palavras_labels)):
        for j in range(4):
            valor = heatmap_array[i, j]
            text = ax.text(j, i, f'{valor:.1f}%',
                         ha="center", va="center", 
                         color="white" if valor > 50 else "black",
                         fontweight='bold', fontsize=10)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, label='Percentual de Erros (%)')
    cbar.ax.tick_params(labelsize=10)
    
    plt.tight_layout()
    return fig_to_base64(fig)

def gerar_graficos_escola_tde(escola_filtro=None):
    """Gera gráficos específicos para uma escola TDE e retorna como base64"""
    
    # Carregar dados da escola
    df, meta = carregar_dados_tde(escola_filtro=escola_filtro)
    
    if len(df) == 0:
        return {}
    
    # Gerar gráficos em memória
    graficos = {}
    
    try:
        # Gráfico pré vs pós
        graficos['prepos'] = gerar_grafico_prepos_tde(df)
        
        # NOVOS GRÁFICOS SOLICITADOS:
        
        # Palavras com maior melhora (Top 20 + Comparação Top 15)
        graficos['palavras_top'] = gerar_grafico_palavras_top_tde(df)
        
        # Comparação detalhada entre grupos (densidade + barras)
        graficos['comparacao_intergrupos'] = gerar_grafico_comparacao_intergrupos_tde(df)
        
        # Heatmap erros pós-teste
        graficos['heatmap_erros_pos'] = gerar_grafico_heatmap_erros_tde(df, "pos")
        
        # Heatmap erros pré-teste
        graficos['heatmap_erros_pre'] = gerar_grafico_heatmap_erros_tde(df, "pre")
        
    except Exception as e:
        print(f"Erro ao gerar gráficos para {escola_filtro}: {e}")
    
    return graficos

def gerar_dados_todas_escolas_tde():
    """Gera dados para todas as escolas TDE para o menu interativo"""
    escolas = obter_escolas_disponiveis_tde()
    dados_escolas = {}
    
    print("📊 Calculando dados TDE para todas as escolas...")
    
    for escola in escolas:
        try:
            print(f"   Processando: {escola}")
            
            # Carregar dados para esta escola
            escola_filtro = escola if escola != "Todas" else None
            df, meta = carregar_dados_tde(escola_filtro=escola_filtro)
            
            if len(df) == 0:
                continue
            
            # Calcular indicadores
            indicadores_geral = calcular_indicadores_tde(df)
            indicadores_6ano = calcular_indicadores_tde(df, "6º ano")
            indicadores_7ano = calcular_indicadores_tde(df, "7º ano")
            indicadores_8ano = calcular_indicadores_tde(df, "8º ano")
            indicadores_9ano = calcular_indicadores_tde(df, "9º ano")
            
            # Gerar gráficos específicos para esta escola
            print(f"     Gerando gráficos TDE para: {escola}")
            graficos = gerar_graficos_escola_tde(escola_filtro)
            
            dados_escolas[escola] = {
                'indicadores_geral': indicadores_geral,
                'indicadores_6ano': indicadores_6ano,
                'indicadores_7ano': indicadores_7ano,
                'indicadores_8ano': indicadores_8ano,
                'indicadores_9ano': indicadores_9ano,
                'graficos': graficos
            }
            
        except Exception as e:
            print(f"   ❌ Erro ao processar {escola}: {e}")
            continue
    
    return dados_escolas

# ======================
# Geração do HTML Interativo
# ======================

def _format_card_tde(label: str, value: str, extra: str = "", theme: str = "default") -> str:
    """Formata um card de indicador seguindo o padrão visual do vocabulário."""
    theme_class = {
        "default": "card",
        "green": "card green", 
        "red": "card red",
        "yellow": "card yellow",
        "blue": "card blue"
    }.get(theme, "card")
    
    desc_html = f"<div class='desc'>{extra}</div>" if extra else ""
    return f"""
    <div class="{theme_class}">
        <div class="card-label">{label}</div>
        <div class="valor">{value}</div>
        {desc_html}
    </div>
    """

def gerar_html_tde_interativo():
    """Gera o relatório HTML TDE interativo com menu de escolas"""
    
    # Gerar dados para todas as escolas (incluindo gráficos específicos)
    dados_escolas = gerar_dados_todas_escolas_tde()
    
    # Usar os gráficos da escola "Todas" como padrão
    figuras_b64 = dados_escolas.get('Todas', {}).get('graficos', {})
    
    # Converter dados para JSON
    import json
    dados_json = json.dumps(dados_escolas, ensure_ascii=False, indent=2)
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no" />
<meta name="format-detection" content="telephone=no" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black" />
<title>Relatório Visual TDE WordGen - Fase 3</title>
<style>
    :root {{
        --bg: #f5f6fa;
        --text: #2c3e50;
        --muted: #6b7280;
        --purple1: #6a11cb;
        --purple2: #8d36ff;
        --card-grad: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --green-grad: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        --red-grad: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);
        --yellow-grad: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        --blue-grad: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }}
    body {{
        margin: 0; 
        background: var(--bg); 
        color: var(--text); 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        -webkit-text-size-adjust: 100%;
    }}
    .header {{
        background: linear-gradient(120deg, var(--purple1) 0%, var(--purple2) 100%);
        color: #fff; 
        padding: 28px 18px; 
        box-shadow: 0 2px 14px rgba(0,0,0,.12);
    }}
    .header .title {{
        font-size: 26px; 
        font-weight: 700; 
        margin: 0;
    }}
    .header .subtitle {{
        font-size: 14px; 
        opacity: 0.95; 
        margin-top: 6px;
    }}
    .header .timestamp {{
        font-size: 12px; 
        opacity: 0.85; 
        margin-top: 4px;
    }}
    
    .menu-container {{
        background: #fff; 
        margin: 18px auto; 
        max-width: 1200px; 
        border-radius: 12px; 
        padding: 18px; 
        box-shadow: 0 4px 12px rgba(0,0,0,.08);
    }}
    .menu-title {{
        font-size: 18px; 
        font-weight: 600; 
        margin-bottom: 12px; 
        color: var(--purple1);
    }}
    .escola-select {{
        width: 100%; 
        padding: 12px; 
        border: 2px solid #e2e8f0; 
        border-radius: 8px; 
        font-size: 16px; 
        background: #fff; 
        cursor: pointer;
        transition: border-color 0.3s ease;
    }}
    .escola-select:focus {{
        outline: none; 
        border-color: var(--purple1);
    }}
    
    .container {{
        max-width: 1200px; 
        margin: 18px auto; 
        background: #fff; 
        border-radius: 12px; 
        padding: 22px; 
        box-shadow: 0 10px 24px rgba(0,0,0,.06);
    }}
    .cards {{
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); 
        gap: 12px; 
        margin-top: 16px;
    }}
    .card {{
        background: var(--card-grad); 
        color: #fff; 
        border-radius: 10px; 
        padding: 14px; 
        box-shadow: 0 4px 12px rgba(0,0,0,.12);
    }}
    .card.green {{ background: var(--green-grad); }}
    .card.red {{ background: var(--red-grad); }}
    .card.yellow {{ background: var(--yellow-grad); }}
    .card.blue {{ background: var(--blue-grad); }}
    .card .card-label {{ 
        font-size: 13px; 
        opacity: 0.95; 
    }}
    .card .valor {{ 
        font-size: 22px; 
        font-weight: 700; 
        margin-top: 6px; 
    }}
    .card .desc {{ 
        font-size: 11px; 
        opacity: 0.9; 
    }}

    h2.section {{
        margin-top: 22px; 
        font-size: 18px; 
        border-left: 4px solid var(--purple1); 
        padding-left: 10px; 
        color: #1f2937;
    }}
    .figs {{ 
        display: grid; 
        grid-template-columns: 1fr; 
        gap: 18px; 
        margin-top: 10px; 
    }}
    .figs-heatmap {{ 
        display: grid; 
        grid-template-columns: 1fr 1fr; 
        gap: 18px; 
        margin-top: 10px; 
    }}
    .fig {{ 
        background: #fafafa; 
        border: 1px solid #eee; 
        border-radius: 10px; 
        padding: 8px; 
    }}
    .figs-heatmap {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 10px; }}
    @media (max-width: 768px) {{ .figs-heatmap {{ grid-template-columns: 1fr; }} }}
    .fig img {{ 
        width: 100%; 
        height: auto; 
        border-radius: 6px; 
        max-width: 100%;
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        -khtml-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }}
    .fig .caption {{ 
        font-size: 12px; 
        color: var(--muted); 
        margin-top: 6px; 
        text-align: center; 
    }}

    .interp {{ 
        background: #fafafa; 
        border: 1px solid #eee; 
        border-radius: 10px; 
        padding: 14px; 
    }}
    .grupo-item {{ 
        background: #fff; 
        border: 1px solid #eee; 
        border-radius: 8px; 
        padding: 10px 12px; 
        margin: 10px 0; 
    }}
    .grupo-titulo {{ 
        font-weight: 600; 
    }}
    .grupo-detalhes {{ 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 
        gap: 6px; 
        color: #374151; 
        font-size: 13px; 
        margin-top: 6px; 
    }}
    .interpretacao-grupo {{ 
        margin-top: 10px; 
        padding: 8px; 
        background: #f8f9fa; 
        border-radius: 6px; 
        border-left: 3px solid var(--purple1); 
    }}
    .interpretacao-grupo p {{ 
        margin: 3px 0; 
        font-size: 12px; 
    }}
    .interpretacao-grupo strong {{ 
        color: var(--purple1); 
    }}

    .foot-note {{ 
        font-size: 12px; 
        color: var(--muted); 
        text-align: center; 
        margin-top: 16px; 
    }}

    @media (max-width: 768px) {{
        .container {{
            margin: 10px;
            padding: 15px;
        }}
        .cards {{
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 8px;
        }}
        .header .title {{
            font-size: 22px;
        }}
        .fig {{
            padding: 5px;
        }}
        .figs-heatmap {{
            grid-template-columns: 1fr;
        }}
    }}
</style>
</head>
<body>
    <div class="header">
        <div class="title">Relatório Visual TDE WordGen - Fase 3</div>
        <div class="subtitle">Teste de Escrita (Análise por anos: 6º, 7º, 8º e 9º anos). Análise pareada por estudante.</div>
        <div class="timestamp" id="timestamp">Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</div>
    </div>

    <div class="menu-container">
        <div class="menu-title">🏫 Selecionar Escola</div>
        <select class="escola-select" id="escolaSelect" onchange="atualizarDados()">
        </select>
    </div>

    <div class="container">
        <h2 class="section">📊 Indicadores Principais</h2>
        <div class="cards" id="cardsContainer">
        </div>

        <h2 class="section">📈 Análises Visuais</h2>
        <div class="figs">
            <div class="fig" id="grafico-prepos">
                <img src="{figuras_b64.get('prepos', '')}" alt="Comparação Pré vs Pós TDE" />
                <div class="caption">Comparação de scores e distribuição de mudanças por grupo etário TDE (4 análises: médias por grupo, distribuição de mudanças, tamanhos amostrais e effect sizes).</div>
            </div>
            <div class="fig" id="grafico-palavras-top">
                <img src="{figuras_b64.get('palavras_top', '')}" alt="Top Palavras TDE" />
                <div class="caption">Palavras com maior melhora na taxa de acerto TDE (Top 20 Geral + Comparação Top 15 por grupo).</div>
            </div>
            <div class="fig" id="grafico-comparacao-intergrupos">
                <img src="{figuras_b64.get('comparacao_intergrupos', '')}" alt="Comparação Detalhada Grupos TDE" />
                <div class="caption">Comparação detalhada entre grupos etários TDE (Densidade separada por grupo + Distribuição de resultados embaixo).</div>
            </div>
        </div>

        <h2 class="section">Percentual de Erros por Palavra e Grupos</h2>
        <div class="figs-heatmap">
            <div class="fig" id="grafico-heatmap-pre">
                <img src="{figuras_b64.get('heatmap_erros_pre', '')}" alt="Heatmap Erros Pré TDE" />
                <div class="caption">Percentual de erros no pré-teste (Top 20 palavras).</div>
            </div>
            <div class="fig" id="grafico-heatmap-pos">
                <img src="{figuras_b64.get('heatmap_erros_pos', '')}" alt="Heatmap Erros Pós TDE" />
                <div class="caption">Percentual de erros no pós-teste (Top 20 palavras).</div>
            </div>
        </div>

        <h2 class="section">Interpretação contextualizada por grupo etário</h2>
        <div class="interp">
            <p style="margin-top:0;color:#374151;">
                <strong>Referências Educacionais para TDE:</strong><br>
                • Hattie (2009): d≥0.4 indica impacto educacional visível<br>
                • Cohen (1988): d=0.5 para efeito médio em escrita<br>
                • Graham & Perin (2007): d≥0.6 para programas efetivos de ensino de escrita<br>
                • Intervenções de Letramento: d≥0.35 como threshold mínimo
            </p>
            <div id="interpretacaoContainer">
            </div>
        </div>

        <div class="foot-note">
            <p><strong>Metodologia TDE:</strong> Effect Size = Δ/SD(Pré). Grupos baseados na série escolar. 
            Categorias Cohen usando SD do pré-teste. Dados com valores faltantes foram removidos.</p>
        </div>
    </div>

<script>
const dadosEscolas = {dados_json};

function inicializar() {{
    const select = document.getElementById('escolaSelect');
    
    // Adicionar opções ao select
    Object.keys(dadosEscolas).forEach(escola => {{
        const option = document.createElement('option');
        option.value = escola;
        option.textContent = escola;
        select.appendChild(option);
    }});
    
    // Definir "Todas" como padrão
    select.value = 'Todas';
    atualizarDados();
}}

function atualizarDados() {{
    const escolaSelecionada = document.getElementById('escolaSelect').value;
    const dados = dadosEscolas[escolaSelecionada];
    
    if (!dados) return;
    
    atualizarCards(dados.indicadores_geral);
    atualizarInterpretacao(dados);
    atualizarGraficos(dados.graficos);
}}

function atualizarCards(indicadores) {{
    const container = document.getElementById('cardsContainer');
    
    container.innerHTML = `
        <div class="card">
            <div class="card-label">Palavras Testadas</div>
            <div class="valor">40</div>
            <div class="desc">questões de escrita</div>
        </div>
        <div class="card">
            <div class="card-label">Pontuação Máxima</div>
            <div class="valor">80</div>
            <div class="desc">pontos (2 por questão)</div>
        </div>
        <div class="card">
            <div class="card-label">Registros</div>
            <div class="valor">${{indicadores.n}}</div>
            <div class="desc">alunos após limpeza</div>
        </div>
        <div class="card">
            <div class="card-label">Média Pré</div>
            <div class="valor">${{indicadores.mean_pre.toFixed(1)}}</div>
            <div class="desc">pontos TDE</div>
        </div>
        <div class="card">
            <div class="card-label">Média Pós</div>
            <div class="valor">${{indicadores.mean_pos.toFixed(1)}}</div>
            <div class="desc">pontos TDE</div>
        </div>
        <div class="card ${{indicadores.mean_delta >= 0 ? 'green' : 'red'}}">
            <div class="card-label">Delta médio</div>
            <div class="valor">${{indicadores.mean_delta >= 0 ? '+' : ''}}${{indicadores.mean_delta.toFixed(1)}}</div>
            <div class="desc">pontos TDE</div>
        </div>
        <div class="card green">
            <div class="card-label">% Melhoraram</div>
            <div class="valor">${{indicadores.percent_improved.toFixed(1)}}%</div>
        </div>
        <div class="card red">
            <div class="card-label">% Pioraram</div>
            <div class="valor">${{indicadores.percent_worsened.toFixed(1)}}%</div>
        </div>
        <div class="card yellow">
            <div class="card-label">% Mantiveram</div>
            <div class="valor">${{indicadores.percent_unchanged.toFixed(1)}}%</div>
        </div>
        <div class="card blue">
            <div class="card-label">Effect Size</div>
            <div class="valor">${{indicadores.cohen_d_global.toFixed(3)}}</div>
        </div>
    `;
}}

function interpretarCohenD(d) {{
    const absD = Math.abs(d);
    const isPositive = d >= 0;
    let magnitude, hattieStatus, educStatus;
    
    if (absD >= 0.8) magnitude = "Grande";
    else if (absD >= 0.5) magnitude = "Médio";
    else if (absD >= 0.2) magnitude = "Pequeno";
    else magnitude = "Negligível";
    
    // Benchmark Hattie com direção
    if (absD >= 0.4) {{
        hattieStatus = isPositive ? 
            "✅ Acima do benchmark (d≥0.4) - Melhoria significativa" : 
            "🚨 Acima do benchmark (|d|≥0.4) - ALERTA: Deterioração significativa";
    }} else {{
        hattieStatus = isPositive ? 
            "⚠️ Abaixo do benchmark (d<0.4) - Melhoria limitada" : 
            "ℹ️ Abaixo do benchmark (|d|<0.4) - Deterioração limitada";
    }}
    
    // TDE com direção
    if (absD >= 0.35) {{
        educStatus = isPositive ? 
            "✅ Significativo para TDE (d≥0.35) - Ganho relevante" : 
            "🚨 Significativo para TDE (|d|≥0.35) - ALERTA: Perda relevante";
    }} else {{
        educStatus = isPositive ? 
            "⚠️ Abaixo do threshold (d<0.35) - Ganho limitado" : 
            "ℹ️ Abaixo do threshold (|d|<0.35) - Perda limitada";
    }}
    
    return {{ magnitude, hattieStatus, educStatus, isPositive }};
}}

function criarGrupoItem(indicadores, nomeGrupo) {{
    const d = indicadores.cohen_d_global;
    const interp = interpretarCohenD(d);
    
    return `
        <div class="grupo-item">
            <div class="grupo-titulo">${{nomeGrupo}} (N=${{indicadores.n}})</div>
            <div class="grupo-detalhes">
                <span>Média Pré: ${{indicadores.mean_pre.toFixed(1)}}</span>
                <span>Média Pós: ${{indicadores.mean_pos.toFixed(1)}}</span>
                <span>Delta: ${{indicadores.mean_delta >= 0 ? '+' : ''}}${{indicadores.mean_delta.toFixed(1)}}</span>
                <span>Cohen's d: ${{d.toFixed(3)}}</span>
                <span>% Melhoraram: ${{indicadores.percent_improved.toFixed(1)}}%</span>
            </div>
            <div class="interpretacao-grupo">
                <p><strong>Magnitude:</strong> ${{interp.magnitude}} (Cohen, 1988)</p>
                <p><strong>Benchmark Educacional:</strong> ${{interp.hattieStatus}} (Hattie, 2009)</p>
                <p><strong>TDE:</strong> ${{interp.educStatus}} (Adaptado de meta-análises)</p>
            </div>
        </div>
    `;
}}

function atualizarInterpretacao(dados) {{
    const container = document.getElementById('interpretacaoContainer');
    
    container.innerHTML = 
        criarGrupoItem(dados.indicadores_6ano, "6º ano") + 
        criarGrupoItem(dados.indicadores_7ano, "7º ano") +
        criarGrupoItem(dados.indicadores_8ano, "8º ano") +
        criarGrupoItem(dados.indicadores_9ano, "9º ano");
}}

function atualizarGraficos(graficos) {{
    if (!graficos) return;
    
    // Atualizar cada gráfico se existir
    const atualizarImg = (id, src) => {{
        const img = document.querySelector(`#${{id}} img`);
        if (img && src) {{
            img.src = src;
        }}
    }};
    
    atualizarImg('grafico-prepos', graficos.prepos);
    atualizarImg('grafico-palavras-top', graficos.palavras_top);
    atualizarImg('grafico-comparacao-intergrupos', graficos.comparacao_intergrupos);
    
    // Heatmaps na nova seção
    atualizarImg('grafico-heatmap-pre', graficos.heatmap_erros_pre);
    atualizarImg('grafico-heatmap-pos', graficos.heatmap_erros_pos);
}}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', inicializar);
</script>
</body>
</html>
"""
    return html

def _interpretacao_contexto_tde_html(indic: Dict[str, float]) -> str:
    """Gera seção de interpretação contextualizada para TDE."""
    d_global = indic.get("cohen_d_global", np.nan)
    
    mag_global = interpretar_magnitude(d_global) if np.isfinite(d_global) else "Indefinido"
    
    # Avaliação contra benchmarks
    benchmarks_html = ""
    for bench_name, bench_data in TDE_BENCHMARKS.items():
        threshold = bench_data['threshold']
        description = bench_data['description']
        
        if np.isfinite(d_global):
            status = "✓ Atende" if abs(d_global) >= threshold else "⚠ Não atende"
            cor = "color: #27ae60;" if abs(d_global) >= threshold else "color: #e74c3c;"
        else:
            status = "? Indefinido"
            cor = "color: #f39c12;"
        
        benchmarks_html += f"""
        <div style="margin: 5px 0;">
            <span style="{cor}"><strong>{status}</strong></span>
            <span>{description} (d≥{threshold})</span>
        </div>
        """
    
    return f"""
    <div class="grupo-item">
        <div class="grupo-titulo">Effect Size Global TDE: d = {d_global:.3f} (N={indic['n']})</div>
        <div class="grupo-detalhes">
            <span><strong>Magnitude:</strong> {mag_global}</span>
            <div style="margin-top: 10px;">
                <strong>Avaliação contra Benchmarks Educacionais:</strong>
                {benchmarks_html}
            </div>
        </div>
    </div>
    """

def gerar_html_tde(indic: Dict[str, float], meta: Dict, 
                   img_prepos: str, 
                   img_palavras_top: str, img_comparacao_intergrupos: str,
                   img_heatmap_pos: str, img_heatmap_pre: str, escola_filtro: str = None) -> str:
    """Gera o HTML completo do relatório TDE."""
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Título baseado no filtro
    titulo_filtro = f" - {escola_filtro}" if escola_filtro and escola_filtro != "Todas" else ""
    
    # Cards de indicadores com o padrão de 40 palavras
    cards_html = "".join([
        _format_card_tde("40 Palavras Grupo A", "20", "palavras teste escrita"),
        _format_card_tde("40 Palavras Grupo B", "20", "palavras teste escrita"),
        _format_card_tde("Estudantes", f"{indic['n']}", "após limpeza de dados"),
        _format_card_tde("Score Médio Pré", f"{indic['mean_pre']:.1f}", f"±{indic['std_pre']:.1f}"),
        _format_card_tde("Score Médio Pós", f"{indic['mean_pos']:.1f}", f"±{indic['std_pos']:.1f}"),
        _format_card_tde("Delta Médio", f"{indic['mean_delta']:.1f}", "pontos TDE", 
                         theme="green" if indic['mean_delta'] > 0 else "red"),
        _format_card_tde("% Melhoraram", f"{indic['percent_improved']:.1f}%", 
                         "delta > 0", theme="green"),
        _format_card_tde("% Pioraram", f"{indic['percent_worsened']:.1f}%", 
                         "delta < 0", theme="red"),
        _format_card_tde("% Mantiveram", f"{indic['percent_unchanged']:.1f}%", 
                         "delta = 0", theme="yellow"),
        _format_card_tde("Effect Size", f"{indic['cohen_d_global']:.3f}", 
                         interpretar_magnitude(indic['cohen_d_global']) if np.isfinite(indic['cohen_d_global']) else "N/A", 
                         theme="blue"),
    ])
    
    # Interpretação contextualizada
    interp_html = _interpretacao_contexto_tde_html(indic)
    
    # Informações dos grupos
    grupo_info = f"6º ano: {meta['n_6ano']} • 7º ano: {meta['n_7ano']} • 8º ano: {meta['n_8ano']} • 9º ano: {meta['n_9ano']}"
    
    # CSS com compatibilidade iOS
    css_styles = """
    :root {
        --bg: #f5f6fa;
        --text: #2c3e50;
        --muted: #6b7280;
        --purple1: #6a11cb;
        --purple2: #8d36ff;
        --card-grad: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --green-grad: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        --red-grad: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);
        --yellow-grad: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        --blue-grad: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    body {
        margin: 0; 
        background: var(--bg); 
        color: var(--text); 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        -webkit-text-size-adjust: 100%;
    }
    .header {
        background: linear-gradient(120deg, var(--purple1) 0%, var(--purple2) 100%);
        color: #fff; 
        padding: 28px 18px; 
        box-shadow: 0 2px 14px rgba(0,0,0,.12);
    }
    .header .title {
        font-size: 26px; 
        font-weight: 700; 
        margin: 0;
    }
    .header .subtitle {
        font-size: 14px; 
        opacity: 0.95; 
        margin-top: 6px;
    }
    .header .timestamp {
        font-size: 12px; 
        opacity: 0.85; 
        margin-top: 4px;
    }
    .container {
        max-width: 1200px; 
        margin: 18px auto; 
        background: #fff; 
        border-radius: 12px; 
        padding: 22px; 
        box-shadow: 0 10px 24px rgba(0,0,0,.06);
    }
    .cards {
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); 
        gap: 12px; 
        margin-top: 16px;
    }
    .card {
        background: var(--card-grad); 
        color: #fff; 
        border-radius: 10px; 
        padding: 14px; 
        box-shadow: 0 4px 12px rgba(0,0,0,.12);
    }
    .card.green { background: var(--green-grad); }
    .card.red { background: var(--red-grad); }
    .card.yellow { background: var(--yellow-grad); }
    .card.blue { background: var(--blue-grad); }
    .card .card-label { 
        font-size: 13px; 
        opacity: 0.95; 
    }
    .card .valor { 
        font-size: 22px; 
        font-weight: 700; 
        margin-top: 6px; 
    }
    .card .desc { 
        font-size: 11px; 
        opacity: 0.9; 
    }

    h2.section {
        margin-top: 22px; 
        font-size: 18px; 
        border-left: 4px solid var(--purple1); 
        padding-left: 10px; 
        color: #1f2937;
    }
    .figs { 
        display: grid; 
        grid-template-columns: 1fr; 
        gap: 18px; 
        margin-top: 10px; 
    }
    .figs-heatmap { 
        display: grid; 
        grid-template-columns: 1fr 1fr; 
        gap: 18px; 
        margin-top: 10px; 
    }
    .fig { 
        background: #fafafa; 
        border: 1px solid #eee; 
        border-radius: 10px; 
        padding: 8px; 
    }
    .figs-heatmap { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 10px; }
    @media (max-width: 768px) { .figs-heatmap { grid-template-columns: 1fr; } }
    .fig img { 
        width: 100%; 
        height: auto; 
        border-radius: 6px; 
        max-width: 100%;
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        -khtml-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }
    .fig .caption { 
        font-size: 12px; 
        color: var(--muted); 
        margin-top: 6px; 
        text-align: center; 
    }

    .interp { 
        background: #fafafa; 
        border: 1px solid #eee; 
        border-radius: 10px; 
        padding: 14px; 
    }
    .grupo-item { 
        background: #fff; 
        border: 1px solid #eee; 
        border-radius: 8px; 
        padding: 10px 12px; 
        margin: 10px 0; 
    }
    .grupo-titulo { 
        font-weight: 600; 
    }
    .grupo-detalhes { 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 
        gap: 6px; 
        color: #374151; 
        font-size: 13px; 
        margin-top: 6px; 
    }

    .filtro-info {
        background: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
        font-size: 14px;
    }

    .foot-note { 
        font-size: 12px; 
        color: var(--muted); 
        text-align: center; 
        margin-top: 16px; 
    }

    @media (max-width: 768px) {
        .container {
            margin: 10px;
            padding: 15px;
        }
        .cards {
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 8px;
        }
        .header .title {
            font-size: 22px;
        }
        .fig {
            padding: 5px;
        }
        .figs-heatmap {
            grid-template-columns: 1fr;
        }
    }
    """
    
    # Informação sobre filtro
    filtro_info_html = ""
    if escola_filtro and escola_filtro != "Todas":
        filtro_info_html = f"""
        <div class="filtro-info">
            <strong>📍 Filtro Ativo:</strong> Dados filtrados para a escola "{escola_filtro}"
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no" />
<meta name="format-detection" content="telephone=no" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black" />
<title>Relatório Visual TDE WordGen - Fase 3{titulo_filtro}</title>
<style>
{css_styles}
</style>
</head>
<body>
    <div class="header">
        <div class="title">Relatório Visual TDE WordGen{titulo_filtro}</div>
        <div class="subtitle">Teste de Escrita – Fase 3 (Pré vs Pós-teste). {grupo_info}</div>
        <div class="timestamp">Gerado em: {now}</div>
    </div>

    <div class="container">
        {filtro_info_html}
        
        <h2 class="section">📊 Indicadores Principais</h2>
        <div class="cards">
            {cards_html}
        </div>

        <h2 class="section">📈 Análises Visuais</h2>
        <div class="figs">
            <div class="fig">
                <img src="{img_prepos}" alt="Comparação Pré vs Pós TDE" />
                <div class="caption">Comparação de scores e distribuição de mudanças por grupo etário TDE (4 análises: médias por grupo, distribuição de mudanças, tamanhos amostrais e effect sizes).</div>
            </div>
            <div class="fig">
                <img src="{img_palavras_top}" alt="Top Palavras TDE" />
                <div class="caption">Palavras com maior melhora na taxa de acerto TDE (Top 20 Geral + Comparação Top 15 por grupo).</div>
            </div>
            <div class="fig">
                <img src="{img_comparacao_intergrupos}" alt="Comparação Detalhada Grupos TDE" />
                <div class="caption">Comparação detalhada entre grupos etários TDE (Densidade separada por grupo + Distribuição de resultados embaixo).</div>
            </div>
        </div>

        <h2 class="section">Percentual de Erros por Palavra e Grupos</h2>
        <div class="figs-heatmap">
            <div class="fig">
                <img src="{img_heatmap_pre}" alt="Heatmap Erros Pré TDE" />
                <div class="caption">Percentual de erros no pré-teste (Top 20 palavras).</div>
            </div>
            <div class="fig">
                <img src="{img_heatmap_pos}" alt="Heatmap Erros Pós TDE" />
                <div class="caption">Percentual de erros no pós-teste (Top 20 palavras).</div>
            </div>
        </div>

        <h2 class="section">🎯 Interpretação Contextualizada</h2>
        <div class="interp">
            <p style="margin-top:0;color:#374151;">
                <strong>Referências Educacionais para TDE:</strong><br>
                • Hattie (2009): d≥0.4 indica impacto educacional visível<br>
                • Cohen (1988): d=0.5 para efeito médio em escrita<br>
                • Graham & Perin (2007): d≥0.6 para programas efetivos de ensino de escrita<br>
                • Intervenções de Letramento: d≥0.35 como threshold mínimo
            </p>
            {interp_html}
        </div>

        <div class="foot-note">
            <p><strong>Metodologia TDE:</strong> Effect Size = Δ/SD(Pré). Grupos baseados na série escolar. 
            Categorias Cohen usando SD do pré-teste. Dados com valores faltantes foram removidos. 
            N total processado: {indic['n']} estudantes.</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

# ======================
# Função Principal
# ======================

def gerar_relatorio_tde(escola_filtro: str = None, output_path: str = None) -> str:
    """Gera o relatório visual completo para TDE."""
    
    if output_path is None:
        if escola_filtro and escola_filtro != "Todas":
            escola_clean = escola_filtro.replace(" ", "_").replace("/", "_")
            output_path = str(DATA_DIR / f"relatorio_visual_TDE_fase3_{escola_clean}.html")
        else:
            output_path = str(HTML_OUT)
    
    print("="*80)
    print("🎯 RELATÓRIO VISUAL TDE - WORDGEN FASE 3")
    print("="*80)
    
    # Carregar e preparar dados
    df, meta = carregar_dados_tde(escola_filtro=escola_filtro)
    
    # Calcular indicadores
    indic = calcular_indicadores_tde(df)
    
    print("📊 GERANDO GRÁFICOS...")
    
    # Gerar gráficos originais
    img_prepos = gerar_grafico_prepos_tde(df)
    
    # Gerar novos gráficos solicitados
    img_palavras_top = gerar_grafico_palavras_top_tde(df)
    img_comparacao_intergrupos = gerar_grafico_comparacao_intergrupos_tde(df)
    img_heatmap_pos = gerar_grafico_heatmap_erros_tde(df, "pos")
    img_heatmap_pre = gerar_grafico_heatmap_erros_tde(df, "pre")
    
    print("🎨 RENDERIZANDO HTML...")
    
    # Gerar HTML
    html = gerar_html_tde(indic, meta, img_prepos, 
                         img_palavras_top, img_comparacao_intergrupos,
                         img_heatmap_pos, img_heatmap_pre, escola_filtro)
    
    # Salvar arquivo
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print("="*80)
    print("✅ RELATÓRIO TDE GERADO COM SUCESSO!")
    print("="*80)
    print(f"📁 Arquivo: {output_path}")
    print(f"📊 Estudantes processados: {indic['n']}")
    print(f"📈 Effect Size Global: {indic['cohen_d_global']:.3f}")
    print(f"📍 Filtro escola: {escola_filtro or 'Todas'}")
    print("="*80)
    
    return output_path

# ======================
# Interface CLI
# ======================

def main():
    """Interface de linha de comando."""
    parser = argparse.ArgumentParser(
        description='Gera relatório visual interativo para dados TDE WordGen Fase 3'
    )
    parser.add_argument('--escola', type=str, default=None,
                       help='Filtrar por escola específica')
    parser.add_argument('--output', type=str, default=None,
                       help='Caminho do arquivo HTML de saída')
    parser.add_argument('--listar-escolas', action='store_true',
                       help='Lista todas as escolas disponíveis')
    parser.add_argument('--interativo', action='store_true',
                       help='Gera relatório interativo com menu de escolas')
    
    args = parser.parse_args()
    
    if args.listar_escolas:
        print("🏫 ESCOLAS DISPONÍVEIS:")
        escolas = obter_escolas_disponiveis_tde()
        for i, escola in enumerate(escolas, 1):
            if escola != "Todas":
                df, _ = carregar_dados_tde(escola_filtro=escola)
                n_estudantes = len(df)
                print(f"   {i}. {escola} (N={n_estudantes})")
        return
    
    if args.interativo:
        print("🔄 Gerando relatório TDE interativo...")
        html_content = gerar_html_tde_interativo()
        arquivo_saida = str(DATA_DIR / "relatorio_visual_TDE_fase3_interativo.html")
        
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Relatório interativo TDE salvo: {arquivo_saida}")
        print(f"🌐 Abra o arquivo em um navegador para usar o menu de seleção")
        return
    
    # Gerar relatório padrão
    arquivo_saida = gerar_relatorio_tde(escola_filtro=args.escola, output_path=args.output)
    
    print(f"\n🌐 Para visualizar o relatório, abra o arquivo:")
    print(f"   {arquivo_saida}")

if __name__ == "__main__":
    main()
