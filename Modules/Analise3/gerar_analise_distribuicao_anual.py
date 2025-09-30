#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise de Escolas e Estudantes por Ano - TDE e Vocabulário
Análise da distribuição de escolas e estudantes por ano (2023 e 2024)
"""

import pandas as pd
import numpy as np
from pathlib import Path

def mapear_fase_para_ano(fase):
    """Mapeia fase para ano"""
    if fase == 2:
        return 2023
    elif fase in [3, 4]:
        return 2024
    else:
        return None

def analisar_distribuicao_por_ano(dados, tipo_avaliacao):
    """Analisa distribuição de escolas e estudantes por ano"""
    
    # Adicionar coluna de ano baseada na fase
    dados['Ano'] = dados['Fase'].apply(mapear_fase_para_ano)
    
    # Remover registros sem ano válido
    dados_validos = dados[dados['Ano'].notna()].copy()
    
    analise_por_ano = {}
    
    for ano in sorted(dados_validos['Ano'].unique()):
        dados_ano = dados_validos[dados_validos['Ano'] == ano]
        
        # Contagens básicas - CORRIGIDO para usar IDs únicos
        num_escolas = dados_ano['Escola'].nunique()
        num_estudantes = dados_ano['ID_Unico'].nunique()  # Esta é a contagem correta
        num_registros = len(dados_ano)  # Pode ser maior devido a múltiplas fases
        
        # Escolas por ordem alfabética
        escolas_lista = sorted(dados_ano['Escola'].unique())
        
        # Estudantes por escola
        estudantes_por_escola = dados_ano.groupby('Escola')['ID_Unico'].nunique().sort_values(ascending=False)
        
        # Registros por escola (considerando múltiplas fases)
        registros_por_escola = dados_ano.groupby('Escola').size().sort_values(ascending=False)
        
        # Fases participadas neste ano
        fases_ano = sorted(dados_ano['Fase'].unique())
        
        # Distribuição por fase dentro do ano
        distribuicao_fases = dados_ano.groupby('Fase').agg({
            'ID_Unico': 'nunique',
            'Escola': 'nunique'
        }).rename(columns={'ID_Unico': 'Estudantes', 'Escola': 'Escolas'})
        
        # Análise de turmas (se disponível)
        turmas_info = {}
        if 'Turma' in dados_ano.columns:
            turmas_por_escola = dados_ano.groupby('Escola')['Turma'].nunique().sort_values(ascending=False)
            total_turmas = dados_ano['Turma'].nunique()
            turmas_info = {
                'total_turmas': total_turmas,
                'turmas_por_escola': turmas_por_escola.to_dict(),
                'media_turmas_por_escola': turmas_por_escola.mean()
            }
        
        # Estatísticas de desempenho por ano
        scores_pre_ano = dados_ano['Score_Pre'].dropna()
        scores_pos_ano = dados_ano['Score_Pos'].dropna()
        
        desempenho_info = {
            'score_pre_medio': scores_pre_ano.mean() if len(scores_pre_ano) > 0 else None,
            'score_pos_medio': scores_pos_ano.mean() if len(scores_pos_ano) > 0 else None,
            'ganho_medio': (scores_pos_ano.mean() - scores_pre_ano.mean()) if len(scores_pre_ano) > 0 and len(scores_pos_ano) > 0 else None
        }
        
        analise_por_ano[int(ano)] = {
            'num_escolas': num_escolas,
            'num_estudantes': num_estudantes,
            'num_registros': num_registros,
            'fases_participadas': fases_ano,
            'escolas_lista': escolas_lista,
            'estudantes_por_escola': estudantes_por_escola.to_dict(),
            'registros_por_escola': registros_por_escola.to_dict(),
            'distribuicao_fases': distribuicao_fases.to_dict(),
            'turmas_info': turmas_info,
            'desempenho_info': desempenho_info,
            'tipo_avaliacao': tipo_avaliacao
        }
    
    return analise_por_ano

def calcular_estatisticas_comparativas(analise_tde, analise_vocab):
    """Calcula estatísticas comparativas entre anos e avaliações"""
    
    comparativas = {}
    
    # Anos disponíveis
    anos_tde = set(analise_tde.keys())
    anos_vocab = set(analise_vocab.keys())
    anos_comuns = anos_tde.intersection(anos_vocab)
    
    for ano in sorted(anos_comuns):
        dados_tde = analise_tde[ano]
        dados_vocab = analise_vocab[ano]
        
        # Escolas em comum
        escolas_tde = set(dados_tde['escolas_lista'])
        escolas_vocab = set(dados_vocab['escolas_lista'])
        escolas_comuns = escolas_tde.intersection(escolas_vocab)
        escolas_apenas_tde = escolas_tde - escolas_vocab
        escolas_apenas_vocab = escolas_vocab - escolas_tde
        
        # Comparação de cobertura
        cobertura = {
            'escolas_comuns': len(escolas_comuns),
            'escolas_apenas_tde': len(escolas_apenas_tde),
            'escolas_apenas_vocab': len(escolas_apenas_vocab),
            'total_escolas_unicas': len(escolas_tde.union(escolas_vocab)),
            'taxa_sobreposicao': len(escolas_comuns) / len(escolas_tde.union(escolas_vocab)) * 100 if len(escolas_tde.union(escolas_vocab)) > 0 else 0
        }
        
        # Comparação de estudantes
        estudantes_comparacao = {
            'tde_estudantes': dados_tde['num_estudantes'],
            'vocab_estudantes': dados_vocab['num_estudantes'],
            'diferenca_absoluta': abs(dados_tde['num_estudantes'] - dados_vocab['num_estudantes']),
            'taxa_diferenca': abs(dados_tde['num_estudantes'] - dados_vocab['num_estudantes']) / max(dados_tde['num_estudantes'], dados_vocab['num_estudantes']) * 100 if max(dados_tde['num_estudantes'], dados_vocab['num_estudantes']) > 0 else 0
        }
        
        comparativas[ano] = {
            'cobertura_escolas': cobertura,
            'comparacao_estudantes': estudantes_comparacao,
            'escolas_comuns_lista': sorted(list(escolas_comuns)),
            'escolas_apenas_tde_lista': sorted(list(escolas_apenas_tde)),
            'escolas_apenas_vocab_lista': sorted(list(escolas_apenas_vocab))
        }
    
    return comparativas

def gerar_relatorio_distribuicao_anual():
    """Gera relatório de distribuição de escolas e estudantes por ano"""
    
    print("Iniciando análise de distribuição anual...")
    
    # Definir caminhos
    pasta_dashboard = Path("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Dashboard")
    pasta_saida = Path("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Modules/Analise3")
    
    arquivo_tde = pasta_dashboard / "TDE_longitudinal.csv"
    arquivo_vocab = pasta_dashboard / "vocabulario_longitudinal.csv"
    
    if not arquivo_tde.exists() or not arquivo_vocab.exists():
        print("ERRO: Arquivos longitudinais não encontrados!")
        return
    
    # Carregar dados
    print("Carregando dados longitudinais...")
    dados_tde = pd.read_csv(arquivo_tde)
    dados_vocab = pd.read_csv(arquivo_vocab)
    
    print(f"TDE Longitudinal: {len(dados_tde)} registros")
    print(f"Vocabulário Longitudinal: {len(dados_vocab)} registros")
    
    # Analisar distribuições por ano
    print("Analisando distribuições por ano...")
    analise_tde = analisar_distribuicao_por_ano(dados_tde, 'TDE')
    analise_vocab = analisar_distribuicao_por_ano(dados_vocab, 'Vocabulário')
    
    # Calcular estatísticas comparativas
    print("Calculando estatísticas comparativas...")
    comparativas = calcular_estatisticas_comparativas(analise_tde, analise_vocab)
    
    # Gerar relatório
    arquivo_relatorio = pasta_saida / "relatorio_distribuicao_anual.txt"
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RELATÓRIO DE DISTRIBUIÇÃO ANUAL DE ESCOLAS E ESTUDANTES\n")
        f.write("Análise por Ano: 2023 (Fase 2) e 2024 (Fases 3-4)\n")
        f.write("=" * 80 + "\n\n")
        
        # Resumo Executivo
        f.write("RESUMO EXECUTIVO\n")
        f.write("-" * 40 + "\n")
        f.write(f"Período de análise: 2023 (Fase 2) e 2024 (Fases 3-4)\n")
        f.write(f"Avaliações: TDE e Vocabulário\n\n")
        
        # === ANÁLISE TDE POR ANO ===
        f.write("ANÁLISE TDE - DISTRIBUIÇÃO POR ANO\n")
        f.write("=" * 40 + "\n\n")
        
        for ano in sorted(analise_tde.keys()):
            dados = analise_tde[ano]
            
            f.write(f"ANO {ano}\n")
            f.write("-" * 20 + "\n")
            f.write(f"Número de escolas: {dados['num_escolas']}\n")
            f.write(f"Número de estudantes: {dados['num_estudantes']}\n")
            f.write(f"Número de registros: {dados['num_registros']}\n")
            f.write(f"Fases participadas: {dados['fases_participadas']}\n")
            
            # Desempenho médio
            if dados['desempenho_info']['score_pre_medio'] is not None:
                f.write(f"Score pré médio: {dados['desempenho_info']['score_pre_medio']:.1f}\n")
                f.write(f"Score pós médio: {dados['desempenho_info']['score_pos_medio']:.1f}\n")
                if dados['desempenho_info']['ganho_medio'] is not None:
                    f.write(f"Ganho médio: {dados['desempenho_info']['ganho_medio']:.1f}\n")
            
            # Turmas (se disponível)
            if dados['turmas_info'] and 'total_turmas' in dados['turmas_info']:
                f.write(f"Total de turmas: {dados['turmas_info']['total_turmas']}\n")
                f.write(f"Média de turmas por escola: {dados['turmas_info']['media_turmas_por_escola']:.1f}\n")
            
            f.write(f"\nLista de escolas ({dados['num_escolas']} escolas):\n")
            for i, escola in enumerate(dados['escolas_lista'], 1):
                f.write(f"{i:2d}. {escola}\n")
            
            f.write(f"\nDistribuição de estudantes por escola:\n")
            for escola, num_estudantes in sorted(dados['estudantes_por_escola'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"{escola}: {num_estudantes} estudantes\n")
            
            # Distribuição por fases dentro do ano
            if 'distribuicao_fases' in dados and dados['distribuicao_fases']:
                f.write(f"\nDistribuição por fases em {ano}:\n")
                for fase_key, valores in dados['distribuicao_fases'].items():
                    if isinstance(valores, dict):
                        for metrica, valor in valores.items():
                            f.write(f"  Fase {fase_key} - {metrica}: {valor}\n")
            
            f.write("\n")
        
        # === ANÁLISE VOCABULÁRIO POR ANO ===
        f.write("\nANÁLISE VOCABULÁRIO - DISTRIBUIÇÃO POR ANO\n")
        f.write("=" * 45 + "\n\n")
        
        for ano in sorted(analise_vocab.keys()):
            dados = analise_vocab[ano]
            
            f.write(f"ANO {ano}\n")
            f.write("-" * 20 + "\n")
            f.write(f"Número de escolas: {dados['num_escolas']}\n")
            f.write(f"Número de estudantes: {dados['num_estudantes']}\n")
            f.write(f"Número de registros: {dados['num_registros']}\n")
            f.write(f"Fases participadas: {dados['fases_participadas']}\n")
            
            # Desempenho médio
            if dados['desempenho_info']['score_pre_medio'] is not None:
                f.write(f"Score pré médio: {dados['desempenho_info']['score_pre_medio']:.1f}\n")
                f.write(f"Score pós médio: {dados['desempenho_info']['score_pos_medio']:.1f}\n")
                if dados['desempenho_info']['ganho_medio'] is not None:
                    f.write(f"Ganho médio: {dados['desempenho_info']['ganho_medio']:.1f}\n")
            
            # Turmas (se disponível)
            if dados['turmas_info'] and 'total_turmas' in dados['turmas_info']:
                f.write(f"Total de turmas: {dados['turmas_info']['total_turmas']}\n")
                f.write(f"Média de turmas por escola: {dados['turmas_info']['media_turmas_por_escola']:.1f}\n")
            
            f.write(f"\nLista de escolas ({dados['num_escolas']} escolas):\n")
            for i, escola in enumerate(dados['escolas_lista'], 1):
                f.write(f"{i:2d}. {escola}\n")
            
            f.write(f"\nDistribuição de estudantes por escola:\n")
            for escola, num_estudantes in sorted(dados['estudantes_por_escola'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"{escola}: {num_estudantes} estudantes\n")
            
            # Distribuição por fases dentro do ano
            if 'distribuicao_fases' in dados and dados['distribuicao_fases']:
                f.write(f"\nDistribuição por fases em {ano}:\n")
                for fase_key, valores in dados['distribuicao_fases'].items():
                    if isinstance(valores, dict):
                        for metrica, valor in valores.items():
                            f.write(f"  Fase {fase_key} - {metrica}: {valor}\n")
            
            f.write("\n")
        
        # === ANÁLISE COMPARATIVA ENTRE ANOS ===
        f.write("\nANÁLISE COMPARATIVA ENTRE ANOS\n")
        f.write("=" * 35 + "\n\n")
        
        anos_tde = sorted(analise_tde.keys())
        anos_vocab = sorted(analise_vocab.keys())
        
        f.write("EVOLUÇÃO TDE:\n")
        f.write("-" * 15 + "\n")
        if len(anos_tde) >= 2:
            ano_inicial = anos_tde[0]
            ano_final = anos_tde[-1]
            
            escolas_inicial = analise_tde[ano_inicial]['num_escolas']
            escolas_final = analise_tde[ano_final]['num_escolas']
            estudantes_inicial = analise_tde[ano_inicial]['num_estudantes']
            estudantes_final = analise_tde[ano_final]['num_estudantes']
            
            f.write(f"Escolas {ano_inicial}: {escolas_inicial} → {ano_final}: {escolas_final} (Δ: {escolas_final - escolas_inicial:+d})\n")
            f.write(f"Estudantes {ano_inicial}: {estudantes_inicial} → {ano_final}: {estudantes_final} (Δ: {estudantes_final - estudantes_inicial:+d})\n")
            
            # Percentuais de mudança
            pct_mudanca_escolas = ((escolas_final - escolas_inicial) / escolas_inicial * 100) if escolas_inicial > 0 else 0
            pct_mudanca_estudantes = ((estudantes_final - estudantes_inicial) / estudantes_inicial * 100) if estudantes_inicial > 0 else 0
            
            f.write(f"Variação escolas: {pct_mudanca_escolas:+.1f}%\n")
            f.write(f"Variação estudantes: {pct_mudanca_estudantes:+.1f}%\n")
        
        f.write(f"\nEVOLUÇÃO VOCABULÁRIO:\n")
        f.write("-" * 20 + "\n")
        if len(anos_vocab) >= 2:
            ano_inicial = anos_vocab[0]
            ano_final = anos_vocab[-1]
            
            escolas_inicial = analise_vocab[ano_inicial]['num_escolas']
            escolas_final = analise_vocab[ano_final]['num_escolas']
            estudantes_inicial = analise_vocab[ano_inicial]['num_estudantes']
            estudantes_final = analise_vocab[ano_final]['num_estudantes']
            
            f.write(f"Escolas {ano_inicial}: {escolas_inicial} → {ano_final}: {escolas_final} (Δ: {escolas_final - escolas_inicial:+d})\n")
            f.write(f"Estudantes {ano_inicial}: {estudantes_inicial} → {ano_final}: {estudantes_final} (Δ: {estudantes_final - estudantes_inicial:+d})\n")
            
            # Percentuais de mudança
            pct_mudanca_escolas = ((escolas_final - escolas_inicial) / escolas_inicial * 100) if escolas_inicial > 0 else 0
            pct_mudanca_estudantes = ((estudantes_final - estudantes_inicial) / estudantes_inicial * 100) if estudantes_inicial > 0 else 0
            
            f.write(f"Variação escolas: {pct_mudanca_escolas:+.1f}%\n")
            f.write(f"Variação estudantes: {pct_mudanca_estudantes:+.1f}%\n")
        
        # === ANÁLISE COMPARATIVA TDE vs VOCABULÁRIO ===
        f.write(f"\nANÁLISE COMPARATIVA TDE vs VOCABULÁRIO\n")
        f.write("=" * 45 + "\n\n")
        
        for ano in sorted(comparativas.keys()):
            comp = comparativas[ano]
            
            f.write(f"ANO {ano}:\n")
            f.write("-" * 10 + "\n")
            f.write(f"Escolas TDE: {comp['comparacao_estudantes']['tde_estudantes']} estudantes\n")
            f.write(f"Escolas Vocabulário: {comp['comparacao_estudantes']['vocab_estudantes']} estudantes\n")
            f.write(f"Diferença absoluta: {comp['comparacao_estudantes']['diferenca_absoluta']} estudantes\n")
            f.write(f"Taxa de diferença: {comp['comparacao_estudantes']['taxa_diferenca']:.1f}%\n")
            
            f.write(f"\nCobertura de escolas:\n")
            f.write(f"  Escolas comuns: {comp['cobertura_escolas']['escolas_comuns']}\n")
            f.write(f"  Apenas TDE: {comp['cobertura_escolas']['escolas_apenas_tde']}\n")
            f.write(f"  Apenas Vocabulário: {comp['cobertura_escolas']['escolas_apenas_vocab']}\n")
            f.write(f"  Total único: {comp['cobertura_escolas']['total_escolas_unicas']}\n")
            f.write(f"  Taxa de sobreposição: {comp['cobertura_escolas']['taxa_sobreposicao']:.1f}%\n")
            
            if comp['escolas_apenas_tde_lista']:
                f.write(f"\nEscolas apenas em TDE ({len(comp['escolas_apenas_tde_lista'])}):\n")
                for escola in comp['escolas_apenas_tde_lista']:
                    f.write(f"  • {escola}\n")
            
            if comp['escolas_apenas_vocab_lista']:
                f.write(f"\nEscolas apenas em Vocabulário ({len(comp['escolas_apenas_vocab_lista'])}):\n")
                for escola in comp['escolas_apenas_vocab_lista']:
                    f.write(f"  • {escola}\n")
            
            f.write("\n")
        
        # === SÍNTESE E RECOMENDAÇÕES ===
        f.write("SÍNTESE E RECOMENDAÇÕES\n")
        f.write("=" * 25 + "\n\n")
        
        # Calcular totais gerais
        total_escolas_tde = sum(dados['num_escolas'] for dados in analise_tde.values())
        total_estudantes_tde = sum(dados['num_estudantes'] for dados in analise_tde.values())
        total_escolas_vocab = sum(dados['num_escolas'] for dados in analise_vocab.values())
        total_estudantes_vocab = sum(dados['num_estudantes'] for dados in analise_vocab.values())
        
        f.write("TOTAIS CONSOLIDADOS:\n")
        f.write("-" * 20 + "\n")
        f.write(f"TDE - Total escolas: {total_escolas_tde}, Total estudantes: {total_estudantes_tde}\n")
        f.write(f"Vocabulário - Total escolas: {total_escolas_vocab}, Total estudantes: {total_estudantes_vocab}\n")
        
        f.write(f"\nRECOMENDAÇÕES:\n")
        f.write("1. Padronizar cobertura de escolas entre TDE e Vocabulário\n")
        f.write("2. Investigar fatores de variação ano a ano\n")
        f.write("3. Monitorar adesão e continuidade das escolas\n")
        f.write("4. Analisar capacidade de atendimento por escola\n")
        f.write("5. Desenvolver estratégias de expansão equilibrada\n")
        
        f.write(f"\n\nRelatório gerado em: {pd.Timestamp.now()}\n")
        f.write("=" * 80 + "\n")
    
    # Salvar dados detalhados
    arquivo_dados_tde = pasta_saida / "dados_distribuicao_tde_por_ano.csv"
    arquivo_dados_vocab = pasta_saida / "dados_distribuicao_vocab_por_ano.csv"
    
    # Converter análises para DataFrames para salvar
    dados_tde_df = []
    for ano, dados in analise_tde.items():
        for escola, num_estudantes in dados['estudantes_por_escola'].items():
            dados_tde_df.append({
                'Ano': ano,
                'Escola': escola,
                'Num_Estudantes': num_estudantes,
                'Num_Registros': dados['registros_por_escola'].get(escola, 0),
                'Tipo_Avaliacao': 'TDE'
            })
    
    dados_vocab_df = []
    for ano, dados in analise_vocab.items():
        for escola, num_estudantes in dados['estudantes_por_escola'].items():
            dados_vocab_df.append({
                'Ano': ano,
                'Escola': escola,
                'Num_Estudantes': num_estudantes,
                'Num_Registros': dados['registros_por_escola'].get(escola, 0),
                'Tipo_Avaliacao': 'Vocabulário'
            })
    
    if dados_tde_df:
        pd.DataFrame(dados_tde_df).to_csv(arquivo_dados_tde, index=False, encoding='utf-8')
    
    if dados_vocab_df:
        pd.DataFrame(dados_vocab_df).to_csv(arquivo_dados_vocab, index=False, encoding='utf-8')
    
    print(f"\nRelatório gerado: {arquivo_relatorio}")
    print(f"Dados TDE detalhados: {arquivo_dados_tde}")
    print(f"Dados Vocabulário detalhados: {arquivo_dados_vocab}")
    print("\nAnálise de distribuição anual concluída!")

if __name__ == "__main__":
    gerar_relatorio_distribuicao_anual()