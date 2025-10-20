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

# ToDo
# Tirar a parte da coleta do endereço (feito)
# Alterar o cabeçalho no caso da formação pra ser "Nome, Maior titulação, Curso de graduação"  (feito)

# Modificar o cleaner degree pra pegar so a maior titulação e o curso de graduação  
#    A ideia é pra cada nome, retornar uma lista do tipo ["Doutorado. Grande área: Ciências Exatas e da Terra", "Graduação em Matemática"]

# Modificar o que se faz com o retorno do clean degree pra colocar essas informações no csv. (feito - conferir) 
#   Note que idealmente será uma linha por nome






# === CONFIGURAÇÃO DO NAVEGADOR ===
options = Options()
options.add_argument("--start-maximized")
# options.add_argument('--headless') # descomente se quiser rodar em background
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
            return False
        except Exception as e:
            print(f"Erro ao abrir currículo: {e}")
            return True

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
        print(f"Erro ao fechar o modal: {e}")

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

# === FUNÇÃO PARA EXTRAÇÃO DOS DADOS ===

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

# Extrai dos dados do curriculo de acordo com a seção desejada #extract_curriculum(section="Endereco") extract_curriculum(section="FormacaoAcademicaTitulacao")
def extract_curriculum(html: str, section: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    anchor = soup.find("a", {"name": section})
    if not anchor:
        return ""

    # Encontra os <hr> seguintes
    hrs = anchor.find_all_next("hr")
    if len(hrs) < 2:
        return ""

    # Pega tudo entre o 1º e o 2º <hr>
    content = []
    for elem in hrs[0].next_siblings:
        if elem == hrs[1]:
            break
        content.append(str(elem))

    return "".join(content).strip()


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
def degree_csv(nome: str, formacoes: list[str], endereco: str='', caminho_csv: str = "formacoes.csv"):
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
            writer.writerow(["Nome", "Maior titulação", "Curso de graduação"])
        
        for f in formacoes:
            writer.writerow([nome, f, endereco])

## === FUNÇÕES AUXILIARES === ###

def cleaner_degree(lista, instituicao=True):
    """
    recebe uma lista de strings (a retornada por clean_degree). Cada string
    é uma formação completa da mesma pessoa. (OBS: o texto ainda tem maiúsculas e acentos)
    
    No caso que realmente precisamos é da GRANDE ÁREA DA MAIOR TITULAÇÃO
    E NOME DO CURSO DE GRADUAÇÃO. Mas por via das dúvidas vou colocar tanto 
    o nome da maior titulação "doutorado, mestrado, especialização, etc", 
    quanto a grande área.

    Retorna uma lista com a maior titulação e o nome do curso de graduação
    exemplo: ["Doutorado. Grande área: Ciências Exatas e da Terra", "Graduação em Matemática"] 
    """
    
    lista_final = []

    graduacao = ""
    maior_titulo = ""
    grande_area = ""

    ranking_titulacao = ["doutorado", "mestrado", "especialização"] # falta terminar esse ranking
    #vou usar pra dps que coletar todas as titulações da formação completa, descobrir qual é a maior.
    #A partir da maior vou descobrir qual é a grande área.
    #Enquanto isso, se eu encontrar graduação vou salvar em "graduação"
    #IMPORTANTE: o que fazer se tiver mais de uma graduação?
    #    Enquanto não tenho resposta oficial vou fazendo graduacao += texto+"; "
    #    onde texto é algo do tipo "Graduação em Ciências atuariais"  

    

    if(len(lista)>0):             
    
        for formacao in lista:

            string_final=""

            frases = formacao.split(".")

            if(len(frases)>0):

                frase = frases[0]
                #adicionando a segunda frase, que normalmente é a instituição
                #mas só se a flag instituicao estiver ativada
                if instituicao and len(frases)>1:
                    frase = frase +"."+ frases[1]
                
                string_final += frase +". "#"ano tal - ano tal Doutorado em tal coisa"

                i = 1

                #procurando a grande área
                while(i<len(frases)):
                    frase = frases[i]
                    if(frase.find("Grande área") != -1): #==0?
                        #é pq encontramos a grande área

                        string_final +=  frase + "."
                        break

                    i+=1



            else: #a formacao por algum motivo nao tinha nem ponto final
                string_final = formacao #vou manter igual por via das dúvidas

        
            #if(appendar ==1):
                #lista_final.append(string_final)

            lista_final.append(string_final)

    return lista_final


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

# Limpa o HTML do endereço profissional
def clean_address(html: str) -> str:
    """
    Limpa o HTML do endereço profissional do currículo Lattes,
    removendo tags e repetições e formatando o texto.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Extrai texto plano (mantendo <br> como quebra de linha)
    for br in soup.find_all("br"):
        br.replace_with("\n")

    texto = soup.get_text(" ", strip=True)

    # Remove repetições da expressão "Endereço Profissional"
    texto = re.sub(r"(Endere[cç]o\s+Profissional\s*)+", "", texto, flags=re.IGNORECASE)

    # Remove múltiplos espaços e espaços antes de pontuação
    texto = re.sub(r"\s{2,}", " ", texto)
    texto = re.sub(r"\s+([.,;:])", r"\1", texto)

    # Corrige quebras de linha excessivas
    texto = re.sub(r"\n{2,}", "\n", texto)

    # Organiza visualmente
    texto = texto.replace(". ", ".\n")
    texto = texto.replace("Telefone:", "\nTelefone:")
    texto = texto.replace("Fax:", "\nFax:")
    texto = texto.replace("URL da Homepage:", "\nURL da Homepage:")
    # x = texto.split("\n")
    # texto = x[0]

    return texto.strip()

# Testa a similaridade entre duas strings
def similar(a: str, b: str) -> float:
    """Retorna o grau de similaridade entre duas strings (0 a 1)."""
    return SequenceMatcher(None, a, b).ratio()

# Tira as duplicatas (inclusive similares) de uma lista de strings
def remove_duplicates(text_list: list[str], threshold: float = 0.90) -> list[str]:
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

#Continua a busca para múltiplos resultados com a opção de formação ativada
def degree_search(name):
    """Função principal para buscar e extrair formações acadêmicas de um nome."""

    for i in range(count_search_results()):
        if click_result_by_index(i): 
            degree_csv(name if i == 0 else name+f"({i})", ['Index não encontrado'], '')
            continue
        if open_lattes_cv():
            degree_csv(name if i == 0 else name+f"({i})", ['Erro na Abertura do Currículo'], '')
            continue
        formation = extract_curriculum(driver.page_source, "FormacaoAcademicaTitulacao")
        adress = extract_curriculum(driver.page_source, "Endereco")
        cleaner_formation = cleaner_degree(clean_degree(formation), instituicao=False) #se tudo der certo o cleaner degree só vai retornar uma lista com dois valores mesmo

        degree_csv(name if i == 0 else name+f"({i})", cleaner_formation[0], cleaner_formation[1]) #nome, maior titulação, curso de graduação
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
    # Deletar o arquivo CSV
    if os.path.exists("formacoes.csv"):
        os.remove("formacoes.csv")
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
            if x == 0:
                degree_csv(name, ['Usuario não encontrado'], '')
                if progress_callback:
                    progress_callback(i, total) 
                continue
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
