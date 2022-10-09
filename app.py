from faulthandler import disable
import streamlit as st
from ibge.localidades import *
import pandas as pd
from bs4 import BeautifulSoup
import requests
from zipfile import ZipFile
from io import BytesIO
from urllib.request import urlopen, Request
import time
from stqdm import stqdm


st.write(""" # Boletim de Urna - Eleições 2022 """)

@st.cache(suppress_st_warning=True)
def progresso(estado, link):
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.3)
        my_bar.progress(percent_complete + 1)

    return getBoletinsDeUrnasPorUF(estado, link)

def setEstado():
    estados = Estados()
    estados = pd.concat([pd.Series('Selecione um Estado'), pd.Series(estados.getSigla()).sort_values()])
    estado = st.selectbox(
        'Estado',
        estados
    )

    return estado

def setMunicipio(estado):
    municipios = MunicipioPorUF(estado).getNome()
    municipios = pd.concat([pd.Series('Selecione um Município'),  pd.Series(municipios).sort_values()])
    municipio = st.selectbox(
        'Município',
        municipios,
    )

    return municipio

def setZona():
    zona = st.text_input('Zona')

    return zona

def setSecao():
    secao = st.text_input('Seção')

    return secao

estado = setEstado()

if estado != 'Selecione um Estado':
    municipio = setMunicipio(estado)

    if municipio != 'Selecione um Município':
        zona = setZona()

        if zona:
            secao = setSecao()

            if secao:
                url_base = 'https://dadosabertos.tse.jus.br'
                def getBoletinsDeUrnas(urlBoletinsDeUrnas):
                    
                    boletinsDeUrnas = requests.get(urlBoletinsDeUrnas)

                    soup = BeautifulSoup(boletinsDeUrnas.text, 'lxml')

                    linksBoletinsDeUrnas = {}
                    for link in soup.find_all('a', class_='heading'):
                        title = link.get('title')
                        if 'Boletim de Urna' in title:
                            linksBoletinsDeUrnas[title[0:2]] = url_base+link.get('href')

                    return linksBoletinsDeUrnas

                urlBoletinsDeUrnas = 'https://dadosabertos.tse.jus.br/dataset/resultados-2022-boletim-de-urna'

                boletinsDeUrnas = getBoletinsDeUrnas(urlBoletinsDeUrnas)

                def getBoletinsDeUrnasPorUF(uf, link):
                    
                    boletinsDeUrnasPorUF = requests.get(link)

                    soup = BeautifulSoup(boletinsDeUrnasPorUF.text, 'lxml')

                    linkDadosBoletinsDeUrnasPorUF = soup.find('a', class_='resource-url-analytics').get('href')

                    reqDadosBoletinsDeUrnasPorUF = Request(linkDadosBoletinsDeUrnasPorUF, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36","X-Requested-With": "XMLHttpRequest"})

                    dadosBoletinsDeUrnasPorUF = urlopen(reqDadosBoletinsDeUrnasPorUF)

                    zipfile = ZipFile(BytesIO(dadosBoletinsDeUrnasPorUF.read()))

                    dadosBoletinsDeUrnasPorUF_FileName = zipfile.namelist()[0]

                    dados = pd.read_csv(zipfile.open(dadosBoletinsDeUrnasPorUF_FileName), dtype=object, encoding='iso8859-1', sep=';')

                    zipfile.close()

                    return dados

                boletinsDeUrnasPorUF = progresso(estado, boletinsDeUrnas[estado])

                boletinsDeUrnasPorUFMunicipio = boletinsDeUrnasPorUF.loc[boletinsDeUrnasPorUF['NM_MUNICIPIO'] == municipio.upper()]

                if (zona in boletinsDeUrnasPorUFMunicipio['NR_ZONA'].unique()) and (secao in boletinsDeUrnasPorUFMunicipio['NR_SECAO'].unique()):
                    boletinsDeUrnasPorUFMunicipioZonaSecao = boletinsDeUrnasPorUFMunicipio.loc[boletinsDeUrnasPorUFMunicipio['NR_ZONA'] == zona].loc[boletinsDeUrnasPorUFMunicipio['NR_SECAO'] == secao]
                    cargos = st.tabs(list(boletinsDeUrnasPorUFMunicipioZonaSecao['DS_CARGO_PERGUNTA'].unique()))

                    with cargos[0]:
                        candidatos = boletinsDeUrnasPorUFMunicipioZonaSecao.loc[boletinsDeUrnasPorUFMunicipioZonaSecao['DS_CARGO_PERGUNTA'] == 'Presidente'][['NM_VOTAVEL', 'SG_PARTIDO', 'NR_PARTIDO', 'QT_VOTOS']]

                        candidatos.rename(columns={'NM_VOTAVEL': 'Candidatos', 'SG_PARTIDO': 'Partido', 'NR_PARTIDO': 'Nº Partido', 'QT_VOTOS': 'Votos'}, inplace=True)

                        candidatos['Votos'] = candidatos['Votos'].astype(int)

                        st.table(candidatos.sort_values(by='Votos', ascending=False).reset_index(drop=True))

                        #html = candidatos.sort_values(by='Votos', ascending=False).reset_index(drop=True).to_html()

                        #html_file = open('export.html', 'w')
                        #html_file.write(html)
                        #html_file.close()

                        #pdfkit.from_file('export.html', output_path='report.pdf', configuration=config)

                    with cargos[1]:
                        candidatos = boletinsDeUrnasPorUFMunicipioZonaSecao.loc[boletinsDeUrnasPorUFMunicipioZonaSecao['DS_CARGO_PERGUNTA'] == 'Governador'][['NM_VOTAVEL', 'SG_PARTIDO', 'NR_PARTIDO', 'QT_VOTOS']]

                        candidatos.rename(columns={'NM_VOTAVEL': 'Candidatos', 'SG_PARTIDO': 'Partido', 'NR_PARTIDO': 'Nº Partido', 'QT_VOTOS': 'Votos'}, inplace=True)

                        candidatos['Votos'] = candidatos['Votos'].astype(int)

                        st.table(candidatos.sort_values(by='Votos', ascending=False).reset_index(drop=True))

                    with cargos[2]:
                        candidatos = boletinsDeUrnasPorUFMunicipioZonaSecao.loc[boletinsDeUrnasPorUFMunicipioZonaSecao['DS_CARGO_PERGUNTA'] == 'Senador'][['NM_VOTAVEL', 'SG_PARTIDO', 'NR_PARTIDO', 'QT_VOTOS']]

                        candidatos.rename(columns={'NM_VOTAVEL': 'Candidatos', 'SG_PARTIDO': 'Partido', 'NR_PARTIDO': 'Nº Partido', 'QT_VOTOS': 'Votos'}, inplace=True)

                        candidatos['Votos'] = candidatos['Votos'].astype(int)

                        st.table(candidatos.sort_values(by='Votos', ascending=False).reset_index(drop=True))

                    with cargos[3]:
                        candidatos = boletinsDeUrnasPorUFMunicipioZonaSecao.loc[boletinsDeUrnasPorUFMunicipioZonaSecao['DS_CARGO_PERGUNTA'] == 'Deputado Federal'][['NM_VOTAVEL', 'SG_PARTIDO', 'NR_PARTIDO', 'QT_VOTOS']]

                        candidatos.rename(columns={'NM_VOTAVEL': 'Candidatos', 'SG_PARTIDO': 'Partido', 'NR_PARTIDO': 'Nº Partido', 'QT_VOTOS': 'Votos'}, inplace=True)

                        candidatos['Votos'] = candidatos['Votos'].astype(int)

                        st.table(candidatos.sort_values(by='Votos', ascending=False).reset_index(drop=True))

                    with cargos[4]:
                        candidatos = boletinsDeUrnasPorUFMunicipioZonaSecao.loc[boletinsDeUrnasPorUFMunicipioZonaSecao['DS_CARGO_PERGUNTA'] == 'Deputado Estadual'][['NM_VOTAVEL', 'SG_PARTIDO', 'NR_PARTIDO', 'QT_VOTOS']]

                        candidatos.rename(columns={'NM_VOTAVEL': 'Candidatos', 'SG_PARTIDO': 'Partido', 'NR_PARTIDO': 'Nº Partido', 'QT_VOTOS': 'Votos'}, inplace=True)

                        candidatos['Votos'] = candidatos['Votos'].astype(int)

                        st.table(candidatos.sort_values(by='Votos', ascending=False).reset_index(drop=True))
                    
                    #st.write(boletinsDeUrnasPorUFMunicipioZonaSecao)
                else:
                    st.write('Verifique o número da zona e da seção e tente novamente.')