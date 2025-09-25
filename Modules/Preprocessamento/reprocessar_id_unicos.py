#!/usr/bin/env python3
"""
Reprocessador de ID_Únicos para Datasets Consolidados
====================================================

Após as correções nos nomes das escolas, alguns ID_únicos ficaram inconsistentes.
Este script reprocessa e corrige todos os ID_únicos nos datasets consolidados.

Formato do ID_Único:
NOME_ESCOLA_TURMA_FASE

Exemplo:
JOÃO SILVA_EMEB PADRE ANCHIETA_7° ANO A_F2
"""

import pandas as pd
import re
import unicodedata
from pathlib import Path

def normalizar_string_para_id(texto: str) -> str:
    """Normaliza string para uso em ID_Único (remove acentos, espaços extras, etc.)"""
    if pd.isna(texto) or texto == "":
        return ""
    
    # Converter para string e normalizar
    texto = str(texto).strip()
    
    # Remover acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    
    # Converter para maiúsculo
    texto = texto.upper()
    
    # Substituir caracteres especiais por espaço
    texto = re.sub(r'[^\w\s]', ' ', texto)
    
    # Remover espaços múltiplos
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()

def gerar_id_unico(nome: str, escola: str, turma: str, fase: str) -> str:
    """Gera um ID_Único padronizado"""
    
    # Normalizar cada componente
    nome_norm = normalizar_string_para_id(nome)
    escola_norm = normalizar_string_para_id(escola)
    turma_norm = normalizar_string_para_id(turma)
    fase_norm = str(fase).strip()
    
    # Validar componentes
    if not nome_norm or not escola_norm or not turma_norm or not fase_norm:
        return ""
    
    # Construir ID_Único
    id_unico = f"{nome_norm}_{escola_norm}_{turma_norm}_F{fase_norm}"
    
    return id_unico

def reprocessar_dataset(arquivo_path: str, backup: bool = True) -> pd.DataFrame:
    """Reprocessa um dataset corrigindo os ID_únicos"""
    
    print(f"🔧 Reprocessando: {Path(arquivo_path).name}")
    
    # Carregar dataset
    df = pd.read_csv(arquivo_path)
    
    # Fazer backup se solicitado
    if backup:
        backup_path = f"{arquivo_path}.backup_id_reprocessado"
        df.to_csv(backup_path, index=False)
        print(f"   💾 Backup criado: {Path(backup_path).name}")
    
    # Verificar colunas necessárias
    colunas_necessarias = ['Nome', 'Escola', 'Turma', 'Fase']
    colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
    
    if colunas_faltantes:
        print(f"   ❌ Colunas faltantes: {colunas_faltantes}")
        return df
    
    # Gerar novos ID_únicos
    print(f"   🔄 Gerando novos ID_únicos...")
    novos_ids = []
    ids_problematicos = 0
    
    for idx, row in df.iterrows():
        novo_id = gerar_id_unico(
            nome=row['Nome'],
            escola=row['Escola'], 
            turma=row['Turma'],
            fase=row['Fase']
        )
        
        if novo_id == "":
            ids_problematicos += 1
            # Manter ID original se não conseguir gerar novo
            novo_id = row.get('ID_Unico', f"PROBLEMA_LINHA_{idx}")
        
        novos_ids.append(novo_id)
    
    # Atualizar coluna ID_Unico
    df['ID_Unico'] = novos_ids
    
    # Estatísticas
    ids_unicos_count = df['ID_Unico'].nunique()
    total_registros = len(df)
    
    print(f"   📊 Estatísticas:")
    print(f"      • Total de registros: {total_registros:,}")
    print(f"      • ID_únicos gerados: {ids_unicos_count:,}")
    print(f"      • IDs problemáticos: {ids_problematicos}")
    
    if ids_problematicos > 0:
        print(f"   ⚠️  {ids_problematicos} IDs problemáticos encontrados")
    
    # Verificar duplicações
    duplicados = df[df.duplicated(subset=['ID_Unico'], keep=False)]
    if not duplicados.empty:
        print(f"   ⚠️  {len(duplicados)} registros com ID_únicos duplicados")
        
        # Mostrar alguns exemplos
        ids_duplicados = duplicados['ID_Unico'].value_counts().head(3)
        print(f"      Exemplos de duplicados:")
        for id_dup, count in ids_duplicados.items():
            print(f"         • {id_dup}: {count} ocorrências")
    
    return df

def validar_id_unicos(df: pd.DataFrame, nome_dataset: str):
    """Valida a qualidade dos ID_únicos gerados"""
    
    print(f"\n🔍 VALIDAÇÃO: {nome_dataset}")
    print("-" * 30)
    
    # Estatísticas básicas
    total = len(df)
    unicos = df['ID_Unico'].nunique()
    duplicados = total - unicos
    
    print(f"📊 Registros totais: {total:,}")
    print(f"📊 ID_únicos: {unicos:,}")
    print(f"📊 Duplicados: {duplicados}")
    
    if duplicados > 0:
        print(f"⚠️  Taxa de duplicação: {(duplicados/total)*100:.2f}%")
    else:
        print(f"✅ Sem duplicações!")
    
    # Verificar padrões dos IDs
    ids_sample = df['ID_Unico'].dropna().head(5).tolist()
    print(f"\n📝 Exemplos de ID_únicos:")
    for i, id_exemplo in enumerate(ids_sample, 1):
        print(f"   {i}. {id_exemplo}")

def main():
    """Função principal de reprocessamento"""
    
    print("🚀 REPROCESSAMENTO DE ID_ÚNICOS")
    print("=" * 60)
    
    # Caminhos dos datasets consolidados
    dashboard_path = Path("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Dashboard")
    
    datasets = [
        dashboard_path / "TDE_consolidado_fases_2_3_4.csv",
        dashboard_path / "vocabulario_consolidado_fases_2_3_4.csv"
    ]
    
    # Verificar se arquivos existem
    datasets_existentes = [d for d in datasets if d.exists()]
    
    if not datasets_existentes:
        print("❌ Nenhum dataset consolidado encontrado!")
        return
    
    # Reprocessar cada dataset
    datasets_processados = {}
    
    for dataset_path in datasets_existentes:
        df_reprocessado = reprocessar_dataset(str(dataset_path))
        datasets_processados[dataset_path.name] = df_reprocessado
        
        # Salvar dataset reprocessado
        df_reprocessado.to_csv(str(dataset_path), index=False)
        print(f"   ✅ Dataset reprocessado salvo\n")
    
    # Validação final
    print("🔍 VALIDAÇÃO FINAL")
    print("=" * 30)
    
    for nome_dataset, df in datasets_processados.items():
        validar_id_unicos(df, nome_dataset)
    
    # Verificar consistência entre datasets
    if len(datasets_processados) > 1:
        print(f"\n🔄 VERIFICAÇÃO DE CONSISTÊNCIA")
        print("-" * 35)
        
        # Comparar estrutura de IDs entre datasets
        datasets_list = list(datasets_processados.items())
        for i in range(len(datasets_list) - 1):
            nome1, df1 = datasets_list[i]
            nome2, df2 = datasets_list[i + 1]
            
            ids_comuns = set(df1['ID_Unico']) & set(df2['ID_Unico'])
            print(f"📊 IDs em comum entre {nome1} e {nome2}: {len(ids_comuns):,}")
    
    print(f"\n✅ REPROCESSAMENTO CONCLUÍDO!")
    print(f"📋 Arquivos processados: {len(datasets_processados)}")
    print(f"💾 Backups criados para segurança")
    print(f"🎯 ID_únicos padronizados e corrigidos")

if __name__ == "__main__":
    main()