import pandas as pd
import xlrd
import pyautogui as pyg

class Dados:

	#O iniciador recebe o path do arquivo e o número do fornecedor
	def __init__(self, arquivo, fornecedor):
		self._arquivo = arquivo
		self._fornecedor = fornecedor
		self._dataframe = None
		
	def abrirArquivo(self):
		#Abre o arquivo informado pelo usuário
		excel = pd.read_csv(self._arquivo.name, sep=';', encoding='latin-1')
		#Seleciona o Dataframe apenas do fornecedor informado
		self._dataframe = excel.loc[excel['nomec'] == self._fornecedor]
		if (self._dataframe.size == 0):
			return False
		else:
			return True

	@property
	def dataframe(self):
		return self._dataframe

	