# 📋 CNPq Lattes Production Extractor

Este projeto automatiza a busca de currículos na base de dados do **CNPq (Plataforma Lattes)** e extrai as produções acadêmicas (bibliográficas, técnicas, artísticas, etc.) de pesquisadores informados pelo nome.

A ferramenta é acessível via **interface gráfica (GUI)** construída com `Tkinter` e realiza a automação utilizando `Selenium`.

---

## 🚀 Funcionalidades

* Busca automática de currículos Lattes por nome.
* Abre a seção "Indicadores da Produção" do pesquisador.
* Seleciona o ano desejado (ou todos os anos).
* Extrai todas as categorias e subcategorias de produção.
* Gera um arquivo `.csv` com os dados formatados.
* Interface simples e amigável para múltiplos nomes.

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
* Escolha o ano inicial de produção (ou "Todos").
* Clique em **"Iniciar Extração"**.

3. O sistema buscará cada currículo, extrairá os dados e salvará um arquivo chamado:

```
producao.csv
```

---

## 📍 Estrutura do CSV gerado

O arquivo gerado contém os seguintes campos:

| Nome            | Categoria              | Tipo                                       | Quantidade |
| --------------- | ---------------------- | ------------------------------------------ | ---------- |
| Fulano da Silva | Produção Bibliográfica | Artigos completos publicados em periódicos | 12         |
| Fulano da Silva | Produção Técnica       | Desenvolvimento de material didático       | 3          |
| ...             | ...                    | ...                                        | ...        |

---

## 🛥️ Possíveis erros e soluções

| Erro                                                | Solução                                                                                  |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `selenium.common.exceptions.NoSuchElementException` | Certifique-se de que a página está carregando corretamente e o nome pesquisado é válido. |
| Janela branca ou sem resposta                       | Verifique se o ChromeDriver está atualizado e compatível com o navegador.                |

---

## 📌 Observações

* O sistema **não usa login**, pois acessa apenas informações públicas dos currículos.
* Não há limitação de nomes, mas para grandes volumes, o tempo de execução pode ser longo.

---

## 📃 Licença

Este projeto é livre para fins acadêmicos e educacionais. Modificações são bem-vindas!

---

## 🙋‍♂️ Suporte

Se tiver dúvidas ou quiser sugestões de melhorias, fique à vontade para abrir uma **issue** ou entrar em contato.
