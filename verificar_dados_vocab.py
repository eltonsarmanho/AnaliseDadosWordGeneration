#!/usr/bin/env python3
"""
Script para verificar se os dados de vocabulário estão sendo carregados corretamente
"""

import pandas as pd
import json
from pathlib import Path

# Configuração dos caminhos
BASE_DIR = Path(__file__).parent
CSV_LONGITUDINAL_VOCAB = BASE_DIR / "Modules" / "Longitudinal" / "Data" / "dados_longitudinais_vocabulario.csv"
JSON_RESUMO_VOCAB = BASE_DIR / "Modules" / "Longitudinal" / "Data" / "resumo_longitudinal_vocabulario.json"

print("🔍 Verificando dados de Vocabulário...")
print("="*50)

# Verificar se os arquivos existem
print(f"📁 CSV Vocabulário: {CSV_LONGITUDINAL_VOCAB}")
print(f"   Existe: {CSV_LONGITUDINAL_VOCAB.exists()}")

print(f"📁 JSON Resumo Vocabulário: {JSON_RESUMO_VOCAB}")
print(f"   Existe: {JSON_RESUMO_VOCAB.exists()}")

# Verificar conteúdo dos arquivos se existirem
if CSV_LONGITUDINAL_VOCAB.exists():
    try:
        df_vocab = pd.read_csv(CSV_LONGITUDINAL_VOCAB)
        print(f"📊 Dados CSV Vocabulário: {len(df_vocab)} registros")
        if not df_vocab.empty:
            print(f"   Colunas: {list(df_vocab.columns)}")
            print(f"   Fases: {sorted(df_vocab['Fase'].unique()) if 'Fase' in df_vocab.columns else 'N/A'}")
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")

if JSON_RESUMO_VOCAB.exists():
    try:
        with open(JSON_RESUMO_VOCAB, 'r', encoding='utf-8') as f:
            resumo_vocab = json.load(f)
        print(f"📋 Resumo JSON Vocabulário:")
        print(f"   Total estudantes: {resumo_vocab.get('total_estudantes', 'N/A')}")
        print(f"   Fases: {list(resumo_vocab.get('por_fase', {}).keys())}")
        print(f"   Escolas: {resumo_vocab.get('perfil_demografico', {}).get('escolas_unicas', 'N/A')}")
    except Exception as e:
        print(f"❌ Erro ao ler JSON: {e}")

# Verificar se pipeline de vocabulário foi executado
pipeline_vocab = BASE_DIR / "Modules" / "Longitudinal" / "PipelineDataLongitudinalVocabulario.py"
print(f"\n🔧 Pipeline Vocabulário: {pipeline_vocab}")
print(f"   Existe: {pipeline_vocab.exists()}")

print(f"\n💡 Sugestão: Execute o pipeline de Vocabulário para gerar os dados:")
print(f"   python {pipeline_vocab}")
