#encoding='utf-8'
import re
from confere import Conferencia
import pandas as pd

#Esse módulo confere o arquivo do fornecedor recebido e retorna o resultado
#Da auditoria em forma de DataFrame
class Auditor:

	def __init__(self, dataframe):
		self._dataframe = dataframe
		#Informa uma ordem para todos os lançamentos
		contagem = 0
		numeracaoUnica = []
		while (contagem < len(self._dataframe['datalan'])):
			numeracaoUnica.append(contagem)
			contagem += 1
		self._dataframe.insert(len(self._dataframe.columns), 'indice', numeracaoUnica)
		#Seleciona as compras que sua caracteristica é justamente por ter o débito zerado e o crédito diferente de zero
		self._compras = self._dataframe.loc[(self._dataframe['valdeb'] == 0) & (self._dataframe['valcre'] != 0)]
		#Seleciona os pagamentos, as suas caracteristicas são, valdeb != 0 e valcre == 0
		#>>>> Dentro dos pagamentos também estão, pagamentos, descontos, devoluções, e demais quitações de compras
		self._pagamentos = self._dataframe.loc[(self._dataframe['valdeb'] != 0) & (self._dataframe['valcre'] == 0) & (self._dataframe['contrap'] != 55)]
		#Seleciona as devoluções
		self._devolucoes = self._dataframe.loc[(self._dataframe['contrap'] == 55) & (self._dataframe['valdeb'] != 0)]
		#Aramazenará o resultado da conferencia parcial em um dicionário
		self._resultado = None
		#Para testar basta fazer um loop for em um desses DataFrames

	def separaHistoricos(self):
		#Essas listas receberão os históricos separados que serão anexados nos seus respectivos dataframe's
		#Compras
		historicosCompras = list()
		for historico in self._compras['historico']:
			# Para retirar os números, é preciso utilizar Expressões Regulares para encontrar números(str) no meio dos históricos,
			# pois eles estão juntos no mesmo campo
			resultado = re.findall('[0-9]+', historico)
			if (len(resultado) > 0):
				historicosCompras.append(resultado[0])
			else:
				historicosCompras.append('Compra sem Nº de NF')
		#Pagamentos
		historicoPagamentos = list()
		for historico in self._pagamentos['historico']:
			resultado = re.findall('[0-9]+', historico)
			if (len(resultado) > 0):
				historicoPagamentos.append(resultado[0])
			else:
				historicoPagamentos.append('Pagamento sem Nº de NF')
		#Devoluções
		historicoDevolucoes = list()
		for historico in self._devolucoes['historico']:
			resultado = re.findall('[0-9]+', historico)
			historicoDevolucoes.append(resultado[0])
		#Adiciona aos dataframes os numeros em uma coluna específica
		self._compras.insert(len(self._compras.columns), 'numnf', historicosCompras)
		self._pagamentos.insert(len(self._pagamentos.columns), 'numnf', historicoPagamentos)
		self._devolucoes.insert(len(self._devolucoes.columns), 'numnf', historicoDevolucoes)
		#Para teste use compras.to_csv('teste.csv', sep=';')

		#Depois informa no campo do pagamento o valor padrão Pagamento não utilizado
		valorPadraoPagamentos = []
		for item in self._pagamentos['historico']:
			valorPadraoPagamentos.append('Pagamento com possivel erro')
		self._pagamentos.insert(len(self._pagamentos.columns), 'resultado', valorPadraoPagamentos)
		#Depois informa no campo da devolução o valor padrão Devolução não utilizada
		valorPadraoDevolucoes = []
		for item in self._devolucoes['historico']:
			valorPadraoDevolucoes.append('Devolução não ultilizada')
		self._devolucoes.insert(len(self._devolucoes.columns), 'resultado', valorPadraoDevolucoes)
		self.buscaPagamentos()

	def buscaPagamentos(self):
		#Essas listam receberão as indicações de compras pagas ou não para agregarem nos dataframes posteriormente
		comprasPagas = []
		#Faz um loop em cada nº de compra do dataframe Compras
		#1) contém pagamento, cujo valor é igual ao valor da compra
		devolucoes = self._devolucoes
		for numero in self._compras['numnf']:
			#Aponta o pagamento dentro do dataframe que tenha o mesmo numero que a compra
			pagamentoLocalizado = self._pagamentos.loc[self._pagamentos['numnf'] == numero]
			self._pagamentos['resultado'].loc[self._pagamentos['numnf'] == numero] = 'Pagamento utilizado'
			#Se encontrar pagamentos
			if (len(pagamentoLocalizado) > 0):
				#Sépara a compra atual
				compraAtual = self._compras.loc[self._compras['numnf'] == numero]
				#Verifica se o pagamento é integral ou parcial(busca Desconto ou devolução)
				localizar = Conferencia(compraAtual, pagamentoLocalizado, devolucoes)
				localizar.somaValores()
				for item in localizar.dadosCompras:
					if (len(item) > 0):
						comprasPagas.append(item)
				for item in localizar.dadosPagamentos:
					if (len(item) > 0):
						self._pagamentos['resultado'].loc[self._pagamentos['numnf'] == numero] = item
				for item in localizar.dadosDevolucoes:
					if (len(item) > 0):

						#Sinaliza a compra e o seu pagamento
						comprasPagas.append('Compra quitada com uso de devolução')
						self._pagamentos['resultado'].loc[self._pagamentos['numnf'] == numero] = 'Pagamento efetuado com uso de devolução'
						self._devolucoes['resultado'].loc[self._devolucoes['numnf'] == item] = 'Devolução usada para descontar um pagamento'
						#Aponta o index no dataframe que contem a devolução
						index = devolucoes.loc[devolucoes['valdeb'] == item].index
						#Apaga a devolução usada para não ser considerada novamente na próxima iteração
						devolucoes.drop(index, inplace=False)
			#Verifica se a compra foi devolvida integralmente
			elif ((len(pagamentoLocalizado) == 0) & (len(self._devolucoes) != 0)):
				compraAtual = self._compras.loc[self._compras['numnf'] == numero]
				#soma as compras encontradas
				valorCompras = compraAtual['valcre'].sum().round(2)
				devolucaoAtual = None
				valoresDevolucoes = []
				for devolucao in self._devolucoes['numnf']:
					devolucaoAtual = (self._devolucoes['valdeb'].loc[self._devolucoes['numnf'] == devolucao]).sum().round(2)
					valoresDevolucoes.append(devolucaoAtual)
				if (valorCompras in valoresDevolucoes):
					comprasPagas.append('Compra devolvida')
					self._devolucoes['resultado'].loc[self._devolucoes['valdeb'] == valorCompras] = 'Devolução de compra integral'
					#Aponta o index no dataframe que contem a devolução
					index = devolucoes.loc[devolucoes['valdeb'] == valorCompras].index
					#Apaga a devolução usada para não ser considerada novamente na próxima iteração
					devolucoes.drop(index, inplace=False)
				#se não	encontrar
				else:
					#Marca no DataFrame que a compra está sem pagamento
					comprasPagas.append('Compra sem pagamento')
			#se não	encontrar
			else:
				#Marca no DataFrame que a compra está sem pagamento
				comprasPagas.append('Compra sem pagamento')
		
		#Atualizando os dataframes
		#print(f'tamanho pag: {len(self._pagamentos)}, tamanho da list: {len(pagamentosUsados)}')
		self._compras.insert(len(self._compras.columns), 'resultado', comprasPagas)
		self._resultado = pd.concat([self._compras, self._pagamentos, self._devolucoes], ignore_index=True)

		self.confereSaldo()

	#Confere o saldo do fornecedor
	def confereSaldo(self):
		#Seleciona o valor do saldo e o deixa positivo
		#Seleciona o saldo, sua caracteristica é o valdeb e valcre == 0
		if (type(self._dataframe['saldoant'].values[0]) != type('str')):
			saldo = self._dataframe['saldoant'].values[0]
		else:
			saldo = (float(self._dataframe['saldoant'].values[0].replace(',','.'))) * -1
		#Seleciona só os pagamentos com erros após as conferencias das compras
		selecaoPagamentos = self._pagamentos.loc[(self._pagamentos['resultado'] == 'Pagamento com possivel erro')]
		soma = 0
		possiveisPagamentos = list()
		for valor in selecaoPagamentos['valdeb']:
		    if (soma < saldo):
		        soma = soma + valor
		        possiveisPagamentos.append(valor)

		if (saldo == round(soma, 2)):
			for item in possiveisPagamentos:
				self._resultado['resultado'].loc[(self._resultado['valdeb'] == item) & (self._resultado['resultado'] == 'Pagamento com possivel erro')] = 'Pagamento de saldo anterior'

		#Para testes use:
		#self._resultado.to_csv('test.csv', sep=';', index=True)
		self._resultado.sort_values('indice', axis=0, inplace=True)
		#self._resultado.to_csv('test1.csv', sep=';', index=True)
		

	@property
	def resultado(self):
		return self._resultado
	
		