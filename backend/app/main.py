import base64
import time  # <--- ADICIONADO: Para medir o tempo de resposta
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import config  # noqa: F401
from app.services.document_analysis import build_analysis

app = FastAPI(title="Verify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (Suas classes DocumentFile, AnalysisRequest, Finding e AnalysisResponse permanecem iguais)

@app.get("/")
def home():
    return {"msg": "API estruturada", "service": "Verify API"}

@app.post("/analises/documento", response_model=AnalysisResponse)
def analyze_document(payload: AnalysisRequest):
    start_time = time.time()  # <--- ADICIONADO: Inicia o cronômetro
    
    file = payload.arquivo
    if file.tipo_mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Formato nao suportado. Envie PDF, JPG, JPEG ou PNG.",
        )

    if file.tamanho_bytes > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Arquivo maior que 10MB.")

    try:
        decoded = base64.b64decode(file.conteudo_base64, validate=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Arquivo invalido.") from exc

    if len(decoded) != file.tamanho_bytes:
        raise HTTPException(
            status_code=400,
            detail="Tamanho do arquivo nao confere com o conteudo enviado.",
        )

    protocol = datetime.now(timezone.utc).strftime("ANL-%Y%m%d-%H%M%S")
    
    # Chama o serviço de análise que utiliza o Gemini e OCR
    report = build_analysis(
        protocolo=protocol,
        solicitante=payload.solicitante.strip(),
        departamento=payload.departamento.strip(),
        tipo_documento=payload.tipo_documento,
        descricao=payload.descricao.strip(),
        file_name=file.nome,
        mime_type=file.tipo_mime,
        file_data_base64=file.conteudo_base64,
        file_size_bytes=file.tamanho_bytes,
    )

    # <--- ADICIONADO: Lógica de Log de Auditoria
    duration = time.time() - start_time
    with open("auditoria_ia.log", "a") as f:
        log_entry = f"{datetime.now()}: {protocol} | Doc: {payload.tipo_documento} | Tempo: {duration:.2f}s | Status: {report.status}\n"
        f.write(log_entry)

    return AnalysisResponse(
        protocolo=report.protocolo,
        status=report.status,
        probabilidade_fraude=report.probabilidade_fraude,
        resumo=report.resumo,
        dados_chave=[Finding(**item) for item in report.dados_chave],
        verificacoes_oficiais=[Finding(**item) for item in report.verificacoes_oficiais],
        alertas=report.alertas,
        fatores_score=report.fatores_score,
        proximos_passos=report.proximos_passos,
        motor_extracao=report.motor_extracao,
        texto_extraido=report.texto_extraido,
    )
