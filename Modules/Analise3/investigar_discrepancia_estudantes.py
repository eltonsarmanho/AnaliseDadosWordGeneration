#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investigação de Discrepância - Contagem de Estudantes Únicos
Comparação entre dados longitudinais e análises agregadas
"""

import pandas as pd
import numpy as np
from pathlib import Path

def investigar_discrepancia_estudantes():
    """Investiga a discrepância na contagem de estudantes únicos"""
    
    print("INVESTIGAÇÃO DE DISCREPÂNCIA - CONTAGEM DE ESTUDANTES")
    print("=" * 60)
    
    # Definir caminhos
    pasta_dashboard = Path("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Dashboard")
    
    arquivo_tde = pasta_dashboard / "TDE_longitudinal.csv"
    arquivo_vocab = pasta_dashboard / "vocabulario_longitudinal.csv"
    
    # Carregar dados
    print("\n1. CARREGANDO DADOS LONGITUDINAIS")
    print("-" * 40)
    
    dados_tde = pd.read_csv(arquivo_tde)
    dados_vocab = pd.read_csv(arquivo_vocab)
    
    print(f"TDE Longitudinal: {len(dados_tde)} registros")
    print(f"Vocabulário Longitudinal: {len(dados_vocab)} registros")
    
    # Análise TDE
    print("\n2. ANÁLISE TDE - CONTAGEM POR ANO")
    print("-" * 40)
    
    # Mapear fases para anos
    dados_tde['Ano'] = dados_tde['Fase'].map({2: 2023, 3: 2024, 4: 2024})
    
    # Contagem total de IDs únicos
    total_ids_unicos_tde = dados_tde['ID_Unico'].nunique()
    print(f"Total IDs únicos TDE (todas as fases): {total_ids_unicos_tde}")
    
    # Contagem por ano
    for ano in [2023, 2024]:
        dados_ano = dados_tde[dados_tde['Ano'] == ano]
        ids_unicos_ano = dados_ano['ID_Unico'].nunique()
        registros_ano = len(dados_ano)
        escolas_ano = dados_ano['Escola'].nunique()
        fases_ano = sorted(dados_ano['Fase'].unique())
        
        print(f"\nAno {ano}:")
        print(f"  Registros: {registros_ano}")
        print(f"  IDs únicos: {ids_unicos_ano}")
        print(f"  Escolas: {escolas_ano}")
        print(f"  Fases: {fases_ano}")
        
        # Verificar duplicatas
        duplicatas = dados_ano.groupby('ID_Unico').size()
        ids_com_duplicatas = duplicatas[duplicatas > 1]
        
        if len(ids_com_duplicatas) > 0:
            print(f"  IDs com múltiplos registros: {len(ids_com_duplicatas)}")
            print(f"  Exemplo de duplicatas: {ids_com_duplicatas.head()}")
    
    # Análise Vocabulário
    print("\n3. ANÁLISE VOCABULÁRIO - CONTAGEM POR ANO")
    print("-" * 45)
    
    # Mapear fases para anos
    dados_vocab['Ano'] = dados_vocab['Fase'].map({2: 2023, 3: 2024, 4: 2024})
    
    # Contagem total de IDs únicos
    total_ids_unicos_vocab = dados_vocab['ID_Unico'].nunique()
    print(f"Total IDs únicos Vocabulário (todas as fases): {total_ids_unicos_vocab}")
    
    # Contagem por ano
    for ano in [2023, 2024]:
        dados_ano = dados_vocab[dados_vocab['Ano'] == ano]
        ids_unicos_ano = dados_ano['ID_Unico'].nunique()
        registros_ano = len(dados_ano)
        escolas_ano = dados_ano['Escola'].nunique()
        fases_ano = sorted(dados_ano['Fase'].unique())
        
        print(f"\nAno {ano}:")
        print(f"  Registros: {registros_ano}")
        print(f"  IDs únicos: {ids_unicos_ano}")
        print(f"  Escolas: {escolas_ano}")
        print(f"  Fases: {fases_ano}")
        
        # Verificar duplicatas
        duplicatas = dados_ano.groupby('ID_Unico').size()
        ids_com_duplicatas = duplicatas[duplicatas > 1]
        
        if len(ids_com_duplicatas) > 0:
            print(f"  IDs com múltiplos registros: {len(ids_com_duplicatas)}")
            print(f"  Exemplo de duplicatas: {ids_com_duplicatas.head()}")
    
    # Comparação de IDs entre TDE e Vocabulário
    print("\n4. COMPARAÇÃO ENTRE TDE E VOCABULÁRIO")
    print("-" * 45)
    
    ids_tde_total = set(dados_tde['ID_Unico'])
    ids_vocab_total = set(dados_vocab['ID_Unico'])
    
    ids_comuns = ids_tde_total.intersection(ids_vocab_total)
    ids_apenas_tde = ids_tde_total - ids_vocab_total
    ids_apenas_vocab = ids_vocab_total - ids_tde_total
    
    print(f"IDs únicos apenas em TDE: {len(ids_apenas_tde)}")
    print(f"IDs únicos apenas em Vocabulário: {len(ids_apenas_vocab)}")
    print(f"IDs comuns: {len(ids_comuns)}")
    print(f"Total união: {len(ids_tde_total.union(ids_vocab_total))}")
    
    # Análise por ano com IDs únicos
    print("\n5. ANÁLISE DETALHADA POR ANO")
    print("-" * 35)
    
    for ano in [2023, 2024]:
        print(f"\nANO {ano}:")
        
        # TDE
        tde_ano = dados_tde[dados_tde['Ano'] == ano]
        ids_tde_ano = set(tde_ano['ID_Unico'])
        
        # Vocabulário
        vocab_ano = dados_vocab[dados_vocab['Ano'] == ano]
        ids_vocab_ano = set(vocab_ano['ID_Unico'])
        
        # Comparações
        ids_comuns_ano = ids_tde_ano.intersection(ids_vocab_ano)
        ids_apenas_tde_ano = ids_tde_ano - ids_vocab_ano
        ids_apenas_vocab_ano = ids_vocab_ano - ids_tde_ano
        
        print(f"  TDE - IDs únicos: {len(ids_tde_ano)}")
        print(f"  Vocabulário - IDs únicos: {len(ids_vocab_ano)}")
        print(f"  IDs comuns: {len(ids_comuns_ano)}")
        print(f"  Apenas TDE: {len(ids_apenas_tde_ano)}")
        print(f"  Apenas Vocabulário: {len(ids_apenas_vocab_ano)}")
        print(f"  Total união: {len(ids_tde_ano.union(ids_vocab_ano))}")
        
        # Verificar escolas que têm apenas TDE ou apenas Vocabulário
        if len(ids_apenas_tde_ano) > 0:
            escolas_apenas_tde = tde_ano[tde_ano['ID_Unico'].isin(ids_apenas_tde_ano)]['Escola'].unique()
            print(f"  Escolas com estudantes apenas em TDE: {list(escolas_apenas_tde)}")
        
        if len(ids_apenas_vocab_ano) > 0:
            escolas_apenas_vocab = vocab_ano[vocab_ano['ID_Unico'].isin(ids_apenas_vocab_ano)]['Escola'].unique()
            print(f"  Escolas com estudantes apenas em Vocabulário: {list(escolas_apenas_vocab)}")
    
    # Análise de múltiplas fases por estudante
    print("\n6. ANÁLISE DE PARTICIPAÇÃO EM MÚLTIPLAS FASES")
    print("-" * 50)
    
    # TDE
    fases_por_estudante_tde = dados_tde.groupby('ID_Unico')['Fase'].nunique()
    print(f"\nTDE - Distribuição de fases por estudante:")
    for num_fases in sorted(fases_por_estudante_tde.unique()):
        count = (fases_por_estudante_tde == num_fases).sum()
        print(f"  {num_fases} fase(s): {count} estudantes")
    
    # Vocabulário
    fases_por_estudante_vocab = dados_vocab.groupby('ID_Unico')['Fase'].nunique()
    print(f"\nVocabulário - Distribuição de fases por estudante:")
    for num_fases in sorted(fases_por_estudante_vocab.unique()):
        count = (fases_por_estudante_vocab == num_fases).sum()
        print(f"  {num_fases} fase(s): {count} estudantes")
    
    # Investigar casos específicos
    print("\n7. INVESTIGAÇÃO DE CASOS ESPECÍFICOS")
    print("-" * 40)
    
    # Estudantes que participaram de múltiplas fases
    estudantes_multiplas_fases_tde = fases_por_estudante_tde[fases_por_estudante_tde > 1]
    estudantes_multiplas_fases_vocab = fases_por_estudante_vocab[fases_por_estudante_vocab > 1]
    
    print(f"TDE - Estudantes em múltiplas fases: {len(estudantes_multiplas_fases_tde)}")
    print(f"Vocabulário - Estudantes em múltiplas fases: {len(estudantes_multiplas_fases_vocab)}")
    
    if len(estudantes_multiplas_fases_tde) > 0:
        exemplo_id = estudantes_multiplas_fases_tde.index[0]
        exemplo_dados = dados_tde[dados_tde['ID_Unico'] == exemplo_id][['ID_Unico', 'Nome', 'Escola', 'Fase', 'Ano']]
        print(f"\nExemplo TDE - Estudante em múltiplas fases:")
        print(exemplo_dados.to_string(index=False))
    
    print("\n8. RESUMO DA INVESTIGAÇÃO")
    print("-" * 30)
    
    print(f"\nDiscrepâncias identificadas:")
    print(f"1. Contagem de registros vs IDs únicos pode diferir devido a:")
    print(f"   - Estudantes participando de múltiplas fases no mesmo ano")
    print(f"   - Estudantes em diferentes fases (3 e 4) em 2024")
    print(f"   - Diferenças de participação entre TDE e Vocabulário")
    
    print(f"\n2. Recomendações:")
    print(f"   - Usar sempre ID_Unico para contagem de estudantes únicos")
    print(f"   - Separar análises por fase quando necessário")
    print(f"   - Documentar critérios de contagem (únicos vs registros)")

if __name__ == "__main__":
    investigar_discrepancia_estudantes()