#!/usr/bin/env python3
"""
Refatoração de Dados Longitudinais - WordGen
===========================================

Este script corrige o problema de ID_Unico inconsistente nos dados consolidados,
criando novos arquivos CSV com IDs únicos verdadeiros que permitem análise longitudinal.

PROBLEMA IDENTIFICADO:
- ID_Unico atual é gerado por Turma + Fase + Escola + Nome
- Mesmo aluno tem IDs diferentes em fases distintas
- Impossibilita rastreamento longitudinal

SOLUÇÃO:
- Criar ID_Unico baseado apenas em Nome + Escola (identificador permanente)
- Adicionar coluna Turma_Origem (turma da primeira aparição)
- Preservar Turma atual para cada fase
- Gerar novos CSVs: TDE_longitudinal.csv e vocabulario_longitudinal.csv
"""

import pandas as pd
import unicodedata
import re
import hashlib
import sys
import os
from datetime import datetime

# Adicionar path do Dashboard
sys.path.append(os.path.join(os.path.dirname(__file__), 'Dashboard'))
from data_loader import get_datasets

def normalizar_nome(nome):
    """Normaliza nome para comparação consistente"""
    if pd.isna(nome):
        return ""
    
    nome = str(nome).upper().strip()
    # Remover acentos
    nome = ''.join(c for c in unicodedata.normalize('NFD', nome) 
                  if unicodedata.category(c) != 'Mn')
    # Remover caracteres especiais e espaços extras
    nome = re.sub(r'[^A-Z0-9\s]', '', nome)
    nome = re.sub(r'\s+', ' ', nome).strip()
    
    return nome

def normalizar_escola(escola):
    """Normaliza nome da escola para comparação consistente"""
    if pd.isna(escola):
        return ""
    
    escola = str(escola).upper().strip()
    # Remover acentos
    escola = ''.join(c for c in unicodedata.normalize('NFD', escola) 
                    if unicodedata.category(c) != 'Mn')
    # Padronizar siglas
    escola = escola.replace('EMEB ', '').replace('EMEF ', '')
    escola = escola.replace('ESCOLA MUNICIPAL ', '')
    # Remover caracteres especiais
    escola = re.sub(r'[^A-Z0-9\s]', '', escola)
    escola = re.sub(r'\s+', ' ', escola).strip()
    
    return escola

def gerar_id_unico_permanente(nome, escola):
    """Gera ID único permanente baseado em nome + escola"""
    nome_norm = normalizar_nome(nome)
    escola_norm = normalizar_escola(escola)
    
    # Criar string única
    string_unica = f"{nome_norm}_{escola_norm}"
    
    # Gerar hash MD5 para criar ID compacto
    hash_obj = hashlib.md5(string_unica.encode('utf-8'))
    id_unico = hash_obj.hexdigest()[:12].upper()  # Primeiros 12 caracteres em maiúscula
    
    return id_unico

def identificar_turma_origem(df_aluno):
    """Identifica a turma de origem (primeira aparição) de um aluno"""
    if df_aluno.empty:
        return None
    
    # Ordenar por fase para pegar a primeira aparição
    df_ordenado = df_aluno.sort_values('Fase')
    turma_origem = df_ordenado.iloc[0]['Turma']
    fase_origem = df_ordenado.iloc[0]['Fase']
    
    return turma_origem, fase_origem

def refatorar_dados(df_original, nome_prova):
    """Refatora um dataset aplicando IDs únicos permanentes"""
    print(f"\n🔄 Refatorando dados de {nome_prova}...")
    print(f"   Total de registros: {len(df_original)}")
    print(f"   IDs únicos atuais: {df_original['ID_Unico'].nunique()}")
    print(f"   Alunos únicos (Nome): {df_original['Nome'].nunique()}")
    
    # Criar cópia para trabalhar
    df_refatorado = df_original.copy()
    
    # Gerar novos IDs únicos permanentes
    print("   Gerando IDs únicos permanentes...")
    df_refatorado['ID_Unico_Novo'] = df_refatorado.apply(
        lambda row: gerar_id_unico_permanente(row['Nome'], row['Escola']), 
        axis=1
    )
    
    # Identificar turma de origem para cada aluno
    print("   Identificando turmas de origem...")
    turmas_origem = {}
    fases_origem = {}
    
    for id_novo in df_refatorado['ID_Unico_Novo'].unique():
        df_aluno = df_refatorado[df_refatorado['ID_Unico_Novo'] == id_novo]
        resultado = identificar_turma_origem(df_aluno)
        
        if resultado:
            turma_origem, fase_origem = resultado
            turmas_origem[id_novo] = turma_origem
            fases_origem[id_novo] = fase_origem
        else:
            turmas_origem[id_novo] = None
            fases_origem[id_novo] = None
    
    # Adicionar colunas de turma e fase de origem
    df_refatorado['Turma_Origem'] = df_refatorado['ID_Unico_Novo'].map(turmas_origem)
    df_refatorado['Fase_Origem'] = df_refatorado['ID_Unico_Novo'].map(fases_origem)
    
    # Renomear colunas para clareza
    df_refatorado['ID_Unico_Antigo'] = df_refatorado['ID_Unico']
    df_refatorado['ID_Unico'] = df_refatorado['ID_Unico_Novo']
    df_refatorado['Turma_Atual'] = df_refatorado['Turma']  # Turma atual na fase
    
    # Reorganizar colunas
    colunas_ordem = [
        'ID_Unico', 'Nome', 'Escola', 'Fase', 
        'Turma_Origem', 'Fase_Origem', 'Turma_Atual',
        'Score_Pre', 'Score_Pos'
    ]
    
    # Adicionar colunas restantes que não estão na lista
    colunas_restantes = [col for col in df_refatorado.columns if col not in colunas_ordem]
    colunas_finais = colunas_ordem + colunas_restantes
    
    # Filtrar apenas colunas que existem no DataFrame
    colunas_existentes = [col for col in colunas_finais if col in df_refatorado.columns]
    df_final = df_refatorado[colunas_existentes]
    
    # Estatísticas pós-refatoração
    print(f"   ✅ Refatoração concluída:")
    print(f"      - Novos IDs únicos: {df_final['ID_Unico'].nunique()}")
    print(f"      - Alunos únicos: {df_final['Nome'].nunique()}")
    print(f"      - Registros totais: {len(df_final)}")
    
    # Análise de participação longitudinal
    participacao = df_final.groupby('ID_Unico')['Fase'].nunique()
    print(f"      - Alunos em 1 fase: {sum(participacao == 1)}")
    print(f"      - Alunos em 2 fases: {sum(participacao == 2)}")
    print(f"      - Alunos em 3 fases: {sum(participacao == 3)}")
    
    return df_final

def validar_consistencia(df_tde, df_vocab):
    """Valida a consistência dos dados refatorados"""
    print("\n🔍 VALIDAÇÃO DE CONSISTÊNCIA:")
    
    # Verificar se mesmo aluno tem mesmo ID em ambos os datasets
    alunos_tde = set(df_tde[['Nome', 'Escola', 'ID_Unico']].drop_duplicates().apply(
        lambda x: (normalizar_nome(x['Nome']), normalizar_escola(x['Escola']), x['ID_Unico']), axis=1
    ))
    
    alunos_vocab = set(df_vocab[['Nome', 'Escola', 'ID_Unico']].drop_duplicates().apply(
        lambda x: (normalizar_nome(x['Nome']), normalizar_escola(x['Escola']), x['ID_Unico']), axis=1
    ))
    
    # Encontrar alunos em comum
    alunos_comuns = set()
    ids_inconsistentes = []
    
    for nome_tde, escola_tde, id_tde in alunos_tde:
        for nome_vocab, escola_vocab, id_vocab in alunos_vocab:
            if nome_tde == nome_vocab and escola_tde == escola_vocab:
                alunos_comuns.add((nome_tde, escola_tde))
                if id_tde != id_vocab:
                    ids_inconsistentes.append((nome_tde, escola_tde, id_tde, id_vocab))
    
    print(f"   ✅ Alunos identificados em ambos os datasets: {len(alunos_comuns)}")
    
    if ids_inconsistentes:
        print(f"   ❌ IDs inconsistentes encontrados: {len(ids_inconsistentes)}")
        for nome, escola, id_tde, id_vocab in ids_inconsistentes[:5]:  # Mostrar primeiros 5
            print(f"      - {nome} ({escola}): TDE={id_tde}, Vocab={id_vocab}")
    else:
        print(f"   ✅ Todos os IDs são consistentes entre datasets!")
    
    # Verificar duplicatas de ID
    duplicatas_tde = df_tde.groupby('ID_Unico')['Nome'].nunique()
    ids_duplicados_tde = duplicatas_tde[duplicatas_tde > 1]
    
    duplicatas_vocab = df_vocab.groupby('ID_Unico')['Nome'].nunique()
    ids_duplicados_vocab = duplicatas_vocab[duplicatas_vocab > 1]
    
    if len(ids_duplicados_tde) > 0:
        print(f"   ❌ IDs duplicados no TDE: {len(ids_duplicados_tde)}")
    else:
        print(f"   ✅ Nenhum ID duplicado no TDE!")
        
    if len(ids_duplicados_vocab) > 0:
        print(f"   ❌ IDs duplicados no Vocabulário: {len(ids_duplicados_vocab)}")
    else:
        print(f"   ✅ Nenhum ID duplicado no Vocabulário!")

def salvar_dados_refatorados(df_tde, df_vocab):
    """Salva os dados refatorados em novos arquivos CSV"""
    print("\n💾 SALVANDO DADOS REFATORADOS:")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Definir nomes dos arquivos
    arquivo_tde = f"Dashboard/TDE_longitudinal_{timestamp}.csv"
    arquivo_vocab = f"Dashboard/vocabulario_longitudinal_{timestamp}.csv"
    
    # Salvar TDE
    df_tde.to_csv(arquivo_tde, index=False, encoding='utf-8')
    print(f"   ✅ TDE salvo: {arquivo_tde}")
    print(f"      - {len(df_tde)} registros, {df_tde['ID_Unico'].nunique()} alunos únicos")
    
    # Salvar Vocabulário
    df_vocab.to_csv(arquivo_vocab, index=False, encoding='utf-8')
    print(f"   ✅ Vocabulário salvo: {arquivo_vocab}")
    print(f"      - {len(df_vocab)} registros, {df_vocab['ID_Unico'].nunique()} alunos únicos")
    
    # Criar também versões sem timestamp para uso padrão
    arquivo_tde_padrao = "Dashboard/TDE_longitudinal.csv"
    arquivo_vocab_padrao = "Dashboard/vocabulario_longitudinal.csv"
    
    df_tde.to_csv(arquivo_tde_padrao, index=False, encoding='utf-8')
    df_vocab.to_csv(arquivo_vocab_padrao, index=False, encoding='utf-8')
    
    print(f"   ✅ Versões padrão criadas:")
    print(f"      - {arquivo_tde_padrao}")
    print(f"      - {arquivo_vocab_padrao}")
    
    return arquivo_tde_padrao, arquivo_vocab_padrao

def gerar_relatorio_refatoracao(df_tde_original, df_vocab_original, df_tde_novo, df_vocab_novo):
    """Gera relatório detalhado da refatoração"""
    print("\n📊 RELATÓRIO DE REFATORAÇÃO:")
    print("=" * 60)
    
    print("\n🔍 DADOS ORIGINAIS:")
    print(f"   TDE:")
    print(f"      - Registros: {len(df_tde_original)}")
    print(f"      - IDs únicos: {df_tde_original['ID_Unico'].nunique()}")
    print(f"      - Nomes únicos: {df_tde_original['Nome'].nunique()}")
    
    print(f"   Vocabulário:")
    print(f"      - Registros: {len(df_vocab_original)}")
    print(f"      - IDs únicos: {df_vocab_original['ID_Unico'].nunique()}")
    print(f"      - Nomes únicos: {df_vocab_original['Nome'].nunique()}")
    
    print(f"\n✨ DADOS REFATORADOS:")
    print(f"   TDE:")
    print(f"      - Registros: {len(df_tde_novo)}")
    print(f"      - IDs únicos: {df_tde_novo['ID_Unico'].nunique()}")
    print(f"      - Nomes únicos: {df_tde_novo['Nome'].nunique()}")
    
    print(f"   Vocabulário:")
    print(f"      - Registros: {len(df_vocab_novo)}")
    print(f"      - IDs únicos: {df_vocab_novo['ID_Unico'].nunique()}")
    print(f"      - Nomes únicos: {df_vocab_novo['Nome'].nunique()}")
    
    # Análise longitudinal
    print(f"\n📈 CAPACIDADE LONGITUDINAL:")
    
    # TDE
    participacao_tde = df_tde_novo.groupby('ID_Unico')['Fase'].nunique()
    print(f"   TDE - Participação por número de fases:")
    for i in range(1, 4):
        count = sum(participacao_tde == i)
        pct = (count / len(participacao_tde)) * 100
        print(f"      - {i} fase(s): {count} alunos ({pct:.1f}%)")
    
    # Vocabulário
    participacao_vocab = df_vocab_novo.groupby('ID_Unico')['Fase'].nunique()
    print(f"   Vocabulário - Participação por número de fases:")
    for i in range(1, 4):
        count = sum(participacao_vocab == i)
        pct = (count / len(participacao_vocab)) * 100
        print(f"      - {i} fase(s): {count} alunos ({pct:.1f}%)")

def main():
    """Função principal de refatoração"""
    print("🔧 REFATORAÇÃO DE DADOS LONGITUDINAIS - WORDGEN")
    print("=" * 60)
    print("Problema: ID_Unico inconsistente impede análise longitudinal")
    print("Solução: Gerar IDs únicos permanentes baseados em Nome + Escola")
    print("=" * 60)
    
    try:
        # Carregar dados originais
        print("📂 Carregando dados originais...")
        tde_original, vocab_original = get_datasets()
        
        print(f"✅ Dados carregados:")
        print(f"   TDE: {len(tde_original)} registros")
        print(f"   Vocabulário: {len(vocab_original)} registros")
        
        # Refatorar datasets
        tde_refatorado = refatorar_dados(tde_original, "TDE")
        vocab_refatorado = refatorar_dados(vocab_original, "Vocabulário")
        
        # Validar consistência
        validar_consistencia(tde_refatorado, vocab_refatorado)
        
        # Salvar dados refatorados
        arquivo_tde, arquivo_vocab = salvar_dados_refatorados(tde_refatorado, vocab_refatorado)
        
        # Gerar relatório
        gerar_relatorio_refatoracao(tde_original, vocab_original, tde_refatorado, vocab_refatorado)
        
        print("\n" + "=" * 60)
        print("✅ REFATORAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"📁 Arquivos gerados:")
        print(f"   - {arquivo_tde}")
        print(f"   - {arquivo_vocab}")
        print("\n🚀 Os dados agora permitem análise longitudinal completa!")
        
        return tde_refatorado, vocab_refatorado
        
    except Exception as e:
        print(f"❌ Erro durante a refatoração: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    main()