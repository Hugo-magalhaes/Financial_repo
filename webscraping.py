from unittest.util import safe_repr
import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
from datetime import datetime, timedelta
import mplfinance as mpf
import mplcyberpunk
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bcb import sgs, currency
from fpdf import FPDF
from matplotlib.dates import date2num
import warnings
import win32com.client as win32
from di_bot import pegando_dados_di, tratamento, transforma_data, PDF
warnings.filterwarnings('ignore')


indices = ['^BVSP', '^GSPC']
hoje = datetime.now()
year_ago = hoje - timedelta(days=366)

dados_mercado = pdr.get_data_yahoo(indices, start=year_ago, end=hoje)
dados_fechamento = dados_mercado['Adj Close']
dados_fechamento.columns = ['Ibov', 'S&P500']
dados_fechamento = dados_fechamento.dropna()
dados_anuais = dados_fechamento.resample('Y').last()
dados_mensais = dados_fechamento.resample('M').last()


retorno_diario = dados_fechamento.pct_change().dropna()
retorno_mes = dados_mensais.pct_change().dropna()
retorno_ano = dados_anuais.pct_change().dropna()

retorno_mes = retorno_mes.iloc[1:, :]
fechamento_dia = retorno_diario.iloc[-1, :]

votil_ano_ibov = retorno_diario['Ibov'].std() * np.sqrt(252)
votil_ano_sp = retorno_diario['S&P500'].std() * np.sqrt(252)

# plt.style.use('cyberpunk')
# fig, ax = plt.subplots()
# ax.plot(dados_fechamento.index, dados_fechamento['S&P500'])
# ax.set_title('Indíce Ibovespa')
# ax.grid(False)
# plt.savefig('ibov.png', dpi=300)
# plt.show()
# plt.style.use('cyberpunk')

# fig, ax = plt.subplots()
# ax.plot(dados_fechamento.index, dados_fechamento['Ibov'])
# ax.set_title('Indíce S&P500')
# ax.grid(False)
# plt.savefig('sp.png', dpi=300)
# plt.show()


data_inicial = dados_fechamento.index[0]
if datetime.now().hour < 10:
    data_final = dados_fechamento.index[-1]
else:
    data_final = dados_fechamento.index[-2]

data_inicial = data_inicial.strftime('%d/%m/%Y')
data_final = data_final.strftime('%d/%m/%Y')

url_mais_att = f'''http://www2.bmf.com.br/pages/portal/bmfbovespa/boletim1/SistemaPregao1.asp?
pagetype=pop&caminho=Resumo%20Estat%EDstico%20-%20Sistema%20Preg%E3o&Data={data_final}
&Mercadoria=DI1'''

url_mais_antiga = f'''http://www2.bmf.com.br/pages/portal/bmfbovespa/boletim1/SistemaPregao1.asp?
pagetype=pop&caminho=Resumo%20Estat%EDstico%20-%20Sistema%20Preg%E3o&Data={data_inicial}
&Mercadoria=DI1'''


di_recente, indice_di_recente = pegando_dados_di(url=url_mais_att)
di_antigo, indice_di_antigo = pegando_dados_di(url=url_mais_antiga)


di_recente_tr = tratamento(di_recente, indice_di_recente)
di_antigo_tr = tratamento(di_antigo, indice_di_antigo)

legenda = pd.Series(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    index=['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z'])


di_antigo_tr = transforma_data(di_antigo_tr)
di_recente_tr = transforma_data(di_recente_tr)

# fig, ax = plt.subplots()
# ax.set_ylim(5, 15)
# ax.set_title('Gráfico de juros')
# ax.plot(di_recente_tr.index, di_recente_tr.values,
#         label=f"Curva {data_final}", marker='o')
# ax.plot(di_antigo_tr.index, di_antigo_tr.values,
#         label=f"Curva {data_inicial}", marker='o')
# ax.yaxis.set_major_formatter(mtick.PercentFormatter())
# plt.legend()
# ax.grid(False)
# plt.savefig('juros.png', dpi=300)
# plt.show()

selic = sgs.get({'selic': 432}, start='2010-01-01')

# fig, ax = plt.subplots()
# ax.plot(selic.index, selic['selic'])
# ax.set_title('Taxa Selic')
# ax.yaxis.set_major_formatter(mtick.PercentFormatter())
# plt.legend()
# ax.grid(False)
# plt.savefig('selic.png', dpi=300)
# plt.show()

inflacao = sgs.get({'ipca': 433, 'igp-m': 189}, year_ago + timedelta(180))
data_numerica = date2num(inflacao.index)

# fig, ax = plt.subplots()
# ax.set_title('IPCA e IGM-P')
# ax.bar(data_numerica-7, inflacao['ipca'], label='ipca', width=7)
# ax.bar(data_numerica, inflacao['igp-m'], label='igp-m', width=7)
# ax.yaxis.set_major_formatter(mtick.PercentFormatter())
# ax.xaxis_date()
# formato_Data = mdates.DateFormatter('%b-%y')
# ax.xaxis.set_major_formatter(formato_Data)
# plt.legend()
# ax.grid(False)
# plt.axhline(y=0, color='w')
# plt.savefig('inflacao.png', dpi=300)
# plt.show()

dolar = currency.get('USD', start=year_ago, end=datetime.now())
dolar_mensal = dolar.resample('M').last()
dolar_anual = dolar.resample('Y').last()

dolar_diario = dolar.pct_change().dropna()
retorno_mes_dolar = dolar_mensal.pct_change().dropna()
retorno_ano_dolar = dolar_anual.pct_change().dropna()

fechamento_dolar = dolar_diario.iloc[-1, :]
retorno_mes_dolar = retorno_mes_dolar.iloc[1:, :]

votil_ano_dolar = dolar_diario['USD'].std() * np.sqrt(252)

# fig, ax = plt.subplots()
# ax.set_title('Variação do Dólar')
# ax.plot(dolar.index, dolar['USD'])
# ax.yaxis.set_major_formatter('R${x:1.2f}')
# plt.legend()
# ax.grid(False)
# plt.savefig('dolar.png', dpi=300)
# plt.show()


meses = []

for indice in retorno_mes.index:
    mes = indice.strftime('%b')
    meses.append(mes)


pdf = PDF("P", "mm", "Letter")
pdf.set_auto_page_break(auto=True, margin=15)
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_fill_color(255, 255, 255)
pdf.set_draw_color(35, 155, 132)

# pdf.image('nave1.png', x=115, y=70, w=75, h=33)
pdf.set_font('Arial', 'B', 18)
pdf.cell(0, 10, "1 - Ações e câmbio", ln=True,  border=False, fill=False)
pdf.ln(2)

pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "1.1 Fechamento do mercado", ln=True,  border=False, fill=True)

pdf.ln(7)

# fechamento ibov
pdf.set_font('Arial', '', 13)
pdf.cell(25, 15, " Ibovespa", ln=False,  border=True, fill=True)
pdf.cell(20, 15, f" {str(round(fechamento_dia[0] * 100, 2))}%", ln=True,
         border=True, fill=False)

# fechamento s&p500
pdf.cell(25, 15, " S&P500", ln=False,  border=True, fill=True)
pdf.cell(
    20, 15, f" {str(round(fechamento_dia[1] * 100, 2))}%", ln=True,  border=True, fill=False)

# fechamento Dólar
pdf.cell(25, 15, " Dólar", ln=False,  border=True, fill=True)
pdf.cell(
    20, 15, f" {str(round(fechamento_dia[0] * 100, 2))}%", ln=True,  border=True, fill=False)

pdf.ln(7)

# imagens
pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "   1.2 Gráficos Ibovespa, S&P500 e Dólar",
         ln=True,  border=False, fill=False)

pdf.cell(95, 15, "Ibovespa", ln=False,  border=False, fill=False, align="C")
pdf.cell(100, 15, "S&P500", ln=True,  border=False, fill=False, align="C")
pdf.image("ibov.png", w=80, h=70, x=20, y=160)
pdf.image("sp.png", w=80, h=70, x=115, y=160)

pdf.ln(130)

pdf.cell(0, 15, "Dólar", ln=True,  border=False, fill=False, align="C")
pdf.image("dolar.png", w=100, h=75, x=58)


pdf.ln(2)

pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "   1.3 Rentabilidade mês a mês",
         ln=True,  border=False, fill=False)


# escrevendo os meses
pdf.cell(17, 10, "", ln=False,  border=False, fill=True, align="C")

for mes in meses:

    pdf.cell(16, 10, mes, ln=False,  border=True, fill=True, align="C")


pdf.ln(10)

# escrevendo o ibov
pdf.cell(17, 10, "Ibov", ln=False,  border=True, fill=True, align="C")

pdf.set_font('Arial', '', 12)
for rent in retorno_mes['Ibov']:

    pdf.cell(16, 10, f" {str(round(rent * 100, 2))}%",
             ln=False,  border=True, align="C")

pdf.ln(10)

# escrevendo o S&P
pdf.cell(17, 10, "S&P500", ln=False,  border=True, fill=True, align="C")

pdf.set_font('Arial', '', 12)
for rent in retorno_mes['S&P500']:

    pdf.cell(16, 10, f" {str(round(rent * 100, 2))}%",
             ln=False,  border=True, align="C")

pdf.ln(10)

# escrevendo o Dólar

pdf.cell(17, 10, "Dólar", ln=False,  border=True, fill=True, align="C")

pdf.set_font('Arial', '', 12)
for rent in retorno_mes_dolar['USD']:

    pdf.cell(16, 10, f" {str(round(rent * 100, 2))}%",
             ln=False,  border=True, align="C")

pdf.ln(10)

# rent anual
pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "   1.4 Rentabilidade no ano",
         ln=True,  border=False, fill=False)

# rent anual ibov
pdf.set_font('Arial', '', 13)
pdf.cell(25, 10, "Ibovespa", ln=False,  border=True, fill=True, align="C")
pdf.cell(
    20, 10, f" {str(round(retorno_ano.iloc[0, 0] * 100, 2))}%", ln=True,  border=True, align="C")

# rent anual S&P
pdf.cell(25, 10, "S&P500", ln=False,  border=True, fill=True, align="C")
pdf.cell(
    20, 10, f" {str(round(retorno_ano.iloc[0, 1] * 100, 2))}%", ln=True,  border=True, align="C")

# rent anual Dólar
pdf.cell(25, 10, "Dólar", ln=False,  border=True, fill=True, align="C")
pdf.cell(
    20, 10, f" {str(round(retorno_ano_dolar.iloc[0, 0] * 100, 2))}%", ln=True,  border=True, align="C")

pdf.ln(20)

# volatilidade
pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "   1.5 Volatilidade 12M", ln=True,  border=False, fill=False)

# vol ibov
pdf.set_font('Arial', '', 13)
pdf.cell(25, 10, "Ibovespa", ln=False,  border=True, fill=True, align="C")
pdf.cell(20, 10, f" {str(round(votil_ano_ibov * 100, 2))}%",
         ln=True,  border=True, align="C")

# vol s&p500
pdf.cell(25, 10, "S&P500", ln=False,  border=True, fill=True, align="C")
pdf.cell(20, 10, f" {str(round(votil_ano_sp * 100, 2))}%",
         ln=True,  border=True, align="C")

# vol dolar
pdf.cell(25, 10, "Dólar", ln=False,  border=True, fill=True, align="C")
pdf.cell(20, 10, f" {str(round(votil_ano_dolar * 100, 2))}%",
         ln=True,  border=True, align="C")

# pdf.image('nave2.png', x=115, y=45, w=70, h=70, type='', link='')

pdf.ln(7)

pdf.set_font('Arial', 'B', 18)
pdf.cell(0, 15, "2 - Dados econômicos", ln=True,  border=False, fill=False)

pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "2.1 Curva de juros", ln=True,  border=False, fill=False)
pdf.image("juros.png", w=125, h=100, x=40, y=140)

pdf.ln(135)

pdf.cell(0, 15, "2.2 Inflacão", ln=True,  border=False, fill=False)
pdf.image("inflacao.png", w=110, h=90, x=40)

pdf.cell(0, 15, "2.3 Selic", ln=True,  border=False, fill=False)
pdf.image("selic.png", w=110, h=90, x=40)

pdf.output('relatorio.pdf')

# mail = win32.Dispatch('outlook.aplicattion')
# email = mail.CreateItem(0)

# email.To = 'hugommjunior@gmail.com'
# email.Subject = 'Relatório'
# email.Body = '''Segue em anexo relatório
# abs, Hugo
# '''

# anexo = r"C:/Users/Hugo Martins/OneDrive/Documentos/neural/web_scrap/.pdf"

# email.Attatchments.Add(anexo)
# email.Send()
