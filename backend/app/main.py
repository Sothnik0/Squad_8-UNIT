import base64
import time  # <--- ADICIONADO: Para medir o tempo de resposta
import logging
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

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}

MAX_FILE_SIZE = 10 * 1024 * 1024

class DocumentFile(BaseModel):
    nome: str
    tipo_mime: str
    tamanho_bytes: int
    conteudo_base64: str

class AnalysisRequest(BaseModel):
    solicitante: str
    departamento: str
    tipo_documento: str
    descricao: str
    arquivo: DocumentFile

class Finding(BaseModel):
    titulo: str
    status: str
    detalhe: str

class AnalysisResponse(BaseModel):
    protocolo: str
    status: str
    probabilidade_fraude: int
    resumo: str
    dados_chave: list[Finding]
    verificacoes_oficiais: list[Finding]
    alertas: list[str]
    fatores_score: list[str]
    proximos_passos: list[str]
    motor_extracao: str
    texto_extraido: str
    tempo_resposta: float
    
@app.get("/")
def home():
    return {"msg": "API estruturada", "service": "Verify API"}

@app.post("/analises/documento", response_model=AnalysisResponse)
def analyze_document(payload: AnalysisRequest):
    start_time = time.time()  # <--- ADICIONADO: Inicia o cronômetro
    
    file = payload.arquivo
    if payload.arquivo.tipo_mime not in ALLOWED_MIME_TYPES:
    raise HTTPException(
        status_code=400,
        detail="Tipo de arquivo não permitido"
    )
    
    file_bytes = base64.b64decode(payload.arquivo.conteudo_base64)

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Arquivo muito grande"
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
    logging.basicConfig(
    filename="auditoria_ia.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

    logging.info(
    f"PROTOCOLO={protocol} | DOC={payload.tipo_documento} | TEMPO={duration:.2f}s | STATUS={report.status}"
)

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
    tempo_resposta=duration,
)
