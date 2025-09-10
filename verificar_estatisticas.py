#!/usr/bin/env python3
"""
Script para verificar as estatísticas do relatório longitudinal
"""

import pandas as pd
import json
from pathlib import Path

# Configuração dos caminhos
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "Modules" / "Longitudinal" / "Data"

CSV_TDE = DATA_DIR / "dados_longitudinais_TDE.csv"
CSV_VOCAB = DATA_DIR / "dados_longitudinais_Vocabulario.csv"
JSON_TDE = DATA_DIR / "resumo_longitudinal_TDE.json"
JSON_VOCAB = DATA_DIR / "resumo_longitudinal_Vocabulario.json"

print("📊 Verificação das Estatísticas do Relatório Longitudinal")
print("="*60)

# Carregar dados
df_tde = pd.read_csv(CSV_TDE) if CSV_TDE.exists() else pd.DataFrame()
df_vocab = pd.read_csv(CSV_VOCAB) if CSV_VOCAB.exists() else pd.DataFrame()

with open(JSON_TDE, 'r', encoding='utf-8') as f:
    resumo_tde = json.load(f) if JSON_TDE.exists() else {}

with open(JSON_VOCAB, 'r', encoding='utf-8') as f:
    resumo_vocab = json.load(f) if JSON_VOCAB.exists() else {}

print(f"✅ Dados carregados:")
print(f"   TDE: {len(df_tde)} registros")
print(f"   Vocabulário: {len(df_vocab)} registros")

print(f"\n📊 TABELA 1: Número de Alunos por Fase")
print("="*50)
print(f"{'Fase':<8} {'TDE':<8} {'Vocabulário':<12} {'Total':<8}")
print("-" * 50)

for fase in [2, 3, 4]:
    # Calcular dos CSVs
    tde_alunos = len(df_tde[df_tde['Fase'] == fase]) if not df_tde.empty else 0
    vocab_alunos = len(df_vocab[df_vocab['Fase'] == fase]) if not df_vocab.empty else 0
    total_alunos = tde_alunos + vocab_alunos
    
    print(f"Fase {fase:<4} {tde_alunos:<8} {vocab_alunos:<12} {total_alunos:<8}")
    
    # Verificar com resumos JSON
    tde_json = resumo_tde.get('por_fase', {}).get(f'Fase {fase}', {}).get('total_estudantes', 0)
    vocab_json = resumo_vocab.get('por_fase', {}).get(f'Fase {fase}', {}).get('total_estudantes', 0)
    
    if tde_alunos != tde_json:
        print(f"   ⚠️  TDE: CSV={tde_alunos}, JSON={tde_json}")
    if vocab_alunos != vocab_json:
        print(f"   ⚠️  Vocab: CSV={vocab_alunos}, JSON={vocab_json}")

# Totais
tde_total = len(df_tde)
vocab_total = len(df_vocab)
total_geral = tde_total + vocab_total

print("-" * 50)
print(f"TOTAL    {tde_total:<8} {vocab_total:<12} {total_geral:<8}")

print(f"\n🏫 TABELA 2: Número de Escolas por Fase")
print("="*50)
print(f"{'Fase':<8} {'TDE':<8} {'Vocabulário':<12} {'Agregado':<10}")
print("-" * 50)

for fase in [2, 3, 4]:
    # Calcular dos CSVs
    df_tde_fase = df_tde[df_tde['Fase'] == fase] if not df_tde.empty else pd.DataFrame()
    df_vocab_fase = df_vocab[df_vocab['Fase'] == fase] if not df_vocab.empty else pd.DataFrame()
    
    tde_escolas = len(df_tde_fase['Escola'].unique()) if not df_tde_fase.empty else 0
    vocab_escolas = len(df_vocab_fase['Escola'].unique()) if not df_vocab_fase.empty else 0
    
    # Escolas agregadas (união)
    if not df_tde_fase.empty and not df_vocab_fase.empty:
        escolas_todas = set(df_tde_fase['Escola'].unique()) | set(df_vocab_fase['Escola'].unique())
        agregado = len(escolas_todas)
    elif not df_tde_fase.empty:
        agregado = tde_escolas
    elif not df_vocab_fase.empty:
        agregado = vocab_escolas
    else:
        agregado = 0
    
    print(f"Fase {fase:<4} {tde_escolas:<8} {vocab_escolas:<12} {agregado:<10}")

# Totais de escolas
tde_escolas_total = len(df_tde['Escola'].unique()) if not df_tde.empty else 0
vocab_escolas_total = len(df_vocab['Escola'].unique()) if not df_vocab.empty else 0

if not df_tde.empty and not df_vocab.empty:
    escolas_todas_geral = set(df_tde['Escola'].unique()) | set(df_vocab['Escola'].unique())
    agregado_total = len(escolas_todas_geral)
else:
    agregado_total = max(tde_escolas_total, vocab_escolas_total)

print("-" * 50)
print(f"TOTAL    {tde_escolas_total:<8} {vocab_escolas_total:<12} {agregado_total:<10}")

print(f"\n✅ Verificação concluída!")
print(f"💾 Relatório disponível em: {DATA_DIR}/relatorio_visual_longitudinal.html")
