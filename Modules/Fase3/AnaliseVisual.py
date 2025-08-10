import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import pathlib
import os

# Configurar estilo dos gráficos
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

class AnaliseVisual:
    def __init__(self, df_pre, df_pos):
        self.df_pre = df_pre
        self.df_pos = df_pos
        self.preparar_dados()
    
    def preparar_dados(self):
        """Prepara os dados para análise visual"""
        # Filtrar IDs comuns
        ids_pre = set(self.df_pre['id'])
        ids_pos = set(self.df_pos['id'])
        ids_comuns = ids_pre.intersection(ids_pos)
        
        self.df_pre_filtrado = self.df_pre[self.df_pre['id'].isin(ids_comuns)]
        self.df_pos_filtrado = self.df_pos[self.df_pos['id'].isin(ids_comuns)]
        
        # Identificar colunas de interesse
        self.colunas_p = [col for col in self.df_pre_filtrado.columns if col.startswith('Q')]
        self.colunas_score = [col for col in self.df_pre_filtrado.columns if 'Score' in col or 'score' in col]
        
        # Converter para dados booleanos
        self.df_pre_bool = self.df_pre_filtrado[self.colunas_p].copy()
        self.df_pos_bool = self.df_pos_filtrado[self.colunas_p].copy()
        
        for col in self.colunas_p:
            self.df_pre_bool[col] = pd.to_numeric(self.df_pre_filtrado[col], errors='coerce').fillna(0)
            self.df_pos_bool[col] = pd.to_numeric(self.df_pos_filtrado[col], errors='coerce').fillna(0)
            self.df_pre_bool[col] = (self.df_pre_bool[col] > 0).astype(int)
            self.df_pos_bool[col] = (self.df_pos_bool[col] > 0).astype(int)
        
        # CORREÇÃO: Ordenar por ID para garantir correspondência
        self.df_pre_bool_sorted = self.df_pre_bool.set_index(self.df_pre_filtrado['id']).sort_index()
        self.df_pos_bool_sorted = self.df_pos_bool.set_index(self.df_pos_filtrado['id']).sort_index()
        
        # Calcular acertos totais com dados ordenados
        self.acertos_pre = self.df_pre_bool_sorted.sum(axis=1)        
        self.acertos_pos = self.df_pos_bool_sorted.sum(axis=1)
       
    
    def grafico_comparacao_medias(self):
        """Gráfico de barras comparando médias pré vs pós"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfico 1: Comparação geral
        categorias = ['Pré-teste', 'Pós-teste']
        medias = [self.acertos_pre.mean(), self.acertos_pos.mean()]
        desvios = [self.acertos_pre.std(), self.acertos_pos.std()]
        
        bars = ax1.bar(categorias, medias, yerr=desvios, capsize=5, 
                      color=['#FF6B6B', '#4ECDC4'], alpha=0.8)
        ax1.set_ylabel('Número médio de acertos')
        ax1.set_title('Comparação de Desempenho: Pré vs Pós-teste')
        ax1.grid(axis='y', alpha=0.3)
        
        # Adicionar valores nas barras
        for i, (bar, media, desvio) in enumerate(zip(bars, medias, desvios)):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + desvio + 0.5,
                    f'{media:.1f}±{desvio:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Gráfico 2: Distribuição por scores (CORREÇÃO: usar tick_labels)
        if (len(self.acertos_pre) == len(self.acertos_pos)) and len(self.acertos_pre) > 0:
            scores_pre = self.acertos_pre
            scores_pos = self.acertos_pos
            
            ax2.boxplot([scores_pre, scores_pos], tick_labels=['Pré-teste', 'Pós-teste'])
            ax2.set_ylabel('Score Final')
            ax2.set_title('Distribuição dos Scores Finais')
            ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def grafico_dispersao_pre_pos(self):
        """Gráfico de dispersão mostrando relação pré vs pós"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # CORREÇÃO: Verificar se os tamanhos são iguais
        print(f"Tamanho acertos_pre: {len(self.acertos_pre)}")
        print(f"Tamanho acertos_pos: {len(self.acertos_pos)}")
        
        # Calcular diferença com mesmo índice
        diferenca = self.acertos_pos - self.acertos_pre
        
        # Scatter plot
        scatter = ax.scatter(self.acertos_pre, self.acertos_pos, alpha=0.6, s=80, 
                           c=diferenca, cmap='RdYlGn', 
                           edgecolors='black', linewidth=0.5)
        
        # Linha de referência (sem mudança)
        min_val = min(self.acertos_pre.min(), self.acertos_pos.min())
        max_val = max(self.acertos_pre.max(), self.acertos_pos.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, 
               label='Sem mudança')
        
        # Configurações
        ax.set_xlabel('Acertos no Pré-teste')
        ax.set_ylabel('Acertos no Pós-teste')
        ax.set_title('Relação entre Desempenho Pré e Pós-teste')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Mudança (Pós - Pré)')
        
        # Estatísticas
        correlacao = np.corrcoef(self.acertos_pre, self.acertos_pos)[0, 1]
        ax.text(0.05, 0.95, f'Correlação: {correlacao:.3f}', 
               transform=ax.transAxes, fontsize=12, 
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    def grafico_distribuicoes(self):
        """Histogramas e boxplots das distribuições"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Histogramas
        ax1.hist(self.acertos_pre, bins=15, alpha=0.7, color='#FF6B6B', 
                label='Pré-teste', density=True)
        ax1.hist(self.acertos_pos, bins=15, alpha=0.7, color='#4ECDC4', 
                label='Pós-teste', density=True)
        ax1.set_xlabel('Número de acertos')
        ax1.set_ylabel('Densidade')
        ax1.set_title('Distribuição dos Acertos')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # Boxplot comparativo (CORREÇÃO: usar tick_labels)
        data_box = [self.acertos_pre, self.acertos_pos]
        box_plot = ax2.boxplot(data_box, tick_labels=['Pré-teste', 'Pós-teste'], 
                              patch_artist=True)
        box_plot['boxes'][0].set_facecolor('#FF6B6B')
        box_plot['boxes'][1].set_facecolor('#4ECDC4')
        ax2.set_ylabel('Número de acertos')
        ax2.set_title('Boxplot Comparativo')
        ax2.grid(axis='y', alpha=0.3)
        
        # Gráfico de mudança individual
        mudancas = self.acertos_pos - self.acertos_pre
        ax3.hist(mudancas, bins=15, alpha=0.7, color='purple', edgecolor='black')
        ax3.axvline(0, color='red', linestyle='--', linewidth=2, label='Sem mudança')
        ax3.set_xlabel('Mudança (Pós - Pré)')
        ax3.set_ylabel('Frequência')
        ax3.set_title('Distribuição das Mudanças Individuais')
        ax3.legend()
        ax3.grid(alpha=0.3)
        
        # Gráfico de barras das mudanças
        melhoraram = (mudancas > 0).sum()
        pioraram = (mudancas < 0).sum()
        mantiveram = (mudancas == 0).sum()
        
        categorias = ['Melhoraram', 'Pioraram', 'Mantiveram']
        valores = [melhoraram, pioraram, mantiveram]
        cores = ['green', 'red', 'gray']
        
        bars = ax4.bar(categorias, valores, color=cores, alpha=0.7)
        ax4.set_ylabel('Número de participantes')
        ax4.set_title('Mudanças Individuais')
        
        # Adicionar percentuais
        total = len(mudancas)
        for bar, valor in zip(bars, valores):
            percentual = (valor/total) * 100
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{valor}\n({percentual:.1f}%)', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
    
    def heatmap_perguntas(self):
        """Heatmap mostrando desempenho por pergunta"""
        # CORREÇÃO: Usar dados ordenados
        prop_pre = self.df_pre_bool_sorted.mean()
        prop_pos = self.df_pos_bool_sorted.mean()
        melhora = prop_pos - prop_pre
        
        # Criar DataFrame para heatmap
        df_heatmap = pd.DataFrame({
            'Pré-teste': prop_pre,
            'Pós-teste': prop_pos,
            'Melhora': melhora
        })
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12))
        
        # Heatmap 1: Proporções de acerto
        sns.heatmap(df_heatmap[['Pré-teste', 'Pós-teste']].T, 
                   annot=True, fmt='.2f', cmap='RdYlGn', 
                   cbar_kws={'label': 'Proporção de acertos'},
                   ax=ax1)
        ax1.set_title('Proporção de Acertos por Pergunta')
        ax1.set_xlabel('Perguntas')
        
        # Heatmap 2: Melhora
        sns.heatmap(df_heatmap[['Melhora']], 
                   annot=True, fmt='+.3f', cmap='RdBu_r', center=0,
                   cbar_kws={'label': 'Melhora (Pós - Pré)'},
                   ax=ax2)
        ax2.set_title('Melhora por Pergunta')
        ax2.set_xlabel('Perguntas')
        
        plt.tight_layout()
        plt.show()
        
        return df_heatmap.sort_values('Melhora', ascending=False)
    
    def grafico_linhas_top_perguntas(self, top_n=10):
        """Gráfico de linhas para as perguntas com maior melhora"""
        # CORREÇÃO: Usar dados ordenados
        prop_pre = self.df_pre_bool_sorted.mean()
        prop_pos = self.df_pos_bool_sorted.mean()
        melhora = prop_pos - prop_pre
        
        # Selecionar top perguntas
        top_perguntas = melhora.nlargest(top_n).index
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = range(len(top_perguntas))
        y_pre = [prop_pre[p] for p in top_perguntas]
        y_pos = [prop_pos[p] for p in top_perguntas]
        
        # Conectar pré e pós com linhas
        for i in range(len(top_perguntas)):
            ax.plot([i, i], [y_pre[i], y_pos[i]], 'k-', alpha=0.3)
        
        # Pontos
        ax.scatter(x, y_pre, color='#FF6B6B', s=100, label='Pré-teste', zorder=3)
        ax.scatter(x, y_pos, color='#4ECDC4', s=100, label='Pós-teste', zorder=3)
        
        ax.set_xticks(x)
        ax.set_xticklabels(top_perguntas, rotation=45)
        ax.set_ylabel('Proporção de acertos')
        ax.set_title(f'Top {top_n} Perguntas com Maior Melhora')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def relatorio_completo(self):
        """Gera todas as visualizações"""
        print("="*60)
        print("RELATÓRIO VISUAL COMPLETO")
        print("="*60)
        
        print("\n1. Comparação de Médias...")
        self.grafico_comparacao_medias()
        
        print("\n2. Relação Pré vs Pós...")
        self.grafico_dispersao_pre_pos()
        
        print("\n3. Distribuições...")
        self.grafico_distribuicoes()
        
        print("\n4. Análise por Pergunta...")
        df_melhora = self.heatmap_perguntas()
        
        print("\n5. Top Perguntas com Melhora...")
        self.grafico_linhas_top_perguntas()
        
        return df_melhora

# Função para usar a classe
def carregar_e_analisar():
    """Função principal para carregar dados e fazer análise visual"""
    # Carregar dados (adapte o caminho)
    current_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
    data_dir = str(current_dir) + '/Data'
    print(f"Carregando dados de: {data_dir}")
    nome = "RESULTADOS_WordGen_TDE_Vocabulario_2024-1_Fase_3.xlsx"
    arquivo_excel = os.path.join(data_dir, nome)
    
    df_pre = pd.read_excel(arquivo_excel, sheet_name='pre')
    df_pos = pd.read_excel(arquivo_excel, sheet_name='pos')
    
    # Criar análise visual
    analise = AnaliseVisual(df_pre, df_pos)
    
    # Gerar relatório completo
    return analise.relatorio_completo()

if __name__ == "__main__":
    df_melhora = carregar_e_analisar()
    print("\nTop 10 perguntas com maior melhora:")
    print(df_melhora.head(10))