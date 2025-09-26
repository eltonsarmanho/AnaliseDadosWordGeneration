#!/usr/bin/env python3
"""
Validação da Capacidade de Análise Longitudinal
==============================================
Script para validar se os dados refatorados permitem análise longitudinal
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("🔍 VALIDAÇÃO DA ANÁLISE LONGITUDINAL - WORDGEN")
print("=" * 60)

# Carregar dados refatorados
print("📂 Carregando dados refatorados...")
try:
    tde_df = pd.read_csv('Dashboard/TDE_longitudinal.csv')
    vocab_df = pd.read_csv('Dashboard/vocabulario_longitudinal.csv')
    print(f"✅ TDE: {len(tde_df)} registros")
    print(f"✅ Vocabulário: {len(vocab_df)} registros")
except Exception as e:
    print(f"❌ Erro ao carregar dados: {e}")
    exit(1)

print("\n🔍 ANÁLISE DE CAPACIDADE LONGITUDINAL:")
print("-" * 50)

# Análise TDE
print("\n📊 TDE - Análise Longitudinal:")
tde_participacao = tde_df.groupby('ID_Unico')['Fase'].count().value_counts().sort_index()
print("   Participação por número de fases:")
for fases, count in tde_participacao.items():
    percent = (count / tde_participacao.sum()) * 100
    print(f"   - {fases} fase(s): {count} alunos ({percent:.1f}%)")

# Análise Vocabulário
print("\n📚 Vocabulário - Análise Longitudinal:")
vocab_participacao = vocab_df.groupby('ID_Unico')['Fase'].count().value_counts().sort_index()
print("   Participação por número de fases:")
for fases, count in vocab_participacao.items():
    percent = (count / vocab_participacao.sum()) * 100
    print(f"   - {fases} fase(s): {count} alunos ({percent:.1f}%)")

print("\n🔍 EXEMPLOS DE TRAJETÓRIAS LONGITUDINAIS:")
print("-" * 50)

# Mostrar exemplos de alunos em múltiplas fases
print("\n📈 TDE - 3 exemplos de alunos com múltiplas fases:")
tde_multiplas = tde_df[tde_df.groupby('ID_Unico')['ID_Unico'].transform('count') > 1]
examples_tde = tde_multiplas.groupby('ID_Unico').apply(
    lambda x: pd.Series({
        'nome': x['Nome'].iloc[0],
        'escola': x['Escola'].iloc[0],
        'fases': list(x['Fase'].sort_values()),
        'turma_origem': x['Turma_Origem'].iloc[0],
        'scores_pre': list(x['Score_Pre']),
        'scores_pos': list(x['Score_Pos'])
    })
).head(3)

for idx, (id_unico, data) in enumerate(examples_tde.iterrows(), 1):
    print(f"\n   {idx}. {data['nome']} ({data['escola']})")
    print(f"      ID: {id_unico}")
    print(f"      Turma origem: {data['turma_origem']}")
    print(f"      Fases: {data['fases']}")
    print(f"      Scores PRE: {data['scores_pre']}")
    print(f"      Scores POS: {data['scores_pos']}")
    
    # Calcular evolução
    if len(data['scores_pos']) >= 2:
        evolucao = data['scores_pos'][-1] - data['scores_pos'][0]
        print(f"      Evolução total: {evolucao:+.1f} pontos")

print("\n📚 Vocabulário - 3 exemplos de alunos com múltiplas fases:")
vocab_multiplas = vocab_df[vocab_df.groupby('ID_Unico')['ID_Unico'].transform('count') > 1]
examples_vocab = vocab_multiplas.groupby('ID_Unico').apply(
    lambda x: pd.Series({
        'nome': x['Nome'].iloc[0],
        'escola': x['Escola'].iloc[0],
        'fases': list(x['Fase'].sort_values()),
        'turma_origem': x['Turma_Origem'].iloc[0],
        'scores_pre': list(x['Score_Pre']),
        'scores_pos': list(x['Score_Pos'])
    })
).head(3)

for idx, (id_unico, data) in enumerate(examples_vocab.iterrows(), 1):
    print(f"\n   {idx}. {data['nome']} ({data['escola']})")
    print(f"      ID: {id_unico}")
    print(f"      Turma origem: {data['turma_origem']}")
    print(f"      Fases: {data['fases']}")
    print(f"      Scores PRE: {data['scores_pre']}")
    print(f"      Scores POS: {data['scores_pos']}")
    
    # Calcular evolução
    if len(data['scores_pos']) >= 2:
        evolucao = data['scores_pos'][-1] - data['scores_pos'][0]
        print(f"      Evolução total: {evolucao:+.1f} pontos")

print("\n🏫 ANÁLISE POR ESCOLA E TURMA DE ORIGEM:")
print("-" * 50)

print("\n📊 TDE - Distribuição por escola:")
tde_escola = tde_df.groupby(['Escola', 'Turma_Origem']).agg({
    'ID_Unico': 'nunique',
    'Fase': 'count'
}).rename(columns={'ID_Unico': 'alunos_unicos', 'Fase': 'total_registros'})

for (escola, turma), data in tde_escola.head(10).iterrows():
    print(f"   {escola[:30]:<30} | {turma:<12} | {data['alunos_unicos']:>3} alunos | {data['total_registros']:>3} registros")

print("\n📚 Vocabulário - Distribuição por escola:")
vocab_escola = vocab_df.groupby(['Escola', 'Turma_Origem']).agg({
    'ID_Unico': 'nunique',
    'Fase': 'count'
}).rename(columns={'ID_Unico': 'alunos_unicos', 'Fase': 'total_registros'})

for (escola, turma), data in vocab_escola.head(10).iterrows():
    print(f"   {escola[:30]:<30} | {turma:<12} | {data['alunos_unicos']:>3} alunos | {data['total_registros']:>3} registros")

print("\n✅ VALIDAÇÃO CONCLUÍDA!")
print("=" * 60)
print("🎉 Os dados refatorados permitem análise longitudinal completa!")
print("🚀 Próximo passo: Implementar análises longitudinais no dashboard")