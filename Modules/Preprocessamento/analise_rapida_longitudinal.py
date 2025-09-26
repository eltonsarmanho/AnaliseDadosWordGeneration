#!/usr/bin/env python3
"""
Análise Rápida dos Dados Longitudinais
"""

import pandas as pd
import sys
import os

# Adicionar path do Dashboard
sys.path.append(os.path.join(os.path.dirname(__file__), 'Dashboard'))
from data_loader import get_datasets

def análise_básica():
    """Análise básica dos dados"""
    print("🔍 ANÁLISE BÁSICA DOS DADOS LONGITUDINAIS")
    print("=" * 60)
    
    tde_df, vocab_df = get_datasets()
    
    print("\n📚 DADOS TDE:")
    print(f"  Total de registros: {len(tde_df)}")
    print(f"  Alunos únicos: {tde_df['Nome'].nunique()}")
    print(f"  Escolas: {tde_df['Escola'].nunique()}")
    print(f"  Fases: {sorted(tde_df['Fase'].unique())}")
    
    print(f"\n  Escolas disponíveis:")
    for escola in sorted(tde_df['Escola'].unique()):
        count = tde_df[tde_df['Escola'] == escola]['Nome'].nunique()
        print(f"    - {escola}: {count} alunos únicos")
    
    print(f"\n  Participação por fase:")
    for fase in sorted(tde_df['Fase'].unique()):
        count = tde_df[tde_df['Fase'] == fase]['Nome'].nunique()
        registros = len(tde_df[tde_df['Fase'] == fase])
        print(f"    - Fase {fase}: {count} alunos únicos, {registros} registros")
    
    print("\n📖 DADOS VOCABULÁRIO:")
    print(f"  Total de registros: {len(vocab_df)}")
    print(f"  Alunos únicos: {vocab_df['Nome'].nunique()}")
    print(f"  Escolas: {vocab_df['Escola'].nunique()}")
    print(f"  Fases: {sorted(vocab_df['Fase'].unique())}")
    
    print(f"\n  Participação por fase:")
    for fase in sorted(vocab_df['Fase'].unique()):
        count = vocab_df[vocab_df['Fase'] == fase]['Nome'].nunique()
        registros = len(vocab_df[vocab_df['Fase'] == fase])
        print(f"    - Fase {fase}: {count} alunos únicos, {registros} registros")
    
    # Análise de participação múltipla (longitudinal)
    print("\n🔗 ANÁLISE LONGITUDINAL:")
    
    # TDE
    participacao_tde = tde_df.groupby('Nome')['Fase'].nunique().value_counts().sort_index()
    print(f"\n  TDE - Participação por número de fases:")
    for num_fases, count in participacao_tde.items():
        pct = (count / len(participacao_tde)) * 100
        print(f"    - {num_fases} fase(s): {count} alunos ({pct:.1f}%)")
    
    # Vocabulário
    participacao_vocab = vocab_df.groupby('Nome')['Fase'].nunique().value_counts().sort_index()
    print(f"\n  VOCABULÁRIO - Participação por número de fases:")
    for num_fases, count in participacao_vocab.items():
        pct = (count / len(participacao_vocab)) * 100
        print(f"    - {num_fases} fase(s): {count} alunos ({pct:.1f}%)")
    
    # Coortes longitudinais (múltiplas fases) - TDE
    alunos_mult_fases_tde = tde_df.groupby('Nome')['Fase'].nunique()
    alunos_longitudinais_tde = alunos_mult_fases_tde[alunos_mult_fases_tde > 1]
    
    print(f"\n  📊 COORTES LONGITUDINAIS TDE:")
    print(f"    - Alunos em múltiplas fases: {len(alunos_longitudinais_tde)}")
    print(f"    - Percentual longitudinal: {len(alunos_longitudinais_tde)/tde_df['Nome'].nunique()*100:.1f}%")
    
    # Análise por escola e ano
    print(f"\n  📈 ANÁLISE POR TURMA/ANO (TDE):")
    turmas_por_fase = {}
    for fase in sorted(tde_df['Fase'].unique()):
        df_fase = tde_df[tde_df['Fase'] == fase]
        turmas = df_fase['Turma'].value_counts().head(5)
        turmas_por_fase[fase] = turmas
        print(f"    Fase {fase} - Top 5 turmas:")
        for turma, count in turmas.items():
            print(f"      - {turma}: {count} alunos")
    
    # Análise de trajetórias de exemplo
    print(f"\n  🎯 EXEMPLOS DE TRAJETÓRIAS LONGITUDINAIS:")
    for nome in list(alunos_longitudinais_tde.head(3).index):
        df_aluno = tde_df[tde_df['Nome'] == nome]
        print(f"    {nome}:")
        for _, row in df_aluno.iterrows():
            print(f"      - Fase {row['Fase']}: {row['Escola']} - {row['Turma']}")

if __name__ == "__main__":
    análise_básica()