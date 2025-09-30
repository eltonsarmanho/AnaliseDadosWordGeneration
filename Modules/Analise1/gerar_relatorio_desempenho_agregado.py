#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIO DE DESEMPENHO AGREGADO POR ANO E FASE
Análise de performance de TDE e Vocabulário agregado por ano escolar e fase,
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
    pooled_sd = math.sqrt(((n_pre - 1) * sd_pre**2 + (n_pos - 1) * sd_pos**2) / (n_pre + n_pos - 2))
    
    if pooled_sd == 0:
        return np.nan
    
    return (m_pos - m_pre) / pooled_sd

def classificar_d_cohen(d: float) -> str:
    """Classifica o tamanho do efeito (Cohen, 1988)"""
    if np.isnan(d):
        return "Sem dados"
    
    abs_d = abs(d)
    if abs_d < 0.2:
        return "Trivial"
    elif abs_d < 0.5:
        return "Pequeno"
    elif abs_d < 0.8:
        return "Médio"
    else:
        return "Grande"

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

def gerar_estatisticas_agregadas(df: pd.DataFrame) -> dict:
    """Gera estatísticas agregadas por diferentes dimensões"""
    resultados = {}
    
    # 1. Por Ano Calendário (2023 vs 2024)
    print("   Calculando por ano calendário...")
    por_ano = df.groupby('Ano_Calendario').agg({
        'Score_Pre': ['count', 'mean', 'std'],
        'Score_Pos': ['mean', 'std'],
        'Delta_Score': ['mean', 'std']
    }).round(2)
    
    # Calcular d de Cohen por ano
    d_cohen_por_ano = {}
    for ano in df['Ano_Calendario'].unique():
        df_ano = df[df['Ano_Calendario'] == ano]
        d_cohen_por_ano[ano] = calcular_d_cohen(df_ano)
    
    resultados['por_ano'] = {
        'estatisticas': por_ano,
        'd_cohen': d_cohen_por_ano
    }
    
    # 2. Por Fase
    print("   Calculando por fase...")
    por_fase = df.groupby('Fase').agg({
        'Score_Pre': ['count', 'mean', 'std'],
        'Score_Pos': ['mean', 'std'], 
        'Delta_Score': ['mean', 'std']
    }).round(2)
    
    d_cohen_por_fase = {}
    for fase in df['Fase'].unique():
        df_fase = df[df['Fase'] == fase]
        d_cohen_por_fase[fase] = calcular_d_cohen(df_fase)
    
    resultados['por_fase'] = {
        'estatisticas': por_fase,
        'd_cohen': d_cohen_por_fase
    }
    
    # 3. Por Ano de Turma
    print("   Calculando por ano de turma...")
    por_turma = df.groupby('Ano_Turma').agg({
        'Score_Pre': ['count', 'mean', 'std'],
        'Score_Pos': ['mean', 'std'],
        'Delta_Score': ['mean', 'std']
    }).round(2)
    
    d_cohen_por_turma = {}
    for turma in df['Ano_Turma'].unique():
        df_turma = df[df['Ano_Turma'] == turma]
        d_cohen_por_turma[turma] = calcular_d_cohen(df_turma)
    
    resultados['por_turma'] = {
        'estatisticas': por_turma,
        'd_cohen': d_cohen_por_turma
    }
    
    # 4. Cruzado: Ano Calendário x Ano Turma
    print("   Calculando cruzamento ano calendário x ano turma...")
    cruzado = df.groupby(['Ano_Calendario', 'Ano_Turma']).agg({
        'Score_Pre': ['count', 'mean', 'std'],
        'Score_Pos': ['mean', 'std'],
        'Delta_Score': ['mean', 'std']
    }).round(2)
    
    d_cohen_cruzado = {}
    for (ano_cal, ano_turma) in df.groupby(['Ano_Calendario', 'Ano_Turma']).groups.keys():
        df_grupo = df[(df['Ano_Calendario'] == ano_cal) & (df['Ano_Turma'] == ano_turma)]
        d_cohen_cruzado[(ano_cal, ano_turma)] = calcular_d_cohen(df_grupo)
    
    resultados['cruzado'] = {
        'estatisticas': cruzado,
        'd_cohen': d_cohen_cruzado
    }
    
    return resultados

def formatar_relatorio(resultados_tde: dict, resultados_vocab: dict) -> str:
    """Formata o relatório final em texto"""
    relatorio = []
    
    # Cabeçalho
    relatorio.extend([
        "=" * 80,
        "RELATÓRIO DE DESEMPENHO AGREGADO - TDE E VOCABULÁRIO",
        "Análise por Ano Calendário e Fase",
        "=" * 80,
        f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "",
        "CONTEXTO:",
        "- Fase 2: Realizada em 2023",
        "- Fases 3 e 4: Realizadas em 2024",
        "- Análise agregada por ano de turma (5º ao 9º ano)",
        "",
        "LEGENDA:",
        "- Score_Pre: Pontuação no pré-teste",
        "- Score_Pos: Pontuação no pós-teste", 
        "- Delta: Diferença (Pós - Pré)",
        "- d de Cohen: Tamanho do efeito (interpretação: <0.2=trivial, 0.2-0.5=pequeno, 0.5-0.8=médio, >0.8=grande)",
        "",
        "=" * 80
    ])
    
    # Função para formatar seção
    def formatar_secao(titulo: str, dados_tde: dict, dados_vocab: dict):
        secao = [f"\n{titulo}", "-" * len(titulo)]
        
        # TDE
        secao.append("\n📝 TDE (Teste de Desempenho Escolar)")
        if 'estatisticas' in dados_tde:
            estatisticas = dados_tde['estatisticas']
            d_cohens = dados_tde['d_cohen']
            
            for idx in estatisticas.index:
                idx_str = str(idx) if not isinstance(idx, tuple) else f"{idx[0]} - {idx[1]}"
                
                n = int(estatisticas.loc[idx, ('Score_Pre', 'count')])
                pre_mean = estatisticas.loc[idx, ('Score_Pre', 'mean')]
                pos_mean = estatisticas.loc[idx, ('Score_Pos', 'mean')]
                delta_mean = estatisticas.loc[idx, ('Delta_Score', 'mean')]
                
                d_cohen = d_cohens.get(idx, np.nan)
                d_class = classificar_d_cohen(d_cohen)
                d_str = f"{d_cohen:.3f}" if not np.isnan(d_cohen) else "N/A"
                
                secao.extend([
                    f"  {idx_str}:",
                    f"    Participantes: {n}",
                    f"    Pré-teste: {pre_mean:.2f} pontos",
                    f"    Pós-teste: {pos_mean:.2f} pontos",
                    f"    Delta médio: {delta_mean:.2f} pontos",
                    f"    d de Cohen: {d_str} ({d_class})",
                    ""
                ])
        
        # Vocabulário
        secao.append("📚 VOCABULÁRIO")
        if 'estatisticas' in dados_vocab:
            estatisticas = dados_vocab['estatisticas']
            d_cohens = dados_vocab['d_cohen']
            
            for idx in estatisticas.index:
                idx_str = str(idx) if not isinstance(idx, tuple) else f"{idx[0]} - {idx[1]}"
                
                n = int(estatisticas.loc[idx, ('Score_Pre', 'count')])
                pre_mean = estatisticas.loc[idx, ('Score_Pre', 'mean')]
                pos_mean = estatisticas.loc[idx, ('Score_Pos', 'mean')]
                delta_mean = estatisticas.loc[idx, ('Delta_Score', 'mean')]
                
                d_cohen = d_cohens.get(idx, np.nan)
                d_class = classificar_d_cohen(d_cohen)
                d_str = f"{d_cohen:.3f}" if not np.isnan(d_cohen) else "N/A"
                
                secao.extend([
                    f"  {idx_str}:",
                    f"    Participantes: {n}",
                    f"    Pré-teste: {pre_mean:.2f} pontos",
                    f"    Pós-teste: {pos_mean:.2f} pontos",
                    f"    Delta médio: {delta_mean:.2f} pontos",
                    f"    d de Cohen: {d_str} ({d_class})",
                    ""
                ])
        
        return secao
    
    # Adicionar seções
    relatorio.extend(formatar_secao(
        "1. ANÁLISE POR ANO CALENDÁRIO (2023 vs 2024)",
        resultados_tde['por_ano'], 
        resultados_vocab['por_ano']
    ))
    
    relatorio.extend(formatar_secao(
        "2. ANÁLISE POR FASE",
        resultados_tde['por_fase'],
        resultados_vocab['por_fase']
    ))
    
    relatorio.extend(formatar_secao(
        "3. ANÁLISE POR ANO DE TURMA",
        resultados_tde['por_turma'],
        resultados_vocab['por_turma']
    ))
    
    relatorio.extend(formatar_secao(
        "4. ANÁLISE CRUZADA (ANO CALENDÁRIO × ANO DE TURMA)",
        resultados_tde['cruzado'],
        resultados_vocab['cruzado']
    ))
    
    # Resumo executivo
    relatorio.extend([
        "\n" + "=" * 80,
        "RESUMO EXECUTIVO",
        "=" * 80,
        ""
    ])
    
    # Função para resumir resultados
    def resumir_d_cohen(dados: dict, nome_prova: str):
        resumo = [f"\n{nome_prova}:"]
        
        # Por ano calendário
        d_2023 = dados['por_ano']['d_cohen'].get(2023, np.nan)
        d_2024 = dados['por_ano']['d_cohen'].get(2024, np.nan)
        
        resumo.extend([
            f"  2023 (Fase 2): d = {d_2023:.3f} ({classificar_d_cohen(d_2023)})" if not np.isnan(d_2023) else "  2023: Sem dados",
            f"  2024 (Fases 3-4): d = {d_2024:.3f} ({classificar_d_cohen(d_2024)})" if not np.isnan(d_2024) else "  2024: Sem dados"
        ])
        
        # Melhor desempenho por ano de turma
        d_por_turma = dados['por_turma']['d_cohen']
        if d_por_turma:
            melhor_turma = max(d_por_turma.items(), key=lambda x: x[1] if not np.isnan(x[1]) else -999)
            resumo.append(f"  Melhor desempenho: {melhor_turma[0]} (d = {melhor_turma[1]:.3f})")
        
        return resumo
    
    relatorio.extend(resumir_d_cohen(resultados_tde, "📝 TDE"))
    relatorio.extend(resumir_d_cohen(resultados_vocab, "📚 VOCABULÁRIO"))
    
    # Rodapé
    relatorio.extend([
        "\n" + "=" * 80,
        "NOTAS METODOLÓGICAS:",
        "- d de Cohen calculado como (M_pos - M_pre) / DP_agrupado",
        "- Interpretação baseada em Cohen (1988) e benchmarks educacionais",
        "- TDE: d ≥ 0.40 considerado bom resultado (Hattie, 2009)",
        "- Vocabulário: d ≥ 0.35 considerado impacto significativo (Marulis & Neuman, 2010)",
        "=" * 80
    ])
    
    return "\n".join(relatorio)

def main():
    """Função principal"""
    print("=" * 80)
    print("🎯 RELATÓRIO DE DESEMPENHO AGREGADO POR ANO E FASE")
    print("=" * 80)
    
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
    
    # Gerar estatísticas
    print("\n📊 Gerando estatísticas agregadas...")
    resultados_tde = gerar_estatisticas_agregadas(df_tde) if not df_tde.empty else {}
    resultados_vocab = gerar_estatisticas_agregadas(df_vocab) if not df_vocab.empty else {}
    
    # Gerar relatório
    print("\n📋 Formatando relatório...")
    relatorio_texto = formatar_relatorio(resultados_tde, resultados_vocab)
    
    # Salvar relatório
    arquivo_saida = ANALISE_DIR / f"relatorio_desempenho_agregado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write(relatorio_texto)
    
    print(f"✅ Relatório salvo em: {arquivo_saida}")
    print(f"📄 Tamanho: {arquivo_saida.stat().st_size / 1024:.1f} KB")
    
    # Mostrar resumo no console
    print("\n" + "=" * 80)
    print("PREVIEW DO RELATÓRIO:")
    print("=" * 80)
    linhas = relatorio_texto.split('\n')
    for linha in linhas[:50]:  # Primeiras 50 linhas
        print(linha)
    
    if len(linhas) > 50:
        print(f"\n... e mais {len(linhas) - 50} linhas no arquivo completo.")
    
    print("\n✅ PROCESSO CONCLUÍDO COM SUCESSO!")

if __name__ == "__main__":
    main()