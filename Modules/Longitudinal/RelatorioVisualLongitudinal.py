#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIO VISUAL LONGITUDINAL - WORDGEN
Interface visual interativa para análise longitudinal de dados TDE e Vocabulário

Baseado na metodologia dos relatórios das Fases 2 e 3 com adaptações para 
análise longitudinal das Fases 2, 3 e 4.

Autor: Sistema de Análise WordGen
Data: 2024
"""

import os
import io
import base64
import pathlib
import json
from typing import List, Tuple, Dict, Any
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

plt.switch_backend("Agg")
sns.set_theme(style="whitegrid")

# ======================
# Configurações de Paths
# ======================
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
DATA_DIR = BASE_DIR / "Data"
LONGITUDINAL_DIR = BASE_DIR / "Modules" / "Longitudinal" / "Data"
FIG_DIR = LONGITUDINAL_DIR / "figures"

# Arquivos de dados longitudinais
CSV_LONGITUDINAL_TDE = LONGITUDINAL_DIR / "dados_longitudinais_TDE.csv"
CSV_LONGITUDINAL_VOCAB = LONGITUDINAL_DIR / "dados_longitudinais_Vocabulario.json"
JSON_RESUMO_TDE = LONGITUDINAL_DIR / "resumo_longitudinal_TDE.json"
JSON_RESUMO_VOCAB = LONGITUDINAL_DIR / "resumo_longitudinal_Vocabulario.json"

# Arquivo de saída
OUTPUT_HTML = LONGITUDINAL_DIR / "relatorio_visual_longitudinal.html"

# Figuras longitudinais
FIG_DEMOGRAFICO = FIG_DIR / "longitudinal_demografico.png"
FIG_EVOLUCAO_FASES = FIG_DIR / "longitudinal_evolucao_fases.png"
FIG_ESCOLAS_PERFORMANCE = FIG_DIR / "longitudinal_escolas_performance.png"
FIG_MELHORIAS_TURMAS = FIG_DIR / "longitudinal_melhorias_turmas.png"
FIG_DISTRIBUICAO_DELTAS = FIG_DIR / "longitudinal_distribuicao_deltas.png"
FIG_HEATMAP_ESCOLAS = FIG_DIR / "longitudinal_heatmap_escolas.png"

plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 120,
    "axes.grid": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ======================
# Funções de utilidade
# ======================

def img_to_base64(fig):
    """Converte figura matplotlib para base64"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white', dpi=120)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_base64

def carregar_dados_longitudinais():
    """Carrega dados longitudinais consolidados"""
    try:
        df_tde = pd.read_csv(CSV_LONGITUDINAL_TDE) if CSV_LONGITUDINAL_TDE.exists() else pd.DataFrame()
        
        with open(JSON_RESUMO_TDE, 'r', encoding='utf-8') as f:
            resumo_tde = json.load(f) if JSON_RESUMO_TDE.exists() else {}
            
        with open(JSON_RESUMO_VOCAB, 'r', encoding='utf-8') as f:
            resumo_vocab = json.load(f) if JSON_RESUMO_VOCAB.exists() else {}
            
        print(f"✅ Dados carregados: {len(df_tde)} registros TDE")
        return df_tde, resumo_tde, resumo_vocab
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame(), {}, {}

def interpretar_cohen_d(d):
    """Interpreta o Cohen's d conforme benchmarks educacionais"""
    abs_d = abs(d)
    is_positive = d >= 0
    
    if abs_d >= 0.8:
        magnitude = "Grande"
    elif abs_d >= 0.5:
        magnitude = "Médio"
    elif abs_d >= 0.2:
        magnitude = "Pequeno"
    else:
        magnitude = "Negligível"
    
    if abs_d >= 0.4:
        if is_positive:
            status = "✅ Acima do benchmark (d≥0.4) - Melhoria significativa"
        else:
            status = "🚨 Acima do benchmark (|d|≥0.4) - ALERTA: Deterioração significativa"
    else:
        if is_positive:
            status = "⚠️ Abaixo do benchmark (d<0.4) - Melhoria limitada"
        else:
            status = "ℹ️ Abaixo do benchmark (|d|<0.4) - Deterioração limitada"
    
    return {
        'magnitude': magnitude,
        'status': status,
        'valor': d,
        'interpretacao': f"Cohen's d = {d:.3f} ({magnitude})"
    }

# ======================
# Funções de Visualização
# ======================

def criar_grafico_demografico(resumo_tde, resumo_vocab):
    """Cria gráfico demográfico longitudinal"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Perfil Demográfico Longitudinal - Fases 2, 3 e 4', fontsize=16, fontweight='bold')
    
    # Dados demográficos TDE
    if 'perfil_demografico' in resumo_tde:
        demo_tde = resumo_tde['perfil_demografico']
        
        # Distribuição por sexo - TDE
        if 'distribuicao_sexo' in demo_tde:
            sexo_data = demo_tde['distribuicao_sexo']
            axes[0,0].pie(sexo_data.values(), labels=sexo_data.keys(), autopct='%1.1f%%', 
                         colors=['#FF6B6B', '#4ECDC4'])
            axes[0,0].set_title('Distribuição por Sexo - TDE', fontweight='bold')
        
        # Número de escolas e turmas - TDE
        if 'escolas_unicas' in demo_tde and 'turmas_unicas' in demo_tde:
            categorias = ['Escolas', 'Turmas']
            valores = [demo_tde['escolas_unicas'], demo_tde['turmas_unicas']]
            axes[0,1].bar(categorias, valores, color=['#95E1D3', '#F8C8DC'])
            axes[0,1].set_title('Escolas e Turmas Participantes - TDE', fontweight='bold')
            axes[0,1].set_ylabel('Quantidade')
            
            # Adicionar valores nas barras
            for i, v in enumerate(valores):
                axes[0,1].text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    # Dados demográficos Vocabulário
    if 'perfil_demografico' in resumo_vocab:
        demo_vocab = resumo_vocab['perfil_demografico']
        
        # Distribuição por sexo - Vocabulário
        if 'distribuicao_sexo' in demo_vocab:
            sexo_data = demo_vocab['distribuicao_sexo']
            axes[1,0].pie(sexo_data.values(), labels=sexo_data.keys(), autopct='%1.1f%%', 
                         colors=['#FF6B6B', '#4ECDC4'])
            axes[1,0].set_title('Distribuição por Sexo - Vocabulário', fontweight='bold')
        
        # Número de escolas e turmas - Vocabulário
        if 'escolas_unicas' in demo_vocab and 'turmas_unicas' in demo_vocab:
            categorias = ['Escolas', 'Turmas']
            valores = [demo_vocab['escolas_unicas'], demo_vocab['turmas_unicas']]
            axes[1,1].bar(categorias, valores, color=['#95E1D3', '#F8C8DC'])
            axes[1,1].set_title('Escolas e Turmas Participantes - Vocabulário', fontweight='bold')
            axes[1,1].set_ylabel('Quantidade')
            
            # Adicionar valores nas barras
            for i, v in enumerate(valores):
                axes[1,1].text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig

def criar_grafico_evolucao_fases(df_tde, resumo_tde):
    """Cria gráfico de evolução por fases"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Evolução de Performance por Fases', fontsize=16, fontweight='bold')
    
    if not df_tde.empty:
        # Evolução dos scores médios
        fase_stats = df_tde.groupby('Fase').agg({
            'Score_Pre': 'mean',
            'Score_Pos': 'mean',
            'Delta': 'mean',
            'Melhoria': lambda x: x.mean() * 100
        }).round(2)
        
        # Gráfico de barras - Scores Pré e Pós
        x = fase_stats.index
        width = 0.35
        x_pos = np.arange(len(x))
        
        axes[0,0].bar(x_pos - width/2, fase_stats['Score_Pre'], width, 
                     label='Pré-teste', color='#FFB6C1', alpha=0.8)
        axes[0,0].bar(x_pos + width/2, fase_stats['Score_Pos'], width, 
                     label='Pós-teste', color='#98FB98', alpha=0.8)
        
        axes[0,0].set_xlabel('Fase')
        axes[0,0].set_ylabel('Score Médio')
        axes[0,0].set_title('Scores Médios por Fase - TDE', fontweight='bold')
        axes[0,0].set_xticks(x_pos)
        axes[0,0].set_xticklabels([f'Fase {i}' for i in x])
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for i, (pre, pos) in enumerate(zip(fase_stats['Score_Pre'], fase_stats['Score_Pos'])):
            axes[0,0].text(i - width/2, pre + 0.5, f'{pre:.1f}', ha='center', va='bottom', fontsize=9)
            axes[0,0].text(i + width/2, pos + 0.5, f'{pos:.1f}', ha='center', va='bottom', fontsize=9)
        
        # Gráfico de linha - Delta médio
        axes[0,1].plot(x, fase_stats['Delta'], marker='o', linewidth=3, markersize=8, color='#FF6B6B')
        axes[0,1].set_xlabel('Fase')
        axes[0,1].set_ylabel('Delta Médio (Pós - Pré)')
        axes[0,1].set_title('Evolução do Delta Médio por Fase', fontweight='bold')
        axes[0,1].grid(True, alpha=0.3)
        
        # Adicionar valores nos pontos
        for i, delta in enumerate(fase_stats['Delta']):
            axes[0,1].text(x[i], delta + 0.2, f'{delta:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Gráfico de barras - Taxa de melhoria
        bars = axes[1,0].bar(x, fase_stats['Melhoria'], color='#4ECDC4', alpha=0.8)
        axes[1,0].set_xlabel('Fase')
        axes[1,0].set_ylabel('Taxa de Melhoria (%)')
        axes[1,0].set_title('Taxa de Melhoria por Fase', fontweight='bold')
        axes[1,0].grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, valor in zip(bars, fase_stats['Melhoria']):
            height = bar.get_height()
            axes[1,0].text(bar.get_x() + bar.get_width()/2., height + 1,
                          f'{valor:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Boxplot dos deltas por fase
        fase_deltas = [df_tde[df_tde['Fase'] == f]['Delta'].values for f in sorted(df_tde['Fase'].unique())]
        box_plot = axes[1,1].boxplot(fase_deltas, labels=[f'Fase {i}' for i in sorted(df_tde['Fase'].unique())], 
                                   patch_artist=True)
        
        # Colorir boxplots
        colors = ['#FFB6C1', '#98FB98', '#87CEEB']
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        axes[1,1].set_ylabel('Delta (Pós - Pré)')
        axes[1,1].set_title('Distribuição dos Deltas por Fase', fontweight='bold')
        axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def criar_grafico_performance_escolas(df_tde, resumo_tde):
    """Cria gráfico de performance por escola"""
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle('Performance por Escola - Análise Longitudinal', fontsize=16, fontweight='bold')
    
    if not df_tde.empty and 'analise_por_escola' in resumo_tde:
        escola_stats = resumo_tde['analise_por_escola']
        
        # Preparar dados
        escolas = list(escola_stats.keys())[:10]  # Limitando a 10 escolas para visualização
        deltas_medios = [escola_stats[escola]['delta_medio'] for escola in escolas]
        taxas_melhoria = [escola_stats[escola]['taxa_melhoria'] for escola in escolas]
        scores_pre = [escola_stats[escola]['score_pre_medio'] for escola in escolas]
        scores_pos = [escola_stats[escola]['score_pos_medio'] for escola in escolas]
        
        # Encurtando nomes das escolas para visualização
        escolas_curtos = [escola.replace('EMEB ', '').replace('ESCOLA ', '')[:20] + '...' 
                         if len(escola) > 20 else escola.replace('EMEB ', '').replace('ESCOLA ', '') 
                         for escola in escolas]
        
        # Delta médio por escola
        bars1 = axes[0,0].barh(escolas_curtos, deltas_medios, color='#FF6B6B', alpha=0.7)
        axes[0,0].set_xlabel('Delta Médio (Pós - Pré)')
        axes[0,0].set_title('Delta Médio por Escola', fontweight='bold')
        axes[0,0].grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, valor in zip(bars1, deltas_medios):
            width = bar.get_width()
            axes[0,0].text(width + 0.1, bar.get_y() + bar.get_height()/2,
                          f'{valor:.1f}', ha='left', va='center', fontsize=9)
        
        # Taxa de melhoria por escola
        bars2 = axes[0,1].barh(escolas_curtos, taxas_melhoria, color='#4ECDC4', alpha=0.7)
        axes[0,1].set_xlabel('Taxa de Melhoria (%)')
        axes[0,1].set_title('Taxa de Melhoria por Escola', fontweight='bold')
        axes[0,1].grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, valor in zip(bars2, taxas_melhoria):
            width = bar.get_width()
            axes[0,1].text(width + 1, bar.get_y() + bar.get_height()/2,
                          f'{valor:.1f}%', ha='left', va='center', fontsize=9)
        
        # Comparação Pré vs Pós
        y_pos = np.arange(len(escolas_curtos))
        width = 0.35
        
        axes[1,0].barh(y_pos - width/2, scores_pre, width, label='Pré-teste', 
                      color='#FFB6C1', alpha=0.8)
        axes[1,0].barh(y_pos + width/2, scores_pos, width, label='Pós-teste', 
                      color='#98FB98', alpha=0.8)
        
        axes[1,0].set_xlabel('Score Médio')
        axes[1,0].set_title('Scores Pré vs Pós por Escola', fontweight='bold')
        axes[1,0].set_yticks(y_pos)
        axes[1,0].set_yticklabels(escolas_curtos)
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
        
        # Scatter plot: Delta vs Taxa de Melhoria
        scatter = axes[1,1].scatter(deltas_medios, taxas_melhoria, 
                                  s=100, alpha=0.6, c=range(len(escolas)), cmap='viridis')
        axes[1,1].set_xlabel('Delta Médio')
        axes[1,1].set_ylabel('Taxa de Melhoria (%)')
        axes[1,1].set_title('Relação Delta vs Taxa de Melhoria', fontweight='bold')
        axes[1,1].grid(True, alpha=0.3)
        
        # Adicionar linha de tendência
        if len(deltas_medios) > 1:
            z = np.polyfit(deltas_medios, taxas_melhoria, 1)
            p = np.poly1d(z)
            axes[1,1].plot(sorted(deltas_medios), p(sorted(deltas_medios)), "r--", alpha=0.8)
    
    plt.tight_layout()
    return fig

def criar_heatmap_escolas(df_tde):
    """Cria heatmap de performance por escola e fase"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    if not df_tde.empty:
        # Criar tabela pivot
        pivot_data = df_tde.groupby(['Escola', 'Fase'])['Delta'].mean().unstack(fill_value=0)
        
        # Limitar a 15 escolas para visualização
        if len(pivot_data) > 15:
            # Ordenar por delta médio geral e pegar as top 15
            escola_medias = pivot_data.mean(axis=1).sort_values(ascending=False)
            pivot_data = pivot_data.loc[escola_medias.head(15).index]
        
        # Encurtar nomes das escolas
        pivot_data.index = [nome.replace('EMEB ', '').replace('ESCOLA ', '')[:30] + '...' 
                           if len(nome) > 30 else nome.replace('EMEB ', '').replace('ESCOLA ', '') 
                           for nome in pivot_data.index]
        
        # Criar heatmap
        sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='RdYlGn', center=0,
                   cbar_kws={'label': 'Delta Médio (Pós - Pré)'}, ax=ax)
        
        ax.set_title('Heatmap: Delta Médio por Escola e Fase', fontsize=14, fontweight='bold')
        ax.set_xlabel('Fase', fontweight='bold')
        ax.set_ylabel('Escola', fontweight='bold')
        
        # Ajustar layout
        plt.setp(ax.get_xticklabels(), rotation=0)
        plt.setp(ax.get_yticklabels(), rotation=0)
    
    plt.tight_layout()
    return fig

def gerar_html_relatorio(df_tde, resumo_tde, resumo_vocab):
    """Gera o relatório HTML longitudinal"""
    
    # Criar todas as visualizações
    print("📊 Gerando visualizações...")
    
    fig_demografico = criar_grafico_demografico(resumo_tde, resumo_vocab)
    img_demografico = img_to_base64(fig_demografico)
    
    fig_evolucao = criar_grafico_evolucao_fases(df_tde, resumo_tde)
    img_evolucao = img_to_base64(fig_evolucao)
    
    fig_escolas = criar_grafico_performance_escolas(df_tde, resumo_tde)
    img_escolas = img_to_base64(fig_escolas)
    
    fig_heatmap = criar_heatmap_escolas(df_tde)
    img_heatmap = img_to_base64(fig_heatmap)
    
    # Estatísticas principais
    stats_gerais_tde = resumo_tde.get('performance_geral', {})
    stats_gerais_vocab = resumo_vocab.get('performance_geral', {})
    
    # Template HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório Longitudinal WordGen - Fases 2, 3 e 4</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f7fa;
                color: #333;
                line-height: 1.6;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }}
            .header p {{
                margin: 10px 0 0 0;
                font-size: 1.2em;
                opacity: 0.9;
            }}
            .content {{
                padding: 30px;
            }}
            .section {{
                margin-bottom: 40px;
                border-left: 4px solid #667eea;
                padding-left: 20px;
            }}
            .section h2 {{
                color: #667eea;
                margin-top: 0;
                font-size: 1.8em;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: #f8f9ff;
                border: 1px solid #e1e5f7;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                transition: transform 0.2s;
            }}
            .stat-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            .stat-number {{
                font-size: 2.5em;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 5px;
            }}
            .stat-label {{
                color: #666;
                font-weight: 500;
            }}
            .chart-container {{
                text-align: center;
                margin: 30px 0;
                padding: 20px;
                background: #fafbff;
                border-radius: 8px;
                border: 1px solid #e1e5f7;
            }}
            .chart-container img {{
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .insight-box {{
                background: #e8f4fd;
                border-left: 4px solid #2196F3;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .warning-box {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .success-box {{
                background: #d4edda;
                border-left: 4px solid #28a745;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                border-top: 1px solid #dee2e6;
                color: #6c757d;
            }}
            @media (max-width: 768px) {{
                .stats-grid {{
                    grid-template-columns: 1fr;
                }}
                .header h1 {{
                    font-size: 2em;
                }}
                .content {{
                    padding: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Relatório Longitudinal WordGen</h1>
                <p>Análise Longitudinal das Fases 2, 3 e 4 - TDE e Vocabulário</p>
                <p>Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            </div>
            
            <div class="content">
                <div class="section">
                    <h2>📈 Resumo Executivo</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{resumo_tde.get('total_estudantes', 0)}</div>
                            <div class="stat-label">Estudantes TDE</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{resumo_vocab.get('total_estudantes', 0)}</div>
                            <div class="stat-label">Estudantes Vocabulário</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{resumo_tde.get('perfil_demografico', {}).get('escolas_unicas', 0)}</div>
                            <div class="stat-label">Escolas Participantes</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{len(resumo_tde.get('fases_analisadas', []))}</div>
                            <div class="stat-label">Fases Analisadas</div>
                        </div>
                    </div>
                    
                    <div class="success-box">
                        <strong>🎯 Principal Resultado:</strong> 
                        Taxa de melhoria TDE: <strong>{stats_gerais_tde.get('taxa_melhoria', 0):.1f}%</strong> | 
                        Taxa de melhoria Vocabulário: <strong>{stats_gerais_vocab.get('taxa_melhoria', 0):.1f}%</strong>
                    </div>
                </div>
                
                <div class="section">
                    <h2>👥 Perfil Demográfico</h2>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{img_demografico}" alt="Perfil Demográfico">
                    </div>
                    
                    <div class="insight-box">
                        <strong>💡 Insights Demográficos:</strong><br>
                        • <strong>Escolas participantes:</strong> {resumo_tde.get('perfil_demografico', {}).get('escolas_unicas', 0)} escolas no TDE<br>
                        • <strong>Distribuição de gênero:</strong> Análise equilibrada entre diferentes perfis<br>
                        • <strong>Abrangência:</strong> {resumo_tde.get('perfil_demografico', {}).get('turmas_unicas', 0)} turmas no total
                    </div>
                </div>
                
                <div class="section">
                    <h2>📊 Evolução por Fases</h2>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{img_evolucao}" alt="Evolução por Fases">
                    </div>
                    
                    <div class="insight-box">
                        <strong>📈 Análise de Evolução:</strong><br>
                        • <strong>Delta médio geral:</strong> {stats_gerais_tde.get('delta_medio', 0):.2f} pontos<br>
                        • <strong>Score pré-teste médio:</strong> {stats_gerais_tde.get('score_pre_medio', 0):.1f} pontos<br>
                        • <strong>Score pós-teste médio:</strong> {stats_gerais_tde.get('score_pos_medio', 0):.1f} pontos<br>
                        • <strong>Tendência:</strong> {'Positiva' if stats_gerais_tde.get('delta_medio', 0) > 0 else 'Estável' if stats_gerais_tde.get('delta_medio', 0) == 0 else 'Negativa'}
                    </div>
                </div>
                
                <div class="section">
                    <h2>🏫 Performance por Escola</h2>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{img_escolas}" alt="Performance por Escola">
                    </div>
                    
                    <div class="insight-box">
                        <strong>🎯 Destaques por Escola:</strong><br>
                        • Análise comparativa entre instituições participantes<br>
                        • Identificação de melhores práticas e oportunidades<br>
                        • Foco em acertos e melhorias (não evidenciando erros)
                    </div>
                </div>
                
                <div class="section">
                    <h2>🔥 Mapa de Calor - Performance</h2>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{img_heatmap}" alt="Heatmap de Performance">
                    </div>
                    
                    <div class="insight-box">
                        <strong>🗺️ Interpretação do Mapa:</strong><br>
                        • <strong>Verde:</strong> Melhorias significativas<br>
                        • <strong>Amarelo:</strong> Estabilidade<br>
                        • <strong>Vermelho:</strong> Áreas para desenvolvimento<br>
                        • Visão consolidada da evolução por escola e fase
                    </div>
                </div>
                
                <div class="section">
                    <h2>📋 Estatísticas Detalhadas por Fase</h2>
    """
    
    # Adicionar estatísticas por fase
    if 'estatisticas_por_fase' in resumo_tde:
        for fase_key, stats in resumo_tde['estatisticas_por_fase'].items():
            fase_num = fase_key.replace('fase_', '')
            html_content += f"""
                    <div class="stat-card" style="margin: 10px 0; text-align: left;">
                        <h3 style="color: #667eea; margin-top: 0;">📚 Fase {fase_num}</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                            <div><strong>Estudantes:</strong> {stats.get('num_estudantes', 0)}</div>
                            <div><strong>Escolas:</strong> {stats.get('num_escolas', 0)}</div>
                            <div><strong>Turmas:</strong> {stats.get('num_turmas', 0)}</div>
                            <div><strong>Delta médio:</strong> {stats.get('delta_medio', 0):.2f}</div>
                            <div><strong>Taxa de melhoria:</strong> {stats.get('taxa_melhoria', 0):.1f}%</div>
                        </div>
                    </div>
            """
    
    html_content += """
                </div>
                
                <div class="section">
                    <h2>🎯 Conclusões e Recomendações</h2>
                    <div class="success-box">
                        <strong>✅ Pontos Positivos:</strong><br>
                        • Implementação bem-sucedida da análise longitudinal<br>
                        • Acompanhamento sistemático da evolução dos estudantes<br>
                        • Identificação de padrões de melhoria entre fases
                    </div>
                    
                    <div class="insight-box">
                        <strong>🔍 Recomendações:</strong><br>
                        • Continuar monitoramento longitudinal para identificar tendências de longo prazo<br>
                        • Investigar fatores que contribuem para melhorias significativas<br>
                        • Implementar estratégias baseadas nas melhores práticas identificadas<br>
                        • Manter foco nos acertos e progressos dos estudantes
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>WordGen - Sistema de Análise Longitudinal</strong></p>
                <p>Relatório gerado automaticamente • Dados das Fases 2, 3 e 4</p>
                <p><em>Foco em melhorias e acertos dos estudantes</em></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def main():
    """Função principal para gerar o relatório longitudinal"""
    print("🚀 Iniciando geração do Relatório Visual Longitudinal")
    print("="*60)
    
    # Carregar dados
    print("📂 Carregando dados longitudinais...")
    df_tde, resumo_tde, resumo_vocab = carregar_dados_longitudinais()
    
    if df_tde.empty:
        print("❌ Nenhum dado TDE encontrado. Execute primeiro os pipelines de dados.")
        return False
    
    # Criar diretório de figuras
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Gerar relatório HTML
    print("🎨 Gerando relatório HTML...")
    html_content = gerar_html_relatorio(df_tde, resumo_tde, resumo_vocab)
    
    # Salvar relatório
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Relatório salvo em: {OUTPUT_HTML}")
    print(f"🌐 Abra o arquivo em um navegador para visualizar")
    print("\n📊 Relatório Longitudinal concluído com sucesso!")
    
    return True

if __name__ == "__main__":
    main()
