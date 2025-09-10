#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICAÇÃO DE DADOS LONGITUDINAIS
Script para verificar a qualidade dos dados processados
"""

import pandas as pd
import json
import pathlib

# Caminhos
BASE_DIR = pathlib.Path(__file__).parent
DATA_DIR = BASE_DIR / "Data"

# Carregar dados
df_tde = pd.read_csv(DATA_DIR / "dados_longitudinais_TDE.csv")
df_vocab = pd.read_csv(DATA_DIR / "dados_longitudinais_Vocabulario.csv")

print("🔍 VERIFICAÇÃO DE DADOS LONGITUDINAIS")
print("="*50)

print("\n📊 DADOS TDE:")
print(f"Total de registros: {len(df_tde)}")
print(f"Fases presentes: {sorted(df_tde['Fase'].unique())}")
print(f"Escolas únicas: {df_tde['Escola'].nunique()}")

print("\nDistribuição por fase:")
print(df_tde['Fase'].value_counts().sort_index())

print("\nDistribuição Score_Pos = 0:")
zeros_pos = df_tde[df_tde['Score_Pos'] == 0]
print(f"Registros com Score_Pos = 0: {len(zeros_pos)} ({len(zeros_pos)/len(df_tde)*100:.1f}%)")

print("\nDistribuição de Score_Pos = 0 por fase:")
print(zeros_pos['Fase'].value_counts().sort_index())

print("\nEstatísticas Score_Pre:")
print(df_tde['Score_Pre'].describe())

print("\nEstatísticas Score_Pos (excluindo zeros):")
df_pos_nao_zero = df_tde[df_tde['Score_Pos'] > 0]
if not df_pos_nao_zero.empty:
    print(df_pos_nao_zero['Score_Pos'].describe())
else:
    print("Nenhum registro com Score_Pos > 0")

print("\n📊 DADOS VOCABULÁRIO:")
print(f"Total de registros: {len(df_vocab)}")
print(f"Fases presentes: {sorted(df_vocab['Fase'].unique())}")
print(f"Escolas únicas: {df_vocab['Escola'].nunique()}")

print("\nDistribuição por fase:")
print(df_vocab['Fase'].value_counts().sort_index())

print("\n🎯 TAXA DE MELHORIA por fase (TDE):")
for fase in sorted(df_tde['Fase'].unique()):
    df_fase = df_tde[df_tde['Fase'] == fase]
    taxa_melhoria = df_fase['Melhoria'].mean() * 100
    print(f"Fase {fase}: {taxa_melhoria:.1f}%")

print("\n🎯 TAXA DE MELHORIA por fase (Vocabulário):")
for fase in sorted(df_vocab['Fase'].unique()):
    df_fase = df_vocab[df_vocab['Fase'] == fase]
    taxa_melhoria = df_fase['Melhoria'].mean() * 100
    print(f"Fase {fase}: {taxa_melhoria:.1f}%")

print("\n✅ Verificação concluída!")
