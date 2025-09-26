#!/usr/bin/env python3
"""
Teste da Funcionalidade de Coortes
==================================
Script para validar se as coortes estão sendo criadas corretamente
"""

import pandas as pd
import sys
import os

# Adicionar path do Dashboard
sys.path.append(os.path.join(os.path.dirname(__file__), 'Dashboard'))

from data_loader import get_datasets

print("🧪 TESTE DA FUNCIONALIDADE DE COORTES")
print("=" * 50)

# Carregar dados
print("📂 Carregando dados...")
try:
    tde_df, vocab_df = get_datasets()
    print(f"✅ TDE: {len(tde_df)} registros")
    print(f"✅ Vocabulário: {len(vocab_df)} registros")
except Exception as e:
    print(f"❌ Erro ao carregar dados: {e}")
    exit(1)

print("\n🔍 ANÁLISE DE COORTES - TDE:")
print("-" * 30)

# Verificar se coluna Coorte_Origem existe
if 'Coorte_Origem' in tde_df.columns:
    print("✅ Coluna 'Coorte_Origem' criada com sucesso")
    
    # Estatísticas de coortes
    total_coortes = tde_df['Coorte_Origem'].nunique()
    print(f"📊 Total de coortes identificadas: {total_coortes}")
    
    # Top 10 coortes com mais alunos
    coortes_count = tde_df.groupby('Coorte_Origem')['ID_Unico'].nunique().sort_values(ascending=False)
    print(f"\n🏆 Top 10 coortes com mais alunos:")
    for i, (coorte, count) in enumerate(coortes_count.head(10).items(), 1):
        print(f"   {i:2d}. {coorte:<30} | {count:3d} alunos")
    
    # Exemplos de alunos e suas coortes
    print(f"\n👥 Exemplos de alunos e suas coortes:")
    exemplos = tde_df.groupby('ID_Unico').agg({
        'Nome': 'first',
        'Escola': 'first', 
        'Coorte_Origem': 'first',
        'Fase': lambda x: list(sorted(x)),
        'Turma_Origem': 'first'
    }).head(5)
    
    for idx, (id_unico, data) in enumerate(exemplos.iterrows(), 1):
        print(f"   {idx}. {data['Nome'][:25]:<25} | Coorte: {data['Coorte_Origem']:<20} | Fases: {data['Fase']}")
    
    # Análise longitudinal por coorte
    print(f"\n📈 Capacidade longitudinal por coorte (Top 5):")
    longitudinal_por_coorte = tde_df.groupby(['Coorte_Origem', 'ID_Unico'])['Fase'].count().reset_index()
    longitudinal_por_coorte = longitudinal_por_coorte.groupby('Coorte_Origem')['Fase'].agg(['mean', 'count']).sort_values('count', ascending=False)
    
    for coorte, stats in longitudinal_por_coorte.head(5).iterrows():
        print(f"   {coorte:<30} | {int(stats['count']):3d} alunos | Média {stats['mean']:.1f} fases/aluno")

else:
    print("❌ Coluna 'Coorte_Origem' não encontrada")

print("\n🔍 ANÁLISE DE COORTES - VOCABULÁRIO:")
print("-" * 35)

if 'Coorte_Origem' in vocab_df.columns:
    print("✅ Coluna 'Coorte_Origem' criada com sucesso")
    
    total_coortes_vocab = vocab_df['Coorte_Origem'].nunique()
    print(f"📊 Total de coortes identificadas: {total_coortes_vocab}")
    
    # Comparação entre TDE e Vocabulário
    print(f"\n🔄 Comparação TDE vs Vocabulário:")
    coortes_comuns = set(tde_df['Coorte_Origem'].unique()) & set(vocab_df['Coorte_Origem'].unique())
    print(f"   Coortes em comum: {len(coortes_comuns)}")
    print(f"   Coortes só no TDE: {total_coortes - len(coortes_comuns)}")
    print(f"   Coortes só no Vocabulário: {total_coortes_vocab - len(coortes_comuns)}")

else:
    print("❌ Coluna 'Coorte_Origem' não encontrada")

print("\n✅ TESTE CONCLUÍDO!")
print("🚀 Dashboard disponível em: http://localhost:8502")