import pyautogui as pyg

#Esse módulo regula a conferencia por etapas
class Conferencia:

	def __init__(self, compra, pagamento, devolucoes):
		self._compra = compra
		self._pagamento = pagamento
		self._devolucoes = devolucoes
		self._situacaoCompra = []
		self._situacaoPagamento = []
		self._situacaoDevolucoes = []

	#Soma o valor das compras e dos pagamentos e verifica se há diferença
	def somaValores(self):
		#soma os pagamentos encontrados
		valorPagamentos = self._pagamento['valdeb'].sum().round(2)
		#soma as compras encontradas
		valorCompras = self._compra['valcre'].sum().round(2)
		#Verifica se os pagamentos são iguais as compras
		if (valorCompras == valorPagamentos):
			self._situacaoCompra.append('Compra correta')
		#se houver diferença
		else:
			diferenca = (valorCompras - valorPagamentos).round(2)
			#Verifica se a diferença é devolução
			valoresDevolucoes = []
			historicaDevolucao = []
			if (len(self._devolucoes) != 0):
				devolucaoAtual = None
				for devolucao in self._devolucoes['numnf']:
					devolucaoAtual = (self._devolucoes['valdeb'].loc[self._devolucoes['numnf'] == devolucao]).sum().round(2)
					nfAtual = (self._devolucoes['numnf'].loc[self._devolucoes['numnf'] == devolucao])
					valoresDevolucoes.append(devolucaoAtual)
					historicaDevolucao.append(nfAtual)
				#Verifica se a diferença é alguma devolução
				if (diferenca in valoresDevolucoes):
					#Pesquisa na lista o indice da devolução
					indiceDevolucao = valoresDevolucoes.index(diferenca)
					numeroDevolucao = historicaDevolucao[indiceDevolucao]
					self._situacaoDevolucoes.append(numeroDevolucao.values[0])
				else:
					self._situacaoCompra.append('Compra com pagamento incompleto')
					self._situacaoPagamento.append('Pagamento insuficiente')
			elif (len(valoresDevolucoes) == 0):
				self._situacaoCompra.append('Compra com pagamento incompleto')
				self._situacaoPagamento.append('Pagamento insuficiente')

	@property
	def dadosCompras(self):
		return self._situacaoCompra

	@property
	def dadosPagamentos(self):
		return self._situacaoPagamento

	@property
	def dadosDevolucoes(self):
		#Para testes
		#print(self._situacaoDevolucoes)
		return self._situacaoDevolucoes