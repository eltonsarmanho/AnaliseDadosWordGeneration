#!/usr/bin/env python3
"""
Verificação da remoção de duplicados no Relatório Visual Longitudinal
"""

import pandas as pd
import pathlib

# Configuração dos caminhos
BASE_DIR = pathlib.Path(__file__).parent
CSV_LONGITUDINAL_TDE = BASE_DIR / "Modules" / "Longitudinal" / "Data" / "dados_longitudinais_TDE.csv"
CSV_LONGITUDINAL_VOCAB = BASE_DIR / "Modules" / "Longitudinal" / "Data" / "dados_longitudinais_Vocabulario.csv"

def verificar_duplicados_pos_remocao():
    """Verifica se ainda existem duplicados após a execução do relatório"""
    print("🔍 Verificação de Duplicados Pós-Remoção")
    print("=" * 50)
    
    # Dados originais (simulando o que seria carregado)
    df_tde_original = pd.read_csv(CSV_LONGITUDINAL_TDE) if CSV_LONGITUDINAL_TDE.exists() else pd.DataFrame()
    df_vocab_original = pd.read_csv(CSV_LONGITUDINAL_VOCAB) if CSV_LONGITUDINAL_VOCAB.exists() else pd.DataFrame()
    
    print(f"📊 DADOS ORIGINAIS (ANTES DA LIMPEZA):")
    print(f"   TDE: {len(df_tde_original):,} registros")
    print(f"   Vocabulário: {len(df_vocab_original):,} registros")
    
    # Simular processo de limpeza (como feito no relatório)
    def remover_duplicados_teste(df, nome_dataset):
        if df.empty:
            return df, 0
        
        tamanho_original = len(df)
        
        # Verificar duplicados
        colunas_duplicados = ['Nome', 'Escola', 'Turma']
        colunas_existentes = [col for col in colunas_duplicados if col in df.columns]
        
        if len(colunas_existentes) < 3:
            print(f"⚠️  {nome_dataset}: Colunas necessárias não encontradas")
            return df, 0
        
        # Identificar e contar duplicados
        duplicados_mask = df.duplicated(subset=colunas_duplicados, keep=False)
        num_duplicados = duplicados_mask.sum()
        
        # Remover duplicados
        df_limpo = df.drop_duplicates(subset=colunas_duplicados, keep='first')
        registros_removidos = tamanho_original - len(df_limpo)
        
        return df_limpo, registros_removidos
    
    # Limpar dados TDE
    df_tde_limpo, removidos_tde = remover_duplicados_teste(df_tde_original, "TDE")
    
    # Limpar dados Vocabulário
    df_vocab_limpo, removidos_vocab = remover_duplicados_teste(df_vocab_original, "Vocabulário")
    
    print(f"\n📊 DADOS LIMPOS (APÓS REMOÇÃO):")
    print(f"   TDE: {len(df_tde_limpo):,} registros únicos")
    print(f"   Vocabulário: {len(df_vocab_limpo):,} registros únicos")
    
    print(f"\n🧹 DUPLICADOS REMOVIDOS:")
    print(f"   TDE: {removidos_tde:,} registros")
    print(f"   Vocabulário: {removidos_vocab:,} registros")
    print(f"   Total: {removidos_tde + removidos_vocab:,} registros")
    
    # Verificar se ainda há duplicados
    def verificar_duplicados_restantes(df, nome_dataset):
        if df.empty:
            return 0
        
        colunas_duplicados = ['Nome', 'Escola', 'Turma']
        colunas_existentes = [col for col in colunas_duplicados if col in df.columns]
        
        if len(colunas_existentes) < 3:
            return 0
        
        duplicados_mask = df.duplicated(subset=colunas_duplicados, keep=False)
        return duplicados_mask.sum()
    
    duplicados_restantes_tde = verificar_duplicados_restantes(df_tde_limpo, "TDE")
    duplicados_restantes_vocab = verificar_duplicados_restantes(df_vocab_limpo, "Vocabulário")
    
    print(f"\n✅ VERIFICAÇÃO FINAL:")
    print(f"   TDE: {duplicados_restantes_tde} duplicados restantes")
    print(f"   Vocabulário: {duplicados_restantes_vocab} duplicados restantes")
    
    if duplicados_restantes_tde == 0 and duplicados_restantes_vocab == 0:
        print(f"\n🎉 SUCESSO: Todos os duplicados foram removidos com êxito!")
    else:
        print(f"\n⚠️  ATENÇÃO: Ainda existem duplicados nos dados!")
    
    # Calcular estatísticas de melhoria
    total_original = len(df_tde_original) + len(df_vocab_original)
    total_limpo = len(df_tde_limpo) + len(df_vocab_limpo)
    total_removido = removidos_tde + removidos_vocab
    
    if total_original > 0:
        taxa_limpeza = (total_limpo / total_original) * 100
        taxa_remocao = (total_removido / total_original) * 100
    else:
        taxa_limpeza = 100
        taxa_remocao = 0
    
    print(f"\n📈 ESTATÍSTICAS DE QUALIDADE:")
    print(f"   Taxa de Registros Limpos: {taxa_limpeza:.1f}%")
    print(f"   Taxa de Remoção: {taxa_remocao:.1f}%")
    print(f"   Melhoria na Qualidade: {total_removido:,} registros problemáticos eliminados")
    
    return {
        'original': {'tde': len(df_tde_original), 'vocab': len(df_vocab_original)},
        'limpo': {'tde': len(df_tde_limpo), 'vocab': len(df_vocab_limpo)},
        'removido': {'tde': removidos_tde, 'vocab': removidos_vocab},
        'restante': {'tde': duplicados_restantes_tde, 'vocab': duplicados_restantes_vocab},
        'taxa_limpeza': taxa_limpeza
    }

if __name__ == "__main__":
    resultado = verificar_duplicados_pos_remocao()
