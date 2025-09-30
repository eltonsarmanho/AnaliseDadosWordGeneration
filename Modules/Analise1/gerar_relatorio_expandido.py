#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIO EXPANDIDO DE DESEMPENHO AGREGADO POR ANO E FASE
Análise detalhada de performance de TDE e Vocabulário com múltiplas dimensões,
considerando que Fase 2 ocorreu em 2023 e Fases 3-4 em 2024.

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
FASE_ANO_MAP = {
    2: 2023,
    3: 2024,
    4: 2024
}

def extrair_ano_turma(turma: str) -> str:
    """Extrai o ano da turma (5º, 6º, 7º, 8º, 9º)"""
    if pd.isna(turma):
        return "Não identificado"
    
    turma_str = str(turma).upper()
    
    # Buscar por padrões de ano
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
    
    # Desvio padrão agrupado
    n_pre, n_pos = len(pre), len(pos)
    if n_pre + n_pos - 2 <= 0:
        return np.nan
    
    pooled_sd = math.sqrt(((n_pre - 1) * sd_pre**2 + (n_pos - 1) * sd_pos**2) / (n_pre + n_pos - 2))
    
    if pooled_sd == 0:
        return np.nan
    
    return (m_pos - m_pre) / pooled_sd

def classificar_d_cohen(d: float, prova: str = None) -> tuple:
    """Classifica o tamanho do efeito com benchmarks específicos por prova"""
    if np.isnan(d):
        return "Sem dados", False
    
    abs_d = abs(d)
    
    # Classificação geral (Cohen, 1988)
    if abs_d < 0.2:
        classe_geral = "Trivial"
    elif abs_d < 0.5:
        classe_geral = "Pequeno"
    elif abs_d < 0.8:
        classe_geral = "Médio"
    else:
        classe_geral = "Grande"
    
    # Benchmarks específicos por prova
    if prova == 'TDE':
        benchmark_ok = d >= 0.40  # Hattie, 2009
        benchmark_desc = "Bom resultado" if benchmark_ok else "Abaixo do esperado"
    elif prova == 'VOCAB':
        benchmark_ok = d >= 0.35  # Marulis & Neuman, 2010
        benchmark_desc = "Impacto significativo" if benchmark_ok else "Abaixo do esperado"
    else:
        benchmark_ok = d > 0
        benchmark_desc = "Positivo" if benchmark_ok else "Negativo"
    
    return f"{classe_geral} ({benchmark_desc})", benchmark_ok

def carregar_dados_por_fase(arquivos_dict: dict) -> pd.DataFrame:
    """Carrega e consolida dados de todas as fases"""
    dataframes = []
    
    for fase, arquivo in arquivos_dict.items():
        if arquivo.exists():
            print(f"   Carregando Fase {fase}: {arquivo.name}")
            df = pd.read_csv(arquivo)
            df['Fase'] = fase
            df['Ano_Calendario'] = FASE_ANO_MAP[fase]
            dataframes.append(df)
        else:
            print(f"   ⚠️ Arquivo não encontrado: {arquivo}")
    
    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        return pd.DataFrame()

def processar_dataset(df: pd.DataFrame, tipo: str) -> pd.DataFrame:
    """Processa dataset e adiciona colunas derivadas"""
    if df.empty:
        return df
    
    # Extrair ano da turma
    df['Ano_Turma'] = df['Turma'].apply(extrair_ano_turma)
    
    # Calcular delta se não existir
    if 'Delta_Score' not in df.columns:
        df['Delta_Score'] = df['Score_Pos'] - df['Score_Pre']
    
    # Adicionar tipo de prova
    df['Tipo_Prova'] = tipo
    
    return df

def calcular_estatisticas_descritivas(grupo_df: pd.DataFrame) -> dict:
    """Calcula estatísticas descritivas completas para um grupo"""
    if grupo_df.empty:
        return {}
    
    stats = {
        'n': len(grupo_df),
        'pre_mean': grupo_df['Score_Pre'].mean(),
        'pre_std': grupo_df['Score_Pre'].std(),
        'pre_min': grupo_df['Score_Pre'].min(),
        'pre_max': grupo_df['Score_Pre'].max(),
        'pos_mean': grupo_df['Score_Pos'].mean(),
        'pos_std': grupo_df['Score_Pos'].std(),
        'pos_min': grupo_df['Score_Pos'].min(),
        'pos_max': grupo_df['Score_Pos'].max(),
        'delta_mean': grupo_df['Delta_Score'].mean(),
        'delta_std': grupo_df['Delta_Score'].std(),
        'delta_min': grupo_df['Delta_Score'].min(),
        'delta_max': grupo_df['Delta_Score'].max(),
        'd_cohen': calcular_d_cohen(grupo_df),
        'melhoria_pct': (grupo_df['Delta_Score'] > 0).sum() / len(grupo_df) * 100,
        'declinio_pct': (grupo_df['Delta_Score'] < 0).sum() / len(grupo_df) * 100,
        'estavel_pct': (grupo_df['Delta_Score'] == 0).sum() / len(grupo_df) * 100
    }
    
    return stats

def gerar_analise_completa(df: pd.DataFrame, tipo_prova: str) -> dict:
    """Gera análise completa por múltiplas dimensões"""
    resultados = {}
    
    print(f"   Analisando {tipo_prova}...")
    
    # 1. Análise Geral
    print("     - Estatísticas gerais")
    resultados['geral'] = calcular_estatisticas_descritivas(df)
    
    # 2. Por Ano Calendário (2023 vs 2024)
    print("     - Por ano calendário")
    resultados['por_ano'] = {}
    for ano in sorted(df['Ano_Calendario'].unique()):
        df_ano = df[df['Ano_Calendario'] == ano]
        resultados['por_ano'][ano] = calcular_estatisticas_descritivas(df_ano)
    
    # 3. Por Fase
    print("     - Por fase")
    resultados['por_fase'] = {}
    for fase in sorted(df['Fase'].unique()):
        df_fase = df[df['Fase'] == fase]
        resultados['por_fase'][fase] = calcular_estatisticas_descritivas(df_fase)
    
    # 4. Por Ano de Turma
    print("     - Por ano de turma")
    resultados['por_turma'] = {}
    for turma in sorted(df['Ano_Turma'].unique()):
        if turma != "Não identificado":
            df_turma = df[df['Ano_Turma'] == turma]
            if not df_turma.empty:
                resultados['por_turma'][turma] = calcular_estatisticas_descritivas(df_turma)
    
    # 5. Análise Cruzada: Ano Calendário × Fase
    print("     - Cruzamento ano × fase")
    resultados['ano_x_fase'] = {}
    for ano in sorted(df['Ano_Calendario'].unique()):
        for fase in sorted(df['Fase'].unique()):
            df_cruzado = df[(df['Ano_Calendario'] == ano) & (df['Fase'] == fase)]
            if not df_cruzado.empty:
                resultados['ano_x_fase'][(ano, fase)] = calcular_estatisticas_descritivas(df_cruzado)
    
    # 6. Análise Cruzada: Ano Calendário × Ano de Turma
    print("     - Cruzamento ano × turma")
    resultados['ano_x_turma'] = {}
    for ano in sorted(df['Ano_Calendario'].unique()):
        for turma in sorted(df['Ano_Turma'].unique()):
            if turma != "Não identificado":
                df_cruzado = df[(df['Ano_Calendario'] == ano) & (df['Ano_Turma'] == turma)]
                if not df_cruzado.empty:
                    resultados['ano_x_turma'][(ano, turma)] = calcular_estatisticas_descritivas(df_cruzado)
    
    # 7. Análise Cruzada: Fase × Ano de Turma
    print("     - Cruzamento fase × turma")
    resultados['fase_x_turma'] = {}
    for fase in sorted(df['Fase'].unique()):
        for turma in sorted(df['Ano_Turma'].unique()):
            if turma != "Não identificado":
                df_cruzado = df[(df['Fase'] == fase) & (df['Ano_Turma'] == turma)]
                if not df_cruzado.empty:
                    resultados['fase_x_turma'][(fase, turma)] = calcular_estatisticas_descritivas(df_cruzado)
    
    # 8. Análise Tripla: Ano × Fase × Turma
    print("     - Análise tripla (ano × fase × turma)")
    resultados['tripla'] = {}
    for ano in sorted(df['Ano_Calendario'].unique()):
        for fase in sorted(df['Fase'].unique()):
            for turma in sorted(df['Ano_Turma'].unique()):
                if turma != "Não identificado":
                    df_tripla = df[
                        (df['Ano_Calendario'] == ano) & 
                        (df['Fase'] == fase) & 
                        (df['Ano_Turma'] == turma)
                    ]
                    if not df_tripla.empty and len(df_tripla) >= 10:  # Mínimo de 10 casos
                        resultados['tripla'][(ano, fase, turma)] = calcular_estatisticas_descritivas(df_tripla)
    
    return resultados

def formatar_secao_estatisticas(titulo: str, stats: dict, prova: str) -> list:
    """Formata uma seção de estatísticas"""
    if not stats:
        return [f"\n{titulo}", "-" * len(titulo), "  Sem dados disponíveis", ""]
    
    d_cohen = stats.get('d_cohen', np.nan)
    classificacao, benchmark_ok = classificar_d_cohen(d_cohen, prova)
    d_str = f"{d_cohen:.3f}" if not np.isnan(d_cohen) else "N/A"
    
    secao = [
        f"\n{titulo}",
        "-" * len(titulo),
        f"  Participantes: {stats['n']}",
        f"  Pré-teste: {stats['pre_mean']:.2f} ± {stats['pre_std']:.2f} (min: {stats['pre_min']:.0f}, max: {stats['pre_max']:.0f})",
        f"  Pós-teste: {stats['pos_mean']:.2f} ± {stats['pos_std']:.2f} (min: {stats['pos_min']:.0f}, max: {stats['pos_max']:.0f})",
        f"  Delta: {stats['delta_mean']:.2f} ± {stats['delta_std']:.2f} (min: {stats['delta_min']:.2f}, max: {stats['delta_max']:.2f})",
        f"  d de Cohen: {d_str} ({classificacao})",
        f"  Distribuição de resultados:",
        f"    • Melhoria: {stats['melhoria_pct']:.1f}% dos casos",
        f"    • Declínio: {stats['declinio_pct']:.1f}% dos casos", 
        f"    • Estável: {stats['estavel_pct']:.1f}% dos casos",
        ""
    ]
    
    return secao

def gerar_relatorio_expandido(resultados_tde: dict, resultados_vocab: dict) -> str:
    """Gera o relatório expandido completo"""
    relatorio = []
    
    # Cabeçalho
    relatorio.extend([
        "=" * 100,
        "RELATÓRIO EXPANDIDO DE DESEMPENHO AGREGADO - TDE E VOCABULÁRIO",
        "Análise Multidimensional por Ano Calendário, Fase e Ano de Turma",
        "=" * 100,
        f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "",
        "CONTEXTO:",
        "- Fase 2: Realizada em 2023",
        "- Fases 3 e 4: Realizadas em 2024",
        "- Análise agregada por ano de turma (6º ao 9º ano)",
        "- Múltiplas dimensões de análise e cruzamentos",
        "",
        "LEGENDA:",
        "- Score_Pre/Pos: Pontuação no pré/pós-teste",
        "- Delta: Diferença (Pós - Pré)",
        "- d de Cohen: Tamanho do efeito",
        "- Distribuição: % de casos com melhoria, declínio ou estabilidade",
        "",
        "BENCHMARKS EDUCACIONAIS:",
        "- TDE: d ≥ 0.40 = Bom resultado (Hattie, 2009)",
        "- Vocabulário: d ≥ 0.35 = Impacto significativo (Marulis & Neuman, 2010)",
        "",
        "=" * 100
    ])
    
    # Seção 1: Análise Geral
    relatorio.extend([
        "\n1. ANÁLISE GERAL",
        "=" * 15
    ])
    
    relatorio.extend(formatar_secao_estatisticas(
        "📝 TDE - Desempenho Geral (Todas as Fases)",
        resultados_tde.get('geral', {}),
        'TDE'
    ))
    
    relatorio.extend(formatar_secao_estatisticas(
        "📚 VOCABULÁRIO - Desempenho Geral (Todas as Fases)",
        resultados_vocab.get('geral', {}),
        'VOCAB'
    ))
    
    # Seção 2: Por Ano Calendário
    relatorio.extend([
        "\n2. ANÁLISE POR ANO CALENDÁRIO (2023 vs 2024)",
        "=" * 44
    ])
    
    for ano in [2023, 2024]:
        relatorio.extend(formatar_secao_estatisticas(
            f"📝 TDE - {ano}",
            resultados_tde.get('por_ano', {}).get(ano, {}),
            'TDE'
        ))
        
        relatorio.extend(formatar_secao_estatisticas(
            f"📚 VOCABULÁRIO - {ano}",
            resultados_vocab.get('por_ano', {}).get(ano, {}),
            'VOCAB'
        ))
    
    # Seção 3: Por Fase
    relatorio.extend([
        "\n3. ANÁLISE POR FASE",
        "=" * 17
    ])
    
    for fase in [2, 3, 4]:
        relatorio.extend(formatar_secao_estatisticas(
            f"📝 TDE - Fase {fase}",
            resultados_tde.get('por_fase', {}).get(fase, {}),
            'TDE'
        ))
        
        relatorio.extend(formatar_secao_estatisticas(
            f"📚 VOCABULÁRIO - Fase {fase}",
            resultados_vocab.get('por_fase', {}).get(fase, {}),
            'VOCAB'
        ))
    
    # Seção 4: Por Ano de Turma
    relatorio.extend([
        "\n4. ANÁLISE POR ANO DE TURMA",
        "=" * 26
    ])
    
    for turma in ["6º Ano", "7º Ano", "8º Ano", "9º Ano"]:
        relatorio.extend(formatar_secao_estatisticas(
            f"📝 TDE - {turma}",
            resultados_tde.get('por_turma', {}).get(turma, {}),
            'TDE'
        ))
        
        relatorio.extend(formatar_secao_estatisticas(
            f"📚 VOCABULÁRIO - {turma}",
            resultados_vocab.get('por_turma', {}).get(turma, {}),
            'VOCAB'
        ))
    
    # Seção 5: Cruzamento Ano × Fase
    relatorio.extend([
        "\n5. ANÁLISE CRUZADA: ANO CALENDÁRIO × FASE",
        "=" * 40
    ])
    
    for ano in [2023, 2024]:
        for fase in [2, 3, 4]:
            key = (ano, fase)
            if key in resultados_tde.get('ano_x_fase', {}):
                relatorio.extend(formatar_secao_estatisticas(
                    f"📝 TDE - {ano} × Fase {fase}",
                    resultados_tde.get('ano_x_fase', {}).get(key, {}),
                    'TDE'
                ))
            
            if key in resultados_vocab.get('ano_x_fase', {}):
                relatorio.extend(formatar_secao_estatisticas(
                    f"📚 VOCABULÁRIO - {ano} × Fase {fase}",
                    resultados_vocab.get('ano_x_fase', {}).get(key, {}),
                    'VOCAB'
                ))
    
    # Seção 6: Cruzamento Fase × Turma
    relatorio.extend([
        "\n6. ANÁLISE CRUZADA: FASE × ANO DE TURMA",
        "=" * 35
    ])
    
    for fase in [2, 3, 4]:
        for turma in ["6º Ano", "7º Ano", "8º Ano", "9º Ano"]:
            key = (fase, turma)
            if key in resultados_tde.get('fase_x_turma', {}):
                relatorio.extend(formatar_secao_estatisticas(
                    f"📝 TDE - Fase {fase} × {turma}",
                    resultados_tde.get('fase_x_turma', {}).get(key, {}),
                    'TDE'
                ))
            
            if key in resultados_vocab.get('fase_x_turma', {}):
                relatorio.extend(formatar_secao_estatisticas(
                    f"📚 VOCABULÁRIO - Fase {fase} × {turma}",
                    resultados_vocab.get('fase_x_turma', {}).get(key, {}),
                    'VOCAB'
                ))
    
    # Seção 7: Análise Tripla (grupos com n ≥ 10)
    relatorio.extend([
        "\n7. ANÁLISE TRIPLA: ANO × FASE × TURMA (grupos com n ≥ 10)",
        "=" * 56
    ])
    
    # TDE Tripla
    relatorio.append("\n📝 TDE - Análise Tripla")
    relatorio.append("-" * 25)
    for key, stats in resultados_tde.get('tripla', {}).items():
        ano, fase, turma = key
        relatorio.extend(formatar_secao_estatisticas(
            f"{ano} × Fase {fase} × {turma}",
            stats,
            'TDE'
        ))
    
    # Vocabulário Tripla
    relatorio.append("\n📚 VOCABULÁRIO - Análise Tripla")
    relatorio.append("-" * 31)
    for key, stats in resultados_vocab.get('tripla', {}).items():
        ano, fase, turma = key
        relatorio.extend(formatar_secao_estatisticas(
            f"{ano} × Fase {fase} × {turma}",
            stats,
            'VOCAB'
        ))
    
    # Seção 8: Resumo Executivo Expandido
    relatorio.extend([
        "\n" + "=" * 100,
        "RESUMO EXECUTIVO EXPANDIDO",
        "=" * 100,
        ""
    ])
    
    # Melhores e piores desempenhos
    def encontrar_extremos(resultados: dict, prova: str):
        melhores = []
        piores = []
        
        # Analisar todas as dimensões
        for dimensao in ['por_ano', 'por_fase', 'por_turma', 'ano_x_turma']:
            if dimensao in resultados:
                for key, stats in resultados[dimensao].items():
                    d_cohen = stats.get('d_cohen', np.nan)
                    if not np.isnan(d_cohen):
                        item = (key, d_cohen, dimensao)
                        melhores.append(item)
                        piores.append(item)
        
        # Ordenar
        melhores.sort(key=lambda x: x[1], reverse=True)
        piores.sort(key=lambda x: x[1])
        
        return melhores[:3], piores[:3]  # Top 3
    
    melhores_tde, piores_tde = encontrar_extremos(resultados_tde, 'TDE')
    melhores_vocab, piores_vocab = encontrar_extremos(resultados_vocab, 'VOCAB')
    
    relatorio.extend([
        "🏆 MELHORES DESEMPENHOS:",
        "",
        "📝 TDE:"
    ])
    for i, (key, d_cohen, dimensao) in enumerate(melhores_tde, 1):
        relatorio.append(f"  {i}. {key} (d = {d_cohen:.3f}) - {dimensao}")
    
    relatorio.extend([
        "",
        "📚 VOCABULÁRIO:"
    ])
    for i, (key, d_cohen, dimensao) in enumerate(melhores_vocab, 1):
        relatorio.append(f"  {i}. {key} (d = {d_cohen:.3f}) - {dimensao}")
    
    relatorio.extend([
        "",
        "⚠️ DESEMPENHOS MAIS PREOCUPANTES:",
        "",
        "📝 TDE:"
    ])
    for i, (key, d_cohen, dimensao) in enumerate(piores_tde, 1):
        relatorio.append(f"  {i}. {key} (d = {d_cohen:.3f}) - {dimensao}")
    
    relatorio.extend([
        "",
        "📚 VOCABULÁRIO:"
    ])
    for i, (key, d_cohen, dimensao) in enumerate(piores_vocab, 1):
        relatorio.append(f"  {i}. {key} (d = {d_cohen:.3f}) - {dimensao}")
    
    # Rodapé
    relatorio.extend([
        "\n" + "=" * 100,
        "NOTAS METODOLÓGICAS:",
        "- Análise baseada em 8 dimensões diferentes de agregação",
        "- d de Cohen calculado como (M_pos - M_pre) / DP_agrupado",
        "- Interpretação baseada em Cohen (1988) e benchmarks educacionais específicos",
        "- Análise tripla limitada a grupos com n ≥ 10 para robustez estatística",
        "- Distribuição de resultados mostra heterogeneidade intragrupo",
        "=" * 100
    ])
    
    return "\n".join(relatorio)

def main():
    """Função principal"""
    print("=" * 100)
    print("🎯 RELATÓRIO EXPANDIDO DE DESEMPENHO AGREGADO POR ANO E FASE")
    print("=" * 100)
    
    # Carregar dados
    print("\n📂 Carregando dados...")
    print("  TDE:")
    df_tde = carregar_dados_por_fase(ARQUIVOS_TDE)
    print("  Vocabulário:")
    df_vocab = carregar_dados_por_fase(ARQUIVOS_VOCAB)
    
    if df_tde.empty and df_vocab.empty:
        print("❌ Nenhum dado foi carregado. Verificar arquivos de entrada.")
        return
    
    # Processar dados
    print("\n🔄 Processando dados...")
    if not df_tde.empty:
        df_tde = processar_dataset(df_tde, 'TDE')
        print(f"  TDE: {len(df_tde)} registros processados")
    
    if not df_vocab.empty:
        df_vocab = processar_dataset(df_vocab, 'VOCABULARIO')
        print(f"  Vocabulário: {len(df_vocab)} registros processados")
    
    # Gerar análises completas
    print("\n📊 Gerando análises multidimensionais...")
    resultados_tde = gerar_analise_completa(df_tde, 'TDE') if not df_tde.empty else {}
    resultados_vocab = gerar_analise_completa(df_vocab, 'VOCABULARIO') if not df_vocab.empty else {}
    
    # Gerar relatório
    print("\n📋 Formatando relatório expandido...")
    relatorio_texto = gerar_relatorio_expandido(resultados_tde, resultados_vocab)
    
    # Salvar relatório
    arquivo_saida = ANALISE_DIR / f"relatorio_desempenho_expandido_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write(relatorio_texto)
    
    print(f"✅ Relatório expandido salvo em: {arquivo_saida}")
    print(f"📄 Tamanho: {arquivo_saida.stat().st_size / 1024:.1f} KB")
    
    # Mostrar resumo no console
    print("\n" + "=" * 100)
    print("PREVIEW DO RELATÓRIO EXPANDIDO:")
    print("=" * 100)
    linhas = relatorio_texto.split('\n')
    for linha in linhas[:60]:  # Primeiras 60 linhas
        print(linha)
    
    if len(linhas) > 60:
        print(f"\n... e mais {len(linhas) - 60} linhas no arquivo completo.")
    
    print("\n✅ PROCESSO CONCLUÍDO COM SUCESSO!")

if __name__ == "__main__":
    main()