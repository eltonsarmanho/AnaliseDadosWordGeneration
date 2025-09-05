import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import pathlib
import os
import json

# Configurar estilo dos gráficos
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

class AnaliseVisualFase2:
    def __init__(self):
        self.base_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
        self.data_dir = self.base_dir / "Data"
        self.fig_dir = self.data_dir / "figures"
        
        # Caminhos dos arquivos
        self.arquivo_pre = self.data_dir / "Fase2/Pre/Avaliação de vocabulário - RelaçãoCompletaAlunos.xlsx"
        self.arquivo_pos = self.data_dir / "Fase2/Pos/Avaliação de vocabulário - RelaçãoCompletaAlunos (São Sebastião, WordGen, fase 2 - 2023.2).xlsx"
        self.arquivo_respostas = self.data_dir / "RespostaVocabulario.json"
        
        # Garantir que existe diretório de figuras
        os.makedirs(self.fig_dir, exist_ok=True)
        
        self.carregar_dados()
    
    def converter_valor_questao(self, valor):
        """Converte valores das questões para sistema numérico"""
        if pd.isna(valor):
            return np.nan
        
        valor_str = str(valor).strip().upper()
        
        if valor_str in ['0', '0.0']:
            return 0  # Erro
        elif valor_str in ['1', '1.0']:
            return 1  # Acerto parcial
        elif valor_str in ['2', '2.0']:
            return 2  # Acerto total
        elif valor_str in ['D', 'M']:
            return np.nan  # Neutro
        else:
            try:
                num_valor = float(valor_str)
                if num_valor == 0:
                    return 0
                elif num_valor == 1:
                    return 1
                elif num_valor == 2:
                    return 2
                else:
                    return np.nan
            except:
                return np.nan
    
    def classificar_grupo_etario(self, turma):
        """Classifica estudantes em grupos etários"""
        turma_str = str(turma).upper()
        
        if '6º' in turma_str or '6°' in turma_str or '7º' in turma_str or '7°' in turma_str:
            return "6º/7º anos"
        elif '8º' in turma_str or '8°' in turma_str or '9º' in turma_str or '9°' in turma_str:
            return "8º/9º anos"
        else:
            return "Indefinido"
    
    def carregar_mapeamento_palavras(self):
        """Carrega o mapeamento de questões para palavras"""
        try:
            with open(self.arquivo_respostas, 'r', encoding='utf-8') as f:
                dados_respostas = json.load(f)
            
            mapeamento = {}
            for item in dados_respostas:
                for questao, info in item.items():
                    mapeamento[questao] = info['Palavra Trabalhada']
            
            return mapeamento
        except Exception as e:
            print(f"Erro ao carregar mapeamento de palavras: {e}")
            return {}
    
    def carregar_dados(self):
        """Carrega e prepara os dados"""
        print("Carregando dados da Fase 2...")
        
        # Carregar dados
        self.df_pre = pd.read_excel(self.arquivo_pre)
        self.df_pos = pd.read_excel(self.arquivo_pos)
        
        # Carregar mapeamento de palavras
        self.mapeamento_palavras = self.carregar_mapeamento_palavras()
        
        # Colunas de questões
        self.colunas_q = [f'Q{i}' for i in range(1, 51)]
        
        # Aplicar conversão de valores
        for col in self.colunas_q:
            if col in self.df_pre.columns:
                self.df_pre[col] = self.df_pre[col].apply(self.converter_valor_questao)
            if col in self.df_pos.columns:
                self.df_pos[col] = self.df_pos[col].apply(self.converter_valor_questao)
        
        # Adicionar grupos etários
        self.df_pre['GrupoEtario'] = self.df_pre['Turma'].apply(self.classificar_grupo_etario)
        self.df_pos['GrupoEtario'] = self.df_pos['Turma'].apply(self.classificar_grupo_etario)
        
        # Criar identificador único
        self.df_pre['ID_Unico'] = self.df_pre['Nome'].astype(str) + "_" + self.df_pre['Turma'].astype(str)
        self.df_pos['ID_Unico'] = self.df_pos['Nome'].astype(str) + "_" + self.df_pos['Turma'].astype(str)
        
        self.preparar_dados_limpos()
    
    def preparar_dados_limpos(self):
        """Limpa e filtra os dados"""
        # Filtrar apenas estudantes que participaram de ambos os testes
        ids_pre = set(self.df_pre['ID_Unico'])
        ids_pos = set(self.df_pos['ID_Unico'])
        ids_comuns = ids_pre.intersection(ids_pos)
        
        df_pre_filtrado = self.df_pre[self.df_pre['ID_Unico'].isin(ids_comuns)].copy()
        df_pos_filtrado = self.df_pos[self.df_pos['ID_Unico'].isin(ids_comuns)].copy()
        
        # Função para verificar questões válidas
        def tem_questoes_validas(row):
            valores_validos = 0
            for col in self.colunas_q:
                if col in row.index and not pd.isna(row[col]):
                    valores_validos += 1
            return valores_validos >= 40  # Pelo menos 80% das questões
        
        # Aplicar filtro
        mask_pre = df_pre_filtrado.apply(tem_questoes_validas, axis=1)
        mask_pos = df_pos_filtrado.apply(tem_questoes_validas, axis=1)
        
        df_pre_filtrado = df_pre_filtrado[mask_pre]
        df_pos_filtrado = df_pos_filtrado[mask_pos]
        
        # Filtrar novamente por IDs comuns após limpeza
        ids_pre_limpo = set(df_pre_filtrado['ID_Unico'])
        ids_pos_limpo = set(df_pos_filtrado['ID_Unico'])
        ids_finais = ids_pre_limpo.intersection(ids_pos_limpo)
        
        self.df_pre_final = df_pre_filtrado[df_pre_filtrado['ID_Unico'].isin(ids_finais)]
        self.df_pos_final = df_pos_filtrado[df_pos_filtrado['ID_Unico'].isin(ids_finais)]
        
        print(f"Dados limpos: {len(self.df_pre_final)} estudantes")
        
        # Calcular scores
        self.calcular_scores()
    
    def calcular_scores(self):
        """Calcula scores por estudante"""
        scores_data = []
        
        for _, row_pre in self.df_pre_final.iterrows():
            id_unico = row_pre['ID_Unico']
            grupo = row_pre['GrupoEtario']
            
            # Encontrar correspondente no pós-teste
            pos_rows = self.df_pos_final[self.df_pos_final['ID_Unico'] == id_unico]
            if len(pos_rows) == 0:
                continue
                
            row_pos = pos_rows.iloc[0]
            
            # Calcular scores
            score_pre = 0
            score_pos = 0
            questoes_validas = 0
            
            for col in self.colunas_q:
                if col in self.df_pre_final.columns and col in self.df_pos_final.columns:
                    val_pre = row_pre[col]
                    val_pos = row_pos[col]
                    
                    if not pd.isna(val_pre) and not pd.isna(val_pos):
                        score_pre += val_pre
                        score_pos += val_pos
                        questoes_validas += 1
            
            if questoes_validas >= 40:  # Pelo menos 80% das questões
                scores_data.append({
                    'ID_Unico': id_unico,
                    'GrupoEtario': grupo,
                    'Score_Pre': score_pre,
                    'Score_Pos': score_pos,
                    'Delta': score_pos - score_pre,
                    'N_Questoes': questoes_validas
                })
        
        self.scores_df = pd.DataFrame(scores_data)
    
    def plot_distribuicao_scores(self, salvar=True):
        """Gráfico da distribuição de scores"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Cores para os grupos
        cores = {'6º/7º anos': '#2E86AB', '8º/9º anos': '#A23B72'}
        
        # 1. Distribuição geral de scores pré-teste
        ax = axes[0, 0]
        for grupo in ['6º/7º anos', '8º/9º anos']:
            data = self.scores_df[self.scores_df['GrupoEtario'] == grupo]['Score_Pre']
            ax.hist(data, alpha=0.6, label=grupo, color=cores[grupo], bins=20)
        
        ax.set_xlabel('Score Pré-teste')
        ax.set_ylabel('Frequência')
        ax.set_title('Distribuição de Scores - Pré-teste')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 2. Distribuição geral de scores pós-teste
        ax = axes[0, 1]
        for grupo in ['6º/7º anos', '8º/9º anos']:
            data = self.scores_df[self.scores_df['GrupoEtario'] == grupo]['Score_Pos']
            ax.hist(data, alpha=0.6, label=grupo, color=cores[grupo], bins=20)
        
        ax.set_xlabel('Score Pós-teste')
        ax.set_ylabel('Frequência')
        ax.set_title('Distribuição de Scores - Pós-teste')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 3. Boxplot comparativo
        ax = axes[1, 0]
        data_box = []
        labels_box = []
        
        for grupo in ['6º/7º anos', '8º/9º anos']:
            data_grupo = self.scores_df[self.scores_df['GrupoEtario'] == grupo]
            data_box.extend([data_grupo['Score_Pre'], data_grupo['Score_Pos']])
            labels_box.extend([f'{grupo}\nPré', f'{grupo}\nPós'])
        
        box_plot = ax.boxplot(data_box, labels=labels_box, patch_artist=True)
        colors = [cores['6º/7º anos'], cores['6º/7º anos'], cores['8º/9º anos'], cores['8º/9º anos']]
        
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        
        ax.set_ylabel('Score')
        ax.set_title('Comparação de Scores por Grupo')
        ax.grid(True, alpha=0.3)
        
        # 4. Scatter plot delta vs score pré
        ax = axes[1, 1]
        for grupo in ['6º/7º anos', '8º/9º anos']:
            data_grupo = self.scores_df[self.scores_df['GrupoEtario'] == grupo]
            ax.scatter(data_grupo['Score_Pre'], data_grupo['Delta'], 
                      alpha=0.6, label=grupo, color=cores[grupo], s=30)
        
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax.set_xlabel('Score Pré-teste')
        ax.set_ylabel('Mudança (Pós - Pré)')
        ax.set_title('Relação Score Inicial vs Mudança')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if salvar:
            plt.savefig(self.fig_dir / 'fase2_distribuicao_scores.png', dpi=300, bbox_inches='tight')
            print("Gráfico salvo: fase2_distribuicao_scores.png")
        
        plt.show()
        return fig
    
    def plot_analise_por_palavra(self, top_n=15, salvar=True):
        """Análise visual por palavra"""
        # Calcular dados por palavra para cada grupo
        resultados_palavras = {}
        
        for grupo in ['6º/7º anos', '8º/9º anos', 'Todos']:
            if grupo == 'Todos':
                df_pre_grupo = self.df_pre_final
                df_pos_grupo = self.df_pos_final
            else:
                df_pre_grupo = self.df_pre_final[self.df_pre_final['GrupoEtario'] == grupo]
                df_pos_grupo = self.df_pos_final[self.df_pos_final['GrupoEtario'] == grupo]
            
            palavras_data = []
            
            for col in self.colunas_q:
                if col in df_pre_grupo.columns and col in df_pos_grupo.columns:
                    palavra = self.mapeamento_palavras.get(col, f"Palavra_{col}")
                    
                    valores_pre = df_pre_grupo[col].dropna()
                    valores_pos = df_pos_grupo[col].dropna()
                    
                    if len(valores_pre) > 0 and len(valores_pos) > 0:
                        # Taxa de acerto
                        acertos_pre = (valores_pre >= 1).sum()
                        acertos_pos = (valores_pos >= 1).sum()
                        
                        taxa_pre = acertos_pre / len(valores_pre)
                        taxa_pos = acertos_pos / len(valores_pos)
                        melhora = taxa_pos - taxa_pre
                        
                        palavras_data.append({
                            'Questao': col,
                            'Palavra': palavra,
                            'Taxa_Pre': taxa_pre,
                            'Taxa_Pos': taxa_pos,
                            'Melhora': melhora
                        })
            
            resultados_palavras[grupo] = pd.DataFrame(palavras_data)
        
        # Gráfico
        fig, axes = plt.subplots(2, 2, figsize=(18, 12))
        
        # 1. Top palavras com maior melhora - Todos
        ax = axes[0, 0]
        top_geral = resultados_palavras['Todos'].nlargest(top_n, 'Melhora')
        y_pos = np.arange(len(top_geral))
        
        bars = ax.barh(y_pos, top_geral['Melhora'], color='#2E86AB', alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([p[:12] + '...' if len(p) > 12 else p for p in top_geral['Palavra']])
        ax.set_xlabel('Melhora na Taxa de Acerto')
        ax.set_title(f'Top {top_n} Palavras - Melhora Geral')
        ax.grid(True, alpha=0.3)
        
        # Valores nas barras
        for i, v in enumerate(top_geral['Melhora']):
            ax.text(v + 0.005, i, f'{v:.3f}', va='center', fontsize=9)
        
        # 2. Comparação entre grupos - Top 10
        ax = axes[0, 1]
        top_10_questoes = resultados_palavras['Todos'].nlargest(10, 'Melhora')['Questao']
        
        melhoras_g1 = []
        melhoras_g2 = []
        palavras_nomes = []
        
        for questao in top_10_questoes:
            palavra = self.mapeamento_palavras.get(questao, questao)
            palavras_nomes.append(palavra[:10] + '...' if len(palavra) > 10 else palavra)
            
            # Buscar melhora para cada grupo
            melhora_g1 = resultados_palavras['6º/7º anos'][
                resultados_palavras['6º/7º anos']['Questao'] == questao]['Melhora']
            melhora_g2 = resultados_palavras['8º/9º anos'][
                resultados_palavras['8º/9º anos']['Questao'] == questao]['Melhora']
            
            melhoras_g1.append(melhora_g1.iloc[0] if len(melhora_g1) > 0 else 0)
            melhoras_g2.append(melhora_g2.iloc[0] if len(melhora_g2) > 0 else 0)
        
        x = np.arange(len(palavras_nomes))
        width = 0.35
        
        ax.bar(x - width/2, melhoras_g1, width, label='6º/7º anos', color='#A23B72', alpha=0.7)
        ax.bar(x + width/2, melhoras_g2, width, label='8º/9º anos', color='#F18F01', alpha=0.7)
        
        ax.set_xlabel('Palavras')
        ax.set_ylabel('Melhora')
        ax.set_title('Comparação de Melhora entre Grupos - Top 10')
        ax.set_xticks(x)
        ax.set_xticklabels(palavras_nomes, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 3. Correlação entre taxa inicial e melhora
        ax = axes[1, 0]
        df_todos = resultados_palavras['Todos']
        
        scatter = ax.scatter(df_todos['Taxa_Pre'], df_todos['Melhora'], 
                           alpha=0.6, c=df_todos['Taxa_Pre'], cmap='viridis', s=50)
        
        # Linha de tendência
        z = np.polyfit(df_todos['Taxa_Pre'], df_todos['Melhora'], 1)
        p = np.poly1d(z)
        ax.plot(df_todos['Taxa_Pre'], p(df_todos['Taxa_Pre']), "r--", alpha=0.8, linewidth=2)
        
        ax.set_xlabel('Taxa de Acerto Inicial (Pré-teste)')
        ax.set_ylabel('Melhora')
        ax.set_title('Relação Taxa Inicial vs Melhora')
        ax.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax, label='Taxa Inicial')
        
        # 4. Heatmap das top 20 palavras por grupo
        ax = axes[1, 1]
        
        # Preparar dados para heatmap
        top_20_questoes = resultados_palavras['Todos'].nlargest(20, 'Melhora')['Questao']
        heatmap_data = []
        
        for questao in top_20_questoes:
            row_data = []
            for grupo in ['6º/7º anos', '8º/9º anos']:
                melhora = resultados_palavras[grupo][
                    resultados_palavras[grupo]['Questao'] == questao]['Melhora']
                row_data.append(melhora.iloc[0] if len(melhora) > 0 else 0)
            heatmap_data.append(row_data)
        
        heatmap_array = np.array(heatmap_data)
        palavras_labels = [self.mapeamento_palavras.get(q, q)[:10] for q in top_20_questoes]
        
        im = ax.imshow(heatmap_array, cmap='RdYlBu_r', aspect='auto')
        
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['6º/7º anos', '8º/9º anos'])
        ax.set_yticks(range(len(palavras_labels)))
        ax.set_yticklabels(palavras_labels)
        ax.set_title('Heatmap de Melhoras - Top 20 Palavras')
        
        # Adicionar valores
        for i in range(len(palavras_labels)):
            for j in range(2):
                text = ax.text(j, i, f'{heatmap_array[i, j]:.3f}',
                             ha="center", va="center", color="white" if abs(heatmap_array[i, j]) > 0.05 else "black")
        
        plt.colorbar(im, ax=ax, label='Melhora')
        
        plt.tight_layout()
        
        if salvar:
            plt.savefig(self.fig_dir / 'fase2_analise_palavras.png', dpi=300, bbox_inches='tight')
            print("Gráfico salvo: fase2_analise_palavras.png")
        
        plt.show()
        return fig
    
    def plot_estatisticas_descritivas(self, salvar=True):
        """Gráficos de estatísticas descritivas"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Médias por grupo com intervalo de confiança
        ax = axes[0, 0]
        grupos = ['6º/7º anos', '8º/9º anos']
        means_pre = []
        means_pos = []
        errs_pre = []
        errs_pos = []
        
        for grupo in grupos:
            data_grupo = self.scores_df[self.scores_df['GrupoEtario'] == grupo]
            
            # Pré-teste
            mean_pre = data_grupo['Score_Pre'].mean()
            se_pre = data_grupo['Score_Pre'].sem()  # Standard error
            means_pre.append(mean_pre)
            errs_pre.append(1.96 * se_pre)  # 95% CI
            
            # Pós-teste
            mean_pos = data_grupo['Score_Pos'].mean()
            se_pos = data_grupo['Score_Pos'].sem()
            means_pos.append(mean_pos)
            errs_pos.append(1.96 * se_pos)
        
        x = np.arange(len(grupos))
        width = 0.35
        
        ax.bar(x - width/2, means_pre, width, yerr=errs_pre, label='Pré-teste', 
               color='#2E86AB', alpha=0.7, capsize=5)
        ax.bar(x + width/2, means_pos, width, yerr=errs_pos, label='Pós-teste', 
               color='#A23B72', alpha=0.7, capsize=5)
        
        ax.set_xlabel('Grupos')
        ax.set_ylabel('Score Médio')
        ax.set_title('Médias com Intervalo de Confiança 95%')
        ax.set_xticks(x)
        ax.set_xticklabels(grupos)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 2. Tamanhos de efeito (Cohen's d) por grupo
        ax = axes[0, 1]
        cohens_d = []
        grupos_labels = []
        
        for grupo in grupos:
            data_grupo = self.scores_df[self.scores_df['GrupoEtario'] == grupo]
            pre_scores = data_grupo['Score_Pre']
            pos_scores = data_grupo['Score_Pos']
            
            # Cohen's d
            pooled_std = np.sqrt((pre_scores.var() + pos_scores.var()) / 2)
            d = (pos_scores.mean() - pre_scores.mean()) / pooled_std if pooled_std > 0 else 0
            
            cohens_d.append(d)
            grupos_labels.append(grupo)
        
        # Adicionar geral
        pre_geral = self.scores_df['Score_Pre']
        pos_geral = self.scores_df['Score_Pos']
        pooled_std_geral = np.sqrt((pre_geral.var() + pos_geral.var()) / 2)
        d_geral = (pos_geral.mean() - pre_geral.mean()) / pooled_std_geral if pooled_std_geral > 0 else 0
        
        cohens_d.append(d_geral)
        grupos_labels.append('Geral')
        
        cores_d = ['#F18F01', '#C73E1D', '#2E86AB']
        bars = ax.bar(grupos_labels, cohens_d, color=cores_d, alpha=0.7)
        
        # Linhas de referência
        ax.axhline(y=0.2, color='green', linestyle='--', alpha=0.7, label='Pequeno (0.2)')
        ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.7, label='Médio (0.5)')
        ax.axhline(y=0.8, color='red', linestyle='--', alpha=0.7, label='Grande (0.8)')
        
        # Valores nas barras
        for bar, d in zip(bars, cohens_d):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{d:.4f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel("Cohen's d")
        ax.set_title("Tamanho do Efeito por Grupo")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 3. Distribuição de mudanças
        ax = axes[1, 0]
        for grupo in grupos:
            data_grupo = self.scores_df[self.scores_df['GrupoEtario'] == grupo]
            ax.hist(data_grupo['Delta'], alpha=0.6, label=grupo, bins=15)
        
        ax.axvline(x=0, color='red', linestyle='--', alpha=0.7)
        ax.set_xlabel('Mudança no Score')
        ax.set_ylabel('Frequência')
        ax.set_title('Distribuição de Mudanças por Grupo')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 4. Percentuais de melhoria/piora
        ax = axes[1, 1]
        melhorou = []
        piorou = []
        igual = []
        
        for grupo in grupos:
            data_grupo = self.scores_df[self.scores_df['GrupoEtario'] == grupo]
            total = len(data_grupo)
            
            melhorou.append((data_grupo['Delta'] > 0).sum() / total * 100)
            piorou.append((data_grupo['Delta'] < 0).sum() / total * 100)
            igual.append((data_grupo['Delta'] == 0).sum() / total * 100)
        
        x = np.arange(len(grupos))
        width = 0.25
        
        ax.bar(x - width, melhorou, width, label='Melhorou', color='#28a745', alpha=0.7)
        ax.bar(x, piorou, width, label='Piorou', color='#dc3545', alpha=0.7)
        ax.bar(x + width, igual, width, label='Igual', color='#6c757d', alpha=0.7)
        
        ax.set_xlabel('Grupos')
        ax.set_ylabel('Percentual (%)')
        ax.set_title('Distribuição de Resultados por Grupo')
        ax.set_xticks(x)
        ax.set_xticklabels(grupos)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for i, grupo in enumerate(grupos):
            ax.text(i - width, melhorou[i] + 1, f'{melhorou[i]:.1f}%', ha='center', va='bottom', fontsize=9)
            ax.text(i, piorou[i] + 1, f'{piorou[i]:.1f}%', ha='center', va='bottom', fontsize=9)
            ax.text(i + width, igual[i] + 1, f'{igual[i]:.1f}%', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        if salvar:
            plt.savefig(self.fig_dir / 'fase2_estatisticas_descritivas.png', dpi=300, bbox_inches='tight')
            print("Gráfico salvo: fase2_estatisticas_descritivas.png")
        
        plt.show()
        return fig
    
    def relatorio_completo(self):
        """Gera todos os gráficos da análise"""
        print("="*60)
        print("ANÁLISE VISUAL COMPLETA - WORDGEN FASE 2")
        print("="*60)
        
        print("\n1. Gerando análise de distribuição de scores...")
        self.plot_distribuicao_scores()
        
        print("\n2. Gerando análise por palavra...")
        self.plot_analise_por_palavra()
        
        print("\n3. Gerando estatísticas descritivas...")
        self.plot_estatisticas_descritivas()
        
        print(f"\n✅ Análise visual completa!")
        print(f"📊 Figuras salvas em: {self.fig_dir}")
        print("="*60)

# Exemplo de uso
if __name__ == "__main__":
    # Criar instância da análise
    analise = AnaliseVisualFase2()
    
    # Gerar relatório completo
    analise.relatorio_completo()
