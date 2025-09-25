#!/usr/bin/env python3
"""
Script de Limpeza Completa dos Datasets Consolidados
===================================================

Problemas identificados:
1. "EMEB EMEB PROFESSOR RICARDO VIEIRA DE LIMA" - duplicação no nome
2. Diferenças de capitalização (Padre vs PADRE, professora vs PROFESSORA)  
3. Header "Escola" não removido
4. Inconsistências entre datasets TDE e Vocabulário

Soluções:
- Normalização de capitalização
- Remoção de duplicações
- Padronização de nomes
"""

import pandas as pd
import re

def criar_mapeamento_limpeza():
    """Cria mapeamento completo para limpeza dos nomes das escolas"""
    
    mapeamento = {
        # Remover header
        "Escola": None,  # Será removido
        
        # Corrigir duplicação EMEB EMEB
        "EMEB EMEB PROFESSOR RICARDO VIEIRA DE LIMA": "EMEB PROFESSOR RICARDO VIEIRA DE LIMA",
        
        # Padronizar capitalização - PADRE ANCHIETA
        "EMEB Padre anchieta": "EMEB PADRE ANCHIETA",
        
        # Padronizar capitalização - PROFESSORA MARIA QUEIROZ FERRO  
        "EMEB professora Maria Queiroz Ferro": "EMEB PROFESSORA MARIA QUEIROZ FERRO",
        
        # Padronizar capitalização - PADRE JOSÉ DOS SANTOS MOUSINHO
        "EMEF Padre José dos Santos Mousinho": "EMEF PADRE JOSÉ DOS SANTOS MOUSINHO"
    }
    
    return mapeamento

def limpar_dataset(arquivo_path: str, backup: bool = True):
    """Limpa um dataset aplicando as correções de nomes de escolas"""
    
    print(f"🔧 Processando: {arquivo_path}")
    
    # Ler dataset
    df = pd.read_csv(arquivo_path)
    
    # Fazer backup se solicitado
    if backup:
        backup_path = f"{arquivo_path}.backup_limpeza"
        df.to_csv(backup_path, index=False)
        print(f"   💾 Backup criado: {backup_path}")
    
    # Aplicar mapeamento
    mapeamento = criar_mapeamento_limpeza()
    correcoes_aplicadas = 0
    
    for nome_antigo, nome_novo in mapeamento.items():
        if nome_novo is None:  # Remover linhas com header
            mascara = df['Escola'] == nome_antigo
            if mascara.any():
                df = df[~mascara]  # Remover linhas
                print(f"   🗑️  Removido header: {nome_antigo} ({mascara.sum()} linhas)")
                correcoes_aplicadas += mascara.sum()
        else:  # Substituir nomes
            mascara = df['Escola'] == nome_antigo
            if mascara.any():
                df.loc[mascara, 'Escola'] = nome_novo
                print(f"   ✅ {nome_antigo} → {nome_novo} ({mascara.sum()} registros)")
                correcoes_aplicadas += mascara.sum()
    
    # Salvar dataset limpo
    if correcoes_aplicadas > 0:
        df.to_csv(arquivo_path, index=False)
        print(f"   ✅ Dataset limpo salvo ({correcoes_aplicadas} correções)")
    else:
        print(f"   ℹ️  Nenhuma correção necessária")
    
    return df, correcoes_aplicadas

def verificar_escolas_unicas(arquivo_path: str):
    """Verifica escolas únicas após limpeza"""
    
    df = pd.read_csv(arquivo_path)
    escolas_unicas = sorted(df['Escola'].dropna().unique())
    
    print(f"\n📊 ESCOLAS ÚNICAS em {arquivo_path.split('/')[-1]}:")
    for i, escola in enumerate(escolas_unicas, 1):
        print(f"   {i:2d}. {escola}")
    
    return escolas_unicas

def main():
    """Função principal de limpeza"""
    
    print("🚀 INICIANDO LIMPEZA COMPLETA DOS DATASETS")
    print("=" * 60)
    
    # Caminhos dos arquivos
    dashboard_path = "/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Dashboard"
    arquivos = [
        f"{dashboard_path}/TDE_consolidado_fases_2_3_4.csv",
        f"{dashboard_path}/vocabulario_consolidado_fases_2_3_4.csv"
    ]
    
    total_correcoes = 0
    
    # Processar cada arquivo
    for arquivo in arquivos:
        df, correcoes = limpar_dataset(arquivo)
        total_correcoes += correcoes
        print()
    
    print(f"📈 RESUMO FINAL:")
    print(f"   • Total de correções aplicadas: {total_correcoes}")
    print()
    
    # Verificar resultado final
    print("🔍 VERIFICAÇÃO FINAL:")
    print("=" * 30)
    
    for arquivo in arquivos:
        escolas = verificar_escolas_unicas(arquivo)
        print(f"   → {len(escolas)} escolas únicas")
        print()
    
    print("✅ LIMPEZA CONCLUÍDA!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Verificar dashboard para confirmar correções")
    print("2. Card 'Escolas' deve mostrar número correto")
    print("3. Drill-down deve funcionar sem duplicações")

if __name__ == "__main__":
    main()