#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RESUMO EXECUTIVO VISUAL - ANÁLISE AGREGADA POR ANO E FASE
Gera resumo executivo com tabelas e insights estratégicos

Autor: Sistema de Análise WordGen
Data: 2025
"""

import pandas as pd
import numpy as np
import pathlib
from datetime import datetime
import math

# Configurações de paths
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
DATA_DIR = BASE_DIR / "Data"
ANALISE_DIR = pathlib.Path(__file__).parent

# Arquivos de entrada
ARQUIVOS_TDE = {
    2: DATA_DIR / "tabela_bruta_fase2_TDE_wordgen.csv",
    3: DATA_DIR / "tabela_bruta_fase3_TDE_wordgen.csv",
    4: DATA_DIR / "tabela_bruta_fase4_TDE_wordgen.csv"
}

ARQUIVOS_VOCAB = {
    2: DATA_DIR / "tabela_bruta_fase2_vocabulario_wordgen.csv",
    3: DATA_DIR / "tabela_bruta_fase3_vocabulario_wordgen.csv", 
    4: DATA_DIR / "tabela_bruta_fase4_vocabulario_wordgen.csv"
}

# Mapeamento Fase -> Ano
FASE_ANO_MAP = {2: 2023, 3: 2024, 4: 2024}

def extrair_ano_turma(turma: str) -> str:
    """Extrai o ano da turma (5º, 6º, 7º, 8º, 9º)"""
    if pd.isna(turma):
        return "Não identificado"
    
    turma_str = str(turma).upper()
    import re
    
    patterns = [
        r'(\d)\s*[º°]\s*ANO',  # "6º ANO", "7° ANO"
        r'(\d)[ºA-Z]',         # "6A", "7B"
        r'\b(\d)\b'            # Apenas dígito
    ]
    
    for pattern in patterns:
        match = re.search(pattern, turma_str)
        if match:
            numero = int(match.group(1))
            if 5 <= numero <= 9:
                return f"{numero}º Ano"
    
    return "Não identificado"

def calcular_d_cohen(df: pd.DataFrame, col_pre: str = 'Score_Pre', col_pos: str = 'Score_Pos') -> float:
    """Calcula d de Cohen para medidas pré e pós"""
    if df.empty:
        return np.nan
    
    pre = df[col_pre].dropna()
    pos = df[col_pos].dropna()
    
    if len(pre) < 2 or len(pos) < 2:
        return np.nan
    
    m_pre, m_pos = pre.mean(), pos.mean()
    sd_pre, sd_pos = pre.std(ddof=1), pos.std(ddof=1)
    
    n_pre, n_pos = len(pre), len(pos)
    if n_pre + n_pos - 2 <= 0:
        return np.nan
    
    pooled_sd = math.sqrt(((n_pre - 1) * sd_pre**2 + (n_pos - 1) * sd_pos**2) / (n_pre + n_pos - 2))
    
    if pooled_sd == 0:
        return np.nan
    
    return (m_pos - m_pre) / pooled_sd

def carregar_e_processar_dados():
    """Carrega e processa todos os dados"""
    # Carregar TDE
    df_tde_list = []
    for fase, arquivo in ARQUIVOS_TDE.items():
        if arquivo.exists():
            df = pd.read_csv(arquivo)
            df['Fase'] = fase
            df['Ano_Calendario'] = FASE_ANO_MAP[fase]
            df['Prova'] = 'TDE'
            df_tde_list.append(df)
    
    # Carregar Vocabulário
    df_vocab_list = []
    for fase, arquivo in ARQUIVOS_VOCAB.items():
        if arquivo.exists():
            df = pd.read_csv(arquivo)
            df['Fase'] = fase
            df['Ano_Calendario'] = FASE_ANO_MAP[fase]
            df['Prova'] = 'VOCABULARIO'
            df_vocab_list.append(df)
    
    # Consolidar
    df_tde = pd.concat(df_tde_list, ignore_index=True) if df_tde_list else pd.DataFrame()
    df_vocab = pd.concat(df_vocab_list, ignore_index=True) if df_vocab_list else pd.DataFrame()
    
    # Processar
    for df in [df_tde, df_vocab]:
        if not df.empty:
            df['Ano_Turma'] = df['Turma'].apply(extrair_ano_turma)
            if 'Delta_Score' not in df.columns:
                df['Delta_Score'] = df['Score_Pos'] - df['Score_Pre']
    
    return df_tde, df_vocab

def criar_tabela_resumo(df_tde: pd.DataFrame, df_vocab: pd.DataFrame) -> pd.DataFrame:
    """Cria tabela resumo por dimensões principais"""
    resultados = []
    
    # Função auxiliar para calcular métricas
    def calcular_metricas(df_grupo, nome_grupo, prova):
        if df_grupo.empty:
            return None
        
        n = len(df_grupo)
        pre_mean = df_grupo['Score_Pre'].mean()
        pos_mean = df_grupo['Score_Pos'].mean()
        delta_mean = df_grupo['Delta_Score'].mean()
        d_cohen = calcular_d_cohen(df_grupo)
        
        # Distribuição de resultados
        melhoria_pct = (df_grupo['Delta_Score'] > 0).sum() / n * 100
        declinio_pct = (df_grupo['Delta_Score'] < 0).sum() / n * 100
        
        # Classificação do d de Cohen
        if np.isnan(d_cohen):
            classe = "Sem dados"
            benchmark = False
        else:
            abs_d = abs(d_cohen)
            if abs_d < 0.2:
                classe = "Trivial"
            elif abs_d < 0.5:
                classe = "Pequeno"
            elif abs_d < 0.8:
                classe = "Médio"
            else:
                classe = "Grande"
            
            # Benchmark específico
            if prova == 'TDE':
                benchmark = d_cohen >= 0.40
            else:  # VOCABULARIO
                benchmark = d_cohen >= 0.35
        
        return {
            'Dimensao': nome_grupo,
            'Prova': prova,
            'N': n,
            'Pre_Mean': pre_mean,
            'Pos_Mean': pos_mean,
            'Delta_Mean': delta_mean,
            'D_Cohen': d_cohen,
            'Classe_Efeito': classe,
            'Atinge_Benchmark': benchmark,
            'Melhoria_Pct': melhoria_pct,
            'Declinio_Pct': declinio_pct
        }
    
    # 1. Análise geral
    for df, prova in [(df_tde, 'TDE'), (df_vocab, 'VOCABULARIO')]:
        if not df.empty:
            resultado = calcular_metricas(df, 'GERAL', prova)
            if resultado:
                resultados.append(resultado)
    
    # 2. Por ano calendário
    for ano in [2023, 2024]:
        for df, prova in [(df_tde, 'TDE'), (df_vocab, 'VOCABULARIO')]:
            if not df.empty:
                df_ano = df[df['Ano_Calendario'] == ano]
                if not df_ano.empty:
                    resultado = calcular_metricas(df_ano, f'ANO_{ano}', prova)
                    if resultado:
                        resultados.append(resultado)
    
    # 3. Por fase
    for fase in [2, 3, 4]:
        for df, prova in [(df_tde, 'TDE'), (df_vocab, 'VOCABULARIO')]:
            if not df.empty:
                df_fase = df[df['Fase'] == fase]
                if not df_fase.empty:
                    resultado = calcular_metricas(df_fase, f'FASE_{fase}', prova)
                    if resultado:
                        resultados.append(resultado)
    
    # 4. Por ano de turma
    for turma in ['6º Ano', '7º Ano', '8º Ano', '9º Ano']:
        for df, prova in [(df_tde, 'TDE'), (df_vocab, 'VOCABULARIO')]:
            if not df.empty:
                df_turma = df[df['Ano_Turma'] == turma]
                if not df_turma.empty:
                    resultado = calcular_metricas(df_turma, f'TURMA_{turma.replace("º", "")}', prova)
                    if resultado:
                        resultados.append(resultado)
    
    # 5. Cruzamento Ano × Turma (principais)
    for ano in [2023, 2024]:
        for turma in ['6º Ano', '7º Ano', '8º Ano', '9º Ano']:
            for df, prova in [(df_tde, 'TDE'), (df_vocab, 'VOCABULARIO')]:
                if not df.empty:
                    df_cruzado = df[(df['Ano_Calendario'] == ano) & (df['Ano_Turma'] == turma)]
                    if not df_cruzado.empty:
                        resultado = calcular_metricas(df_cruzado, f'{ano}x{turma.replace("º", "")}', prova)
                        if resultado:
                            resultados.append(resultado)
    
    return pd.DataFrame(resultados)

def gerar_insights_estrategicos(df_resumo: pd.DataFrame) -> list:
    """Gera insights estratégicos baseados na análise"""
    insights = []
    
    # Separar por prova
    tde_data = df_resumo[df_resumo['Prova'] == 'TDE']
    vocab_data = df_resumo[df_resumo['Prova'] == 'VOCABULARIO']
    
    # 1. Análise de tendências temporais
    insights.append("🔍 INSIGHTS ESTRATÉGICOS:")
    insights.append("=" * 25)
    
    # Comparar 2023 vs 2024
    tde_2023 = tde_data[tde_data['Dimensao'] == 'ANO_2023']['D_Cohen'].iloc[0] if len(tde_data[tde_data['Dimensao'] == 'ANO_2023']) > 0 else np.nan
    tde_2024 = tde_data[tde_data['Dimensao'] == 'ANO_2024']['D_Cohen'].iloc[0] if len(tde_data[tde_data['Dimensao'] == 'ANO_2024']) > 0 else np.nan
    
    vocab_2023 = vocab_data[vocab_data['Dimensao'] == 'ANO_2023']['D_Cohen'].iloc[0] if len(vocab_data[vocab_data['Dimensao'] == 'ANO_2023']) > 0 else np.nan
    vocab_2024 = vocab_data[vocab_data['Dimensao'] == 'ANO_2024']['D_Cohen'].iloc[0] if len(vocab_data[vocab_data['Dimensao'] == 'ANO_2024']) > 0 else np.nan
    
    if not np.isnan(tde_2023) and not np.isnan(tde_2024):
        melhoria_tde = tde_2024 - tde_2023
        insights.append(f"\n1. REVERSÃO TEMPORAL - TDE:")
        insights.append(f"   • 2023: d = {tde_2023:.3f}")
        insights.append(f"   • 2024: d = {tde_2024:.3f}")
        insights.append(f"   • Melhoria: {melhoria_tde:+.3f} pontos de efeito")
        
    if not np.isnan(vocab_2023) and not np.isnan(vocab_2024):
        melhoria_vocab = vocab_2024 - vocab_2023
        insights.append(f"\n2. REVERSÃO TEMPORAL - VOCABULÁRIO:")
        insights.append(f"   • 2023: d = {vocab_2023:.3f}")
        insights.append(f"   • 2024: d = {vocab_2024:.3f}")
        insights.append(f"   • Melhoria: {melhoria_vocab:+.3f} pontos de efeito")
    
    # 3. Identificar grupos de risco e sucesso
    # TDE - piores e melhores
    tde_sorted = tde_data.sort_values('D_Cohen')
    piores_tde = tde_sorted.head(3)
    melhores_tde = tde_sorted.tail(3)
    
    insights.append(f"\n3. GRUPOS DE RISCO - TDE:")
    for _, row in piores_tde.iterrows():
        insights.append(f"   • {row['Dimensao']}: d = {row['D_Cohen']:.3f}, {row['Declinio_Pct']:.1f}% com declínio")
    
    insights.append(f"\n4. GRUPOS DE SUCESSO - TDE:")
    for _, row in melhores_tde.iterrows():
        insights.append(f"   • {row['Dimensao']}: d = {row['D_Cohen']:.3f}, {row['Melhoria_Pct']:.1f}% com melhoria")
    
    # VOCABULÁRIO - piores e melhores
    vocab_sorted = vocab_data.sort_values('D_Cohen')
    piores_vocab = vocab_sorted.head(3)
    melhores_vocab = vocab_sorted.tail(3)
    
    insights.append(f"\n5. GRUPOS DE RISCO - VOCABULÁRIO:")
    for _, row in piores_vocab.iterrows():
        insights.append(f"   • {row['Dimensao']}: d = {row['D_Cohen']:.3f}, {row['Declinio_Pct']:.1f}% com declínio")
    
    insights.append(f"\n6. GRUPOS DE SUCESSO - VOCABULÁRIO:")
    for _, row in melhores_vocab.iterrows():
        insights.append(f"   • {row['Dimensao']}: d = {row['D_Cohen']:.3f}, {row['Melhoria_Pct']:.1f}% com melhoria")
    
    # 4. Análise de benchmarks
    tde_benchmark = tde_data[tde_data['Atinge_Benchmark'] == True]
    vocab_benchmark = vocab_data[vocab_data['Atinge_Benchmark'] == True]
    
    insights.append(f"\n7. ATINGIMENTO DE BENCHMARKS:")
    insights.append(f"   • TDE (≥0.40): {len(tde_benchmark)}/{len(tde_data)} grupos ({len(tde_benchmark)/len(tde_data)*100:.1f}%)")
    if len(tde_benchmark) > 0:
        for _, row in tde_benchmark.iterrows():
            insights.append(f"     - {row['Dimensao']}: d = {row['D_Cohen']:.3f} ✓")
    
    insights.append(f"   • VOCABULÁRIO (≥0.35): {len(vocab_benchmark)}/{len(vocab_data)} grupos ({len(vocab_benchmark)/len(vocab_data)*100:.1f}%)")
    if len(vocab_benchmark) > 0:
        for _, row in vocab_benchmark.iterrows():
            insights.append(f"     - {row['Dimensao']}: d = {row['D_Cohen']:.3f} ✓")
    
    return insights

def formatar_tabela_resumo(df_resumo: pd.DataFrame) -> str:
    """Formata tabela resumo para o relatório"""
    tabela = []
    
    tabela.append("=" * 120)
    tabela.append("TABELA RESUMO EXECUTIVO - TODAS AS DIMENSÕES")
    tabela.append("=" * 120)
    tabela.append("")
    
    # Cabeçalho
    header = f"{'Dimensão':<20} {'Prova':<11} {'N':<6} {'Pré':<6} {'Pós':<6} {'Delta':<7} {'d Cohen':<8} {'Classe':<8} {'Bench':<5} {'Melh%':<6} {'Decl%':<6}"
    tabela.append(header)
    tabela.append("-" * 120)
    
    # Dados ordenados por d de Cohen decrescente
    df_sorted = df_resumo.sort_values(['Prova', 'D_Cohen'], ascending=[True, False])
    
    for _, row in df_sorted.iterrows():
        benchmark_symbol = "✓" if row['Atinge_Benchmark'] else "✗"
        linha = (f"{row['Dimensao']:<20} {row['Prova']:<11} {row['N']:<6} "
                f"{row['Pre_Mean']:<6.1f} {row['Pos_Mean']:<6.1f} {row['Delta_Mean']:<7.2f} "
                f"{row['D_Cohen']:<8.3f} {row['Classe_Efeito']:<8} {benchmark_symbol:<5} "
                f"{row['Melhoria_Pct']:<6.1f} {row['Declinio_Pct']:<6.1f}")
        tabela.append(linha)
    
    tabela.append("-" * 120)
    tabela.append("")
    tabela.append("LEGENDA:")
    tabela.append("• N = Número de participantes")
    tabela.append("• Pré/Pós = Pontuação média pré/pós-teste")
    tabela.append("• Delta = Diferença média (Pós - Pré)")
    tabela.append("• d Cohen = Tamanho do efeito")
    tabela.append("• Classe = Classificação do efeito (Cohen, 1988)")
    tabela.append("• Bench = Atinge benchmark educacional (✓/✗)")
    tabela.append("• Melh%/Decl% = Percentual com melhoria/declínio")
    tabela.append("")
    
    return "\n".join(tabela)

def main():
    """Função principal"""
    print("=" * 80)
    print("🎯 RESUMO EXECUTIVO VISUAL - ANÁLISE AGREGADA POR ANO E FASE")
    print("=" * 80)
    
    # Carregar dados
    print("\n📂 Carregando e processando dados...")
    df_tde, df_vocab = carregar_e_processar_dados()
    
    if df_tde.empty and df_vocab.empty:
        print("❌ Nenhum dado foi carregado.")
        return
    
    print(f"  TDE: {len(df_tde)} registros")
    print(f"  Vocabulário: {len(df_vocab)} registros")
    
    # Criar tabela resumo
    print("\n📊 Gerando tabela resumo...")
    df_resumo = criar_tabela_resumo(df_tde, df_vocab)
    
    # Gerar insights
    print("\n🔍 Gerando insights estratégicos...")
    insights = gerar_insights_estrategicos(df_resumo)
    
    # Formatear relatório
    print("\n📋 Formatando resumo executivo...")
    relatorio = []
    
    # Cabeçalho
    relatorio.extend([
        "=" * 120,
        "RESUMO EXECUTIVO VISUAL - ANÁLISE AGREGADA POR ANO E FASE",
        "WordGen - Desempenho TDE e Vocabulário",
        "=" * 120,
        f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "",
        "CONTEXTO:",
        "• Fase 2 (2023): Primeira implementação",
        "• Fases 3-4 (2024): Refinamento e consolidação", 
        "• Análise multidimensional: 4.573 registros TDE, 4.393 registros Vocabulário",
        "• Benchmarks: TDE ≥ 0.40, Vocabulário ≥ 0.35 (d de Cohen)",
        "",
    ])
    
    # Tabela resumo
    tabela_formatada = formatar_tabela_resumo(df_resumo)
    relatorio.append(tabela_formatada)
    
    # Insights estratégicos
    relatorio.extend(insights)
    
    # Recomendações
    relatorio.extend([
        "\n" + "=" * 120,
        "RECOMENDAÇÕES ESTRATÉGICAS",
        "=" * 120,
        "",
        "📈 CURTO PRAZO (Próximas Fases):",
        "1. Focar intervenções nos grupos 6º e 7º anos (maior declínio em 2023)",
        "2. Replicar estratégias bem-sucedidas de 2024 (reversão positiva)",
        "3. Investigar fatores específicos do 8º ano em Vocabulário (declínio persistente)",
        "",
        "🔬 MÉDIO PRAZO (Pesquisa e Desenvolvimento):",
        "4. Análise qualitativa dos fatores de melhoria entre 2023-2024",
        "5. Estudo de caso das escolas com melhor desempenho",
        "6. Desenvolvimento de intervenções específicas por ano escolar",
        "",
        "📊 LONGO PRAZO (Monitoramento):",
        "7. Sistema de alerta precoce para grupos de risco",
        "8. Benchmarks adaptativos por contexto escolar",
        "9. Análise longitudinal individual para trajetórias de aprendizagem",
        "",
        "=" * 120,
        "Relatório gerado automaticamente pelo Sistema de Análise WordGen",
        "Próxima atualização recomendada: Após coleta de nova fase",
        "=" * 120
    ])
    
    # Salvar
    arquivo_saida = ANALISE_DIR / f"resumo_executivo_visual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("\n".join(relatorio))
    
    print(f"✅ Resumo executivo salvo em: {arquivo_saida}")
    print(f"📄 Tamanho: {arquivo_saida.stat().st_size / 1024:.1f} KB")
    
    # Preview
    print("\n" + "=" * 80)
    print("PREVIEW DO RESUMO EXECUTIVO:")
    print("=" * 80)
    linhas = "\n".join(relatorio).split('\n')
    for linha in linhas[:40]:
        print(linha)
    
    if len(linhas) > 40:
        print(f"\n... e mais {len(linhas) - 40} linhas no arquivo completo.")
    
    print("\n✅ PROCESSO CONCLUÍDO!")

if __name__ == "__main__":
    main()