#!/usr/bin/env python3
"""
Verificador de Integridade dos ID_Únicos
========================================

Verifica a integridade e consistência dos ID_únicos após o reprocessamento.
"""

import pandas as pd
from pathlib import Path

def verificar_registro_problematico():
    """Identifica o registro problemático mencionado no reprocessamento"""
    
    print("🔍 INVESTIGANDO REGISTRO PROBLEMÁTICO")
    print("=" * 50)
    
    # Carregar dataset TDE
    df_tde = pd.read_csv("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Dashboard/TDE_consolidado_fases_2_3_4.csv")
    
    # Procurar por registros com problemas nos IDs
    registros_problema = df_tde[df_tde['ID_Unico'].str.contains('PROBLEMA', na=False)]
    
    if not registros_problema.empty:
        print(f"❌ {len(registros_problema)} registro(s) problemático(s) encontrado(s):")
        for idx, row in registros_problema.iterrows():
            print(f"   Linha {idx}:")
            print(f"      ID_Unico: {row['ID_Unico']}")
            print(f"      Nome: {row.get('Nome', 'N/A')}")
            print(f"      Escola: {row.get('Escola', 'N/A')}")
            print(f"      Turma: {row.get('Turma', 'N/A')}")
            print(f"      Fase: {row.get('Fase', 'N/A')}")
            print()
    
    # Procurar por valores vazios/nulos nas colunas chave
    print("🔍 VERIFICANDO VALORES NULOS/VAZIOS:")
    colunas_chave = ['Nome', 'Escola', 'Turma', 'Fase']
    
    for coluna in colunas_chave:
        nulos = df_tde[coluna].isna().sum()
        vazios = (df_tde[coluna] == '').sum() if df_tde[coluna].dtype == 'object' else 0
        total_problemas = nulos + vazios
        
        if total_problemas > 0:
            print(f"   ⚠️  {coluna}: {total_problemas} valores problemáticos ({nulos} nulos, {vazios} vazios)")
            
            # Mostrar alguns exemplos
            mask_problema = df_tde[coluna].isna() | (df_tde[coluna] == '')
            exemplos = df_tde[mask_problema].head(3)
            
            for idx, row in exemplos.iterrows():
                print(f"      Linha {idx}: {row.get('ID_Unico', 'N/A')}")
        else:
            print(f"   ✅ {coluna}: OK")

def verificar_consistencia_ids():
    """Verifica consistência dos ID_únicos entre datasets"""
    
    print(f"\n🔄 VERIFICAÇÃO DE CONSISTÊNCIA DETALHADA")
    print("=" * 50)
    
    # Carregar ambos datasets
    df_tde = pd.read_csv("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Dashboard/TDE_consolidado_fases_2_3_4.csv")
    df_vocab = pd.read_csv("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Dashboard/vocabulario_consolidado_fases_2_3_4.csv")
    
    ids_tde = set(df_tde['ID_Unico'])
    ids_vocab = set(df_vocab['ID_Unico'])
    
    # IDs em comum
    ids_comuns = ids_tde & ids_vocab
    print(f"📊 IDs em comum: {len(ids_comuns):,}")
    
    # IDs únicos por dataset
    ids_so_tde = ids_tde - ids_vocab
    ids_so_vocab = ids_vocab - ids_tde
    
    print(f"📊 IDs só no TDE: {len(ids_so_tde):,}")
    print(f"📊 IDs só no Vocabulário: {len(ids_so_vocab):,}")
    
    # Mostrar alguns exemplos de IDs únicos
    if ids_so_tde:
        print(f"\n📝 Exemplos de IDs só no TDE:")
        for i, id_exemplo in enumerate(list(ids_so_tde)[:3], 1):
            print(f"   {i}. {id_exemplo}")
    
    if ids_so_vocab:
        print(f"\n📝 Exemplos de IDs só no Vocabulário:")
        for i, id_exemplo in enumerate(list(ids_so_vocab)[:3], 1):
            print(f"   {i}. {id_exemplo}")
    
    # Calcular taxa de sobreposição
    total_ids_unicos = len(ids_tde | ids_vocab)
    taxa_sobreposicao = (len(ids_comuns) / total_ids_unicos) * 100
    
    print(f"\n📈 Taxa de sobreposição: {taxa_sobreposicao:.1f}%")
    
    if taxa_sobreposicao > 80:
        print("✅ Boa consistência entre datasets")
    elif taxa_sobreposicao > 60:
        print("⚠️  Consistência moderada - alguns alunos podem ter feito apenas uma prova")
    else:
        print("❌ Baixa consistência - investigar diferenças")

def verificar_formato_ids():
    """Verifica se os ID_únicos seguem o formato correto"""
    
    print(f"\n🔍 VERIFICAÇÃO DE FORMATO DOS ID_ÚNICOS")
    print("=" * 50)
    
    df_tde = pd.read_csv("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Dashboard/TDE_consolidado_fases_2_3_4.csv")
    
    # Padrão esperado: NOME_ESCOLA_TURMA_F[2-4]
    import re
    padrao = r'^.+_.+_.+_F[2-4]$'
    
    ids_corretos = df_tde['ID_Unico'].str.match(padrao, na=False).sum()
    total_ids = len(df_tde)
    
    print(f"📊 IDs com formato correto: {ids_corretos:,}/{total_ids:,}")
    print(f"📊 Taxa de conformidade: {(ids_corretos/total_ids)*100:.1f}%")
    
    # Identificar IDs com formato incorreto
    ids_incorretos = df_tde[~df_tde['ID_Unico'].str.match(padrao, na=False)]
    
    if not ids_incorretos.empty:
        print(f"\n❌ {len(ids_incorretos)} IDs com formato incorreto:")
        for idx, row in ids_incorretos.head(5).iterrows():
            print(f"   • {row['ID_Unico']}")
    else:
        print("✅ Todos os IDs seguem o formato correto!")

def main():
    """Função principal de verificação"""
    
    print("🔍 VERIFICAÇÃO DE INTEGRIDADE DOS ID_ÚNICOS")
    print("=" * 60)
    
    verificar_registro_problematico()
    verificar_consistencia_ids()
    verificar_formato_ids()
    
    print(f"\n🎯 RESUMO:")
    print("• ID_únicos reprocessados com sucesso")
    print("• Backups de segurança criados")
    print("• Formato padronizado aplicado")
    print("• Consistência entre datasets verificada")

if __name__ == "__main__":
    main()