#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Adicionar Data de Aniversário aos Datasets Longitudinais
====================================================================

Lê arquivos CSV da pasta Data/DadosGerais que contêm informações de data de
aniversário dos alunos e mapeia essas informações para os arquivos longitudinais
(TDE_longitudinal.csv e vocabulario_longitudinal.csv).

O mapeamento é feito por nome do aluno (normalizado para evitar problemas com
acentos e maiúsculas/minúsculas).

Autor: Sistema de Análise WordGen
Data: 16 de outubro de 2025
"""

import pandas as pd
import unicodedata
import re
from pathlib import Path
from typing import Dict

# Configurações de paths
BASE_DIR = Path(__file__).parent.parent.parent.resolve()
DATA_DIR = BASE_DIR / "Data"
DASHBOARD_DIR = BASE_DIR / "Dashboard"
DADOS_GERAIS_DIR = DATA_DIR / "DadosGerais"

# Arquivos longitudinais
TDE_LONGITUDINAL = DASHBOARD_DIR / "TDE_longitudinal.csv"
VOCAB_LONGITUDINAL = DASHBOARD_DIR / "vocabulario_longitudinal.csv"


def normalizar_nome(nome: str) -> str:
    """
    Normaliza nome para facilitar matching (remove acentos, converte para maiúscula).
    
    Args:
        nome: Nome a ser normalizado
        
    Returns:
        Nome normalizado
    """
    if pd.isna(nome) or nome == "":
        return ""
    
    # Converter para string e remover espaços extras
    nome = str(nome).strip()
    
    # Remover acentos (NFD normalization)
    nome_nfd = unicodedata.normalize('NFD', nome)
    nome_sem_acento = ''.join(c for c in nome_nfd if unicodedata.category(c) != 'Mn')
    
    # Converter para maiúsculo
    nome_upper = nome_sem_acento.upper()
    
    # Remover caracteres especiais e múltiplos espaços
    nome_limpo = re.sub(r'[^\w\s]', ' ', nome_upper)
    nome_limpo = re.sub(r'\s+', ' ', nome_limpo)
    
    return nome_limpo.strip()


def carregar_datas_aniversario() -> Dict[str, str]:
    """
    Carrega dados de aniversário de todos os arquivos CSV em DadosGerais.
    
    Returns:
        Dicionário {nome_normalizado: data_aniversario}
    """
    print("📅 Carregando datas de aniversário...")
    
    mapeamento_datas = {}
    arquivos_processados = 0
    total_registros = 0
    
    # Verificar se diretório existe
    if not DADOS_GERAIS_DIR.exists():
        print(f"❌ Diretório não encontrado: {DADOS_GERAIS_DIR}")
        return mapeamento_datas
    
    # Processar cada arquivo CSV no diretório DadosGerais
    arquivos_csv = list(DADOS_GERAIS_DIR.glob("*.csv"))
    
    if not arquivos_csv:
        print(f"⚠️  Nenhum arquivo CSV encontrado em {DADOS_GERAIS_DIR}")
        return mapeamento_datas
    
    print(f"   Encontrados {len(arquivos_csv)} arquivos CSV")
    
    for arquivo in arquivos_csv:
        try:
            print(f"   📂 Processando: {arquivo.name}")
            
            # Carregar CSV
            df = pd.read_csv(arquivo, encoding='utf-8')
            
            # Tentar identificar colunas de nome e data de aniversário
            # Possíveis nomes de colunas (case-insensitive)
            coluna_nome = None
            coluna_data = None
            
            for col in df.columns:
                col_lower = col.lower().strip()
                
                # Identificar coluna de nome
                if 'nome' in col_lower and coluna_nome is None:
                    coluna_nome = col
                
                # Identificar coluna de data de aniversário
                if any(keyword in col_lower for keyword in ['aniversario', 'aniversário', 'nascimento', 'data_nasc', 'dt_nasc']):
                    coluna_data = col
            
            if coluna_nome is None:
                print(f"      ⚠️  Coluna 'Nome' não encontrada. Colunas disponíveis: {list(df.columns)}")
                continue
            
            if coluna_data is None:
                print(f"      ⚠️  Coluna de data de aniversário não encontrada. Colunas disponíveis: {list(df.columns)}")
                continue
            
            print(f"      ✅ Coluna Nome: '{coluna_nome}'")
            print(f"      ✅ Coluna Data: '{coluna_data}'")
            
            # Processar registros
            registros_arquivo = 0
            for _, row in df.iterrows():
                nome = row[coluna_nome]
                data = row[coluna_data]
                
                # Validar dados
                if pd.isna(nome) or pd.isna(data) or nome == "" or data == "":
                    continue
                
                nome_norm = normalizar_nome(nome)
                data_str = str(data).strip()
                
                if nome_norm and data_str:
                    # Se já existe, manter o primeiro encontrado
                    if nome_norm not in mapeamento_datas:
                        mapeamento_datas[nome_norm] = data_str
                        registros_arquivo += 1
            
            total_registros += registros_arquivo
            arquivos_processados += 1
            print(f"      📊 {registros_arquivo} datas de aniversário carregadas")
            
        except Exception as e:
            print(f"      ❌ Erro ao processar {arquivo.name}: {str(e)}")
            continue
    
    print(f"\n✅ Total: {total_registros} datas únicas carregadas de {arquivos_processados} arquivos")
    
    return mapeamento_datas


def adicionar_coluna_aniversario(arquivo_path: Path, mapeamento_datas: Dict[str, str], tipo_dataset: str):
    """
    Adiciona coluna DataAniversario ao arquivo longitudinal.
    
    Args:
        arquivo_path: Caminho do arquivo longitudinal
        mapeamento_datas: Dicionário com mapeamento nome->data
        tipo_dataset: Nome do dataset (para log)
    """
    print(f"\n📝 Processando: {tipo_dataset}")
    
    if not arquivo_path.exists():
        print(f"   ❌ Arquivo não encontrado: {arquivo_path}")
        return
    
    # Criar backup
    backup_path = str(arquivo_path) + ".backup_antes_aniversario"
    print(f"   💾 Criando backup: {Path(backup_path).name}")
    
    # Carregar dataset
    df = pd.read_csv(arquivo_path)
    print(f"   📊 Total de registros: {len(df):,}")
    
    # Verificar se coluna já existe
    if 'DataAniversario' in df.columns:
        print(f"   ⚠️  Coluna 'DataAniversario' já existe. Será sobrescrita.")
    
    # Criar coluna DataAniversario
    datas_aniversario = []
    matches = 0
    sem_match = 0
    
    for _, row in df.iterrows():
        nome = row.get('Nome', '')
        nome_norm = normalizar_nome(nome)
        
        # Buscar data no mapeamento
        data = mapeamento_datas.get(nome_norm, '')
        
        if data:
            matches += 1
        else:
            sem_match += 1
        
        datas_aniversario.append(data)
    
    # Adicionar coluna ao DataFrame
    df['DataAniversario'] = datas_aniversario
    
    # Salvar backup
    df_original = pd.read_csv(arquivo_path)
    df_original.to_csv(backup_path, index=False)
    
    # Salvar arquivo atualizado
    df.to_csv(arquivo_path, index=False)
    
    # Estatísticas
    print(f"   ✅ Coluna 'DataAniversario' adicionada")
    print(f"   📊 Estatísticas:")
    print(f"      • Matches encontrados: {matches:,} ({(matches/len(df)*100):.1f}%)")
    print(f"      • Sem match: {sem_match:,} ({(sem_match/len(df)*100):.1f}%)")
    print(f"   💾 Arquivo atualizado: {arquivo_path.name}")


def validar_resultado(arquivo_path: Path, tipo_dataset: str):
    """
    Valida o resultado da adição da coluna DataAniversario.
    
    Args:
        arquivo_path: Caminho do arquivo longitudinal
        tipo_dataset: Nome do dataset
    """
    print(f"\n🔍 Validando: {tipo_dataset}")
    
    df = pd.read_csv(arquivo_path)
    
    # Verificar se coluna existe
    if 'DataAniversario' not in df.columns:
        print(f"   ❌ Coluna 'DataAniversario' não encontrada!")
        return
    
    # Estatísticas
    total = len(df)
    com_data = df['DataAniversario'].notna().sum()
    sem_data = df['DataAniversario'].isna().sum()
    vazios = (df['DataAniversario'] == '').sum()
    
    print(f"   📊 Total de registros: {total:,}")
    print(f"   ✅ Com data de aniversário: {com_data:,} ({(com_data/total*100):.1f}%)")
    print(f"   ⚠️  Sem data (NA): {sem_data:,} ({(sem_data/total*100):.1f}%)")
    print(f"   ⚠️  Vazios (''): {vazios:,} ({(vazios/total*100):.1f}%)")
    
    # Mostrar alguns exemplos
    exemplos_com_data = df[df['DataAniversario'].notna() & (df['DataAniversario'] != '')].head(3)
    
    if not exemplos_com_data.empty:
        print(f"\n   📋 Exemplos de registros com data:")
        for _, row in exemplos_com_data.iterrows():
            print(f"      • {row['Nome']}: {row['DataAniversario']}")


def main():
    """Função principal"""
    print("=" * 70)
    print("ADIÇÃO DE DATA DE ANIVERSÁRIO AOS DATASETS LONGITUDINAIS")
    print("=" * 70)
    print()
    
    # 1. Carregar datas de aniversário
    mapeamento_datas = carregar_datas_aniversario()
    
    if not mapeamento_datas:
        print("\n❌ Nenhuma data de aniversário foi carregada. Abortando.")
        return
    
    print(f"\n📋 Exemplos do mapeamento:")
    for i, (nome, data) in enumerate(list(mapeamento_datas.items())[:5]):
        print(f"   {i+1}. {nome}: {data}")
    
    # 2. Processar TDE_longitudinal
    adicionar_coluna_aniversario(
        TDE_LONGITUDINAL,
        mapeamento_datas,
        "TDE_longitudinal.csv"
    )
    
    # 3. Processar vocabulario_longitudinal
    adicionar_coluna_aniversario(
        VOCAB_LONGITUDINAL,
        mapeamento_datas,
        "vocabulario_longitudinal.csv"
    )
    
    # 4. Validar resultados
    print("\n" + "=" * 70)
    print("VALIDAÇÃO DOS RESULTADOS")
    print("=" * 70)
    
    validar_resultado(TDE_LONGITUDINAL, "TDE_longitudinal.csv")
    validar_resultado(VOCAB_LONGITUDINAL, "vocabulario_longitudinal.csv")
    
    # 5. Resumo final
    print("\n" + "=" * 70)
    print("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    print()
    print("📁 Arquivos atualizados:")
    print(f"   • {TDE_LONGITUDINAL.name}")
    print(f"   • {VOCAB_LONGITUDINAL.name}")
    print()
    print("💾 Backups criados:")
    print(f"   • {TDE_LONGITUDINAL.name}.backup_antes_aniversario")
    print(f"   • {VOCAB_LONGITUDINAL.name}.backup_antes_aniversario")
    print()
    print("📊 Nova coluna adicionada: 'DataAniversario'")
    print()


if __name__ == "__main__":
    main()
