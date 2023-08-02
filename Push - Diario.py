import time
import os
import pdfplumber
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta
from escavador import *

def configure_browser_download_path(download_path):
    # Configuração para abrir o navegador em modo oculto (headless)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    # Configura a pasta de downloads para a pasta do script
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    # Inicializa o navegador (Chrome)
    driver = webdriver.Chrome(options=options)
    return driver

def wait_for_pdf_to_download(download_path, timeout=60):
    waited_time = 0
    while not any(fname.lower().endswith('.pdf') for fname in os.listdir(download_path)):
        time.sleep(1)
        waited_time += 1
        if waited_time > timeout:
            raise TimeoutError("O download do arquivo PDF excedeu o tempo limite.")

def consultar_api(numero):
    config("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZGI3OWIyZDhkZjhlNmRiMmFlMGI4NzhjOTllMDg0MDVjODE4MDcwMzc2NjU2Mzc4ZGI5OGVmNTE5OWJjOWIwNWZjNzkxN2NhMDY0MDIyY2YiLCJpYXQiOjE2OTA0ODEwOTcuODg0MzI2LCJuYmYiOjE2OTA0ODEwOTcuODg0MzI3LCJleHAiOjIwMDYxMDAyOTcuODgyNjA5LCJzdWIiOiIxNDY1MjQ3Iiwic2NvcGVzIjpbImFjZXNzYXJfYXBpX3BhZ2EiXX0.Agnz6cxWgICkxA9RyEQoKoZKKruO_Qg24CkuFVB89pjLGnw7PW9UegeX6-fsRAlFNRSuS8V7sDMA4XAqKFzB2PPc_KPs8IAowjbpNkiJ4M47N6flFJGHD0ocw7z-FLKyxVbghle1z_jUovvOarO3kg6R9IEl9f0YARm3yE7kTp-R8uWwvAyCGvfhGvKQ3x1j-MyDO8zwHAtwDhCNuXpOt9exiD8eP2cpKnoolKW0HHgtO6KGBMPi6RQ3f8wYykC54MFSLl1s0Fl6TrbHLdbZZE89g-4JQjc4fbHKzNlF6y75TSUq4d1a8ONk9kYjvKQUM3GHTIIadrXvIvrv_YDee4sImR6MtAoVOfVYMIEpzQ9I5oo8GiG_8hv5qSuZTBB2hPaRyu0nCCH-p_yZeoYuqaQkaxwWi7UFtNNkbvXaY5CbOJlqnWvh9mwFcmfFM2dzitvYl_Ktfu7TUCEoHVfEHSVi3p0_icJ3-XGMnXYgYJRnsf39wFPnh6L8fF9lf8KaGP_y_lVHAvx5i2rfMO-7n_AAaHxbKI48Iu35OeBwRemwvmhYGeyjnJiMI_7TyIPH9jicFlglLvmHB4qM0KfWZ91A33M1G-PErIBErpJgvezP41W1WFcRS59Pg3pK1uNN3otBfT2gRkgllKXSvslR9nXv7z32lYPBWK72zjCKGJw")
    return Processo.processo_por_numero_em_diarios(numero)

if __name__ == "__main__":
    print("Weverton Gostosão está trabalhando pra você aguarde...")
    url = "https://dejt.jt.jus.br/dejt/f/n/diariocon"
    opcao_menu = "Judiciário"
    opcao_menu2 = "TRT 7ª Região"

    # Configura a pasta de downloads para a pasta raiz do script
    script_path = os.path.dirname(os.path.abspath(__file__))
    download_path = script_path

    driver = configure_browser_download_path(download_path)

    try:
        wait = WebDriverWait(driver, 10)

        driver.get(url)

        time.sleep(2)

        data_atual = datetime.today()
        data_anterior = data_atual - timedelta(days=1)
        data_anterior_formatada = data_anterior.strftime('%d-%m-%Y')

        campo_data_inicio = driver.find_element(By.NAME, 'corpo:formulario:dataIni')
        campo_data_inicio.clear()  
        campo_data_inicio.send_keys(data_anterior_formatada)

        campo_data_fim = driver.find_element(By.NAME, 'corpo:formulario:dataFim')
        campo_data_fim.clear()
        campo_data_fim.send_keys(data_anterior_formatada)

        menu_tipo_caderno = Select(driver.find_element(By.ID, 'corpo:formulario:tipoCaderno'))
        menu_tipo_caderno.select_by_visible_text(opcao_menu)
        menu_tipo_caderno = Select(driver.find_element(By.ID, 'corpo:formulario:tribunal'))
        menu_tipo_caderno.select_by_visible_text(opcao_menu2)

        botao_search = driver.find_element(By.ID, 'corpo:formulario:botaoAcaoPesquisar')
        botao_search.click()

        time.sleep(5)

        botao_download = driver.find_element(By.XPATH, '//*[@id="diarioCon"]/fieldset/table/tbody/tr[2]/td[3]/button')
        botao_download.click()

        wait_for_pdf_to_download(download_path)

        # Localiza o arquivo PDF baixado na pasta de downloads do navegador
        nome_arquivo_pdf = next(fname for fname in os.listdir(download_path) if fname.lower().endswith('.pdf'))
        caminho_arquivo_pdf = os.path.join(download_path, nome_arquivo_pdf)

        #######################################################################
        # Extrair e armazenar os números no formato "0001302-80.2015.5.07.0014"
        #######################################################################

        padrao_termo_unico = r"ATSum-\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4}"

        numeros_encontrados = set()

        with pdfplumber.open(caminho_arquivo_pdf) as pdf:
            for num_pagina in range(25):  # Limita a leitura até a página 25
                page = pdf.pages[num_pagina]
                texto_pagina = page.extract_text()

                # Procurar o termo no formato ATSUM
                for match in re.finditer(padrao_termo_unico, texto_pagina):
                    termo_encontrado = match.group()
                    numeros_termo = re.search(r"\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4}", termo_encontrado)
                    if numeros_termo:
                        numeros_encontrados.add(numeros_termo.group())

        if numeros_encontrados:
            print("Números encontrados:")
            for numero in numeros_encontrados:
                response = consultar_api(numero)
                print(response)
        else:
            print("Nenhum número no formato '0001302-80.2015.5.07.0014' foi encontrado nas primeiras 25 páginas do arquivo PDF.")
        
        os.remove(caminho_arquivo_pdf)

    finally:
        driver.quit()