#!/usr/bin/env python3
"""
Script de Teste - Sistema de Anonimização
Valida a implementação do sistema de anonimização LGPD
"""

import sys
import os

# Adicionar path do projeto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from Dashboard.data_loader import anonimizar_estudante, get_datasets
import pandas as pd

def test_anonimizacao_basica():
    """Testa função básica de anonimização"""
    print("=" * 70)
    print("TESTE 1: Função Básica de Anonimização")
    print("=" * 70)
    
    casos = [
        ('56E9C824252F', 'ABIGAIL ALVES DOS SANTOS', '56E9C8 - AADS'),
        ('7F3D12AB98CD', 'João Pedro Silva', '7F3D12 - JPS'),
        ('A1B2C3D4E5F6', 'Maria Fernanda Oliveira Costa', 'A1B2C3 - MFOC'),
        ('B9F8E7D6C5A4', 'Ana', 'B9F8E7 - A'),
    ]
    
    total = len(casos)
    passou = 0
    
    for id_unico, nome, esperado in casos:
        resultado = anonimizar_estudante(id_unico, nome)
        status = "✅" if resultado == esperado else "❌"
        
        if resultado == esperado:
            passou += 1
        
        print(f"\n{status} Teste: {nome}")
        print(f"   ID Original:  {id_unico}")
        print(f"   Esperado:     {esperado}")
        print(f"   Resultado:    {resultado}")
    
    print(f"\n{'=' * 70}")
    print(f"Resultado: {passou}/{total} testes passaram")
    print(f"{'=' * 70}\n")
    
    return passou == total

def test_datasets():
    """Testa criação da coluna ID_Anonimizado nos datasets"""
    print("=" * 70)
    print("TESTE 2: Datasets (TDE e Vocabulário)")
    print("=" * 70)
    
    try:
        tde, vocab = get_datasets()
        
        # Verificar se coluna existe
        print("\n✅ Datasets carregados com sucesso")
        
        # TDE
        print(f"\n📊 TDE:")
        print(f"   Total de registros: {len(tde)}")
        print(f"   Coluna ID_Anonimizado existe: {'ID_Anonimizado' in tde.columns}")
        
        if 'ID_Anonimizado' in tde.columns:
            print(f"   IDs únicos: {tde['ID_Unico'].nunique()}")
            print(f"   IDs anonimizados únicos: {tde['ID_Anonimizado'].nunique()}")
            print(f"   Exemplo: {tde['ID_Anonimizado'].iloc[0]}")
            
            # Verificar unicidade
            if tde['ID_Anonimizado'].nunique() == tde['ID_Unico'].nunique():
                print(f"   ✅ Unicidade mantida (sem colisões)")
            else:
                print(f"   ⚠️ Possíveis colisões detectadas")
        
        # Vocabulário
        print(f"\n📚 Vocabulário:")
        print(f"   Total de registros: {len(vocab)}")
        print(f"   Coluna ID_Anonimizado existe: {'ID_Anonimizado' in vocab.columns}")
        
        if 'ID_Anonimizado' in vocab.columns:
            print(f"   IDs únicos: {vocab['ID_Unico'].nunique()}")
            print(f"   IDs anonimizados únicos: {vocab['ID_Anonimizado'].nunique()}")
            print(f"   Exemplo: {vocab['ID_Anonimizado'].iloc[0]}")
            
            # Verificar unicidade
            if vocab['ID_Anonimizado'].nunique() == vocab['ID_Unico'].nunique():
                print(f"   ✅ Unicidade mantida (sem colisões)")
            else:
                print(f"   ⚠️ Possíveis colisões detectadas")
        
        print(f"\n{'=' * 70}")
        print(f"Resultado: ✅ Datasets processados corretamente")
        print(f"{'=' * 70}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao carregar datasets: {e}")
        print(f"\n{'=' * 70}")
        print(f"Resultado: ❌ Falha no teste de datasets")
        print(f"{'=' * 70}\n")
        return False

def test_colisoes():
    """Verifica se há colisões (dois alunos com mesmo ID anonimizado)"""
    print("=" * 70)
    print("TESTE 3: Verificação de Colisões")
    print("=" * 70)
    
    try:
        tde, vocab = get_datasets()
        
        colisoes_tde = 0
        colisoes_vocab = 0
        
        # TDE
        if 'ID_Anonimizado' in tde.columns:
            duplicados_tde = tde.groupby('ID_Anonimizado')['ID_Unico'].nunique()
            colisoes_tde = len(duplicados_tde[duplicados_tde > 1])
            
            if colisoes_tde == 0:
                print(f"\n✅ TDE: Nenhuma colisão detectada")
            else:
                print(f"\n⚠️ TDE: {colisoes_tde} colisões detectadas")
                print("   IDs com colisão:")
                for id_anonimizado in duplicados_tde[duplicados_tde > 1].index:
                    ids_originais = tde[tde['ID_Anonimizado'] == id_anonimizado]['ID_Unico'].unique()
                    print(f"   - {id_anonimizado}: {ids_originais}")
        
        # Vocabulário
        if 'ID_Anonimizado' in vocab.columns:
            duplicados_vocab = vocab.groupby('ID_Anonimizado')['ID_Unico'].nunique()
            colisoes_vocab = len(duplicados_vocab[duplicados_vocab > 1])
            
            if colisoes_vocab == 0:
                print(f"\n✅ Vocabulário: Nenhuma colisão detectada")
            else:
                print(f"\n⚠️ Vocabulário: {colisoes_vocab} colisões detectadas")
                print("   IDs com colisão:")
                for id_anonimizado in duplicados_vocab[duplicados_vocab > 1].index:
                    ids_originais = vocab[vocab['ID_Anonimizado'] == id_anonimizado]['ID_Unico'].unique()
                    print(f"   - {id_anonimizado}: {ids_originais}")
        
        total_colisoes = colisoes_tde + colisoes_vocab
        
        print(f"\n{'=' * 70}")
        if total_colisoes == 0:
            print(f"Resultado: ✅ Nenhuma colisão detectada em ambos os datasets")
        else:
            print(f"Resultado: ⚠️ {total_colisoes} colisões detectadas no total")
        print(f"{'=' * 70}\n")
        
        return total_colisoes == 0
        
    except Exception as e:
        print(f"\n❌ Erro ao verificar colisões: {e}")
        print(f"\n{'=' * 70}")
        print(f"Resultado: ❌ Falha no teste de colisões")
        print(f"{'=' * 70}\n")
        return False

def test_formato():
    """Verifica se todos os IDs seguem o formato correto"""
    print("=" * 70)
    print("TESTE 4: Verificação de Formato")
    print("=" * 70)
    
    try:
        import re
        tde, vocab = get_datasets()
        
        # Padrão esperado: 6 caracteres alfanuméricos - espaço - até 4 letras
        padrao = r'^[A-Z0-9]{6} - [A-Z]{1,4}$'
        
        # TDE
        if 'ID_Anonimizado' in tde.columns:
            invalidos_tde = tde[~tde['ID_Anonimizado'].str.match(padrao, na=False)]
            
            if len(invalidos_tde) == 0:
                print(f"\n✅ TDE: Todos os IDs seguem o formato correto")
                print(f"   Total validado: {len(tde)}")
            else:
                print(f"\n⚠️ TDE: {len(invalidos_tde)} IDs com formato inválido")
                print(f"   Exemplos:")
                for idx, row in invalidos_tde.head(5).iterrows():
                    print(f"   - {row['ID_Anonimizado']} (ID: {row['ID_Unico']})")
        
        # Vocabulário
        if 'ID_Anonimizado' in vocab.columns:
            invalidos_vocab = vocab[~vocab['ID_Anonimizado'].str.match(padrao, na=False)]
            
            if len(invalidos_vocab) == 0:
                print(f"\n✅ Vocabulário: Todos os IDs seguem o formato correto")
                print(f"   Total validado: {len(vocab)}")
            else:
                print(f"\n⚠️ Vocabulário: {len(invalidos_vocab)} IDs com formato inválido")
                print(f"   Exemplos:")
                for idx, row in invalidos_vocab.head(5).iterrows():
                    print(f"   - {row['ID_Anonimizado']} (ID: {row['ID_Unico']})")
        
        total_invalidos = len(invalidos_tde) + len(invalidos_vocab)
        
        print(f"\n{'=' * 70}")
        if total_invalidos == 0:
            print(f"Resultado: ✅ Todos os IDs seguem o formato correto")
        else:
            print(f"Resultado: ⚠️ {total_invalidos} IDs com formato inválido")
        print(f"{'=' * 70}\n")
        
        return total_invalidos == 0
        
    except Exception as e:
        print(f"\n❌ Erro ao verificar formato: {e}")
        print(f"\n{'=' * 70}")
        print(f"Resultado: ❌ Falha no teste de formato")
        print(f"{'=' * 70}\n")
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "=" * 70)
    print("SISTEMA DE TESTES - ANONIMIZAÇÃO LGPD")
    print("=" * 70 + "\n")
    
    resultados = {
        'Função Básica': test_anonimizacao_basica(),
        'Datasets': test_datasets(),
        'Colisões': test_colisoes(),
        'Formato': test_formato()
    }
    
    # Resumo final
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    
    total = len(resultados)
    passou = sum(resultados.values())
    
    for teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{status}: {teste}")
    
    print(f"\n{'=' * 70}")
    print(f"RESULTADO FINAL: {passou}/{total} testes passaram")
    
    if passou == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM. Revisar implementação.")
    
    print("=" * 70 + "\n")
    
    return passou == total

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
