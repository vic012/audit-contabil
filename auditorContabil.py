#encoding='utf-8'
# Importa a biblioteca de interfaces Tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
# importa outras bibliotecas
from datetime import datetime
import pandas as pd
import pyautogui as pyg
#Módulos do projeto
from lerDados import Dados
from auditor import Auditor

# -----------------------------

# -----------------------------
# Cria a janela de diálogo com o usuário
# Variáveis globais que solicita ao usuário os nomes dos CSV's de comrpa e pagamentclass

class Janela:
    def __init__(self, master=None):
        #Determina o tamanho da fonte padrão da tela
        self.fonte_padrao = ('Arial', '10')

        #Cabeçalho da janela
        self.configuracaoMaior = Frame(master)
        self.configuracaoMaior['background'] = '#036f79'
        self.configuracaoMaior.pack(side=TOP)

        #Nome do cliente
        self.descricao = Label(self.configuracaoMaior, font=('Arial', '8', 'bold'))
        self.descricao['background'] = '#036f79'
        self.descricao.pack(side=TOP, anchor=CENTER)

        #Frame das configurações
        self.configuracao = Frame(self.configuracaoMaior)
        self.configuracao['background'] = '#036f79'
        self.configuracao.pack(side=RIGHT ,anchor=E)       

        #Adiciona o botão na tela
        self.imagem1 = PhotoImage(file='.\\imagens\\botao1.png')
        self.autentica = Button(self.configuracao, image=self.imagem1, bd=0)
        self.autentica['width'] = 177
        self.autentica['height'] = 23
        self.autentica['command'] = self.dadosAuditor
        self.autentica.pack(side=LEFT)

        self.espaco1 = Frame(self.configuracao)
        self.espaco1['padx'] = 10
        self.espaco1['pady'] = 10
        self.espaco1['width'] = 5
        self.espaco1['background'] = '#036f79'
        self.espaco1.pack(side=LEFT)

        #Frame das configurações
        self.msg = Frame(master)
        #Largura do frame
        self.msg['padx'] = 20
        #Altura do frame
        self.msg['height'] = 20
        #self.configuracao['pady'] = 400
        self.msg['background'] = '#036f79'
        self.msg.pack() 

        #Adicina a tela o nome do arquivo
        self.msgfeedback = Label(self.msg, text='', font=self.fonte_padrao)
        self.msgfeedback['background'] = '#036f79'
        self.msgfeedback['height'] = 1
        self.msgfeedback.pack(side=LEFT)

        #Frame das configurações
        self.somatorio = Frame(master)
        #Largura do frame
        self.somatorio['padx'] = 20
        #Altura do frame
        self.somatorio['height'] = 2
        #self.configuracao['pady'] = 400
        self.somatorio['background'] = '#036f79'
        self.somatorio.pack() 

        self.mensagemSomaDebito = Label(self.somatorio, text='', font=self.fonte_padrao)
        self.mensagemSomaDebito['background'] = '#036f79'
        self.mensagemSomaDebito['height'] = 1
        self.mensagemSomaDebito.pack(side=LEFT)

        self.mensagemSomaCredito = Label(self.somatorio, text='', font=self.fonte_padrao)
        self.mensagemSomaCredito['background'] = '#036f79'
        self.mensagemSomaCredito['height'] = 1
        self.mensagemSomaCredito.pack(side=LEFT)

        #Frame que demonstra a conferencia de saldos
        self.resultado = Frame(master, highlightbackground="#03125a", highlightcolor="#03125a", highlightthickness=1, width=100, height=100, bd= 0)
        self.resultado['background'] = '#ffffff'
        self.resultado['width'] = 1260
        self.resultado['height'] = 660
        self.resultado.pack(side=BOTTOM)

        #Adiciona a visualização dos dados
        self.dados = ttk.Treeview(self.resultado)
        self.dados['height'] = 660
        self.dados['columns'] = ('Data', 'Débito', 'Crédito', 'Contra Partida', 'Histórico', 'Resultado')
        self.dados.column('#0', width=0, stretch=NO)
        self.dados.column('Data', anchor=CENTER, width=100)
        self.dados.column('Débito', anchor=CENTER, width=100)
        self.dados.column('Crédito', anchor=CENTER, width=100)
        self.dados.column('Contra Partida', anchor=CENTER, width=100)
        self.dados.column('Histórico', width=620)
        self.dados.column('Resultado', width=345)

        self.dados.heading('#0', text='', anchor=CENTER)
        self.dados.heading('Data', text='Data', anchor=CENTER)
        self.dados.heading('Débito', text='Débito', anchor=CENTER)
        self.dados.heading('Crédito', text='Crédito', anchor=CENTER)
        self.dados.heading('Contra Partida', text='Contra Partida', anchor=CENTER)
        self.dados.heading('Histórico', text='Histórico')
        self.dados.heading('Resultado', text='Resultado')

        self.dados.bind('<ButtonRelease-1>', self.selectItem)

        self.dados.pack()

        self.scrollBar = ttk.Scrollbar(self.resultado, 
                           orient ="vertical", 
                           command = self.dados.yview)
  
        # Calling pack method w.r.to verical 
        # scrollbar
        self.scrollBar.place(x=1140+204+2, y=25, height=572+20+15)
          
        # Configuring treeview
        self.dados.configure(yscrollcommand = self.scrollBar.set)

        #Recebe a soma dos itens selecionados
        self.selecaoDebito = 0
        self.selecaoCredito = 0

        #Confirmação para adcionar o botão filtro
        self.confirmacaoFiltro = False

        #Recebe o path do arquivo
        self.arquivo = None
        self.dataframe = None

    def selectItem(self, eventButton):
        selecao = self.dados.focus()
        item = self.dados.item(selecao)
        if ((item['values'][5] == 'Saldo Anterior') or (item['values'][5] == 'Saldo Devedor')):
            pass
        elif (item['values'][0] == 'Totalizador'):
            pass
        #Para valores Crédito
        elif (item['values'][1] == '0.00'):
            valorDecimal = item['values'][2][-3:]
            valorAnteDecimal = item['values'][2][:-3].replace('.','')
            self.selecaoCredito += float(valorAnteDecimal + valorDecimal)         
            #Atualiza na tela o valor
            self.mensagemSomaCredito['text'] = 'CRÉDITO R$ ' + str(round(self.selecaoCredito, 2))
            self.mensagemSomaCredito['padx'] = 10
            self.mensagemSomaCredito['pady'] = 2
            self.mensagemSomaCredito['foreground'] = 'white'

        #Para valores Débito
        elif (item['values'][2] == '0.00'):
            valorDecimal = item['values'][1][-3:]
            valorAnteDecimal = item['values'][1][:-3].replace('.','')
            self.selecaoDebito += float(valorAnteDecimal + valorDecimal)
            #Atualiza na tela o valor
            self.mensagemSomaDebito['text'] = 'DÉBITO R$ ' + str(round(self.selecaoDebito, 2))
            self.mensagemSomaDebito['padx'] = 10
            self.mensagemSomaDebito['pady'] = 2
            self.mensagemSomaDebito['foreground'] = 'white'

        #Retorna na tela o Path inteiro do arquivo
        if (not self.confirmacaoFiltro):
            #Adiciona o botão prara limpar os dados
            self.limparSomatorio = Button(self.somatorio, text='Limpar')
            self.limparSomatorio['width'] = 8
            self.limparSomatorio['height'] = 1
            self.limparSomatorio['command'] = self.limparTotais
            self.limparSomatorio.pack(side=LEFT)
        self.confirmacaoFiltro = True
   
    def limparTotais(self):
        self.mensagemSomaCredito['text'] = ''
        self.mensagemSomaDebito['text'] = ''
        self.selecaoDebito = 0
        self.selecaoCredito = 0
        self.confirmacaoFiltro = False
        self.limparSomatorio.pack_forget()
        
    def dadosAuditor(self):

        if (self.arquivo == None):

            #Abre uma janela para o usuário selecionar o arquivo
            self.arquivo = filedialog.askopenfile()
            
            self.msgfeedback['text'] = self.arquivo.name
            self.msgfeedback['padx'] = 10
            self.msgfeedback['pady'] = 10
            self.msgfeedback['foreground'] = '#000000'
            self.msgfeedback['background'] = '#036f79'
            #Alimenta o combobox
            excel = pd.read_csv(self.arquivo.name, sep=';', encoding='latin-1')
            
            self.descricao['text'] = excel.get('descricao_scp')[0]
            self.descricao['foreground'] = 'white'
            self.descricao['background'] = '#036f79'
            
            codigosFornecedores = [set(excel.get('nomec'))]
            #Valores que aparecerão no combobox
            self.fornecedores = [" Selecionar fornecedor"]

            for item in codigosFornecedores[0]:
                self.fornecedores.append(item)

            #Adiciona o campo para que o usuario informe o nº do Fornecedor
            self.numeroFornecedor = ttk.Combobox(self.configuracao, values=sorted(self.fornecedores))
            self.numeroFornecedor.set(" Selecionar fornecedor")
            self.numeroFornecedor.config(width = 60)
            self.numeroFornecedor.pack(side=LEFT)

            #Adiciona um espaço
            self.espaco2 = Frame(self.configuracao)
            self.espaco2['padx'] = 10
            self.espaco2['pady'] = 10
            self.espaco2['width'] = 5
            self.espaco2['background'] = '#036f79'
            self.espaco2.pack(side=LEFT)

            #Adiciona o botão na tela Conferir
            self.imagem2 = PhotoImage(file='.\\imagens\\botao2.png')
            self.conferir = Button(self.configuracao, image=self.imagem2, bd=0,relief=GROOVE)
            self.conferir['width'] = 100
            self.conferir['height'] = 22
            self.conferir['command'] = self.pegaNumero
            self.conferir.pack(side=LEFT)

            #Adiciona um espaço
            self.espaco3 = Frame(self.configuracao)
            self.espaco3['padx'] = 10
            self.espaco3['pady'] = 10
            self.espaco3['width'] = 5
            self.espaco3['background'] = '#036f79'
            self.espaco3.pack(side=LEFT)

            #Adiciona o botão prara limpar os dados
            self.imagem3 = PhotoImage(file='.\\imagens\\botao3.png')
            self.limpar = Button(self.configuracao, image=self.imagem3, bd=0,relief=GROOVE)
            self.limpar['width'] = 90
            self.limpar['height'] = 22
            self.limpar['command'] = self.limpaDados
            self.limpar.pack(side=LEFT)

        else:
            messagebox.showinfo(title='Auditor error', message='Perdão, mas no momento já existe um Razão aberto, para abrir outro relatório o Auditor precisa ser reiniciado.')
            confirmacao = messagebox.askyesno(title='Fechar o Auditor?', message='Você deseja Fechar e abrir um novo Razão?')
            if (confirmacao == True):
                self.configuracaoMaior.quit()

    def pegaNumero(self):
        #Recupera o Número do fornecedor
        fornecedor = self.numeroFornecedor.get()
        
        #Faz uma rápida verificação e passa paras as próximas etapas
        if (fornecedor == 'Selecionar fornecedor'):
            messagebox.showinfo(title='Seleção de fornecedor', message='Por favor, selecione um fornecedor')
        else:
            self.validaArquivo(fornecedor)


    def validaArquivo(self, fornecedor):
        if (self.arquivo != None):
            #Recebe o arquivo e verifica se ele é um xls
            if (self.arquivo.name.find('.csv') != -1):
                self.confere(fornecedor)
            #Se não for retorna um aviso e somente continua se o usuário fornecer um xls
            else:
                messagebox.showinfo(title='Erro de arquivo', message='Por favor, selecione um arquivo (*.csv) (Separado por vírgula)')
        #Se nenhum arquvio for selecionado
        else:
            messagebox.showinfo(title='Erro de seleção de arquivo', message='Por favor, selecione primeiro o arquivo!')
       
    def confere(self, fornecedor):
        #Chama a função que deve abrir o arquivo
        arquivo = Dados(self.arquivo, fornecedor)
        #Retorna o arquivo apenas com o fornecedor indicado
        if (arquivo.abrirArquivo()):
            dadosArquivo = arquivo.dataframe
            valoresDebito = []
            valoresCredito = []
            for valorDebito in dadosArquivo['valdeb']:
                valoresDebito.append(float(valorDebito.replace(',','.')))
            for valorCredito in dadosArquivo['valcre']:
                valoresCredito.append(float(valorCredito.replace(',','.')))
                
            dadosArquivo['valdeb'] = valoresDebito
            dadosArquivo['valcre'] = valoresCredito
        else:
            messagebox.showinfo(title='Selecione um fornecedor válido', message='Fornecedor inválido!')
        #Inicia a conferencia passando o resultado do dataframe
        auditoria = Auditor(dadosArquivo)
        auditoria.separaHistoricos()
        #print(dadosArquivo['saldoant'].values[0])
        seriesSaldo = dadosArquivo.loc[(dadosArquivo['valdeb'] == 0) & (dadosArquivo['valcre'] == 0)]
        if (type(dadosArquivo['saldoant'].values[0]) != type('str')):
            saldo = dadosArquivo['saldoant'].values[0]
        else:
            saldo = (float(dadosArquivo['saldoant'].values[0].replace(',','.'))) * -1
        #Se o fornecedor estiver com saldo Credor
        
        if (type(dadosArquivo['saldoant'].values[0]) == type('str')):
            dados = dadosArquivo['saldoant'].values[0].replace(',','.')
            dados = float(dados)
        else:
            dados = float(dadosArquivo['saldoant'].values[0])
        
        if (dados < 0):
            dados = (f'{(dados):,.2f}' + ' C' .replace(',','.')).replace('-','')
        elif (dados == 0):
            dados = saldo
        else:
            dados = f'{(dados):,.2f}' + ' D' .replace(',','.')

        if (saldo < 0):
            self.dados.insert(parent='', index=0, iid=0, text='', tags='saldo', values=([dadosArquivo['datalan'].values[0], dadosArquivo['valdeb'].values[0], dados, dadosArquivo['contrap'].values[0], dadosArquivo['historico'].values[0], "Saldo Devedor"]))
            self.dados.tag_configure('saldo', background='#f5a895', foreground='white')
            self.dados.pack()
        #Se o fornecedor estiver com saldo Credor
        else:
            self.dados.insert(parent='', index=0, iid=0, text='', tags='saldo', values=([dadosArquivo['datalan'].values[0], dadosArquivo['valdeb'].values[0], dados, dadosArquivo['contrap'].values[0], dadosArquivo['historico'].values[0], "Saldo Anterior"]))
            self.dados.tag_configure('saldo', background='black', foreground='white')
            self.dados.pack()

        self.dataframe = auditoria.resultado
        indices = self.dataframe.get('indice')

        contagem = 1
        for item in indices:
            contagem += 1
            datas = (self.dataframe['datalan'].loc[self.dataframe['indice'] == item].values)[0]
            debitos = (self.dataframe['valdeb'].loc[self.dataframe['indice'] == item].values)[0]
            debitos = f'{debitos:,.2f}'.replace(',','.')
            creditos = (self.dataframe['valcre'].loc[self.dataframe['indice'] == item].values)[0]
            creditos = f'{creditos:,.2f}'.replace(',','.')
            contrap = (self.dataframe['contrap'].loc[self.dataframe['indice'] == item].values)[0]
            historicos = (self.dataframe['historico'].loc[self.dataframe['indice'] == item].values)[0]
            resultados = (self.dataframe['resultado'].loc[self.dataframe['indice'] == item].values)[0]      

            try:
                #Sinaliza as compras e os pagamentos como corretos
                if (resultados == 'Compra correta') or (resultados == 'Compra quitada com uso de devolução') or (resultados == 'Pagamento utilizado') or (resultados == 'Pagamento efetuado com uso de devolução') or (resultados == 'Pagamento efetuado com uso de devolução') or (resultados == 'Devolução usada para descontar um pagamento') or (resultados == 'Compra devolvida') or (resultados == 'Devolução de compra integral'): 
                    if (item % 2 == 0):
                        self.dados.insert(parent='', index=item, iid=item, text='', tags='comprasPagamentosCertosCinza', values=([datas, debitos, creditos, contrap, historicos, resultados]))
                        self.dados.tag_configure('comprasPagamentosCertosCinza', background='#ccc4c4')
                        self.dados.pack()
                    else:
                        self.dados.insert(parent='', index=item, iid=item, text='', tags='comprasPagamentosCertos', values=([datas, debitos, creditos, contrap, historicos, resultados]))
                        self.dados.tag_configure('comprasPagamentosCertos', background='#fcfcfc')
                        self.dados.pack()
                #Compras sem pagamentos, Pagamentos incompletos, ou pagamentos sem compras
                elif (resultados == 'Compra com pagamento incompleto') or (resultados == 'Pagamento insuficiente') or (resultados == 'Compra sem pagamento') or (resultados == 'Pagamento com possivel erro') or (resultados == 'Devolução não ultilizada'):
                    self.dados.insert(parent='', index=item, iid=item, text='', tags='comprasPagamentosErrados', values=([datas, debitos, creditos, contrap, historicos, resultados]))
                    self.dados.tag_configure('comprasPagamentosErrados', background='#f5a895')
                    self.dados.pack()
                #Sinaliza os pagamentos de saldo anterior
                elif (resultados == 'Pagamento de saldo anterior'):
                    self.dados.insert(parent='', index=item, iid=item, text='', tags='saldoAnterior', values=([datas, debitos, creditos, contrap, historicos, resultados]))
                    self.dados.tag_configure('saldoAnterior', background='#c7ffc9')
                    self.dados.pack()
            except:
                self.limpaDados()

        totalDebito = self.dataframe.get('valdeb').sum()
        totalDebitoFormatado = f'{float(totalDebito):,.2f}'.replace(',','.')
        totalCredito = self.dataframe.get('valcre').sum()
        totalCreditoFormatado = f'{float(totalCredito):,.2f}'.replace(',','.')
        saldoExercicio = saldo - float(totalDebito) + float(totalCredito)
        if (saldoExercicio < 0):
            saldoExercicio = f'{float(saldoExercicio):,.2f}' + ' D'.replace(',','.')
            self.dados.insert(parent='', index=contagem + 1, iid=contagem + 1, text='', tags='total', values=(['Totalizador', totalDebitoFormatado, totalCreditoFormatado, 'Saldo Final', saldoExercicio, 'Saldo Devedor']))
            self.dados.tag_configure('total', background='#e86b5d')
            self.dados.pack()
        elif (saldoExercicio == 0):
            self.dados.insert(parent='', index=contagem + 1, iid=contagem + 1, text='', tags='total', values=(['Totalizador', totalDebitoFormatado, totalCreditoFormatado, 'Saldo Final', saldoExercicio, 'Saldo Zerado']))
            self.dados.tag_configure('total', background='#c7e4f0')
            self.dados.pack()
        else:
            saldoExercicio = f'{float(saldoExercicio):,.2f}' + ' C'.replace(',','.')
            self.dados.insert(parent='', index=contagem + 1, iid=contagem + 1, text='', tags='total', values=(['Totalizador', totalDebitoFormatado, totalCreditoFormatado,'Saldo Final', saldoExercicio, 'Saldo Credor']))
            self.dados.tag_configure('total', background='#c7e4f0')
            self.dados.pack()
            
    def limpaDados(self):
        for janela in self.dados.get_children():
            self.dados.delete(janela)
        self.mensagemSomaDebito['text'] = ''
        self.mensagemSomaDebito['background'] = '#036f79'
        self.mensagemSomaCredito['text'] = ''
        self.mensagemSomaCredito['background'] = '#036f79'
        self.selecaoDebito = 0
        self.selecaoCredito = 0
        self.confirmacaoFiltro = False
        self.limparSomatorio.pack_forget()
     
root = Tk()
imagem = PhotoImage(file='.\\imagens\\icon.png')
root.configure(background='#036f79')
root.title('Auditor')
#root.geometry('1350x700')
root.iconphoto(False, imagem)
Janela(root)
root.mainloop()