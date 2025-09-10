"""
Módulo para detectar sexo baseado no nome da pessoa.
Utiliza padrões comuns de nomes brasileiros para classificar como Masculino ou Feminino.
"""

import re
from typing import Dict, List, Optional

class DetectorSexo:
    """
    Classe para detectar o sexo de uma pessoa baseado no seu nome.
    """
    
    def __init__(self):
        """Inicializa o detector com listas de nomes e padrões."""
        
        # Nomes tipicamente femininos (primeiros nomes mais comuns)
        self.nomes_femininos = {
            'ana', 'maria', 'julia', 'sofia', 'isabela', 'helena', 'alice', 'valentina',
            'laura', 'beatriz', 'manuela', 'lorena', 'livia', 'antonella', 'giovanna',
            'sarah', 'marina', 'lara', 'nicole', 'yasmin', 'gabriela', 'rafaela',
            'amanda', 'leticia', 'carolina', 'fernanda', 'bruna', 'camila', 'jessica',
            'aline', 'luciana', 'patricia', 'renata', 'cristina', 'andrea', 'carla',
            'daniela', 'simone', 'monica', 'sandra', 'claudia', 'vanessa', 'adriana',
            'mariana', 'larissa', 'priscila', 'fabiana', 'michele', 'tatiane', 'viviane',
            'bianca', 'natalia', 'thais', 'roberta', 'kelly', 'barbara', 'sabrina',
            'eliane', 'silvia', 'rosana', 'katia', 'solange', 'denise', 'regina',
            'edna', 'vera', 'marta', 'rose', 'rita', 'celia', 'ines', 'lourdes',
            'fatima', 'terezinha', 'marlene', 'francisca', 'aparecida', 'conceicao',
            'antonia', 'raimunda', 'iracema', 'socorro', 'geralda', 'sebastiana',
            'luana', 'raquel', 'ingrid', 'debora', 'poliana', 'milena', 'isadora',
            'agatha', 'clara', 'cecilia', 'vitoria', 'emanuelly', 'hadassa', 'erika',
            'ariele', 'ariana', 'abigail', 'evelyn', 'pietra', 'stephanie', 'rayssa'
        }
        
        # Nomes tipicamente masculinos (primeiros nomes mais comuns)
        self.nomes_masculinos = {
            'joao', 'pedro', 'lucas', 'gabriel', 'miguel', 'rafael', 'samuel', 'daniel',
            'david', 'arthur', 'felipe', 'bernardo', 'matheus', 'henrique', 'nicolas',
            'eduardo', 'leonardo', 'gustavo', 'bruno', 'ricardo', 'rodrigo', 'carlos',
            'marcelo', 'fernando', 'andre', 'paulo', 'jose', 'antonio', 'marcos',
            'luis', 'francisco', 'sergio', 'alexandre', 'fabio', 'mario', 'julio',
            'roberto', 'leandro', 'diego', 'vinicius', 'thiago', 'caio', 'otavio',
            'enzo', 'heitor', 'davi', 'isaac', 'emanuel', 'theo', 'lorenzo', 'luca',
            'benjamin', 'matias', 'noah', 'joaquim', 'benicio', 'pietro', 'anthony',
            'ryan', 'ian', 'levi', 'cauã', 'bryan', 'kevin', 'ravi', 'yuri',
            'wesley', 'renan', 'douglas', 'jean', 'cristiano', 'everton', 'alan',
            'anderson', 'jefferson', 'wagner', 'william', 'patrick', 'jonathan',
            'raimundo', 'sebastiao', 'geraldo', 'benedito', 'valdeci', 'valdemir',
            'ademir', 'ademar', 'waldir', 'oswaldo', 'edson', 'edison', 'nelson',
            'wilson', 'milton', 'gilberto', 'alberto', 'roberto', 'wanderley',
            'carlos', 'emanuel', 'felipe', 'isac', 'ezequias', 'deivid', 'davi',
            'everton', 'carlito', 'carlos'
        }
        
        # Padrões de terminações femininas
        self.terminacoes_femininas = {
            'a', 'ana', 'ina', 'inha', 'lia', 'nia', 'ria', 'sia', 'tia', 'via',
            'ella', 'elly', 'elle', 'ette', 'issa', 'essa', 'esca', 'ilda', 'anda',
            'enda', 'onda', 'unda', 'adora', 'eira', 'eira', 'ava', 'eva', 'iva',
            'ova', 'uva', 'ice', 'ece', 'ace', 'uce', 'ose', 'ase', 'ese', 'ise'
        }
        
        # Padrões de terminações masculinas
        self.terminacoes_masculinas = {
            'o', 'os', 'an', 'on', 'un', 'in', 'en', 'or', 'er', 'ir', 'ur',
            'ar', 'al', 'el', 'il', 'ol', 'ul', 'ael', 'iel', 'uel', 'son',
            'ton', 'ron', 'don', 'jon', 'von', 'wan', 'yan', 'ian', 'rian',
            'tian', 'sian', 'cio', 'gio', 'lio', 'nio', 'rio', 'sio', 'tio',
            'vio', 'zio', 'aldo', 'ardo', 'endo', 'indo', 'ondo', 'undo'
        }
        
        # Nomes compostos que são tipicamente femininos
        self.compostos_femininos = {
            'ana', 'maria', 'jose', 'joana', 'clara', 'beatriz', 'vitoria',
            'leticia', 'carolina', 'fernanda', 'patricia', 'cristina'
        }
        
        # Nomes compostos que são tipicamente masculinos
        self.compostos_masculinos = {
            'joao', 'jose', 'carlos', 'luis', 'pedro', 'paulo', 'antonio',
            'francisco', 'fernando', 'eduardo', 'ricardo', 'rafael'
        }
    
    def normalizar_nome(self, nome: str) -> str:
        """
        Normaliza o nome removendo acentos, convertendo para minúsculas
        e removendo caracteres especiais.
        """
        if not nome or pd.isna(nome):
            return ""
        
        # Converter para string e remover espaços extras
        nome = str(nome).strip()
        
        # Remover acentos
        acentos = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
            'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n'
        }
        
        nome = nome.lower()
        for acento, sem_acento in acentos.items():
            nome = nome.replace(acento, sem_acento)
        
        return nome
    
    def extrair_primeiro_nome(self, nome_completo: str) -> str:
        """
        Extrai o primeiro nome de um nome completo.
        """
        nome_normalizado = self.normalizar_nome(nome_completo)
        if not nome_normalizado:
            return ""
        
        # Dividir por espaços e pegar a primeira parte
        partes = nome_normalizado.split()
        if partes:
            return partes[0]
        return ""
    
    def extrair_nomes_compostos(self, nome_completo: str) -> List[str]:
        """
        Extrai os primeiros nomes quando há nomes compostos.
        Ex: "Ana Maria" -> ["ana", "maria"]
        """
        nome_normalizado = self.normalizar_nome(nome_completo)
        partes = nome_normalizado.split()
        
        # Pegar até os primeiros 2-3 nomes (antes dos sobrenomes)
        nomes = []
        for i, parte in enumerate(partes[:3]):  # Máximo 3 primeiros nomes
            # Parar se encontrar sobrenomes comuns
            sobrenomes_comuns = {'da', 'de', 'do', 'dos', 'das', 'e', 'silva', 'santos', 'oliveira', 'souza'}
            if parte in sobrenomes_comuns:
                break
            nomes.append(parte)
        
        return nomes
    
    def detectar_por_lista_nomes(self, nome: str) -> Optional[str]:
        """
        Detecta sexo baseado em listas de nomes conhecidos.
        """
        primeiro_nome = self.extrair_primeiro_nome(nome)
        if not primeiro_nome:
            return None
        
        # Verificar nomes diretos
        if primeiro_nome in self.nomes_femininos:
            return 'F'
        if primeiro_nome in self.nomes_masculinos:
            return 'M'
        
        # Verificar nomes compostos
        nomes_compostos = self.extrair_nomes_compostos(nome)
        for nome_composto in nomes_compostos:
            if nome_composto in self.nomes_femininos:
                return 'F'
            if nome_composto in self.nomes_masculinos:
                return 'M'
        
        return None
    
    def detectar_por_terminacao(self, nome: str) -> Optional[str]:
        """
        Detecta sexo baseado em terminações do primeiro nome.
        """
        primeiro_nome = self.extrair_primeiro_nome(nome)
        if not primeiro_nome or len(primeiro_nome) < 2:
            return None
        
        # Verificar terminações femininas (mais específicas primeiro)
        for terminacao in sorted(self.terminacoes_femininas, key=len, reverse=True):
            if primeiro_nome.endswith(terminacao) and len(primeiro_nome) > len(terminacao):
                return 'F'
        
        # Verificar terminações masculinas (mais específicas primeiro)
        for terminacao in sorted(self.terminacoes_masculinas, key=len, reverse=True):
            if primeiro_nome.endswith(terminacao) and len(primeiro_nome) > len(terminacao):
                return 'M'
        
        return None
    
    def detectar_por_padrao_composto(self, nome: str) -> Optional[str]:
        """
        Detecta sexo em nomes compostos baseado em padrões.
        """
        nomes_compostos = self.extrair_nomes_compostos(nome)
        
        # Se tem nomes compostos, verificar padrões
        for nome_parte in nomes_compostos:
            if nome_parte in self.compostos_femininos:
                return 'F'
            if nome_parte in self.compostos_masculinos:
                return 'M'
        
        return None
    
    def detectar_sexo(self, nome: str) -> str:
        """
        Detecta o sexo baseado no nome usando múltiplas estratégias.
        
        Args:
            nome (str): Nome completo da pessoa
            
        Returns:
            str: 'M' para masculino, 'F' para feminino, 'M' como padrão se incerto
        """
        if not nome or pd.isna(nome):
            return 'M'  # Padrão masculino se nome vazio
        
        # Estratégia 1: Lista de nomes conhecidos (mais confiável)
        resultado = self.detectar_por_lista_nomes(nome)
        if resultado:
            return resultado
        
        # Estratégia 2: Nomes compostos
        resultado = self.detectar_por_padrao_composto(nome)
        if resultado:
            return resultado
        
        # Estratégia 3: Terminações
        resultado = self.detectar_por_terminacao(nome)
        if resultado:
            return resultado
        
        # Estratégia 4: Heurísticas adicionais para casos específicos
        primeiro_nome = self.extrair_primeiro_nome(nome)
        
        # Nomes que terminam em 'a' são geralmente femininos (com exceções)
        excecoes_masculinas_a = {'luca', 'joshua', 'garcia', 'lima', 'costa', 'silva'}
        if primeiro_nome.endswith('a') and primeiro_nome not in excecoes_masculinas_a:
            return 'F'
        
        # Nomes que terminam em 'o' são geralmente masculinos
        if primeiro_nome.endswith('o'):
            return 'M'
        
        # Se chegou até aqui, usar padrão baseado na primeira letra
        # (estatisticamente algumas letras são mais comuns em cada sexo)
        primeira_letra = primeiro_nome[0] if primeiro_nome else 'a'
        letras_mais_femininas = {'a', 'b', 'c', 'd', 'e', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'y', 'z'}
        
        if primeira_letra in letras_mais_femininas:
            return 'F'
        else:
            return 'M'
    
    def detectar_sexo_lote(self, nomes: List[str]) -> List[str]:
        """
        Detecta sexo para uma lista de nomes.
        
        Args:
            nomes (List[str]): Lista de nomes completos
            
        Returns:
            List[str]: Lista com 'M' ou 'F' para cada nome
        """
        return [self.detectar_sexo(nome) for nome in nomes]
    
    def estatisticas_deteccao(self, nomes: List[str]) -> Dict[str, int]:
        """
        Retorna estatísticas da detecção de sexo.
        
        Args:
            nomes (List[str]): Lista de nomes
            
        Returns:
            Dict[str, int]: Estatísticas da distribuição
        """
        resultados = self.detectar_sexo_lote(nomes)
        
        return {
            'Masculino': resultados.count('M'),
            'Feminino': resultados.count('F'),
            'Total': len(resultados)
        }


# Importar pandas para usar pd.isna
import pandas as pd
