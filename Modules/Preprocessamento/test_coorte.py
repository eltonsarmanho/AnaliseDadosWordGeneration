"""
Script de teste para validar a implementação de coortes.
Verifica se a coluna Coorte_Origem está sendo criada corretamente
e se acompanha o ID_Unico ao longo das fases.
"""

import pandas as pd
from data_loader import get_datasets

def test_coorte_implementation():
    """Testa se a implementação de coortes está correta"""
    print("=" * 80)
    print("TESTE: Implementação de Coortes")
    print("=" * 80)
    
    # Carregar dados
    tde, vocab = get_datasets()
    
    # Teste 1: Verificar se coluna existe
    print("\n✓ TESTE 1: Verificar se coluna Coorte_Origem existe")
    assert 'Coorte_Origem' in tde.columns, "❌ Coluna Coorte_Origem não encontrada no TDE"
    assert 'Coorte_Origem' in vocab.columns, "❌ Coluna Coorte_Origem não encontrada no Vocabulário"
    print("  ✅ Coluna Coorte_Origem encontrada em ambos os datasets")
    
    # Teste 2: Verificar valores válidos
    print("\n✓ TESTE 2: Verificar valores de coorte")
    coortes_tde = tde['Coorte_Origem'].dropna().unique()
    coortes_vocab = vocab['Coorte_Origem'].dropna().unique()
    print(f"  Coortes TDE: {sorted(coortes_tde)}")
    print(f"  Coortes Vocabulário: {sorted(coortes_vocab)}")
    
    valores_esperados = {'Coorte 1', 'Coorte 2', 'Coorte 3'}
    assert set(coortes_tde).issubset(valores_esperados), f"❌ Valores inesperados no TDE: {set(coortes_tde) - valores_esperados}"
    assert set(coortes_vocab).issubset(valores_esperados), f"❌ Valores inesperados no Vocab: {set(coortes_vocab) - valores_esperados}"
    print("  ✅ Todos os valores de coorte são válidos")
    
    # Teste 3: Verificar consistência por ID_Unico
    print("\n✓ TESTE 3: Verificar consistência da coorte por ID_Unico")
    # Cada ID_Unico deve ter sempre a mesma coorte em todas as fases
    for df_name, df in [('TDE', tde), ('Vocabulário', vocab)]:
        inconsistencias = []
        for id_unico in df['ID_Unico'].unique():
            coortes_aluno = df[df['ID_Unico'] == id_unico]['Coorte_Origem'].unique()
            if len(coortes_aluno) > 1:
                inconsistencias.append((id_unico, coortes_aluno))
        
        if inconsistencias:
            print(f"  ❌ {df_name}: Encontradas {len(inconsistencias)} inconsistências:")
            for id_u, coortes in inconsistencias[:5]:  # Mostrar apenas 5 primeiros
                print(f"     ID {id_u}: {coortes}")
        else:
            print(f"  ✅ {df_name}: Todas as coortes são consistentes por ID_Unico")
    
    # Teste 4: Verificar mapeamento fase → coorte
    print("\n✓ TESTE 4: Verificar mapeamento fase inicial → coorte")
    for df_name, df in [('TDE', tde), ('Vocabulário', vocab)]:
        # Para cada aluno, verificar se a coorte corresponde à sua primeira fase
        primeira_fase = df.groupby('ID_Unico')['Fase'].min()
        coorte_por_id = df.groupby('ID_Unico')['Coorte_Origem'].first()
        
        erros = []
        for id_unico in primeira_fase.index:
            fase = primeira_fase[id_unico]
            coorte = coorte_por_id[id_unico]
            
            # Mapear esperado
            if fase == 2:
                coorte_esperada = 'Coorte 1'
            elif fase == 3:
                coorte_esperada = 'Coorte 2'
            elif fase == 4:
                coorte_esperada = 'Coorte 3'
            else:
                coorte_esperada = None
            
            if coorte != coorte_esperada:
                erros.append((id_unico, fase, coorte, coorte_esperada))
        
        if erros:
            print(f"  ❌ {df_name}: Encontrados {len(erros)} erros no mapeamento:")
            for id_u, fase, coorte, esperada in erros[:5]:
                print(f"     ID {id_u}: Fase {fase} → {coorte} (esperado: {esperada})")
        else:
            print(f"  ✅ {df_name}: Mapeamento fase → coorte correto para todos os alunos")
    
    # Teste 5: Estatísticas gerais
    print("\n✓ TESTE 5: Estatísticas de distribuição")
    for df_name, df in [('TDE', tde), ('Vocabulário', vocab)]:
        print(f"\n  {df_name}:")
        print(f"    Total de alunos únicos: {df['ID_Unico'].nunique()}")
        for coorte in sorted(df['Coorte_Origem'].dropna().unique()):
            n_alunos = df[df['Coorte_Origem'] == coorte]['ID_Unico'].nunique()
            print(f"    {coorte}: {n_alunos} alunos")
    
    # Teste 6: Validar acompanhamento longitudinal
    print("\n✓ TESTE 6: Validar acompanhamento longitudinal")
    for df_name, df in [('TDE', tde), ('Vocabulário', vocab)]:
        # Alunos da Coorte 1 devem ter registros nas Fases 2, 3 e 4 (idealmente)
        coorte1 = df[df['Coorte_Origem'] == 'Coorte 1']['ID_Unico'].unique()
        if len(coorte1) > 0:
            # Verificar quantos alunos da Coorte 1 têm dados em múltiplas fases
            alunos_multiplas_fases = 0
            for id_u in coorte1:
                fases_aluno = df[df['ID_Unico'] == id_u]['Fase'].nunique()
                if fases_aluno > 1:
                    alunos_multiplas_fases += 1
            
            percentual = (alunos_multiplas_fases / len(coorte1)) * 100
            print(f"  {df_name} - Coorte 1:")
            print(f"    {alunos_multiplas_fases}/{len(coorte1)} alunos ({percentual:.1f}%) têm dados em múltiplas fases")
    
    print("\n" + "=" * 80)
    print("✅ TODOS OS TESTES CONCLUÍDOS")
    print("=" * 80)

if __name__ == "__main__":
    test_coorte_implementation()
