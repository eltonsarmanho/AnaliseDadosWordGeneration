#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise de Estratos Longitudinais de Desempenho - TDE e Vocabulário
Análise das trajetórias de progresso dos estudantes ao longo das fases 2, 3 e 4
"""

import pandas as pd
import numpy as np
from pathlib import Path

def calcular_progresso_longitudinal(dados, tipo_avaliacao):
    """Calcula o progresso longitudinal de cada estudante através das fases"""
    progressos = []
    
    # Agrupar por ID único para analisar trajetória individual
    for id_unico, dados_aluno in dados.groupby('ID_Unico'):
        fases = sorted(dados_aluno['Fase'].unique())
        
        if len(fases) == 0:
            continue
            
        # Extrair dados básicos do estudante
        nome = dados_aluno['Nome'].iloc[0]
        escola = dados_aluno['Escola'].iloc[0]
        ano = dados_aluno['Ano'].iloc[0] if 'Ano' in dados_aluno.columns else None
        
        # Coletar scores por fase
        scores_pre_fases = {}
        scores_pos_fases = {}
        
        for fase in fases:
            dados_fase = dados_aluno[dados_aluno['Fase'] == fase]
            if not dados_fase.empty:
                score_pre = dados_fase['Score_Pre'].iloc[0]
                score_pos = dados_fase['Score_Pos'].iloc[0]
                
                if pd.notna(score_pre) and pd.notna(score_pos):
                    scores_pre_fases[fase] = score_pre
                    scores_pos_fases[fase] = score_pos
        
        if len(scores_pre_fases) >= 1:
            # Calcular métricas de progresso
            fases_validas = sorted(scores_pre_fases.keys())
            
            # Score inicial (primeiro pré) e final (último pós)
            score_inicial = scores_pre_fases[fases_validas[0]]
            score_final = scores_pos_fases[fases_validas[-1]]
            
            # Progresso total acumulado
            progresso_total = score_final - score_inicial
            
            # Progresso percentual
            base_calculo = max(score_inicial, 1)  # Evitar divisão por zero
            progresso_percentual = (progresso_total / base_calculo) * 100
            
            # Calcular ganhos intra-fase para cada fase
            ganhos_intra_fase = {}
            for fase in fases_validas:
                ganho = scores_pos_fases[fase] - scores_pre_fases[fase]
                ganhos_intra_fase[fase] = ganho
            
            # Ganho médio por fase
            ganho_medio = np.mean(list(ganhos_intra_fase.values()))
            
            # Calcular progresso inter-fases (se múltiplas fases)
            progresso_inter_fases = 0
            if len(fases_validas) > 1:
                # Do pós da primeira fase ao pré da última fase
                progresso_inter_fases = scores_pre_fases[fases_validas[-1]] - scores_pos_fases[fases_validas[0]]
            
            # Determinar trajetória (crescente, decrescente, oscilante)
            trajetoria = "Única Fase"
            if len(fases_validas) > 1:
                if progresso_total > 0:
                    trajetoria = "Crescente"
                elif progresso_total < 0:
                    trajetoria = "Decrescente"
                else:
                    trajetoria = "Estável"
            
            progressos.append({
                'ID_Unico': id_unico,
                'Nome': nome,
                'Escola': escola,
                'Ano': ano,
                'Tipo_Avaliacao': tipo_avaliacao,
                'Num_Fases': len(fases_validas),
                'Fases_Participadas': fases_validas,
                'Score_Inicial': score_inicial,
                'Score_Final': score_final,
                'Progresso_Total_Acumulado': progresso_total,
                'Progresso_Percentual': progresso_percentual,
                'Ganho_Medio_Por_Fase': ganho_medio,
                'Progresso_Inter_Fases': progresso_inter_fases,
                'Trajetoria': trajetoria,
                'Scores_Pre_Por_Fase': scores_pre_fases,
                'Scores_Pos_Por_Fase': scores_pos_fases,
                'Ganhos_Intra_Fase': ganhos_intra_fase
            })
    
    return pd.DataFrame(progressos)

def classificar_estratos_progresso(df_progresso):
    """Classifica estudantes em estratos de desempenho longitudinal"""
    
    def classificar_por_percentual(pct):
        if pct >= 75:
            return "Avanço Excepcional (≥75%)"
        elif pct >= 50:
            return "Alto Avanço (50-74%)"
        elif pct >= 25:
            return "Avanço Moderado (25-49%)"
        elif pct >= 10:
            return "Avanço Baixo (10-24%)"
        elif pct >= 0:
            return "Manutenção (0-9%)"
        elif pct >= -15:
            return "Declínio Leve (0 a -15%)"
        else:
            return "Declínio Severo (<-15%)"
    
    def classificar_por_absoluto(valor, tipo_avaliacao):
        if tipo_avaliacao == 'TDE':
            if valor >= 20:
                return "Ganho Alto (≥20 pontos)"
            elif valor >= 10:
                return "Ganho Moderado (10-19 pontos)"
            elif valor >= 5:
                return "Ganho Baixo (5-9 pontos)"
            elif valor >= 0:
                return "Estabilidade (0-4 pontos)"
            elif valor >= -10:
                return "Perda Leve (-1 a -10 pontos)"
            else:
                return "Perda Significativa (<-10 pontos)"
        else:  # Vocabulário
            if valor >= 15:
                return "Ganho Alto (≥15 pontos)"
            elif valor >= 8:
                return "Ganho Moderado (8-14 pontos)"
            elif valor >= 3:
                return "Ganho Baixo (3-7 pontos)"
            elif valor >= 0:
                return "Estabilidade (0-2 pontos)"
            elif valor >= -5:
                return "Perda Leve (-1 a -5 pontos)"
            else:
                return "Perda Significativa (<-5 pontos)"
    
    def classificar_desempenho_final(score, tipo_avaliacao):
        if tipo_avaliacao == 'TDE':
            if score >= 32:  # 80% de 40
                return "Proficiente (≥80%)"
            elif score >= 24:  # 60% de 40
                return "Adequado (60-79%)"
            elif score >= 16:  # 40% de 40
                return "Básico (40-59%)"
            else:
                return "Abaixo do Básico (<40%)"
        else:  # Vocabulário
            if score >= 40:
                return "Proficiente (≥40 pontos)"
            elif score >= 30:
                return "Adequado (30-39 pontos)"
            elif score >= 20:
                return "Básico (20-29 pontos)"
            else:
                return "Abaixo do Básico (<20 pontos)"
    
    # Aplicar classificações
    df_progresso['Estrato_Percentual'] = df_progresso['Progresso_Percentual'].apply(classificar_por_percentual)
    df_progresso['Estrato_Absoluto'] = df_progresso.apply(
        lambda row: classificar_por_absoluto(row['Progresso_Total_Acumulado'], row['Tipo_Avaliacao']), axis=1
    )
    df_progresso['Nivel_Desempenho_Final'] = df_progresso.apply(
        lambda row: classificar_desempenho_final(row['Score_Final'], row['Tipo_Avaliacao']), axis=1
    )
    
    return df_progresso

def analisar_estratos_por_dimensoes(df_progresso):
    """Analisa estratos por múltiplas dimensões"""
    
    analise = {}
    
    # Por número de fases
    for num_fases in sorted(df_progresso['Num_Fases'].unique()):
        subset = df_progresso[df_progresso['Num_Fases'] == num_fases]
        
        analise[f"fases_{num_fases}"] = {
            'total_estudantes': len(subset),
            'progresso_medio_pct': subset['Progresso_Percentual'].mean(),
            'progresso_mediano_pct': subset['Progresso_Percentual'].median(),
            'progresso_medio_abs': subset['Progresso_Total_Acumulado'].mean(),
            'score_inicial_medio': subset['Score_Inicial'].mean(),
            'score_final_medio': subset['Score_Final'].mean(),
            'pct_com_avanco': (subset['Progresso_Total_Acumulado'] > 0).mean() * 100,
            'pct_avanco_significativo': (subset['Progresso_Percentual'] >= 25).mean() * 100,
            'pct_declinio': (subset['Progresso_Total_Acumulado'] < 0).mean() * 100,
            'distribuicao_estratos': subset['Estrato_Percentual'].value_counts(normalize=True).mul(100).round(1).to_dict()
        }
    
    # Por trajetória
    for trajetoria in df_progresso['Trajetoria'].unique():
        subset = df_progresso[df_progresso['Trajetoria'] == trajetoria]
        
        analise[f"trajetoria_{trajetoria.lower().replace(' ', '_')}"] = {
            'total_estudantes': len(subset),
            'progresso_medio_pct': subset['Progresso_Percentual'].mean(),
            'score_inicial_medio': subset['Score_Inicial'].mean(),
            'score_final_medio': subset['Score_Final'].mean(),
            'distribuicao_estratos': subset['Estrato_Percentual'].value_counts(normalize=True).mul(100).round(1).to_dict()
        }
    
    # Por ano escolar (se disponível)
    if 'Ano' in df_progresso.columns and df_progresso['Ano'].notna().any():
        for ano in sorted(df_progresso['Ano'].dropna().unique()):
            subset = df_progresso[df_progresso['Ano'] == ano]
            
            analise[f"ano_{int(ano)}"] = {
                'total_estudantes': len(subset),
                'progresso_medio_pct': subset['Progresso_Percentual'].mean(),
                'pct_avanco_significativo': (subset['Progresso_Percentual'] >= 25).mean() * 100,
                'distribuicao_niveis_finais': subset['Nivel_Desempenho_Final'].value_counts(normalize=True).mul(100).round(1).to_dict()
            }
    
    return analise

def gerar_relatorio_estratos_longitudinais():
    """Gera relatório completo dos estratos longitudinais"""
    
    print("Iniciando análise de estratos longitudinais...")
    
    # Definir caminhos
    pasta_dashboard = Path("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Dashboard")
    pasta_saida = Path("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Modules/Analise2")
    
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
    
    # Calcular progressos longitudinais
    print("Calculando progressos longitudinais...")
    progresso_tde = calcular_progresso_longitudinal(dados_tde, 'TDE')
    progresso_vocab = calcular_progresso_longitudinal(dados_vocab, 'Vocabulário')
    
    print(f"Progressos TDE calculados: {len(progresso_tde)}")
    print(f"Progressos Vocabulário calculados: {len(progresso_vocab)}")
    
    # Classificar em estratos
    print("Classificando estratos...")
    progresso_tde_estratos = classificar_estratos_progresso(progresso_tde)
    progresso_vocab_estratos = classificar_estratos_progresso(progresso_vocab)
    
    # Análises dimensionais
    print("Analisando por dimensões...")
    analise_tde = analisar_estratos_por_dimensoes(progresso_tde_estratos)
    analise_vocab = analisar_estratos_por_dimensoes(progresso_vocab_estratos)
    
    # Gerar relatório
    arquivo_relatorio = pasta_saida / "relatorio_estratos_longitudinais.txt"
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RELATÓRIO DE ESTRATOS LONGITUDINAIS DE DESEMPENHO\n")
        f.write("Análise de Trajetórias Estudantis Através das Fases 2, 3 e 4\n")
        f.write("=" * 80 + "\n\n")
        
        # Resumo Executivo
        f.write("RESUMO EXECUTIVO\n")
        f.write("-" * 40 + "\n")
        f.write(f"Estudantes TDE analisados: {len(progresso_tde_estratos)}\n")
        f.write(f"Estudantes Vocabulário analisados: {len(progresso_vocab_estratos)}\n")
        f.write(f"Período: Fases 2 (2023), 3-4 (2024)\n\n")
        
        # === TDE ===
        f.write("ANÁLISE TDE - ESTRATOS LONGITUDINAIS\n")
        f.write("=" * 50 + "\n\n")
        
        if len(progresso_tde_estratos) > 0:
            # Distribuição geral
            f.write("DISTRIBUIÇÃO DE ESTRATOS DE PROGRESSO LONGITUDINAL\n")
            f.write("-" * 45 + "\n")
            dist_estratos = progresso_tde_estratos['Estrato_Percentual'].value_counts()
            total = len(progresso_tde_estratos)
            
            for estrato, count in dist_estratos.items():
                pct = (count / total) * 100
                f.write(f"{estrato}: {count} estudantes ({pct:.1f}%)\n")
            
            # Estatísticas gerais
            f.write(f"\nESTATÍSTICAS GERAIS:\n")
            f.write(f"Progresso médio acumulado: {progresso_tde_estratos['Progresso_Percentual'].mean():.1f}%\n")
            f.write(f"Progresso mediano: {progresso_tde_estratos['Progresso_Percentual'].median():.1f}%\n")
            f.write(f"Score inicial médio: {progresso_tde_estratos['Score_Inicial'].mean():.1f}\n")
            f.write(f"Score final médio: {progresso_tde_estratos['Score_Final'].mean():.1f}\n")
            
            # Percentuais de avanço
            avanco_positivo = (progresso_tde_estratos['Progresso_Total_Acumulado'] > 0).sum()
            avanco_significativo = (progresso_tde_estratos['Progresso_Percentual'] >= 25).sum()
            declinio = (progresso_tde_estratos['Progresso_Total_Acumulado'] < 0).sum()
            
            f.write(f"\nDISTRIBUIÇÃO DE DESEMPENHO:\n")
            f.write(f"Estudantes com avanço positivo: {avanco_positivo} ({avanco_positivo/total*100:.1f}%)\n")
            f.write(f"Estudantes com avanço ≥25%: {avanco_significativo} ({avanco_significativo/total*100:.1f}%)\n")
            f.write(f"Estudantes em declínio: {declinio} ({declinio/total*100:.1f}%)\n\n")
            
            # Análise por número de fases
            f.write("ANÁLISE POR NÚMERO DE FASES PARTICIPADAS:\n")
            f.write("-" * 40 + "\n")
            for key, dados in analise_tde.items():
                if key.startswith('fases_'):
                    num_fases = key.split('_')[1]
                    f.write(f"\n{num_fases} FASE(S):\n")
                    f.write(f"  Total: {dados['total_estudantes']} estudantes\n")
                    f.write(f"  Progresso médio: {dados['progresso_medio_pct']:.1f}%\n")
                    f.write(f"  Score inicial médio: {dados['score_inicial_medio']:.1f}\n")
                    f.write(f"  Score final médio: {dados['score_final_medio']:.1f}\n")
                    f.write(f"  % com avanço: {dados['pct_com_avanco']:.1f}%\n")
                    f.write(f"  % avanço significativo: {dados['pct_avanco_significativo']:.1f}%\n")
                    
                    f.write("  Distribuição de estratos:\n")
                    for estrato, pct in dados['distribuicao_estratos'].items():
                        f.write(f"    {estrato}: {pct:.1f}%\n")
            
            # Análise por desempenho final
            f.write("\nNÍVEIS DE DESEMPENHO FINAL:\n")
            f.write("-" * 30 + "\n")
            niveis_finais = progresso_tde_estratos['Nivel_Desempenho_Final'].value_counts()
            for nivel, count in niveis_finais.items():
                pct = (count / total) * 100
                f.write(f"{nivel}: {count} ({pct:.1f}%)\n")
        
        # === VOCABULÁRIO ===
        f.write("\n\nANÁLISE VOCABULÁRIO - ESTRATOS LONGITUDINAIS\n")
        f.write("=" * 50 + "\n\n")
        
        if len(progresso_vocab_estratos) > 0:
            # Distribuição geral
            f.write("DISTRIBUIÇÃO DE ESTRATOS DE PROGRESSO LONGITUDINAL\n")
            f.write("-" * 45 + "\n")
            dist_estratos = progresso_vocab_estratos['Estrato_Percentual'].value_counts()
            total = len(progresso_vocab_estratos)
            
            for estrato, count in dist_estratos.items():
                pct = (count / total) * 100
                f.write(f"{estrato}: {count} estudantes ({pct:.1f}%)\n")
            
            # Estatísticas gerais
            f.write(f"\nESTATÍSTICAS GERAIS:\n")
            f.write(f"Progresso médio acumulado: {progresso_vocab_estratos['Progresso_Percentual'].mean():.1f}%\n")
            f.write(f"Progresso mediano: {progresso_vocab_estratos['Progresso_Percentual'].median():.1f}%\n")
            f.write(f"Score inicial médio: {progresso_vocab_estratos['Score_Inicial'].mean():.1f}\n")
            f.write(f"Score final médio: {progresso_vocab_estratos['Score_Final'].mean():.1f}\n")
            
            # Percentuais de avanço
            avanco_positivo = (progresso_vocab_estratos['Progresso_Total_Acumulado'] > 0).sum()
            avanco_significativo = (progresso_vocab_estratos['Progresso_Percentual'] >= 25).sum()
            declinio = (progresso_vocab_estratos['Progresso_Total_Acumulado'] < 0).sum()
            
            f.write(f"\nDISTRIBUIÇÃO DE DESEMPENHO:\n")
            f.write(f"Estudantes com avanço positivo: {avanco_positivo} ({avanco_positivo/total*100:.1f}%)\n")
            f.write(f"Estudantes com avanço ≥25%: {avanco_significativo} ({avanco_significativo/total*100:.1f}%)\n")
            f.write(f"Estudantes em declínio: {declinio} ({declinio/total*100:.1f}%)\n\n")
            
            # Análise por número de fases
            f.write("ANÁLISE POR NÚMERO DE FASES PARTICIPADAS:\n")
            f.write("-" * 40 + "\n")
            for key, dados in analise_vocab.items():
                if key.startswith('fases_'):
                    num_fases = key.split('_')[1]
                    f.write(f"\n{num_fases} FASE(S):\n")
                    f.write(f"  Total: {dados['total_estudantes']} estudantes\n")
                    f.write(f"  Progresso médio: {dados['progresso_medio_pct']:.1f}%\n")
                    f.write(f"  Score inicial médio: {dados['score_inicial_medio']:.1f}\n")
                    f.write(f"  Score final médio: {dados['score_final_medio']:.1f}\n")
                    f.write(f"  % com avanço: {dados['pct_com_avanco']:.1f}%\n")
                    f.write(f"  % avanço significativo: {dados['pct_avanco_significativo']:.1f}%\n")
                    
                    f.write("  Distribuição de estratos:\n")
                    for estrato, pct in dados['distribuicao_estratos'].items():
                        f.write(f"    {estrato}: {pct:.1f}%\n")
            
            # Análise por desempenho final
            f.write("\nNÍVEIS DE DESEMPENHO FINAL:\n")
            f.write("-" * 30 + "\n")
            niveis_finais = progresso_vocab_estratos['Nivel_Desempenho_Final'].value_counts()
            for nivel, count in niveis_finais.items():
                pct = (count / total) * 100
                f.write(f"{nivel}: {count} ({pct:.1f}%)\n")
        
        # === ANÁLISE COMPARATIVA ===
        f.write("\n\nANÁLISE COMPARATIVA TDE vs VOCABULÁRIO\n")
        f.write("=" * 50 + "\n\n")
        
        if len(progresso_tde_estratos) > 0 and len(progresso_vocab_estratos) > 0:
            f.write("COMPARAÇÃO DE AVANÇOS SIGNIFICATIVOS (≥25%):\n")
            f.write("-" * 40 + "\n")
            
            tde_avanco_sig = (progresso_tde_estratos['Progresso_Percentual'] >= 25).sum()
            vocab_avanco_sig = (progresso_vocab_estratos['Progresso_Percentual'] >= 25).sum()
            
            f.write(f"TDE: {tde_avanco_sig} de {len(progresso_tde_estratos)} ({tde_avanco_sig/len(progresso_tde_estratos)*100:.1f}%)\n")
            f.write(f"Vocabulário: {vocab_avanco_sig} de {len(progresso_vocab_estratos)} ({vocab_avanco_sig/len(progresso_vocab_estratos)*100:.1f}%)\n\n")
            
            f.write("COMPARAÇÃO DE DECLÍNIOS:\n")
            f.write("-" * 25 + "\n")
            
            tde_declinio = (progresso_tde_estratos['Progresso_Total_Acumulado'] < 0).sum()
            vocab_declinio = (progresso_vocab_estratos['Progresso_Total_Acumulado'] < 0).sum()
            
            f.write(f"TDE: {tde_declinio} de {len(progresso_tde_estratos)} ({tde_declinio/len(progresso_tde_estratos)*100:.1f}%)\n")
            f.write(f"Vocabulário: {vocab_declinio} de {len(progresso_vocab_estratos)} ({vocab_declinio/len(progresso_vocab_estratos)*100:.1f}%)\n\n")
            
            # Progresso médio
            f.write("PROGRESSOS MÉDIOS ACUMULADOS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"TDE: {progresso_tde_estratos['Progresso_Percentual'].mean():.1f}%\n")
            f.write(f"Vocabulário: {progresso_vocab_estratos['Progresso_Percentual'].mean():.1f}%\n\n")
        
        # === INSIGHTS E RECOMENDAÇÕES ===
        f.write("INSIGHTS E RECOMENDAÇÕES\n")
        f.write("=" * 30 + "\n\n")
        
        # Calcular insights específicos
        if len(progresso_tde_estratos) > 0:
            tde_alta_performance = (progresso_tde_estratos['Progresso_Percentual'] >= 50).sum()
            tde_baixa_performance = (progresso_tde_estratos['Progresso_Percentual'] < -15).sum()
            
            f.write("TDE:\n")
            f.write(f"• Alta performance longitudinal: {tde_alta_performance} estudantes ({tde_alta_performance/len(progresso_tde_estratos)*100:.1f}%)\n")
            f.write(f"• Baixa performance longitudinal: {tde_baixa_performance} estudantes ({tde_baixa_performance/len(progresso_tde_estratos)*100:.1f}%)\n")
            
        if len(progresso_vocab_estratos) > 0:
            vocab_alta_performance = (progresso_vocab_estratos['Progresso_Percentual'] >= 50).sum()
            vocab_baixa_performance = (progresso_vocab_estratos['Progresso_Percentual'] < -15).sum()
            
            f.write(f"\nVocabulário:\n")
            f.write(f"• Alta performance longitudinal: {vocab_alta_performance} estudantes ({vocab_alta_performance/len(progresso_vocab_estratos)*100:.1f}%)\n")
            f.write(f"• Baixa performance longitudinal: {vocab_baixa_performance} estudantes ({vocab_baixa_performance/len(progresso_vocab_estratos)*100:.1f}%)\n")
        
        f.write(f"\nRecomendações Estratégicas:\n")
        f.write("1. Foco em intervenções para estudantes em declínio severo\n")
        f.write("2. Análise das estratégias dos estudantes de alta performance\n")
        f.write("3. Implementação de programas de acompanhamento longitudinal\n")
        f.write("4. Investigação dos fatores associados às diferentes trajetórias\n")
        f.write("5. Desenvolvimento de indicadores de alerta precoce\n")
        
        f.write(f"\n\nRelatório gerado: {pd.Timestamp.now()}\n")
        f.write("=" * 80 + "\n")
    
    # Salvar dados detalhados
    arquivo_detalhado_tde = pasta_saida / "dados_estratos_tde_longitudinal.csv"
    arquivo_detalhado_vocab = pasta_saida / "dados_estratos_vocabulario_longitudinal.csv"
    
    progresso_tde_estratos.to_csv(arquivo_detalhado_tde, index=False, encoding='utf-8')
    progresso_vocab_estratos.to_csv(arquivo_detalhado_vocab, index=False, encoding='utf-8')
    
    print(f"\nRelatório gerado: {arquivo_relatorio}")
    print(f"Dados TDE detalhados: {arquivo_detalhado_tde}")
    print(f"Dados Vocabulário detalhados: {arquivo_detalhado_vocab}")
    print("\nAnálise de estratos longitudinais concluída!")

if __name__ == "__main__":
    gerar_relatorio_estratos_longitudinais()