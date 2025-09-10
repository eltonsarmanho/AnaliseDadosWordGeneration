#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDAÇÃO DE DADOS LONGITUDINAIS - WORDGEN
Script para validar a qualidade dos dados longitudinais das Fases 2, 3 e 4

Verifica:
1. Dados duplicados dentro de cada CSV (nome, escola, turma iguais)
2. Integridade dos dados por fase
3. Consistência entre TDE e Vocabulário

Autor: Sistema de Análise WordGen
Data: 2024
"""

import pandas as pd
import pathlib
from typing import Dict, List, Tuple
import json

# ======================
# Configurações de Paths
# ======================
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
DATA_DIR = BASE_DIR / "Data"
LONGITUDINAL_DIR = BASE_DIR / "Modules" / "Longitudinal" / "Data"

# Arquivos longitudinais consolidados
CSV_LONGITUDINAL_TDE = LONGITUDINAL_DIR / "dados_longitudinais_TDE.csv"
CSV_LONGITUDINAL_VOCAB = LONGITUDINAL_DIR / "dados_longitudinais_Vocabulario.csv"

# Arquivos originais por fase
FASES_ORIGINAIS = {
    'Fase 2': {
        'TDE': {
            'Pre': DATA_DIR / "Fase 2" / "Pre" / "DadosTDE.csv",
            'Pos': DATA_DIR / "Fase 2" / "Pos" / "DadosTDE.csv"
        },
        'Vocabulario': {
            'Pre': DATA_DIR / "Fase 2" / "Pre" / "DadosVocabulario.csv", 
            'Pos': DATA_DIR / "Fase 2" / "Pos" / "DadosVocabulario.csv"
        }
    },
    'Fase 3': {
        'TDE': {
            'Pre': DATA_DIR / "Fase 3" / "Pre" / "DadosTDE.csv",
            'Pos': DATA_DIR / "Fase 3" / "Pos" / "DadosTDE.csv"
        },
        'Vocabulario': {
            'Pre': DATA_DIR / "Fase 3" / "Pre" / "DadosVocabulario.csv",
            'Pos': DATA_DIR / "Fase 3" / "Pos" / "DadosVocabulario.csv"
        }
    },
    'Fase 4': {
        'TDE': {
            'Pre': DATA_DIR / "Fase 4" / "Pre" / "DadosTDE.csv",
            'Pos': DATA_DIR / "Fase 4" / "Pos" / "DadosVocabulario.csv"  # Nota: arquivo tem nome incorreto
        },
        'Vocabulario': {
            'Pre': DATA_DIR / "Fase 4" / "Pre" / "DadosVocabulario.csv",
            'Pos': DATA_DIR / "Fase 4" / "Pos" / "DadosTDE.csv"  # Nota: arquivo tem nome incorreto
        }
    }
}

def normalizar_nomes_colunas(df):
    """Normaliza nomes das colunas para padrão consistente"""
    # Mapeamento de variações de nomes
    mapeamento = {
        # Variações de Escola
        'escola': 'Escola',
        'ESCOLA': 'Escola',
        'School': 'Escola',
        
        # Variações de Turma
        'turma': 'Turma',
        'TURMA': 'Turma',
        'Class': 'Turma',
        
        # Variações de Nome
        'nome': 'Nome',
        'NOME': 'Nome',
        'Name': 'Nome',
        
        # Variações de Sexo
        'sexo': 'Sexo',
        'SEXO': 'Sexo',
        'Gender': 'Sexo',
        
        # Variações de questões
        'Q1': 'P1', 'Q2': 'P2', 'Q3': 'P3', 'Q4': 'P4',
        'Q5': 'P5', 'Q6': 'P6', 'Q7': 'P7', 'Q8': 'P8'
    }
    
    # Renomear colunas conforme mapeamento
    df_normalizado = df.rename(columns=mapeamento)
    return df_normalizado

def verificar_duplicados_csv(caminho_arquivo: pathlib.Path) -> Dict:
    """
    Verifica duplicados em um arquivo CSV baseado em nome, escola e turma
    
    Returns:
        Dict com informações sobre duplicados encontrados
    """
    resultado = {
        'arquivo': str(caminho_arquivo),
        'existe': caminho_arquivo.exists(),
        'total_registros': 0,
        'duplicados_encontrados': 0,
        'registros_duplicados': [],
        'grupos_duplicados': [],
        'erro': None
    }
    
    if not caminho_arquivo.exists():
        resultado['erro'] = "Arquivo não encontrado"
        return resultado
    
    try:
        # Carregar CSV
        df = pd.read_csv(caminho_arquivo, encoding='utf-8')
        df = normalizar_nomes_colunas(df)
        
        resultado['total_registros'] = len(df)
        
        # Verificar se existem as colunas necessárias
        colunas_necessarias = ['Nome', 'Escola', 'Turma']
        colunas_existentes = [col for col in colunas_necessarias if col in df.columns]
        
        if len(colunas_existentes) < 3:
            resultado['erro'] = f"Colunas necessárias não encontradas. Disponíveis: {list(df.columns)}"
            return resultado
        
        # Limpar dados vazios/nulos para análise de duplicados
        df_limpo = df.dropna(subset=colunas_necessarias)
        
        # Identificar duplicados baseado em Nome, Escola e Turma
        duplicados_mask = df_limpo.duplicated(subset=colunas_necessarias, keep=False)
        duplicados_df = df_limpo[duplicados_mask]
        
        resultado['duplicados_encontrados'] = len(duplicados_df)
        
        if len(duplicados_df) > 0:
            # Agrupar duplicados
            grupos = duplicados_df.groupby(colunas_necessarias)
            
            for grupo_key, grupo_df in grupos:
                nome, escola, turma = grupo_key
                grupo_info = {
                    'nome': nome,
                    'escola': escola, 
                    'turma': turma,
                    'num_ocorrencias': len(grupo_df),
                    'indices': grupo_df.index.tolist()
                }
                resultado['grupos_duplicados'].append(grupo_info)
                
                # Adicionar registros individuais
                for idx, row in grupo_df.iterrows():
                    registro = {
                        'indice': idx,
                        'nome': row['Nome'],
                        'escola': row['Escola'],
                        'turma': row['Turma']
                    }
                    resultado['registros_duplicados'].append(registro)
        
    except Exception as e:
        resultado['erro'] = str(e)
    
    return resultado

def validar_arquivos_longitudinais():
    """Valida arquivos longitudinais consolidados"""
    print("🔍 VALIDAÇÃO DE DADOS LONGITUDINAIS - WORDGEN")
    print("=" * 60)
    
    arquivos_longitudinais = [
        ('TDE Longitudinal', CSV_LONGITUDINAL_TDE),
        ('Vocabulário Longitudinal', CSV_LONGITUDINAL_VOCAB)
    ]
    
    resultados_longitudinais = {}
    
    for nome, arquivo in arquivos_longitudinais:
        print(f"\n📊 Validando: {nome}")
        print("-" * 40)
        
        resultado = verificar_duplicados_csv(arquivo)
        resultados_longitudinais[nome] = resultado
        
        if resultado['erro']:
            print(f"❌ ERRO: {resultado['erro']}")
            continue
            
        print(f"📁 Arquivo: {resultado['arquivo']}")
        print(f"📈 Total de registros: {resultado['total_registros']:,}")
        print(f"🔍 Duplicados encontrados: {resultado['duplicados_encontrados']:,}")
        
        if resultado['duplicados_encontrados'] > 0:
            print(f"⚠️  ATENÇÃO: Encontrados {resultado['duplicados_encontrados']} registros duplicados!")
            print(f"🔢 Grupos de duplicação: {len(resultado['grupos_duplicados'])}")
            
            print("\n📋 Detalhes dos grupos duplicados:")
            for i, grupo in enumerate(resultado['grupos_duplicados'][:5], 1):  # Mostrar apenas 5 primeiros
                print(f"  {i}. {grupo['nome']} | {grupo['escola']} | {grupo['turma']} ({grupo['num_ocorrencias']} ocorrências)")
            
            if len(resultado['grupos_duplicados']) > 5:
                print(f"  ... e mais {len(resultado['grupos_duplicados']) - 5} grupos")
        else:
            print("✅ Nenhum duplicado encontrado!")
    
    return resultados_longitudinais

def validar_arquivos_originais():
    """Valida arquivos originais por fase"""
    print(f"\n🔍 VALIDAÇÃO DE ARQUIVOS ORIGINAIS POR FASE")
    print("=" * 60)
    
    resultados_originais = {}
    
    for fase, tipos in FASES_ORIGINAIS.items():
        print(f"\n📅 {fase}")
        print("-" * 30)
        
        resultados_originais[fase] = {}
        
        for tipo, momentos in tipos.items():
            print(f"\n  📊 {tipo}")
            
            resultados_originais[fase][tipo] = {}
            
            for momento, arquivo in momentos.items():
                print(f"    📁 {momento}: ", end="")
                
                resultado = verificar_duplicados_csv(arquivo)
                resultados_originais[fase][tipo][momento] = resultado
                
                if resultado['erro']:
                    print(f"❌ {resultado['erro']}")
                    continue
                
                status = "✅ OK" if resultado['duplicados_encontrados'] == 0 else f"⚠️  {resultado['duplicados_encontrados']} duplicados"
                print(f"{status} ({resultado['total_registros']} registros)")
                
                if resultado['duplicados_encontrados'] > 0:
                    print(f"      🔍 Grupos duplicados: {len(resultado['grupos_duplicados'])}")
    
    return resultados_originais

def gerar_relatorio_validacao(resultados_longitudinais, resultados_originais):
    """Gera relatório de validação em JSON"""
    relatorio = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'validacao_longitudinal': resultados_longitudinais,
        'validacao_original': resultados_originais,
        'resumo': {
            'total_arquivos_validados': 0,
            'arquivos_com_duplicados': 0,
            'total_duplicados_encontrados': 0
        }
    }
    
    # Calcular resumo
    total_arquivos = 0
    arquivos_com_duplicados = 0
    total_duplicados = 0
    
    # Arquivos longitudinais
    for nome, resultado in resultados_longitudinais.items():
        if not resultado['erro']:
            total_arquivos += 1
            if resultado['duplicados_encontrados'] > 0:
                arquivos_com_duplicados += 1
                total_duplicados += resultado['duplicados_encontrados']
    
    # Arquivos originais
    for fase, tipos in resultados_originais.items():
        for tipo, momentos in tipos.items():
            for momento, resultado in momentos.items():
                if not resultado['erro']:
                    total_arquivos += 1
                    if resultado['duplicados_encontrados'] > 0:
                        arquivos_com_duplicados += 1
                        total_duplicados += resultado['duplicados_encontrados']
    
    relatorio['resumo'] = {
        'total_arquivos_validados': total_arquivos,
        'arquivos_com_duplicados': arquivos_com_duplicados,
        'total_duplicados_encontrados': total_duplicados,
        'porcentagem_arquivos_com_duplicados': (arquivos_com_duplicados / total_arquivos * 100) if total_arquivos > 0 else 0
    }
    
    # Salvar relatório
    arquivo_relatorio = LONGITUDINAL_DIR / "relatorio_validacao_duplicados.json"
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Relatório salvo em: {arquivo_relatorio}")
    
    return relatorio

def main():
    """Função principal de validação"""
    print("🚀 INICIANDO VALIDAÇÃO DE DADOS LONGITUDINAIS")
    print("=" * 70)
    
    # Validar arquivos longitudinais consolidados
    resultados_longitudinais = validar_arquivos_longitudinais()
    
    # Validar arquivos originais por fase
    resultados_originais = validar_arquivos_originais()
    
    # Gerar relatório
    relatorio = gerar_relatorio_validacao(resultados_longitudinais, resultados_originais)
    
    # Resumo final
    print(f"\n📊 RESUMO DA VALIDAÇÃO")
    print("=" * 30)
    print(f"📁 Total de arquivos validados: {relatorio['resumo']['total_arquivos_validados']}")
    print(f"⚠️  Arquivos com duplicados: {relatorio['resumo']['arquivos_com_duplicados']}")
    print(f"🔍 Total de duplicados encontrados: {relatorio['resumo']['total_duplicados_encontrados']}")
    print(f"📈 Porcentagem com duplicados: {relatorio['resumo']['porcentagem_arquivos_com_duplicados']:.1f}%")
    
    if relatorio['resumo']['total_duplicados_encontrados'] == 0:
        print("\n✅ VALIDAÇÃO CONCLUÍDA: Nenhum duplicado encontrado!")
    else:
        print("\n⚠️  VALIDAÇÃO CONCLUÍDA: Duplicados encontrados - revisar dados!")
    
    return relatorio

if __name__ == "__main__":
    main()