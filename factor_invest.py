from pandas_datareader import data as pdr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dateutil.relativedelta import relativedelta
import quantstats as qs
import jinja2
import mplcyberpunk
import matplotlib.ticker as mtick
import warnings
warnings.filterwarnings('ignore')

tickers = pd.read_excel('composicao_ibov.xlsx')
delta_t = tickers.columns

lista_tickers = []

for mes in delta_t:
    ticker_mes = tickers[mes]
    ticker_mes = ticker_mes.dropna()
    ticker_mes = ticker_mes + '.SA'
    lista_tickers.append(ticker_mes)

lista_ticker_f = pd.concat(lista_tickers)
lista_tickers_f = lista_ticker_f.drop_duplicates()
lista_ticker_f = list(lista_ticker_f)

dados_cotacoes = pdr.get_data_yahoo(
    symbols=lista_ticker_f, start='2015-06-30', end='2022-10-15')

dados_cotacoes.to_excel('Cotas_ibov_15_22.xlsx')

ultima = dados_cotacoes.iloc[-1:]
dados_cotacoes_m = dados_cotacoes.resample('M').last()
dados_cotacoes_m = dados_cotacoes_m.append(ultima)
dados_cotacoes_m = dados_cotacoes_m.drop('2022-10-31', axis=0)

data_carteiras = list(dados_cotacoes_m.index)[6:]

dados_cotacoes_m = dados_cotacoes_m.fillna(0)

# REposiciona -infinito, infinito e -1 por zero
df_retorno = dados_cotacoes_m.pct_chage().replace(
    [np.inf, -np.inf, -1], 0)

df_retorno_6m = dados_cotacoes_m.pct_chape(
    periods=6).replace([-np.inf, np.inf, -1], 0)

df_retorno = df_retorno.loc['2015-12-31':]
df_retorno_6m = df_retorno_6m.loc['2015-12-31':]

dados_cotacoes_m = dados_cotacoes_m.reset_index()
df_retorno = df_retorno.reset_index()
df_retorno_6m = df_retorno_6m.reset_index()

dados_cotacoes_m = pd.melt(
    dados_cotacoes_m, id_vars='Date', var_name='cod', value_name='cotacoes')
df_retorno = pd.melt(df_retorno, id_vars='Date',
                     var_name='cod', value_name='retorno_1m')
df_retorno_6m = pd.melt(df_retorno_6m, id_vars='Date',
                        var_name='cod', value_name='retorno_6m')


dados_cotacoes_m = dados_cotacoes_m.dropna()
df_retorno = df_retorno.dropna()
df_retorno_6m = df_retorno_6m.dropna()


lista_retorno = []

for indice, mes in enumerate(data_carteiras):

    empresas_ibov = tickers[delta_t[indice]]
    empresas_ibov = list(empresas_ibov.dropna().values)
    empresas_ibov = [empresa + '.SA' for empresa in empresas_ibov]

    retorno_empresas_ano = df_retorno_6m[(df_retorno_6m['cod'].isin(
        empresas_ibov)) & (df_retorno_6m['Date'] == mes)]
    top_10_rank = retorno_empresas_ano.sort_values(
        by='retorno_6m', ascending=False).head(10)
    tickers_top_rank = top_10_rank['cod'].to_list()

    if indice != (len(data_carteiras) - 1):
        retorno_prox_mes = df_retorno[(df_retorno['cod'].isin(tickers_top_rank) & (
            df_retorno['Date'] == data_carteiras[indice + 1]))]
        retorno_mes = np.mean(retorno_prox_mes['retorno_1m'])
        df_retorno_model = pd.DataFrame(data={'retorno': retorno_mes},
                                        index=[(mes + relativedelta(months=1))])

        lista_retorno.append(df_retorno_model)

retorno_model = pd.concat(lista_retorno)


ibovespa = pdr.get_data_yahoo(
    symbols='^BVSP', start='2015-12-30', end='2022-10-15')['Adj Close']

retorno_ibov = ibovespa.resample('M').last().pct_change().dropna()
retorno_model['ibovespa'] = retorno_ibov.values
retorno_model_view = retorno_model.mul(100).round(2).astype(str).add('%')

qs.extend_pandas()

retorno_model['retorno'].plot_monthly_heatmap()
retorno_model['ibovespa'].plot_monthly_heatmap()

serie_long_short = retorno_model['retorno'] - retorno_model['ibovespa']
serie_long_short.plot_monthly_heatmap()

retorno_bateu_modelo = retorno_model.copy()
retorno_bateu_modelo['bateu_mercado'] = retorno_model['retorno'] > retorno_model['ibovespa']
proporcao_mes_bateu = sum(
    retorno_bateu_modelo['bateu_mercado'])/len(retorno_bateu_modelo['bateu_mercado'])

retorno_ano = retorno_model.copy()
retorno_ano['ano'] = retorno_ano.index.year
retorno_ano['retorno_acumulado_ano'] = retorno_ano.groupby('ano')[
    'retorno'].cumprod()-1
retorno_ano['retorno_acumulado_ibov'] = retorno_ano.groupby('ano')[
    'ibovespa'].cumprod()-1
retorno_ano = retorno_ano.reset_index()

retorno_ano = (retorno_ano.groupby(['ano']).tail(1))[
    ['ano', 'retorno_acumulado_ano', 'retorno_acumulado_ibov']]

retorno_ano_view = retorno_ano.copy()

retorno_ano_view[['retorno_acumulado_ano',
                  'retorno_acumulado_ibov']] = retorno_ano_view[['retorno_acumulado_ano',
                                                                'retorno_acumulado_ibov']].mul(100).round(2).astype(str).add('%')

cumulative_ret_model = (retorno_model.retorno + 1).cumprod() - 1
cumulative_ret_ibov = (retorno_model.ibovespa + 1).cumprod() - 1

df_acumulado = pd.DataFrame(data={'retorno_acum_model': cumulative_ret_model,
                                  'retorno_acum_ibov': cumulative_ret_ibov},
                            index=cumulative_ret_ibov.index)
df_acumulado = df_acumulado.resample('Y').last()
df_acumulado = df_acumulado[['retorno_acum_model', 'retorno_acum_ibov']]

df_acumulado.mul(100).round(2).astype(str).add('%')

fig, ax = plt.subplots()

plt.style.use('cyberpunk')

ax.plot(df_acumulado.index, df_acumulado['retorno_acum_model'], label='Modelo')
ax.plot(df_acumulado.index,
        df_acumulado['retorno_acum_ibov'], label='Ibovespa')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
plt.legend()
plt.show()
