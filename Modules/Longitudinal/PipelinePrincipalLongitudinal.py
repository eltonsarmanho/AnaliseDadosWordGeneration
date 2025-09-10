#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE PRINCIPAL - ANÁLISE LONGITUDINAL WORDGEN
Executa análise completa longitudinal das Fases 2, 3 e 4 para TDE e Vocabulário

Este script executa:
1. Pipeline de dados longitudinais TDE
2. Pipeline de dados longitudinais Vocabulário  
3. Geração do relatório visual HTML

Autor: Sistema de Análise WordGen
Data: 2024
"""

import sys
import pathlib
from datetime import datetime

# Adicionar o diretório base ao path
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
sys.path.append(str(BASE_DIR))

# Imports dos módulos longitudinais
from Modules.Longitudinal.TDE.PipelineDataLongitudinalTDE import PipelineDataLongitudinalTDE
from Modules.Longitudinal.Vocabulario.PipelineDataLongitudinalVocabulario import PipelineDataLongitudinalVocabulario
from Modules.Longitudinal.RelatorioVisualLongitudinal import main as gerar_relatorio

def executar_pipeline_completo():
    """Executa o pipeline completo de análise longitudinal"""
    
    print("🚀 INICIANDO ANÁLISE LONGITUDINAL WORDGEN")
    print("="*60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print("📊 Fases analisadas: 2, 3 e 4")
    print("🎯 Foco: Acertos e melhorias (não evidenciando erros)")
    print("="*60)
    
    try:
        # ETAPA 1: Pipeline TDE
        print("\n🔄 ETAPA 1: Processando dados longitudinais TDE...")
        print("-" * 50)
        
        pipeline_tde = PipelineDataLongitudinalTDE()
        sucesso_tde = pipeline_tde.executar_pipeline()
        
        if sucesso_tde:
            print("✅ Pipeline TDE concluído com sucesso!")
        else:
            print("⚠️ Pipeline TDE concluído com avisos")
        
        # ETAPA 2: Pipeline Vocabulário
        print("\n🔄 ETAPA 2: Processando dados longitudinais Vocabulário...")
        print("-" * 50)
        
        pipeline_vocab = PipelineDataLongitudinalVocabulario()
        sucesso_vocab = pipeline_vocab.executar_pipeline()
        
        if sucesso_vocab:
            print("✅ Pipeline Vocabulário concluído com sucesso!")
        else:
            print("⚠️ Pipeline Vocabulário concluído com avisos")
        
        # ETAPA 3: Relatório Visual
        print("\n🎨 ETAPA 3: Gerando Relatório Visual HTML...")
        print("-" * 50)
        
        sucesso_relatorio = gerar_relatorio()
        
        if sucesso_relatorio:
            print("✅ Relatório Visual gerado com sucesso!")
        else:
            print("❌ Erro na geração do relatório visual")
        
        # RESUMO FINAL
        print("\n" + "="*60)
        print("🎉 ANÁLISE LONGITUDINAL CONCLUÍDA!")
        print("="*60)
        
        print(f"\n📋 RESUMO DA EXECUÇÃO:")
        print(f"   • Pipeline TDE: {'✅ Sucesso' if sucesso_tde else '⚠️ Avisos'}")
        print(f"   • Pipeline Vocabulário: {'✅ Sucesso' if sucesso_vocab else '⚠️ Avisos'}")
        print(f"   • Relatório Visual: {'✅ Sucesso' if sucesso_relatorio else '❌ Erro'}")
        
        print(f"\n📁 ARQUIVOS GERADOS:")
        print(f"   • Dados TDE: Modules/Longitudinal/Data/dados_longitudinais_TDE.csv")
        print(f"   • Dados Vocabulário: Modules/Longitudinal/Data/dados_longitudinais_Vocabulario.csv")
        print(f"   • Resumo TDE: Modules/Longitudinal/Data/resumo_longitudinal_TDE.json")
        print(f"   • Resumo Vocabulário: Modules/Longitudinal/Data/resumo_longitudinal_Vocabulario.json")
        print(f"   • Relatório HTML: Modules/Longitudinal/Data/relatorio_visual_longitudinal.html")
        print(f"   • Figuras: Modules/Longitudinal/Data/figures/")
        
        print(f"\n🌐 COMO VISUALIZAR:")
        print(f"   1. Abra o arquivo 'relatorio_visual_longitudinal.html' em um navegador")
        print(f"   2. O relatório contém análises interativas e visualizações")
        print(f"   3. Foco nos acertos e melhorias dos estudantes")
        
        if sucesso_tde and sucesso_vocab and sucesso_relatorio:
            print(f"\n🎯 STATUS FINAL: ✅ SUCESSO TOTAL")
            return True
        else:
            print(f"\n🎯 STATUS FINAL: ⚠️ CONCLUÍDO COM AVISOS")
            return True
            
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        print(f"🔧 Verifique os dados das Fases 2, 3 e 4")
        return False

def main():
    """Função principal"""
    return executar_pipeline_completo()

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
