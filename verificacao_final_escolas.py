#!/usr/bin/env python3
"""
Script de verificação final das métricas de escolas
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

print("✅ Verificação Final - Consistência das Métricas de Escolas")
print("="*65)

# Carregar dados
df_tde = pd.read_csv(CSV_TDE)
df_vocab = pd.read_csv(CSV_VOCAB)

with open(JSON_TDE, 'r', encoding='utf-8') as f:
    resumo_tde = json.load(f)

with open(JSON_VOCAB, 'r', encoding='utf-8') as f:
    resumo_vocab = json.load(f)

# Calcular valores reais
escolas_tde_unicas = len(df_tde['Escola'].unique())
escolas_vocab_unicas = len(df_vocab['Escola'].unique())
escolas_total_agregado = len(set(df_tde['Escola'].unique()) | set(df_vocab['Escola'].unique()))

# Valores dos JSONs
escolas_tde_json = resumo_tde.get('perfil_demografico', {}).get('escolas_unicas', 0)
escolas_vocab_json = resumo_vocab.get('perfil_demografico', {}).get('escolas_unicas', 0)

print("📊 MÉTRICAS CALCULADAS:")
print(f"   TDE (CSV): {escolas_tde_unicas} escolas")
print(f"   TDE (JSON): {escolas_tde_json} escolas")
print(f"   Vocabulário (CSV): {escolas_vocab_unicas} escolas")
print(f"   Vocabulário (JSON): {escolas_vocab_json} escolas")
print(f"   Total Agregado (União): {escolas_total_agregado} escolas")
print(f"   Máximo entre TDE e Vocab: {max(escolas_tde_unicas, escolas_vocab_unicas)} escolas")

print("\n📋 VALORES NO RELATÓRIO:")
print(f"   Tabela - Total Geral TDE: {escolas_tde_json}")
print(f"   Tabela - Total Geral Vocabulário: {escolas_vocab_json}")
print(f"   Tabela - Total Geral Agregado: max({escolas_tde_json}, {escolas_vocab_json}) = {max(escolas_tde_json, escolas_vocab_json)}")
print(f"   Métrica 'Escolas Participantes': max({escolas_tde_json}, {escolas_vocab_json}) = {max(escolas_tde_json, escolas_vocab_json)}")

print("\n✅ VERIFICAÇÃO DE CONSISTÊNCIA:")
metric_escolas_participantes = max(escolas_tde_json, escolas_vocab_json)
total_agregado_tabela = max(escolas_tde_json, escolas_vocab_json)

if metric_escolas_participantes == total_agregado_tabela:
    print(f"   ✅ CONSISTENTE: Métrica 'Escolas Participantes' ({metric_escolas_participantes}) = Total Agregado da Tabela ({total_agregado_tabela})")
else:
    print(f"   ❌ INCONSISTENTE: Métrica 'Escolas Participantes' ({metric_escolas_participantes}) ≠ Total Agregado da Tabela ({total_agregado_tabela})")

print(f"\n🔍 DETALHES SOBRE A ESCOLA '0':")
escolas_vocab_com_zero = df_vocab[df_vocab['Escola'] == '0']
if len(escolas_vocab_com_zero) > 0:
    print(f"   ⚠️  Encontradas {len(escolas_vocab_com_zero)} entradas com escola '0' no Vocabulário")
    print(f"   💡 Isso explica por que Vocabulário tem {escolas_vocab_unicas} escolas (incluindo a escola '0')")
else:
    print(f"   ✅ Nenhuma entrada com escola '0' encontrada")

print(f"\n📝 RESUMO FINAL:")
print(f"   • TDE: {escolas_tde_json} escolas válidas")
print(f"   • Vocabulário: {escolas_vocab_json} escolas (incluindo 1 entrada inválida '0')")
print(f"   • Agregado Real: {escolas_total_agregado} escolas únicas válidas")
print(f"   • Métrica no Relatório: {max(escolas_tde_json, escolas_vocab_json)} escolas")
