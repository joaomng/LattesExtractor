# === IMPORTAÇÕES ===
from difflib import SequenceMatcher
import os
import re
import csv
import time
import datetime
import unicodedata
import tkinter as tk
from threading import Thread
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tkinter import messagebox, scrolledtext, ttk
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# === CONFIGURAÇÃO DO NAVEGADOR ===
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# === FUNÇÕES DE NAVEGAÇÃO E INTERAÇÃO COM A PÁGINA DO CNPq ===

# Abre a página inicial do CNPq
def open_cnpq_homepage():
    print("Acessando a página do CNPq...")
    driver.get("https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar")

# Marca o checkbox para buscar todos os currículos (sem filtros)
def check_all_curricula():
    try:
        checkbox = wait.until(EC.element_to_be_clickable((By.ID, "buscarDemais")))
        checkbox.click()
        print("Checkbox 'Buscar todos os currículos' marcado.")
    except Exception as e:
        print(f"Erro ao marcar o checkbox: {e}")

# Insere um nome no campo de busca
def enter_search_name(name):
    try:
        campo_nome = wait.until(EC.presence_of_element_located((By.ID, "textoBusca")))
        campo_nome.clear()
        campo_nome.send_keys(name)
        print(f"Nome '{name}' inserido no campo de busca.")
    except Exception as e:
        print(f"Erro ao inserir nome: {e}")

# Clica no botão de buscar
def click_search_button():
    try:
        botao_buscar = wait.until(EC.element_to_be_clickable((By.ID, "botaoBuscaFiltros")))
        botao_buscar.click()
        print("Botão de busca clicado.")
    except Exception as e:
        print(f"Erro ao clicar no botão de busca: {e}")

# Conta o número de resultados retornados pela busca
def count_search_results():
    try:
        resultados = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.resultado ol li")))
        return len(resultados)
    except Exception as e:
        print(f"Erro ao contar resultados: {e}")
        return 0

# Clica no primeiro resultado retornado pela busca
def click_result_by_index(index=0):
    try:
        resultados = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.resultado ol li a")))
        if index < 0 or index >= len(resultados):
            print(f"Índice {index} fora do intervalo de resultados ({len(resultados)} encontrados).")
            return True
        resultado = resultados[index]
        driver.execute_script("arguments[0].scrollIntoView(true);", resultado)
        resultado.click()
        print(f"Resultado {index + 1} clicado.")
    except Exception as e:
        print(f"Erro ao clicar no resultado {index + 1}: {e}")
        return True

# Abre o currículo detalhado via botão
def open_lattes_cv():
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "moldal-interna")))
        time.sleep(1)
        botao_abrir = wait.until(EC.element_to_be_clickable((By.ID, "idbtnabrircurriculo")))
        driver.execute_script("arguments[0].scrollIntoView(true);", botao_abrir)
        time.sleep(0.5)
        botao_abrir.click()
        print("Currículo aberto via fluxo normal.")

        # Espera abrir uma nova aba
        wait.until(lambda d: len(d.window_handles) > 1)
        new_tab = driver.window_handles[-1]  # última aba aberta
        driver.switch_to.window(new_tab)
        print("Trocado para a nova aba do currículo.")

    except Exception as e:
        print(f"Erro ao abrir currículo: {e}")

# Fecha o modal de currículo
def close_modal():
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "moldal-interna")))
        time.sleep(1)
        botao_fechar = wait.until(EC.element_to_be_clickable((By.ID, "idbtnfechar")))
        driver.execute_script("arguments[0].scrollIntoView(true);", botao_fechar)
        time.sleep(0.5)
        botao_fechar.click()
        print("modal fechado.")
    except Exception as e:
        print(f"Erro ao abrir currículo: {e}")

# === FUNÇÕES PARA ACESSO ÀS SEÇÕES DE PRODUÇÃO ===

# Clica no link "Indicadores da Produção"
def click_production_indicators():
    try:
        iframe = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "iframe-modal")))
        driver.switch_to.frame(iframe)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        links = driver.find_elements(By.TAG_NAME, "a")

        def normalize(text):
            return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').upper().strip()

        alvo = None
        for link in links:
            if "INDICADORES DA PRODUCAO" in normalize(link.text):
                alvo = link
                break

        if not alvo:
            raise Exception("Link 'Indicadores da Produção' não encontrado!")

        driver.execute_script("arguments[0].click();", alvo)
        print("Clique realizado em 'Indicadores da Produção'.")
    except Exception as e:
        print(f"Erro ao clicar em 'Indicadores da Produção': {e}")
    finally:
        driver.switch_to.default_content()

# Seleciona o ano desejado no filtro (ou "Todos")
def select_year_filter(year="Todos"):
    try:
        iframe = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "iframe-modal")))
        driver.switch_to.frame(iframe)

        if driver.find_elements(By.XPATH, "//b[contains(text(), 'Não existem produções cadastradas para este currículo')]"):
            driver.switch_to.default_content()
            return 1

        select_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
        options = [opt.text.strip() for opt in select_element.find_elements(By.TAG_NAME, "option")]

        if str(year) not in options:
            raise ValueError(f"Ano '{year}' não está entre as opções disponíveis: {options}")

        Select(select_element).select_by_visible_text(str(year))
        print(f"Ano '{year}' selecionado com sucesso.")
    except Exception as e:
        print(f"Erro ao selecionar ano: {e}")
        if str(year).isdigit() and int(year) + 1 <= datetime.datetime.now().year:
            print(f"Selecionando ano {int(year) + 1} por padrão.")
            driver.switch_to.default_content()
            return select_year_filter(str(int(year) + 1))
        else:
            driver.switch_to.default_content()
            return 2
    finally:
        try:
            driver.switch_to.default_content()
        except:
            pass

# === FUNÇÃO PARA EXTRAÇÃO DOS DADOS DE PRODUÇÃO ===

# Extrai os dados da produção agrupando por seção (ex: Produção Bibliográfica)
def extract_sectioned_tables(name):
    results = []
    try:
        iframe = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "iframe-modal")))
        driver.switch_to.frame(iframe)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "carregando-cont-indicadores")))

        last_height = 0
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        blocos = driver.find_elements(By.CSS_SELECTOR, "div.grafico")
        print(f"Total de blocos encontrados: {len(blocos)}")
        for bloco in blocos:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", bloco)
                time.sleep(0.3)
                try:
                    titulo_secao = bloco.find_element(By.TAG_NAME, "h2").text.strip()
                except:
                    titulo_secao = "Seção Desconhecida"
                print(titulo_secao)
            except Exception as e:
                print(f"Erro ao processar bloco: {e}")
            tabelas = bloco.find_elements(By.CSS_SELECTOR, "table")
            for tabela in tabelas:
                linhas = tabela.find_elements(By.XPATH, ".//tr")
                for linha in linhas:
                    colunas = linha.find_elements(By.XPATH, ".//td")
                    if len(colunas) >= 2:
                        descricao = colunas[0].text.strip()
                        total = colunas[-1].text.strip()
                        if descricao and total:
                            results.append([name, titulo_secao, descricao, total])
        print(f"{len(results)} registros com seções extraídos. Para o nome: {name}")
        return results
    except Exception as e:
        print(f"Erro ao extrair tabelas com seções: {e}")
    finally:
        driver.switch_to.default_content()

# Extrai dos dados da formação acadêmica
def extract_degree(html: str) -> str:
    """
    Extrai o conteúdo HTML entre as duas primeiras <hr> após o elemento
    <a name="FormacaoAcademicaTitulacao">.
    """
    # Aguarda o carregamento do nome no currículo
    try: 
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h2[@class='nome']"))
        )
    except Exception as e:
        print(f"Erro ao aguardar o nome do currículo: {e}")
    soup = BeautifulSoup(html, "html.parser")

    # Localiza o <a> de referência
    anchor = soup.find("a", {"name": "FormacaoAcademicaTitulacao"})
    if not anchor:
        return ""

    # Percorre os elementos seguintes no DOM
    hr_count = 0
    content_parts = []

    for elem in anchor.next_elements:
        if getattr(elem, "name", None) == "hr":
            hr_count += 1
            if hr_count == 2:
                break
            continue
        if hr_count < 1:
            continue  # só começa após a primeira <hr>
        content_parts.append(str(elem))

    return "".join(content_parts).strip()

# === FUNÇÃO PARA SALVAR RESULTADOS EM CSV ===

# Gera um CSV com os dados extraídos
def generate_csv(data, filename="producao.csv"):
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Nome", "Categoria", "Tipo", "Quantidade"])
        for group in data:
            for row in group:
                writer.writerow(row)
    print(f"Arquivo '{filename}' gerado com sucesso!")

# Gera um CSV com as formações acadêmicas
def degree_csv(nome: str, formacoes: list[str], caminho_csv: str = "formacoes.csv"):
    """
    Cria (ou adiciona a) um arquivo CSV com duas colunas:
    Nome | Formacao

    - nome: nome da pessoa buscada
    - formacoes: lista de strings com as formações (retorno de clean_degree)
    - caminho_csv: caminho do arquivo CSV de saída
    """

    # Modo "a" (append) adiciona novas linhas se o arquivo já existir
    with open(caminho_csv, mode="a", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        
        # Escreve o cabeçalho apenas se o arquivo estiver vazio
        if arquivo.tell() == 0:
            writer.writerow(["Nome", "Formacao"])
        
        for f in formacoes:
            writer.writerow([nome, f])

## === FUNÇÕES AUXILIARES === ###

# Limpa e extrai as formações acadêmicas do HTML
def clean_degree(html: str):
    """
    Extrai e limpa as formações acadêmicas do HTML da seção 'Formação Acadêmica'
    de um currículo Lattes, parando antes de 'Formação Complementar'.
    Retorna uma lista de strings, cada uma representando uma formação completa.
    """

    soup = BeautifulSoup(html, "html.parser")

    # Extrai blocos com texto
    blocos = [b.get_text(" ", strip=True) for b in soup.find_all(["p", "div"]) if b.get_text(strip=True)]

    # Junta todo o texto
    texto_geral = " ".join(blocos)

    # Remove tudo após "Formação Complementar"
    texto_geral = re.split(r"Formação\s+Complementar", texto_geral, flags=re.IGNORECASE)[0]

    # Divide cada formação por padrão de anos (ex: 2007 - 2011)
    partes = re.split(r"(?=\b\d{4}\s*-\s*\d{4}\b)", texto_geral)

    limpas = []
    vistos = set()

    for parte in partes:
        texto = parte.strip()
        if not texto:
            continue

        # Limpeza geral
        texto = re.sub(r"\s+", " ", texto)
        texto = re.sub(r"Oasisbr|O\s*Portal\s*Brasileiro\s*de\s*Publicações.*", "", texto, flags=re.IGNORECASE)
        texto = re.sub(r"[,.]{2,}", ".", texto)
        texto = texto.strip(" ,.;")

        # Ignora textos muito curtos
        if len(texto) < 30:
            continue

        # --- 🔹 Remove repetições internas (ex: "Graduação em X. Graduação em X") ---
        frases = [f.strip() for f in re.split(r"[.]", texto) if f.strip()]
        frases_unicas = []
        vistos_local = set()
        for f in frases:
            f_norm = re.sub(r"\s+", " ", f.lower().strip())
            if f_norm not in vistos_local:
                vistos_local.add(f_norm)
                frases_unicas.append(f)
        texto = ". ".join(frases_unicas).strip()
        if not texto.endswith("."):
            texto += "."

        # Evita duplicatas entre formações
        texto_norm = re.sub(r"\s+", " ", texto.lower().strip(". ,;"))
        if texto_norm not in vistos:
            vistos.add(texto_norm)
            limpas.append(texto)

    return limpas

# Testa a similaridade entre duas strings
def similar(a: str, b: str) -> float:
    """Retorna o grau de similaridade entre duas strings (0 a 1)."""
    return SequenceMatcher(None, a, b).ratio()

# Tira as duplicatas (inclusive similares) de uma lista de strings
def remove_duplicates(text_list: list[str], threshold: float = 0.9) -> list[str]:
    """
    Remove duplicatas (inclusive similares) de uma lista de strings.
    threshold define o quão parecidas duas entradas precisam ser para serem consideradas iguais.
    """
    cleaned = []
    for text in text_list:
        # Normaliza espaços e letras
        normalized = " ".join(text.split()).strip().lower()
        
        # Só adiciona se não for muito parecido com algo já guardado
        if not any(similar(normalized, existing.lower()) > threshold for existing in cleaned):
            cleaned.append(text.strip())
    return cleaned

### === FLUXO DE BUSCA PARA LISTA DE NOMES === ###

#
def degree_search(name):
    """Função principal para buscar e extrair formações acadêmicas de um nome."""
    for i in range(count_search_results()):
        click_result_by_index(i)
        open_lattes_cv()
        dados = extract_degree(driver.page_source)
        degree_csv(name if i == 0 else name+f"({i})", remove_duplicates(clean_degree(dados), threshold=0.8))
        driver.close()  # Fecha aba do currículo
        driver.switch_to.window(driver.window_handles[0])  # Volta à busca
        close_modal()
        time.sleep(2)

# Continua a busca para múltiplos resultados
def continue_search(name, year, progress_callback, i, total, index):
    if click_result_by_index(index): 
            results.append([[name, 'Usuario não encontrado', '', '']])
            if progress_callback:
                progress_callback(i, total)
            return 1
    click_production_indicators()
    match select_year_filter(year):
        case 1:
            results.append([[name, 'Nenhuma produção encontrada', '', '']])
            if progress_callback:
                progress_callback(i, total)
            return 1
        case 2:    
            results.append([[name, f'Não tem produções pós {year}', '', '']])
            if progress_callback:
                progress_callback(i, total)
            return 1        
    results.append(extract_sectioned_tables(name))
    if progress_callback:
        progress_callback(i, total)


results = []
# Executa a automação completa para uma lista de nomes
def run_search(name_list, year="Todos", progress_callback=None):
    total = len(name_list)
    for i, name in enumerate(name_list, 1):
        os.system('cls' if os.name == 'nt' else 'clear')
        open_cnpq_homepage()
        check_all_curricula()
        enter_search_name(name)
        click_search_button()
        x = count_search_results()
        print(f"Resultados encontrados para '{name}': {x}")
        if switch_var.get():
            print("Modo Formação Ativado")
            degree_search(name)
            if progress_callback:
                progress_callback(i, total) 
            continue
        if x > 1:
            for a in range(0,x):
                if continue_search(name + f" ({a+ 1})", year, progress_callback, i, total, a) == 1:
                    close_modal() 
                    continue    
                close_modal()
        else:
            if continue_search(name, year, progress_callback, i, total, 0) == 1:
                continue    
            # close_modal()
    if switch_var.get():        
        print("Arquivo formacao.csv gerado com sucesso!")
    else:
        generate_csv(results)
 
# === INTERFACE GRÁFICA (TKINTER) ===

# Inicia a busca ao clicar no botão da interface
def start_gui_search():
    nomes_texto = entrada_nomes.get("1.0", tk.END).strip()
    nomes = [nome.strip() for nome in nomes_texto.split("\n") if nome.strip()]
    if not nomes:
        messagebox.showwarning("Aviso", "Insira ao menos um nome.")
        return

    ano = ano_var.get()
    status_label.config(text="Iniciando busca...")
    btn_iniciar.config(state=tk.DISABLED)
    progresso_bar["value"] = 0
    progresso_bar["maximum"] = len(nomes)

    def update_progress(current, total):
        progresso_bar["value"] = current
        status_label.config(text=f"Processando {current}/{total}...")

    def task():
        try:
            run_search(nomes, ano, progress_callback=update_progress)
            status_label.config(text="Busca finalizada com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            status_label.config(text="Erro durante a busca.")
        finally:
            btn_iniciar.config(state=tk.NORMAL)

    Thread(target=task).start()

# === CONSTRUÇÃO DA JANELA PRINCIPAL ===

janela = tk.Tk()
janela.title("Extrator CNPq - Produção Lattes")
janela.geometry("500x500")

tk.Label(janela, text="Digite os nomes (um por linha):").pack(pady=5)
entrada_nomes = scrolledtext.ScrolledText(janela, width=60, height=10)
entrada_nomes.pack()

tk.Label(janela, text="Pesquisar as produções a partir do ano:").pack(pady=5)
ano_var = tk.StringVar(value="Todos")
anos_opcoes = ["Todos"] + [str(ano) for ano in range(int((datetime.datetime.now()).year)-1, 1998, -1)]
ano_menu = tk.OptionMenu(janela, ano_var, *anos_opcoes)
ano_menu.pack()

style = ttk.Style()
style.configure("Switch.TCheckbutton",
                foreground="black",
                background=janela["bg"],
                font=("Arial", 10))
style.map("Switch.TCheckbutton",
          foreground=[('selected', 'white')],
          background=[('selected', '#4caf50')])

switch_var = tk.BooleanVar(value=False)


switch = ttk.Checkbutton(
    janela,
    text="Modo Formação/Produção",
    style="Switch.TCheckbutton",
    variable=switch_var,
    command=lambda: label_modo.config(
        text="Extração de Formação" if switch_var.get() else "Extração de Produção"
    )
)
switch.pack(pady=5)

label_modo = tk.Label(janela, text="Extração de Produção")
label_modo.pack(pady=5)

btn_iniciar = tk.Button(janela, text="Iniciar Extração", command=start_gui_search)
btn_iniciar.pack(pady=10)

progresso_bar = ttk.Progressbar(janela, orient="horizontal", length=400, mode="determinate")
progresso_bar.pack(pady=10)

status_label = tk.Label(janela, text="Aguardando...")
status_label.pack()

janela.mainloop()
