#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline de Pré-processamento e Limpeza de Dados Educacionais Fase 5
Transforma dados brutos de avaliações (Língua Portuguesa e Matemática) 
em DataFrames analíticos limpos, pareados e no formato largo (wide).

Disciplinas: Língua Portuguesa e Matemática
Fases: Pré e Pós
Séries: 6º, 7º, 8º e 9º Ano
"""

import pandas as pd
import numpy as np
import json
import hashlib
import unicodedata
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

class PipelineFase5:
    """
    Pipeline completo para processamento dos dados da Fase 5
    """
    
    def __init__(self, pasta_dados: str):
        """
        Inicializa o pipeline
        
        Args:
            pasta_dados: Caminho para a pasta com os dados da Fase 5
        """
        self.pasta_dados = Path(pasta_dados)
        self.pasta_saida = Path(__file__).parent / "Data"
        self.pasta_saida.mkdir(parents=True, exist_ok=True)
        
        # Arquivos de entrada
        self.arquivo_matematica = self.pasta_dados / "Matematica_CONSOLIDADO.csv"
        self.arquivo_portugues = self.pasta_dados / "Lingua_Portuguesa_CONSOLIDADO.csv"
        self.gabarito_matematica = self.pasta_dados / "Gabarito" / "Gabarito_Matematica.json"
        self.gabarito_portugues = self.pasta_dados / "Gabarito" / "Gabarito_Portugues.json"
        
        print("="*80)
        print("PIPELINE DE PRÉ-PROCESSAMENTO - FASE 5")
        print("Língua Portuguesa e Matemática (Pré/Pós)")
        print("="*80)
    
    def normalizar_texto(self, texto):
        """
        Normaliza texto: minúsculas, remove acentos e espaços extras
        
        Args:
            texto: String a ser normalizada
            
        Returns:
            String normalizada
        """
        if pd.isna(texto) or texto == '':
            return texto
        
        # Converte para string se não for
        texto = str(texto)
        
        # Minúsculas e remove espaços
        texto = texto.lower().strip()
        
        # Remove acentos
        texto_nfd = unicodedata.normalize('NFKD', texto)
        texto_sem_acento = texto_nfd.encode('ascii', errors='ignore').decode('utf-8')
        
        return texto_sem_acento
    
    def padronizar_serie(self, serie):
        """
        Padroniza formato da série para corresponder ao JSON
        
        Args:
            serie: String da série (ex: "6 ANO")
            
        Returns:
            String padronizada (ex: "6º ANO")
        """
        if pd.isna(serie):
            return serie
        
        serie = str(serie).strip()
        
        # Mapeia formatos comuns
        mapeamento = {
            '6 ANO': '6º ANO',
            '7 ANO': '7º ANO', 
            '8 ANO': '8º ANO',
            '9 ANO': '9º ANO',
            '6º ANO': '6º ANO',
            '7º ANO': '7º ANO',
            '8º ANO': '8º ANO',
            '9º ANO': '9º ANO'
        }
        
        return mapeamento.get(serie.upper(), serie)
    
    def criar_id_aluno(self, row):
        """
        Cria ID único do aluno usando hash de dados identificadores
        
        Args:
            row: Linha do DataFrame
            
        Returns:
            String com hash MD5
        """
        # Usa nome, escola, série e turma para criar ID único (colunas em maiúscula)
        identificador = f"{row['Nome']}_{row['Escola']}_{row['Serie']}_{row['Turma']}"
        return hashlib.md5(identificador.encode()).hexdigest()[:12]
    
    def carregar_gabarito(self, arquivo_gabarito: Path):
        """
        Carrega gabarito do JSON
        
        Args:
            arquivo_gabarito: Caminho do arquivo JSON
            
        Returns:
            Dicionário com gabaritos por série
        """
        with open(arquivo_gabarito, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        gabaritos = {}
        for item in dados['Gabaritos']:
            serie = item['Serie']
            questoes = {}
            habilidades = {}
            
            for q in item['Questoes']:
                questao = f"Q{q['QUESTÃO']}"
                questoes[questao] = q['GABARITO']
                habilidades[questao] = q['HABILIDADE']
            
            gabaritos[serie] = {
                'questoes': questoes,
                'habilidades': habilidades
            }
        
        return gabaritos
    
    def padronizar_dataframe(self, df: pd.DataFrame):
        """
        Etapa 1: Padronização inicial do DataFrame
        
        Args:
            df: DataFrame bruto
            
        Returns:
            DataFrame padronizado
        """
        print("   - Padronizando colunas de identificação...")
        
        # Cria ID do aluno ANTES de normalizar (precisa dos dados originais)
        df['ID_Aluno'] = df.apply(self.criar_id_aluno, axis=1)
        
        # Normaliza colunas de texto
        colunas_texto = ['Nome', 'Escola', 'Turma', 'Municipio', 'Estado']
        for col in colunas_texto:
            if col in df.columns:
                df[col] = df[col].apply(self.normalizar_texto)
        
        # Padroniza série
        if 'Serie' in df.columns:
            df['Serie'] = df['Serie'].apply(self.padronizar_serie)
        
        # Padroniza fase
        if 'Fase' in df.columns:
            df['Fase'] = df['Fase'].str.strip()
            df['Fase'] = df['Fase'].replace({'Pre': 'Pré', 'Pos': 'Pós'})
        
        print(f"   - DataFrame padronizado: {len(df)} registros")
        return df
    
    def funcao_de_correcao(self, grupo_serie, gabaritos):
        """
        Função de correção para cada grupo por série
        
        Args:
            grupo_serie: DataFrame agrupado por série
            gabaritos: Dicionário com gabaritos
            
        Returns:
            DataFrame com scores calculados
        """
        serie = grupo_serie.name
        
        if serie not in gabaritos:
            print(f"     ⚠️  Gabarito não encontrado para série: {serie}")
            return grupo_serie
        
        gabarito_serie = gabaritos[serie]
        questoes = gabarito_serie['questoes']
        habilidades = gabarito_serie['habilidades']
        
        print(f"     - Corrigindo {serie}: {len(questoes)} questões")
        
        # Trata respostas nulas como erro (marca com 'X')
        for questao in questoes.keys():
            if questao in grupo_serie.columns:
                grupo_serie[questao] = grupo_serie[questao].fillna('X')
        
        # Gera colunas de pontuação (P_Qn)
        for questao, gabarito in questoes.items():
            if questao in grupo_serie.columns:
                col_pontuacao = f"P_{questao}"
                grupo_serie[col_pontuacao] = np.where(
                    grupo_serie[questao] == gabarito, 1, 0
                )
        
        # Calcula total de acertos
        colunas_pontuacao = [f"P_{q}" for q in questoes.keys() if q in grupo_serie.columns]
        grupo_serie['Total_Acertos'] = grupo_serie[colunas_pontuacao].sum(axis=1)
        
        # Calcula scores por habilidade
        habilidades_unicas = set(habilidades.values())
        for hab in habilidades_unicas:
            questoes_habilidade = [
                f"P_{q}" for q, h in habilidades.items() 
                if h == hab and q in grupo_serie.columns
            ]
            if questoes_habilidade:
                grupo_serie[f'Total_Acertos_{hab}'] = grupo_serie[questoes_habilidade].sum(axis=1)
        
        return grupo_serie
    
    def corrigir_e_pontuar(self, df: pd.DataFrame, gabaritos: dict):
        """
        Etapa 2: Correção e geração de scores
        
        Args:
            df: DataFrame padronizado
            gabaritos: Dicionário com gabaritos
            
        Returns:
            DataFrame com scores calculados
        """
        print("   - Iniciando correção por série...")
        
        df_corrigido = df.groupby('Serie').apply(
            self.funcao_de_correcao, 
            gabaritos=gabaritos
        ).reset_index(drop=True)
        
        print(f"   - Correção concluída: {len(df_corrigido)} registros")
        return df_corrigido
    
    def filtrar_registros_invalidos(self, df: pd.DataFrame):
        """
        Etapa 3: Filtragem de registros inválidos
        
        Args:
            df: DataFrame com scores
            
        Returns:
            DataFrame filtrado
        """
        print("   - Iniciando filtragem de registros inválidos...")
        
        registros_inicial = len(df)
        
        # Identifica colunas de questões
        colunas_questoes = [col for col in df.columns if col.startswith('Q') and not col.startswith('Q_')]
        
        # Filtro 1: Remove testes em branco
        print("     - Filtro 1: Removendo testes em branco...")
        df_filtrado = df.dropna(subset=colunas_questoes, how='all')
        removidos_branco = registros_inicial - len(df_filtrado)
        print(f"       Removidos {removidos_branco} testes em branco")
        
        # Filtro 2: Remove duplicatas Aluno-Fase
        print("     - Filtro 2: Removendo duplicatas Aluno-Fase...")
        antes_duplicatas = len(df_filtrado)
        df_filtrado = df_filtrado.drop_duplicates(subset=['ID_Aluno', 'Fase'], keep='first')
        removidos_duplicatas = antes_duplicatas - len(df_filtrado)
        print(f"       Removidos {removidos_duplicatas} registros duplicados")
        
        # Filtro 3: Mantém apenas pares completos (Pré E Pós)
        print("     - Filtro 3: Mantendo apenas pares completos (Pré E Pós)...")
        fase_counts = df_filtrado.groupby('ID_Aluno')['Fase'].nunique()
        alunos_completos = fase_counts[fase_counts == 2].index
        df_pareado = df_filtrado[df_filtrado['ID_Aluno'].isin(alunos_completos)]
        
        removidos_incompletos = len(df_filtrado) - len(df_pareado)
        print(f"       Removidos {removidos_incompletos} alunos sem par Pré/Pós")
        
        # Estatísticas finais
        print(f"   - Filtragem concluída:")
        print(f"     * Registros iniciais: {registros_inicial}")
        print(f"     * Registros finais: {len(df_pareado)}")
        print(f"     * Alunos únicos: {df_pareado['ID_Aluno'].nunique()}")
        print(f"     * Taxa de retenção: {len(df_pareado)/registros_inicial*100:.1f}%")
        
        return df_pareado
    
    def pivotar_para_largo(self, df: pd.DataFrame):
        """
        Etapa 4: Reestruturação para formato largo
        
        Args:
            df: DataFrame pareado
            
        Returns:
            DataFrame no formato largo
        """
        print("   - Pivotando para formato largo...")
        
        # Identifica colunas de identificação
        colunas_id = ['ID_Aluno', 'Nome', 'Escola', 'Serie', 'Turma', 'Municipio', 'Estado']
        
        # Identifica colunas de valores (scores)
        colunas_valores = [col for col in df.columns if col.startswith('Total_Acertos')]
        
        # Adiciona colunas P_Q individuais se existirem
        colunas_p = [col for col in df.columns if col.startswith('P_Q')]
        colunas_valores.extend(colunas_p)
        
        print(f"     - Pivotando {len(colunas_valores)} colunas de valores")
        
        # Pivota
        df_largo = df.pivot_table(
            index=colunas_id,
            columns='Fase',
            values=colunas_valores,
            aggfunc='first'
        ).reset_index()
        
        # Limpa nomes das colunas (remove MultiIndex)
        df_largo.columns = [
            f"{col[0]}_{col[1]}" if col[1] else col[0] 
            for col in df_largo.columns
        ]
        
        print(f"   - Formato largo criado: {len(df_largo)} registros")
        return df_largo
    
    def calcular_deltas(self, df_largo: pd.DataFrame):
        """
        Etapa 5: Cálculos finais (deltas)
        
        Args:
            df_largo: DataFrame no formato largo
            
        Returns:
            DataFrame com deltas calculados
        """
        print("   - Calculando deltas (evolução Pré → Pós)...")
        
        deltas_calculados = 0
        
        # Encontra pares de colunas Pré/Pós
        colunas = df_largo.columns.tolist()
        colunas_pre = [col for col in colunas if col.endswith('_Pré')]
        
        for col_pre in colunas_pre:
            base_name = col_pre.replace('_Pré', '')
            col_pos = f"{base_name}_Pós"
            
            if col_pos in colunas:
                col_delta = f"Delta_{base_name}"
                df_largo[col_delta] = df_largo[col_pos] - df_largo[col_pre]
                deltas_calculados += 1
        
        print(f"     - {deltas_calculados} deltas calculados")
        return df_largo
    
    def processar_disciplina(self, arquivo_csv: Path, arquivo_gabarito: Path, nome_disciplina: str):
        """
        Processa uma disciplina completa
        
        Args:
            arquivo_csv: Caminho do CSV de dados
            arquivo_gabarito: Caminho do JSON de gabarito
            nome_disciplina: Nome da disciplina
            
        Returns:
            DataFrame processado
        """
        print(f"\n{'='*60}")
        print(f"PROCESSANDO: {nome_disciplina.upper()}")
        print(f"{'='*60}")
        
        # Etapa 1: Carregamento e padronização
        print("ETAPA 1: Carregamento e Padronização")
        df = pd.read_csv(arquivo_csv)
        print(f"   - Dados carregados: {len(df)} registros")
        
        gabaritos = self.carregar_gabarito(arquivo_gabarito)
        print(f"   - Gabaritos carregados: {len(gabaritos)} séries")
        
        df = self.padronizar_dataframe(df)
        
        # Etapa 2: Correção e pontuação
        print("\nETAPA 2: Correção e Geração de Scores")
        df = self.corrigir_e_pontuar(df, gabaritos)
        
        # Etapa 3: Filtragem
        print("\nETAPA 3: Filtragem de Registros Inválidos")
        df = self.filtrar_registros_invalidos(df)
        
        # Etapa 4: Pivotagem
        print("\nETAPA 4: Reestruturação para Formato Largo")
        df_largo = self.pivotar_para_largo(df)
        
        # Etapa 5: Cálculos finais
        print("\nETAPA 5: Cálculos Finais")
        df_final = self.calcular_deltas(df_largo)
        
        # Salva resultado
        nome_arquivo = f"df_{nome_disciplina.lower().replace(' ', '_')}_analitico.csv"
        arquivo_saida = self.pasta_saida / nome_arquivo
        df_final.to_csv(arquivo_saida, index=False)
        
        print(f"\n✅ {nome_disciplina} processada com sucesso!")
        print(f"   - Arquivo salvo: {arquivo_saida}")
        print(f"   - Registros finais: {len(df_final)}")
        print(f"   - Colunas: {len(df_final.columns)}")
        
        return df_final
    
    def executar_pipeline(self):
        """
        Executa o pipeline completo para ambas as disciplinas
        """
        print("Iniciando pipeline para Fase 5...")
        print(f"Pasta de dados: {self.pasta_dados}")
        print(f"Pasta de saída: {self.pasta_saida}")
        
        resultados = {}
        
        # Processa Matemática
        if self.arquivo_matematica.exists() and self.gabarito_matematica.exists():
            resultados['matematica'] = self.processar_disciplina(
                self.arquivo_matematica,
                self.gabarito_matematica,
                "Matemática"
            )
        else:
            print("❌ Arquivos de Matemática não encontrados")
        
        # Processa Língua Portuguesa
        if self.arquivo_portugues.exists() and self.gabarito_portugues.exists():
            resultados['portugues'] = self.processar_disciplina(
                self.arquivo_portugues,
                self.gabarito_portugues,
                "Língua Portuguesa"
            )
        else:
            print("❌ Arquivos de Língua Portuguesa não encontrados")
        
        # Resumo final
        print(f"\n{'='*80}")
        print("PIPELINE CONCLUÍDO!")
        print(f"{'='*80}")
        
        for disciplina, df in resultados.items():
            print(f"✅ {disciplina.title()}: {len(df)} registros processados")
        
        print(f"\n📁 Arquivos salvos em: {self.pasta_saida}")
        
        return resultados

def main():
    """Função principal"""
    # Caminho para os dados da Fase 5
    pasta_dados = "/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Data/Fase 5"
    
    # Cria e executa pipeline
    pipeline = PipelineFase5(pasta_dados)
    resultados = pipeline.executar_pipeline()
    
    return resultados

if __name__ == "__main__":
    main()