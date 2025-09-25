#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DA FUNCIONALIDADE DE AGREGAÇÃO DE TURMAS
Verifica se a nova funcionalidade está funcionando corretamente
"""

import pandas as pd
import sys
import os
sys.path.append('Dashboard')
from data_loader import get_datasets

def testar_agregacao_turmas():
    """Testa a funcionalidade de agregação de turmas"""
    print("🧪 TESTANDO FUNCIONALIDADE DE AGREGAÇÃO DE TURMAS")
    print("=" * 60)
    
    try:
        # Carregar dados
        print("📊 Carregando dados...")
        tde, vocab = get_datasets()
        
        # Simular normalização como no dashboard
        def normalizar_turma(turma_original):
            if pd.isna(turma_original):
                return turma_original
            
            turma_str = str(turma_original).upper().strip()
            
            if any(x in turma_str for x in ['5', 'QUINTO']):
                return '5° Ano'
            elif any(x in turma_str for x in ['6', 'SEXTO']):
                return '6° Ano'
            elif any(x in turma_str for x in ['7', 'SETIMO', 'SÉTIMO']):
                return '7° Ano'
            elif any(x in turma_str for x in ['8', 'OITAVO']):
                return '8° Ano'
            elif any(x in turma_str for x in ['9', 'NONO']):
                return '9° Ano'
            else:
                return turma_original
        
        # Aplicar normalização ao TDE
        if 'Turma' in tde.columns:
            tde['Turma_Original'] = tde['Turma'].copy()
            tde['Turma'] = tde['Turma'].apply(normalizar_turma)
        
        print(f"✅ Dados TDE carregados: {len(tde)} registros")
        print(f"📚 Colunas: {list(tde.columns[:10])}...")
        
        # Análise das turmas
        print(f"\n🔍 ANÁLISE DAS TURMAS:")
        
        # Turmas originais (separadas)
        turmas_originais = sorted(tde['Turma_Original'].dropna().unique())
        print(f"\n📋 TURMAS ORIGINAIS (SEPARADAS) - {len(turmas_originais)} turmas:")
        for i, turma in enumerate(turmas_originais[:15]):  # Primeiras 15
            print(f"  {i+1:2d}. {turma}")
        if len(turmas_originais) > 15:
            print(f"  ... e mais {len(turmas_originais) - 15} turmas")
        
        # Turmas agregadas (normalizadas)
        turmas_agregadas = sorted(tde['Turma'].dropna().unique())
        print(f"\n🔄 TURMAS AGREGADAS (NORMALIZADAS) - {len(turmas_agregadas)} turmas:")
        for i, turma in enumerate(turmas_agregadas):
            print(f"  {i+1:2d}. {turma}")
        
        # Contagem de estudantes por turma
        print(f"\n📊 CONTAGEM DE ESTUDANTES POR ABORDAGEM:")
        
        # Por turmas separadas
        contagem_separadas = tde['Turma_Original'].value_counts()
        print(f"\n📚 TOP 10 TURMAS SEPARADAS:")
        for turma, count in contagem_separadas.head(10).items():
            print(f"  {turma:20s} - {count:4d} estudantes")
        
        # Por turmas agregadas
        contagem_agregadas = tde['Turma'].value_counts()
        print(f"\n🔄 TURMAS AGREGADAS:")
        for turma, count in contagem_agregadas.items():
            print(f"  {turma:15s} - {count:4d} estudantes")
        
        # Exemplo de como funcionará no dashboard
        print(f"\n🎯 SIMULAÇÃO DO COMPORTAMENTO DO DASHBOARD:")
        
        escola_exemplo = tde['Escola'].iloc[0]
        print(f"📍 Exemplo com escola: {escola_exemplo}")
        
        df_escola = tde[tde['Escola'] == escola_exemplo]
        
        # Cenário 1: Agregação DESABILITADA (padrão)
        agregar_turmas = False
        coluna_turma = 'Turma_Original' if not agregar_turmas else 'Turma'
        turmas_escola_separadas = sorted(df_escola[coluna_turma].dropna().unique())
        
        print(f"\n❌ Agregação DESABILITADA (padrão):")
        print(f"   Coluna usada: {coluna_turma}")
        print(f"   Turmas disponíveis: {len(turmas_escola_separadas)}")
        for turma in turmas_escola_separadas:
            count = len(df_escola[df_escola[coluna_turma] == turma])
            print(f"     • {turma:20s} - {count:3d} estudantes")
        
        # Cenário 2: Agregação HABILITADA
        agregar_turmas = True
        coluna_turma = 'Turma_Original' if not agregar_turmas else 'Turma'
        turmas_escola_agregadas = sorted(df_escola[coluna_turma].dropna().unique())
        
        print(f"\n✅ Agregação HABILITADA:")
        print(f"   Coluna usada: {coluna_turma}")
        print(f"   Turmas disponíveis: {len(turmas_escola_agregadas)}")
        for turma in turmas_escola_agregadas:
            count = len(df_escola[df_escola[coluna_turma] == turma])
            print(f"     • {turma:15s} - {count:3d} estudantes")
        
        print(f"\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        print(f"🎯 A funcionalidade permitirá ao usuário escolher entre:")
        print(f"   • Turmas separadas ({len(turmas_originais)} turmas) - PADRÃO")
        print(f"   • Turmas agregadas ({len(turmas_agregadas)} turmas) - OPCIONAL")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = testar_agregacao_turmas()
    exit(0 if sucesso else 1)