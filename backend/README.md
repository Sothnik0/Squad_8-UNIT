# 🛡️ Squad 8 - Backend: Sistema de Análise de Documentos (IA)

Este é o servidor backend do projeto da Squad 8 (UNIT), desenvolvido em **Python** utilizando **FastAPI**. O sistema é responsável por receber documentos, processar imagens via IA (Google Gemini) e validar dados em APIs oficiais (BrasilAPI).

## 🚀 Tecnologias Utilizadas

* **FastAPI**: Framework web de construção de APIs de alta performance.
* **Google Gemini API (2.0 Flash)**: Inteligência Artificial para análise visual e extração de dados.
* **Pydantic**: Validação de dados e tipagem estática.
* **Uvicorn**: Servidor ASGI leve e rápido para rodar a aplicação em Python.
* **BrasilAPI**: Integração para validação de status de CNPJs em tempo real.

---

## 🛠️ Pré-requisitos

Antes de começar, você precisará ter instalado em sua máquina:
* [Python 3.10 ou superior](https://www.python.org/downloads/)
* Uma chave de API válida gerada no [Google AI Studio](https://aistudio.google.com/)

---

## 📥 Instalação e Configuração

Siga o passo a passo abaixo para rodar o backend localmente:

1. **Acesse a pasta do backend:**
   ```bash
   cd backend

2. **Crie um ambiente virtual (venv)**
    python -m venv .venv

3. **Ative o ambiente virtual**
    Windows = .venv\Scripts\activate

    Linux/macOS = source .venv/bin/activate

4. **Instale as dependências do projeto**
    pip install fastapi uvicorn google-genai python-dotenv requests pydantic


## ⚙️ Variáveis de Ambiente
Para que o sistema consiga se comunicar com a inteligência artificial, você precisa configurar a sua chave de acesso.

---

1. **Na raiz da pasta backend, crie um arquivo chamado .env.**

2. **Adicione a seguinte linha dentro dele, substituindo pela sua chave real**
    GEMINI_API_KEY=SUA_CHAVE_AQUI


## 🏃 Como Rodar o Servidor
Com o ambiente ativado e as dependências instaladas, inicie o servidor executando

    uvicorn app.main:app --reload

    O servidor estará rodando em: http://127.0.0.1:8000

    Documentação Swagger: http://127.0.0.1:8000/docs


## 🧪 Como Testar a API
Com o servidor rodando em um terminal, abra outro terminal, ative o .venv e rode o teste:

    python app/testar_api.py