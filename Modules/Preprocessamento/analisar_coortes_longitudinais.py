#!/usr/bin/env python3
"""
Análise Longitudinal de Coortes - WordGen
=========================================

Este script analisa os dados consolidados das fases 2, 3 e 4 para:
1. Identificar grupos de alunos que participaram das fases
2. Analisar progressão/repetência por ano escolar
3. Mapear coortes por escola e turma de origem
4. Quantificar participação e evolução dos grupos
"""

import pandas as pd
import numpy as np
import sys
import os

# Adicionar path do Dashboard
sys.path.append(os.path.join(os.path.dirname(__file__), 'Dashboard'))
from data_loader import get_datasets

def normalizar_nome_escola(escola):
    """Normaliza nomes de escolas para agrupamento"""
    if pd.isna(escola):
        return escola
    
    escola = str(escola).upper().strip()
    # Remover acentos
    import unicodedata
    escola = ''.join(c for c in unicodedata.normalize('NFD', escola) 
                    if unicodedata.category(c) != 'Mn')
    
    # Padronizar termos comuns
    escola = escola.replace('EMEB ', '').replace('EMEF ', '')
    escola = escola.replace('ESCOLA MUNICIPAL ', '')
    
    return escola

def extrair_ano_escolar(turma):
    """Extrai o ano escolar (6, 7, 8, 9) da string da turma"""
    if pd.isna(turma):
        return None
    
    turma_str = str(turma).upper()
    
    # Procurar padrões de ano
    import re
    match = re.search(r'\b([6-9])\b', turma_str)
    if match:
        return int(match.group(1))
    
    return None

def analisar_trajetoria_aluno(df_aluno):
    """Analisa a trajetória de um aluno específico"""
    if df_aluno.empty:
        return None
        
    trajetoria = {
        'nome': df_aluno['Nome'].iloc[0],
        'escola_origem': df_aluno['Escola'].iloc[0],
        'turma_origem': df_aluno['Turma'].iloc[0],
        'fases_participou': sorted(df_aluno['Fase'].unique()),
        'num_fases': len(df_aluno['Fase'].unique()),
        'anos_escolares': {}
    }
    
    # Mapear ano escolar por fase
    for _, row in df_aluno.iterrows():
        fase = row['Fase']
        ano = extrair_ano_escolar(row['Turma'])
        trajetoria['anos_escolares'][fase] = ano
    
    # Determinar tipo de trajetória
    anos_unicos = list(trajetoria['anos_escolares'].values())
    anos_unicos = [a for a in anos_unicos if a is not None]
    
    if len(anos_unicos) <= 1:
        trajetoria['tipo'] = 'ÚNICA_FASE_OU_MESMO_ANO'
    elif len(set(anos_unicos)) == 1:
        trajetoria['tipo'] = 'REPETÊNCIA'
    elif anos_unicos == sorted(anos_unicos):
        trajetoria['tipo'] = 'PROGRESSÃO_NORMAL'
    else:
        trajetoria['tipo'] = 'TRAJETÓRIA_IRREGULAR'
    
    return trajetoria

def identificar_coortes(df):
    """Identifica coortes de alunos baseado em escola e turma de origem"""
    print(f"Analisando {len(df)} registros...")
    
    # Agrupar por aluno
    trajetorias = []
    alunos_únicos = df['Nome'].unique()
    
    print(f"Encontrados {len(alunos_únicos)} alunos únicos")
    
    for nome in alunos_únicos:
        df_aluno = df[df['Nome'] == nome]
        if not df_aluno.empty:
            trajetoria = analisar_trajetoria_aluno(df_aluno)
            if trajetoria is not None:
                trajetorias.append(trajetoria)
    
    # Converter para DataFrame para análise
    df_trajetorias = pd.DataFrame(trajetorias)
    
    # Criar identificador de coorte baseado em escola + ano inicial
    def criar_id_coorte(row):
        escola_norm = normalizar_nome_escola(row['escola_origem'])
        
        # Pegar o primeiro ano escolar mencionado
        primeiro_ano = None
        if row['anos_escolares']:
            fases_ordenadas = sorted(row['anos_escolares'].keys())
            for fase in fases_ordenadas:
                if row['anos_escolares'][fase] is not None:
                    primeiro_ano = row['anos_escolares'][fase]
                    break
        
        if primeiro_ano is None:
            return f"INDETERMINADO_{escola_norm}"
        
        return f"COORTE_{primeiro_ano}ANO_{escola_norm}"
    
    df_trajetorias['coorte_id'] = df_trajetorias.apply(criar_id_coorte, axis=1)
    
    return df_trajetorias

def analisar_dados_tde():
    """Análise específica dos dados TDE"""
    print("=" * 80)
    print("📚 ANÁLISE DOS DADOS TDE")
    print("=" * 80)
    
    tde_df, _ = get_datasets()
    
    # Informações gerais
    print(f"Total de registros: {len(tde_df)}")
    print(f"Alunos únicos: {tde_df['Nome'].nunique()}")
    print(f"Escolas: {tde_df['Escola'].nunique()}")
    print(f"Fases: {sorted(tde_df['Fase'].unique())}")
    
    # Análise de trajetórias
    df_trajetorias = identificar_coortes(tde_df)
    
    print("\n--- ANÁLISE DE TRAJETÓRIAS ---")
    tipos_trajetoria = df_trajetorias['tipo'].value_counts()
    for tipo, count in tipos_trajetoria.items():
        pct = (count / len(df_trajetorias)) * 100
        print(f"  {tipo}: {count} alunos ({pct:.1f}%)")
    
    print("\n--- PARTICIPAÇÃO POR NÚMERO DE FASES ---")
    participacao_fases = df_trajetorias['num_fases'].value_counts().sort_index()
    for num_fases, count in participacao_fases.items():
        pct = (count / len(df_trajetorias)) * 100
        print(f"  {num_fases} fase(s): {count} alunos ({pct:.1f}%)")
    
    print("\n--- TOP 10 COORTES POR NÚMERO DE ALUNOS ---")
    coortes_count = df_trajetorias['coorte_id'].value_counts().head(10)
    for coorte, count in coortes_count.items():
        print(f"  {coorte}: {count} alunos")
    
    # Análise detalhada de coortes longitudinais (múltiplas fases)
    coortes_longitudinais = df_trajetorias[df_trajetorias['num_fases'] > 1]
    print(f"\n--- COORTES LONGITUDINAIS (múltiplas fases): {len(coortes_longitudinais)} alunos ---")
    
    if len(coortes_longitudinais) > 0:
        print("\nDistribuição por tipo de trajetória:")
        tipos_long = coortes_longitudinais['tipo'].value_counts()
        for tipo, count in tipos_long.items():
            pct = (count / len(coortes_longitudinais)) * 100
            print(f"  {tipo}: {count} alunos ({pct:.1f}%)")
        
        print("\nTop 5 coortes longitudinais:")
        coortes_long_count = coortes_longitudinais['coorte_id'].value_counts().head(5)
        for coorte, count in coortes_long_count.items():
            print(f"  {coorte}: {count} alunos")
    
    return df_trajetorias

def analisar_dados_vocabulario():
    """Análise específica dos dados Vocabulário"""
    print("\n" + "=" * 80)
    print("📖 ANÁLISE DOS DADOS VOCABULÁRIO")
    print("=" * 80)
    
    _, vocab_df = get_datasets()
    
    # Informações gerais
    print(f"Total de registros: {len(vocab_df)}")
    print(f"Alunos únicos: {vocab_df['Nome'].nunique()}")
    print(f"Escolas: {vocab_df['Escola'].nunique()}")
    print(f"Fases: {sorted(vocab_df['Fase'].unique())}")
    
    # Análise de trajetórias
    df_trajetorias = identificar_coortes(vocab_df)
    
    print("\n--- ANÁLISE DE TRAJETÓRIAS ---")
    tipos_trajetoria = df_trajetorias['tipo'].value_counts()
    for tipo, count in tipos_trajetoria.items():
        pct = (count / len(df_trajetorias)) * 100
        print(f"  {tipo}: {count} alunos ({pct:.1f}%)")
    
    print("\n--- PARTICIPAÇÃO POR NÚMERO DE FASES ---")
    participacao_fases = df_trajetorias['num_fases'].value_counts().sort_index()
    for num_fases, count in participacao_fases.items():
        pct = (count / len(df_trajetorias)) * 100
        print(f"  {num_fases} fase(s): {count} alunos ({pct:.1f}%)")
    
    print("\n--- TOP 10 COORTES POR NÚMERO DE ALUNOS ---")
    coortes_count = df_trajetorias['coorte_id'].value_counts().head(10)
    for coorte, count in coortes_count.items():
        print(f"  {coorte}: {count} alunos")
    
    # Análise detalhada de coortes longitudinais
    coortes_longitudinais = df_trajetorias[df_trajetorias['num_fases'] > 1]
    print(f"\n--- COORTES LONGITUDINAIS (múltiplas fases): {len(coortes_longitudinais)} alunos ---")
    
    if len(coortes_longitudinais) > 0:
        print("\nDistribuição por tipo de trajetória:")
        tipos_long = coortes_longitudinais['tipo'].value_counts()
        for tipo, count in tipos_long.items():
            pct = (count / len(coortes_longitudinais)) * 100
            print(f"  {tipo}: {count} alunos ({pct:.1f}%)")
        
        print("\nTop 5 coortes longitudinais:")
        coortes_long_count = coortes_longitudinais['coorte_id'].value_counts().head(5)
        for coorte, count in coortes_long_count.items():
            print(f"  {coorte}: {count} alunos")
    
    return df_trajetorias

def análise_cruzada():
    """Análise cruzada entre TDE e Vocabulário"""
    print("\n" + "=" * 80)
    print("🔗 ANÁLISE CRUZADA TDE vs VOCABULÁRIO")
    print("=" * 80)
    
    tde_df, vocab_df = get_datasets()
    
    # Alunos que participaram de ambas as provas
    alunos_tde = set(tde_df['Nome'].unique())
    alunos_vocab = set(vocab_df['Nome'].unique())
    
    alunos_ambas = alunos_tde.intersection(alunos_vocab)
    apenas_tde = alunos_tde - alunos_vocab
    apenas_vocab = alunos_vocab - alunos_tde
    
    print(f"Alunos que fizeram TDE: {len(alunos_tde)}")
    print(f"Alunos que fizeram Vocabulário: {len(alunos_vocab)}")
    print(f"Alunos que fizeram ambas: {len(alunos_ambas)} ({len(alunos_ambas)/max(len(alunos_tde), len(alunos_vocab))*100:.1f}%)")
    print(f"Apenas TDE: {len(apenas_tde)}")
    print(f"Apenas Vocabulário: {len(apenas_vocab)}")
    
    # Análise por fase
    print("\n--- PARTICIPAÇÃO POR FASE ---")
    for fase in sorted(set(tde_df['Fase'].unique()).union(set(vocab_df['Fase'].unique()))):
        tde_fase = tde_df[tde_df['Fase'] == fase]['Nome'].nunique()
        vocab_fase = vocab_df[vocab_df['Fase'] == fase]['Nome'].nunique()
        print(f"  Fase {fase}: TDE={tde_fase} alunos, Vocabulário={vocab_fase} alunos")

def main():
    """Função principal de análise"""
    print("🔍 ANÁLISE LONGITUDINAL DE COORTES - WORDGEN")
    print("=" * 80)
    
    try:
        # Análise TDE
        trajetorias_tde = analisar_dados_tde()
        
        # Análise Vocabulário  
        trajetorias_vocab = analisar_dados_vocabulario()
        
        # Análise cruzada
        análise_cruzada()
        
        print("\n" + "=" * 80)
        print("✅ ANÁLISE CONCLUÍDA COM SUCESSO")
        print("=" * 80)
        
        return trajetorias_tde, trajetorias_vocab
        
    except Exception as e:
        print(f"❌ Erro durante a análise: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    main()