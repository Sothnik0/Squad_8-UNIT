# Squad_8-UNIT

## Como rodar o backend

1. Abra um terminal na pasta `backend`.
2. Ative o ambiente virtual.
3. Inicie o servidor FastAPI com Uvicorn.

### PowerShell

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

O backend ficara disponivel em:

- `http://127.0.0.1:8000`
- docs interativa: `http://127.0.0.1:8000/docs`

## Como rodar o frontend

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

O frontend ficara disponivel em:

- `http://127.0.0.1:5173`

## Observacoes

- O backend usa variaveis de ambiente em `backend/.env`.
- Para OCR, configure `OCR_API_KEY`.
- A camada complementar de IA pode usar `GEMINI_API_KEY` ou `GOOGLE_API_KEY` quando houver quota disponivel.
# 🚀 Squad 8 - UNIT

Um projeto fullstack com backend em **FastAPI** e frontend em **Vue.js**, focado em análise de documentos utilizando IA.

---

## 📌 Visão Geral

Este sistema permite o envio de arquivos (como documentos) para análise automatizada utilizando inteligência artificial (integração com API Gemini).

O fluxo básico funciona assim:

1. Usuário envia um documento pelo frontend
2. O backend processa e valida os dados
3. A IA analisa o conteúdo
4. O resultado é retornado para o usuário

---

## 🧠 Tecnologias Utilizadas

### Backend

* Python
* FastAPI
* Pydantic
* Google Gemini API
* Dotenv

### Frontend

* Vue 3
* TypeScript
* Vite
* Cypress (testes)

---

## 📁 Estrutura do Projeto

```
Squad_8-UNIT/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── testar_api.py
│   └── .env.example
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
└── README.md
```

---

## ⚙️ Como Rodar o Projeto

### 🔧 Backend

1. Acesse a pasta:

```
cd backend
```

2. Crie um ambiente virtual:

```
python -m venv venv
```

3. Ative o ambiente:

* Windows:

```
venv\Scripts\activate
```

* Linux/Mac:

```
source venv/bin/activate
```

4. Instale as dependências:

```
pip install -r requirements.txt
```

5. Configure o arquivo `.env`:

```
OCR_API_KEY=sua_chave_ocr_space
GEMINI_API_KEY=sua_chave_gemini
GEMINI_MODEL=gemini-2.5-flash-lite
```

6. Rode o servidor:

```
uvicorn app.main:app --reload
```

---

### 🎨 Frontend

1. Acesse a pasta:

```
cd frontend
```

2. Instale as dependências:

```
npm install
```

3. Rode o projeto:

```
npm run dev
```

---

## 🔗 Comunicação entre Frontend e Backend

Certifique-se de que o backend está rodando antes de iniciar o frontend.

Por padrão, o backend roda em:

```
http://localhost:8000
```

---

## 📬 Endpoint Principal

### POST `/analisar`

Envia um documento para análise.

#### Exemplo de corpo da requisição:

```json
{
  "solicitante": "João",
  "departamento": "Financeiro",
  "tipo_documento": "Nota Fiscal",
  "descricao": "Documento para validação",
  "arquivo": {
    "nome": "doc.pdf",
    "tipo_mime": "application/pdf",
    "tamanho_bytes": 12345,
    "conteudo_base64": "..."
  }
}
```

---

## 🧪 Testes

O frontend utiliza **Cypress** para testes end-to-end.

Para rodar:

```
npx cypress open
```

---

## 🧩 Possíveis Melhorias

* Autenticação de usuários
* Dashboard com histórico de análises
* Upload de múltiplos arquivos
* Melhor tratamento de erros
* Logs estruturados

---

## 👥 Equipe

Projeto desenvolvido pelo Squad 8.

---

## 📄 Licença

Este projeto é apenas para fins educacionais.
