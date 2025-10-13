# 📋 CNPq Lattes Production Extractor

Esta ferramenta automatiza a busca de currículos na base de dados do CNPq (Plataforma Lattes) e extrai tanto as produções acadêmicas quanto as formações acadêmicas de pesquisadores informados pelo nome.

A ferramenta é acessível via **interface gráfica (GUI)** construída com `Tkinter` e realiza a automação utilizando `Selenium`.

---

## 🚀 Funcionalidades

* Busca automática de currículos Lattes por nome.
* Extrai Produções Acadêmicas:
  * Seleciona o ano desejado (ou todos os anos).
  * Extrai categorias e subcategorias de produção.
  * Gera um arquivo .csv com os dados formatados.
* Extrai Formações Acadêmicas:
  * Localiza a seção "Formação acadêmica/titulação".
  * Limpa duplicações e textos irrelevantes.
  * Salva em arquivo .csv separado.
* Interface simples e amigável para múltiplos nomes.
* Permite alternar entre modo Produção ou modo Formação.

---

## 🛠️ Pré-requisitos

* **Python 3.8+**
* **Google Chrome** instalado
* **[ChromeDriver](https://chromedriver.chromium.org/downloads)** compatível com sua versão do Chrome

---

## 📆 Instalação

1. Clone este repositório:

```bash
git clone https://github.com/FilipeGH03/LattesExtractor.git
cd LattesExtractor
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```
---

## ▶️ Como usar

1. Execute o script principal:

```bash
python consultaLattes.py
```

2. A interface gráfica será aberta. Siga os passos:

* Insira os nomes dos pesquisadores (um por linha).
* Selecione o modo de busca.
* Escolha o ano inicial de produção (ou "Todos").
* Clique em **"Iniciar Extração"**.

3. O sistema buscará cada currículo, extrairá os dados e salvará um arquivo chamado:


```
producao.csv #para a busca de produções 
formacao.csv #para a busca de formações
```
---

## 📍 Estrutura do CSV gerado

O arquivo gerado contém os seguintes campos:
                                                          
**producao.csv – 📊 Produções Acadêmicas**

| Nome            | Categoria              | Tipo                                       | Quantidade |
| --------------- | ---------------------- | ------------------------------------------ | ---------- |
| Fulano da Silva | Produção Bibliográfica | Artigos completos publicados em periódicos | 12         |
| Fulano da Silva | Produção Técnica       | Desenvolvimento de material didático       | 3          |
| ...             | ...                    | ...                                        | ...        |

**formaca.csv – 🎓 Formações Acadêmicas**

| Nome            | Formação                                                                 |
| --------------- | ------------------------------------------------------------------------ |
| Fulano da Silva | Graduação em Ciência da Computação - Universidade XYZ - 2007-2011        |
| Fulano da Silva | Mestrado em Inteligência Artificial - Universidade ABC - 2012-2014       |
| ...             | ...                                                                      |

---

## 🛥️ Possíveis erros e soluções

| Erro                                    | Solução                                                                 |
| --------------------------------------- | ---------------------------------------------------------------------- |
| `selenium.common.exceptions.NoSuchElementException` | Certifique-se de que a página está carregando corretamente e o nome pesquisado é válido. |
| Janela branca ou sem resposta           | Verifique se o ChromeDriver está atualizado e compatível com o navegador. |
| Currículo sem seção de Formação         | O pesquisador não possui formações cadastradas publicamente.           |
| Aba de currículo não abre               | Verifique se o ChromeDriver está atualizado e compatível com o Chrome. |


---

## 📌 Observações

* O sistema **não usa login**, pois acessa apenas informações públicas dos currículos.
* Não há limitação de nomes, mas para grandes volumes, o tempo de execução pode ser longo.
* É possível alternar entre Extração de Produção e Extração de Formação pelo interruptor na interface.
---

## 📃 Licença

Este projeto é livre para fins acadêmicos e educacionais. Modificações são bem-vindas!

---

## 🙋‍♂️ Suporte

Se tiver dúvidas ou quiser sugestões de melhorias, fique à vontade para abrir uma **issue** ou entrar em contato.
