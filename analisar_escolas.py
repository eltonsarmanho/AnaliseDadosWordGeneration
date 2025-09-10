#!/usr/bin/env python3
"""
Script para analisar as escolas únicas entre TDE e Vocabulário
"""

import pandas as pd
import json
from pathlib import Path

# Configuração dos caminhos
BASE_DIR = Path(__file__).parent
CSV_TDE = BASE_DIR / "Modules" / "Longitudinal" / "Data" / "dados_longitudinais_TDE.csv"
CSV_VOCAB = BASE_DIR / "Modules" / "Longitudinal" / "Data" / "dados_longitudinais_Vocabulario.csv"
JSON_TDE = BASE_DIR / "Modules" / "Longitudinal" / "Data" / "resumo_longitudinal_TDE.json"
JSON_VOCAB = BASE_DIR / "Modules" / "Longitudinal" / "Data" / "resumo_longitudinal_Vocabulario.json"

print("🔍 Analisando Escolas Únicas - TDE vs Vocabulário")
print("="*60)

# Carregar dados
df_tde = pd.read_csv(CSV_TDE)
df_vocab = pd.read_csv(CSV_VOCAB)

with open(JSON_TDE, 'r', encoding='utf-8') as f:
    resumo_tde = json.load(f)

with open(JSON_VOCAB, 'r', encoding='utf-8') as f:
    resumo_vocab = json.load(f)

# Analisar escolas únicas
escolas_tde = set(df_tde['Escola'].unique())
escolas_vocab = set(df_vocab['Escola'].unique())
escolas_todas = escolas_tde | escolas_vocab

print(f"📊 ANÁLISE DE ESCOLAS:")
print(f"   TDE: {len(escolas_tde)} escolas únicas")
print(f"   Vocabulário: {len(escolas_vocab)} escolas únicas")
print(f"   Total Agregado (União): {len(escolas_todas)} escolas únicas")

print(f"\n📋 RESUMOS JSON:")
print(f"   TDE JSON: {resumo_tde.get('perfil_demografico', {}).get('escolas_unicas', 0)} escolas")
print(f"   Vocabulário JSON: {resumo_vocab.get('perfil_demografico', {}).get('escolas_unicas', 0)} escolas")

print(f"\n🏫 ESCOLAS TDE:")
for i, escola in enumerate(sorted(escolas_tde), 1):
    print(f"   {i:2d}. {escola}")

print(f"\n🏫 ESCOLAS VOCABULÁRIO:")
for i, escola in enumerate(sorted(escolas_vocab), 1):
    print(f"   {i:2d}. {escola}")

print(f"\n🔄 COMPARAÇÃO:")
escolas_apenas_tde = escolas_tde - escolas_vocab
escolas_apenas_vocab = escolas_vocab - escolas_tde
escolas_ambos = escolas_tde & escolas_vocab

print(f"   Apenas TDE: {len(escolas_apenas_tde)} escolas")
for escola in sorted(escolas_apenas_tde):
    print(f"      • {escola}")

print(f"   Apenas Vocabulário: {len(escolas_apenas_vocab)} escolas")
for escola in sorted(escolas_apenas_vocab):
    print(f"      • {escola}")

print(f"   Em ambos: {len(escolas_ambos)} escolas")
for escola in sorted(escolas_ambos):
    print(f"      • {escola}")

print(f"\n💡 RECOMENDAÇÃO:")
print(f"   Para o total agregado, usar: max({len(escolas_tde)}, {len(escolas_vocab)}) = {max(len(escolas_tde), len(escolas_vocab))}")
print(f"   Ou união completa: {len(escolas_todas)} escolas")
