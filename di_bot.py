from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium import webdriver
import pandas as pd
import datetime
from fpdf import FPDF


def pegando_dados_di(self, url):
    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install()))
    driver.get(url)

    local_tabela = '''
    //div[@id = "containerPop"]//div[@id = "pageContent"]//form//table//tbody//tr[3]//td[3]//table
    '''

    local_indice = '''
    //div[@id = "containerPop"]//div[@id = "pageContent"]//form//table//tbody//tr[3]//td[1]//table
    '''

    elemento = driver.find_element("xpath", local_tabela)
    elemento_indice = driver.find_element("xpath", local_indice)
    html_tabela = elemento.get_attribute('outerHTML')
    html_indice = elemento_indice.get_attribute('outerHTML')
    driver.quit()

    tabela = pd.read_html(html_tabela)[0]
    indice = pd.read_html(html_indice)[0]

    return tabela, indice


def tratamento(df_dados, indice):
    df_dados.columns = df_dados.loc[0]
    df_dados = df_dados['ÚLT. PREÇO']
    df_dados = df_dados.drop(0, axis=0)

    indice, columns = indice.loc[0]
    indice_di = indice.loc[0]
    indice = indice.drop(0, axis=0)
    indice_di = indice['VENCTO']
    indice = indice.drop(0, axis=0)
    df_dados.index = indice['VENCTO']

    df_dados = df_dados.astype(int)
    df_dados = df_dados[df_dados != 0]
    df_dados = df_dados/1000

    return df_dados


def transforma_data(df, legenda):
    lista_datas = []

    for indice in df.index:

        letra = indice[0]
        ano = indice[1:3]

        mes = legenda[letra]
        data = f"{mes}-{ano}"
        data = datetime.strftime(data, "%b-%y")
        lista_datas.append(data)

        return df


class PDF(FPDF):
    def header(self, data_final):

        self.image('logo.png', 10, 8, 40)
        self.set_font('Arial', 'B', 20)
        self.ln(15)
        self.set_draw_color(35, 155, 132)  # cor RGB
        self.cell(15, ln=False)
        self.cell(150, 15, f"Relatório de mercado {data_final}",
                  border=True, ln=True, align="C")
        self.ln(5)

    def footer(self):

        self.set_y(-15)  # espaço ate o final da folha
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"{self.page_no()}/{{nb}}", align="C")
