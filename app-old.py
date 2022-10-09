import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
from zipfile import ZipFile
from io import BytesIO
from urllib.request import urlopen, Request
#import pdfkit

#path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
#config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

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

def setUF(UFs):
    uf = st.selectbox(
        'Estado:',
        UFs
    )

    return uf

uf = setUF(boletinsDeUrnas.keys())

def getBoletinsDeUrnasPorUF(uf, link):
    
    boletinsDeUrnasPorUF = requests.get(link)

    soup = BeautifulSoup(boletinsDeUrnasPorUF.text, 'lxml')

    linkDadosBoletinsDeUrnasPorUF = soup.find('a', class_='resource-url-analytics').get('href')

    #reqDadosBoletinsDeUrnasPorUF = Request(linkDadosBoletinsDeUrnasPorUF, headers={'User-Agent': 'Mozilla/5.0'})

    reqDadosBoletinsDeUrnasPorUF = Request(linkDadosBoletinsDeUrnasPorUF, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36","X-Requested-With": "XMLHttpRequest"})

    dadosBoletinsDeUrnasPorUF = urlopen(reqDadosBoletinsDeUrnasPorUF)

    zipfile = ZipFile(BytesIO(dadosBoletinsDeUrnasPorUF.read()))

    dadosBoletinsDeUrnasPorUF_FileName = zipfile.namelist()[0]

    dados = pd.read_csv(zipfile.open(dadosBoletinsDeUrnasPorUF_FileName), dtype=object, encoding='iso8859-1', sep=';')

    zipfile.close()

    return dados

boletinsDeUrnasPorUF = getBoletinsDeUrnasPorUF(uf, boletinsDeUrnas[uf])

def setMunicipio(municipios):
    municipio = st.selectbox(
        'Município:',
        municipios
    )

    return municipio

municipio = setMunicipio(boletinsDeUrnasPorUF['NM_MUNICIPIO'].sort_values().unique())

boletinsDeUrnasPorUFMunicipio = boletinsDeUrnasPorUF.loc[boletinsDeUrnasPorUF['NM_MUNICIPIO'] == municipio]

def setZona(zonas):
    zona = st.selectbox(
        'Zona:',
        zonas
    )

    return zona

zona = setZona(boletinsDeUrnasPorUFMunicipio['NR_ZONA'].sort_values().unique())

boletinsDeUrnasPorUFMunicipioZona = boletinsDeUrnasPorUFMunicipio.loc[boletinsDeUrnasPorUFMunicipio['NR_ZONA'] == zona]

def setSecao(secoes):
    secao = st.selectbox(
        'Zona:',
        secoes
    )

    return secao

secao = setSecao(boletinsDeUrnasPorUFMunicipioZona['NR_SECAO'].sort_values().unique())

boletinsDeUrnasPorUFMunicipioZonaSecao = boletinsDeUrnasPorUFMunicipioZona.loc[boletinsDeUrnasPorUFMunicipioZona['NR_SECAO'] == secao]


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