import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import pathlib
import os
from datetime import datetime
from scipy import stats
from scipy.stats import shapiro, ttest_rel, wilcoxon
import warnings
warnings.filterwarnings('ignore')

# Configurações visuais
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AnalisadorVisualWordGen:
    """
    Classe para análise visual avançada dos dados do WordGen
    """
    
    def __init__(self, data_path=None):
        self.current_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
        self.data_dir = str(self.current_dir) + '/Data'
        self.output_dir = str(self.current_dir) + '/Outputs'
        
        # Criar diretório de outputs se não existir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Carregar dados
        if data_path:
            self.arquivo_excel = data_path
        else:
            nome = "RESULTADOS_WordGen_TDE_Vocabulario_2024-1_Fase_4.xlsx"
            self.arquivo_excel = os.path.join(self.data_dir, nome)
        
        self.df = None
        self.baseline_sd = None
        self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega e prepara os dados"""
        print("="*80)
        print("ANALISADOR VISUAL WORDGEN - INTERPRETAÇÃO AVANÇADA DOS DADOS")
        print("="*80)
        print(f"Carregando dados de: {self.arquivo_excel}")
        
        self.df = pd.read_excel(self.arquivo_excel, sheet_name='WG SSb (2024-2) - TDE, Vocabulá')
        
        # Converter e limpar dados
        self.df['total_pre_voc'] = pd.to_numeric(self.df['total_pre_voc'], errors='coerce')
        self.df['total_pos_voc'] = pd.to_numeric(self.df['total_pos_voc'], errors='coerce')
        self.df = self.df.dropna(subset=['total_pre_voc', 'total_pos_voc'])
        
        # Calcular métricas
        self.df['delta_voc'] = self.df['total_pos_voc'] - self.df['total_pre_voc']
        self.baseline_sd = self.df['total_pre_voc'].std()
        self.df['effect_size'] = self.df['delta_voc'] / self.baseline_sd
        
        print(f"Dados carregados: {len(self.df)} participantes")
        print(f"Grupos únicos: {len(self.df['group'].unique())}")
        print(f"Baseline SD: {self.baseline_sd:.2f}")
    
    def categorizar_effect_size(self, es):
        """Categoriza effect size baseado em benchmarks educacionais"""
        abs_es = abs(es)
        if abs_es >= 0.6:
            return "Excelente (≥0.6)"
        elif abs_es >= 0.4:
            return "Bom (0.4-0.6)"
        elif abs_es >= 0.35:
            return "Adequado (0.35-0.4)"
        elif abs_es >= 0.2:
            return "Marginal (0.2-0.35)"
        else:
            return "Insuficiente (<0.2)"
    
    def preparar_dados_grupo(self):
        """Prepara dados agregados por grupo"""
        resultado = []
        
        for grupo in sorted(self.df['group'].unique()):
            df_grupo = self.df[self.df['group'] == grupo]
            
            resultado.append({
                'grupo': grupo,
                'n_alunos': len(df_grupo),
                'pre_media': df_grupo['total_pre_voc'].mean(),
                'pos_media': df_grupo['total_pos_voc'].mean(),
                'delta_medio': df_grupo['delta_voc'].mean(),
                'effect_size': df_grupo['delta_voc'].mean() / self.baseline_sd,
                'pre_std': df_grupo['total_pre_voc'].std(),
                'pos_std': df_grupo['total_pos_voc'].std(),
                'delta_std': df_grupo['delta_voc'].std(),
                'prop_melhoraram': (df_grupo['delta_voc'] > 0).sum() / len(df_grupo),
                'ano_escolar': self.extrair_ano(grupo)
            })
        
        df_grupos = pd.DataFrame(resultado)
        df_grupos['categoria_es'] = df_grupos['effect_size'].apply(self.categorizar_effect_size)
        
        return df_grupos
    
    def extrair_ano(self, grupo):
        """Extrai ano escolar do nome do grupo"""
        if '6' in grupo and 'ANO' in grupo:
            return '6º ano'
        elif '7' in grupo and 'ANO' in grupo:
            return '7º ano'
        elif '8' in grupo and 'ANO' in grupo:
            return '8º ano'
        elif '9' in grupo and 'ANO' in grupo:
            return '9º ano'
        else:
            return 'Outros'
    
    def grafico_effect_size_benchmarks(self):
        """Gráfico de Effect Size com benchmarks educacionais"""
        df_grupos = self.preparar_dados_grupo()
        
        fig = go.Figure()
        
        # Cores por categoria
        cores = {
            'Excelente (≥0.6)': '#2E8B57',      # Verde escuro
            'Bom (0.4-0.6)': '#32CD32',         # Verde claro
            'Adequado (0.35-0.4)': '#FFD700',   # Amarelo
            'Marginal (0.2-0.35)': '#FF8C00',   # Laranja
            'Insuficiente (<0.2)': '#DC143C'    # Vermelho
        }
        
        # Adicionar pontos por categoria
        for categoria in cores.keys():
            df_cat = df_grupos[df_grupos['categoria_es'] == categoria]
            if not df_cat.empty:
                fig.add_trace(go.Scatter(
                    x=df_cat['grupo'],
                    y=df_cat['effect_size'],
                    mode='markers',
                    marker=dict(
                        size=df_cat['n_alunos'],
                        color=cores[categoria],
                        line=dict(width=2, color='white'),
                        sizemode='diameter',
                        sizeref=2.*max(df_grupos['n_alunos'])/(40.**2),
                        sizemin=4
                    ),
                    name=categoria,
                    text=[f"Grupo: {g}<br>ES: {es:.3f}<br>N: {n}<br>Δ: {d:.2f}" 
                          for g, es, n, d in zip(df_cat['grupo'], df_cat['effect_size'], 
                                                df_cat['n_alunos'], df_cat['delta_medio'])],
                    hovertemplate="%{text}<extra></extra>"
                ))
        
        # Linhas de benchmark
        fig.add_hline(y=0.6, line_dash="dash", line_color="green", 
                     annotation_text="Excelente (Hattie)", annotation_position="right")
        fig.add_hline(y=0.4, line_dash="dash", line_color="orange", 
                     annotation_text="Bom (Hattie)", annotation_position="right")
        fig.add_hline(y=0.35, line_dash="dash", line_color="gold", 
                     annotation_text="Significativo (Vocabulário)", annotation_position="right")
        fig.add_hline(y=0.2, line_dash="dash", line_color="red", 
                     annotation_text="Pequeno (Cohen)", annotation_position="right")
        fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
        
        fig.update_layout(
            title="Effect Size por Grupo - Benchmarks Educacionais<br><sub>Tamanho do ponto = número de alunos</sub>",
            xaxis_title="Grupos",
            yaxis_title="Effect Size (Cohen's d)",
            xaxis_tickangle=-45,
            height=600,
            showlegend=True,
            template="plotly_white"
        )
        
        return fig
    
    def grafico_distribuicao_mudancas(self):
        """Distribuição das mudanças individuais"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Distribuição dos Deltas', 'Box Plot por Grupo', 
                          'Histograma por Ano Escolar', 'Violin Plot - Effect Sizes'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Histograma geral dos deltas
        fig.add_trace(go.Histogram(
            x=self.df['delta_voc'],
            nbinsx=30,
            name="Distribuição Δ",
            marker_color='lightblue',
            opacity=0.7
        ), row=1, col=1)
        
        # Linha vertical na média
        media_delta = self.df['delta_voc'].mean()
        fig.add_vline(x=media_delta, line_dash="dash", line_color="red", 
                     annotation_text=f"Média: {media_delta:.2f}", row=1, col=1)
        
        # 2. Box plot por grupo (top 10 grupos por tamanho)
        df_grupos = self.preparar_dados_grupo()
        top_grupos = df_grupos.nlargest(10, 'n_alunos')['grupo'].tolist()
        
        for grupo in top_grupos:
            df_grupo = self.df[self.df['group'] == grupo]
            fig.add_trace(go.Box(
                y=df_grupo['delta_voc'],
                name=grupo,
                showlegend=False
            ), row=1, col=2)
        
        # 3. Histograma por ano escolar
        anos = ['6º ano', '7º ano', '8º ano', '9º ano']
        cores_anos = ['red', 'blue', 'green', 'purple']
        
        for ano, cor in zip(anos, cores_anos):
            df_ano = self.df[self.df['group'].str.contains(ano.split('º')[0], na=False)]
            if not df_ano.empty:
                fig.add_trace(go.Histogram(
                    x=df_ano['delta_voc'],
                    name=ano,
                    opacity=0.6,
                    marker_color=cor,
                    showlegend=False
                ), row=2, col=1)
        
        # 4. Violin plot dos effect sizes
        for ano, cor in zip(anos, cores_anos):
            df_ano = self.df[self.df['group'].str.contains(ano.split('º')[0], na=False)]
            if not df_ano.empty:
                fig.add_trace(go.Violin(
                    y=df_ano['effect_size'],
                    name=ano,
                    marker_color=cor,
                    showlegend=False
                ), row=2, col=2)
        
        fig.update_layout(height=800, title_text="Análise de Distribuições - Mudanças no Vocabulário")
        
        return fig
    
    def grafico_pre_pos_comparacao(self):
        """Comparação pré vs pós por grupo"""
        df_grupos = self.preparar_dados_grupo()
        
        fig = go.Figure()
        
        # Pontos pré-teste
        fig.add_trace(go.Scatter(
            x=df_grupos['grupo'],
            y=df_grupos['pre_media'],
            mode='markers+lines',
            name='Pré-teste',
            marker=dict(size=10, color='red'),
            line=dict(color='red', dash='dash')
        ))
        
        # Pontos pós-teste
        fig.add_trace(go.Scatter(
            x=df_grupos['grupo'],
            y=df_grupos['pos_media'],
            mode='markers+lines',
            name='Pós-teste',
            marker=dict(size=10, color='blue'),
            line=dict(color='blue')
        ))
        
        # Setas de mudança
        for i, row in df_grupos.iterrows():
            fig.add_annotation(
                x=row['grupo'],
                y=row['pre_media'],
                ax=row['grupo'],
                ay=row['pos_media'],
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='green' if row['delta_medio'] > 0 else 'red'
            )
        
        fig.update_layout(
            title="Comparação Pré vs Pós-teste por Grupo",
            xaxis_title="Grupos",
            yaxis_title="Pontuação Média em Vocabulário",
            xaxis_tickangle=-45,
            height=600,
            template="plotly_white"
        )
        
        return fig
    
    def mapa_calor_performance(self):
        """Mapa de calor da performance por grupo e métrica"""
        df_grupos = self.preparar_dados_grupo()
        
        # Preparar dados para o heatmap
        metricas = ['effect_size', 'delta_medio', 'prop_melhoraram']
        nomes_metricas = ['Effect Size', 'Δ Médio', 'Prop. Melhorou']
        
        data_heatmap = []
        for metrica in metricas:
            data_heatmap.append(df_grupos[metrica].values)
        
        fig = go.Figure(data=go.Heatmap(
            z=data_heatmap,
            x=df_grupos['grupo'],
            y=nomes_metricas,
            colorscale='RdYlGn',
            showscale=True,
            text=[[f"{val:.3f}" for val in row] for row in data_heatmap],
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Mapa de Calor - Performance por Grupo",
            xaxis_title="Grupos",
            yaxis_title="Métricas",
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def analise_correlacoes(self):
        """Análise de correlações entre variáveis"""
        # Preparar dados de correlação
        df_corr = self.df[['total_pre_voc', 'total_pos_voc', 'delta_voc', 'effect_size']].copy()
        
        # Adicionar variáveis categóricas numéricas
        df_corr['grupo_num'] = pd.Categorical(self.df['group']).codes
        
        correlation_matrix = df_corr.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.round(3),
            texttemplate="%{text}",
            showscale=True
        ))
        
        fig.update_layout(
            title="Matriz de Correlações - Variáveis do Estudo",
            height=500
        )
        
        return fig
    
    def ranking_grupos(self):
        """Ranking dos grupos por diferentes métricas"""
        df_grupos = self.preparar_dados_grupo()
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Ranking por Effect Size', 'Ranking por Δ Médio', 'Ranking por % Melhora'),
            horizontal_spacing=0.1
        )
        
        # Ranking por Effect Size
        df_es = df_grupos.nlargest(10, 'effect_size')
        fig.add_trace(go.Bar(
            x=df_es['effect_size'],
            y=df_es['grupo'],
            orientation='h',
            name='Effect Size',
            marker_color='green',
            showlegend=False
        ), row=1, col=1)
        
        # Ranking por Delta Médio
        df_delta = df_grupos.nlargest(10, 'delta_medio')
        fig.add_trace(go.Bar(
            x=df_delta['delta_medio'],
            y=df_delta['grupo'],
            orientation='h',
            name='Δ Médio',
            marker_color='blue',
            showlegend=False
        ), row=1, col=2)
        
        # Ranking por Proporção que Melhorou
        df_prop = df_grupos.nlargest(10, 'prop_melhoraram')
        fig.add_trace(go.Bar(
            x=df_prop['prop_melhoraram'],
            y=df_prop['grupo'],
            orientation='h',
            name='% Melhora',
            marker_color='orange',
            showlegend=False
        ), row=1, col=3)
        
        fig.update_layout(height=600, title_text="Rankings - Top 10 Grupos por Métrica")
        
        return fig
    
    def analise_anos_escolares(self):
        """Análise específica por anos escolares"""
        anos_data = []
        
        for ano_num in ['6', '7', '8', '9']:
            df_ano = self.df[self.df['group'].str.contains(ano_num, na=False) & 
                           self.df['group'].str.contains('ANO', na=False)]
            
            if not df_ano.empty:
                anos_data.append({
                    'ano': f'{ano_num}º ano',
                    'n_alunos': len(df_ano),
                    'n_grupos': df_ano['group'].nunique(),
                    'effect_size_medio': df_ano['effect_size'].mean(),
                    'delta_medio': df_ano['delta_voc'].mean(),
                    'prop_melhoraram': (df_ano['delta_voc'] > 0).sum() / len(df_ano),
                    'pre_medio': df_ano['total_pre_voc'].mean(),
                    'pos_medio': df_ano['total_pos_voc'].mean()
                })
        
        df_anos = pd.DataFrame(anos_data)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Effect Size por Ano', 'Mudança Absoluta', 
                          'Proporção que Melhorou', 'Pré vs Pós por Ano'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        cores = ['red', 'blue', 'green', 'purple']
        
        # Effect Size por ano
        fig.add_trace(go.Bar(
            x=df_anos['ano'],
            y=df_anos['effect_size_medio'],
            marker_color=cores,
            name='Effect Size',
            showlegend=False
        ), row=1, col=1)
        
        # Delta médio por ano
        fig.add_trace(go.Bar(
            x=df_anos['ano'],
            y=df_anos['delta_medio'],
            marker_color=cores,
            name='Δ Médio',
            showlegend=False
        ), row=1, col=2)
        
        # Proporção que melhorou
        fig.add_trace(go.Bar(
            x=df_anos['ano'],
            y=df_anos['prop_melhoraram'],
            marker_color=cores,
            name='% Melhora',
            showlegend=False
        ), row=2, col=1)
        
        # Pré vs Pós
        fig.add_trace(go.Scatter(
            x=df_anos['ano'],
            y=df_anos['pre_medio'],
            mode='markers+lines',
            name='Pré',
            marker_color='red'
        ), row=2, col=2)
        
        fig.add_trace(go.Scatter(
            x=df_anos['ano'],
            y=df_anos['pos_medio'],
            mode='markers+lines',
            name='Pós',
            marker_color='blue'
        ), row=2, col=2)
        
        # Linhas de benchmark
        fig.add_hline(y=0.4, line_dash="dash", line_color="orange", row=1, col=1,
                     annotation_text="Benchmark Hattie")
        fig.add_hline(y=0.35, line_dash="dash", line_color="gold", row=1, col=1,
                     annotation_text="Vocabulário")
        
        fig.update_layout(height=600, title_text="Análise por Ano Escolar")
        
        return fig
    
    def dashboard_executivo(self):
        """Dashboard executivo com métricas principais"""
        df_grupos = self.preparar_dados_grupo()
        
        # Métricas gerais
        total_alunos = len(self.df)
        effect_size_geral = self.df['effect_size'].mean()
        prop_melhorou_geral = (self.df['delta_voc'] > 0).sum() / total_alunos
        
        # Grupos por categoria
        grupos_excelentes = len(df_grupos[df_grupos['effect_size'] >= 0.6])
        grupos_bons = len(df_grupos[df_grupos['effect_size'] >= 0.4])
        grupos_adequados = len(df_grupos[df_grupos['effect_size'] >= 0.35])
        
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=('Métricas Gerais', 'Classificação dos Grupos', 'Effect Size por Categoria',
                          'Distribuição por Ano', 'Top 5 Grupos', 'Evolução Pré-Pós',
                          'Benchmarks Atingidos', 'Análise de Variabilidade', 'Recomendações'),
            specs=[[{"type": "indicator"}, {"type": "pie"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "box"}, {"type": "table"}]]
        )
        
        # 1. Métricas gerais (indicadores)
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=effect_size_geral,
            delta={"reference": 0.4, "relative": True},
            title={"text": "Effect Size Geral"},
            number={'suffix': ""},
            domain={'row': 0, 'column': 0}
        ), row=1, col=1)
        
        # 2. Pizza - classificação dos grupos
        categorias = df_grupos['categoria_es'].value_counts()
        fig.add_trace(go.Pie(
            labels=categorias.index,
            values=categorias.values,
            name="Classificação"
        ), row=1, col=2)
        
        # 3. Effect Size por categoria
        fig.add_trace(go.Bar(
            x=categorias.index,
            y=categorias.values,
            name="Grupos por Categoria"
        ), row=1, col=3)
        
        return fig
    
    def gerar_relatorio_completo(self):
        """Gera relatório visual completo"""
        print("\n" + "="*80)
        print("GERANDO RELATÓRIO VISUAL COMPLETO")
        print("="*80)
        
        # Lista de gráficos para gerar
        graficos = [
            ("effect_size_benchmarks", "Effect Size com Benchmarks"),
            ("distribuicao_mudancas", "Distribuição das Mudanças"),
            ("pre_pos_comparacao", "Comparação Pré vs Pós"),
            ("mapa_calor_performance", "Mapa de Calor Performance"),
            ("ranking_grupos", "Ranking dos Grupos"),
            ("analise_anos_escolares", "Análise por Anos Escolares"),
            ("correlacoes", "Análise de Correlações")
        ]
        
        arquivos_gerados = []
        
        for nome_metodo, titulo in graficos:
            try:
                print(f"Gerando: {titulo}")
                
                # Chamar método correspondente
                fig = getattr(self, f"grafico_{nome_metodo}")()
                
                # Salvar como HTML
                arquivo_html = os.path.join(self.output_dir, f"{nome_metodo}.html")
                fig.write_html(arquivo_html)
                
                # Salvar como PNG
                arquivo_png = os.path.join(self.output_dir, f"{nome_metodo}.png")
                fig.write_image(arquivo_png, width=1200, height=800)
                
                arquivos_gerados.extend([arquivo_html, arquivo_png])
                
            except Exception as e:
                print(f"Erro ao gerar {titulo}: {e}")
        
        # Gerar resumo estatístico
        self.gerar_resumo_estatistico()
        
        print(f"\n✅ Relatório visual completo gerado!")
        print(f"📁 Arquivos salvos em: {self.output_dir}")
        print(f"📊 Total de arquivos gerados: {len(arquivos_gerados)}")
        
        return arquivos_gerados
    
    def gerar_resumo_estatistico(self):
        """Gera resumo estatístico em formato texto"""
        df_grupos = self.preparar_dados_grupo()
        
        resumo = []
        resumo.append("="*80)
        resumo.append("RESUMO ESTATÍSTICO - ANÁLISE VISUAL WORDGEN")
        resumo.append("="*80)
        resumo.append(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        resumo.append("")
        
        # Estatísticas gerais
        resumo.append("1. ESTATÍSTICAS GERAIS")
        resumo.append("-"*40)
        resumo.append(f"Total de participantes: {len(self.df)}")
        resumo.append(f"Total de grupos: {len(df_grupos)}")
        resumo.append(f"Effect Size médio geral: {self.df['effect_size'].mean():.4f}")
        resumo.append(f"Mudança média (Δ): {self.df['delta_voc'].mean():.2f}")
        resumo.append(f"Proporção que melhorou: {(self.df['delta_voc'] > 0).sum() / len(self.df):.1%}")
        resumo.append("")
        
        # Análise por benchmarks
        resumo.append("2. ANÁLISE POR BENCHMARKS EDUCACIONAIS")
        resumo.append("-"*40)
        
        excelentes = len(df_grupos[df_grupos['effect_size'] >= 0.6])
        bons = len(df_grupos[(df_grupos['effect_size'] >= 0.4) & (df_grupos['effect_size'] < 0.6)])
        adequados = len(df_grupos[(df_grupos['effect_size'] >= 0.35) & (df_grupos['effect_size'] < 0.4)])
        marginais = len(df_grupos[(df_grupos['effect_size'] >= 0.2) & (df_grupos['effect_size'] < 0.35)])
        insuficientes = len(df_grupos[df_grupos['effect_size'] < 0.2])
        
        resumo.append(f"Grupos EXCELENTES (ES ≥ 0.6): {excelentes} ({excelentes/len(df_grupos):.1%})")
        resumo.append(f"Grupos BONS (0.4 ≤ ES < 0.6): {bons} ({bons/len(df_grupos):.1%})")
        resumo.append(f"Grupos ADEQUADOS (0.35 ≤ ES < 0.4): {adequados} ({adequados/len(df_grupos):.1%})")
        resumo.append(f"Grupos MARGINAIS (0.2 ≤ ES < 0.35): {marginais} ({marginais/len(df_grupos):.1%})")
        resumo.append(f"Grupos INSUFICIENTES (ES < 0.2): {insuficientes} ({insuficientes/len(df_grupos):.1%})")
        resumo.append("")
        
        # Top 5 grupos
        resumo.append("3. TOP 5 GRUPOS POR EFFECT SIZE")
        resumo.append("-"*40)
        top5 = df_grupos.nlargest(5, 'effect_size')
        for i, row in top5.iterrows():
            resumo.append(f"{row['grupo']}: ES = {row['effect_size']:.3f} (n={row['n_alunos']})")
        resumo.append("")
        
        # Análise por ano
        resumo.append("4. ANÁLISE POR ANO ESCOLAR")
        resumo.append("-"*40)
        for ano_num in ['6', '7', '8', '9']:
            df_ano = self.df[self.df['group'].str.contains(ano_num, na=False) & 
                           self.df['group'].str.contains('ANO', na=False)]
            if not df_ano.empty:
                es_medio = df_ano['effect_size'].mean()
                resumo.append(f"{ano_num}º ano: ES médio = {es_medio:.3f} (n={len(df_ano)}, {df_ano['group'].nunique()} grupos)")
        resumo.append("")
        
        # Recomendações
        resumo.append("5. RECOMENDAÇÕES PRINCIPAIS")
        resumo.append("-"*40)
        
        if excelentes > 0:
            resumo.append("✅ Há grupos com resultados EXCELENTES - documentar e replicar práticas")
        
        if bons + adequados >= len(df_grupos) * 0.5:
            resumo.append("✅ Maioria dos grupos com resultados satisfatórios")
        else:
            resumo.append("⚠️ Menos de 50% dos grupos com resultados satisfatórios - revisar estratégia")
        
        if insuficientes > len(df_grupos) * 0.3:
            resumo.append("❌ Muitos grupos com resultados insuficientes - reformulação necessária")
        
        resumo.append("")
        resumo.append("="*80)
        
        # Salvar resumo
        arquivo_resumo = os.path.join(self.output_dir, "resumo_estatistico_visual.txt")
        with open(arquivo_resumo, 'w', encoding='utf-8') as f:
            f.write('\n'.join(resumo))
        
        print(f"📄 Resumo estatístico salvo: {arquivo_resumo}")


def main():
    """Função principal para executar a análise visual"""
    print("Iniciando Análise Visual WordGen...")
    
    # Criar analisador
    analisador = AnalisadorVisualWordGen()
    
    # Gerar relatório completo
    arquivos = analisador.gerar_relatorio_completo()
    
    print("\n" + "="*80)
    print("ANÁLISE VISUAL CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print("\nArquivos gerados:")
    for arquivo in arquivos:
        print(f"  • {os.path.basename(arquivo)}")
    
    print(f"\n📁 Todos os arquivos estão em: {analisador.output_dir}")
    print("\n🎯 Para visualizar:")
    print("  1. Abra os arquivos .html no navegador para gráficos interativos")
    print("  2. Use os arquivos .png para relatórios estáticos")
    print("  3. Consulte resumo_estatistico_visual.txt para síntese")


if __name__ == "__main__":
    main()