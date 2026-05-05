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
