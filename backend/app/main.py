import base64
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import config  # noqa: F401
from app.services.document_analysis import build_analysis

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


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


class DocumentFile(BaseModel):
    nome: str
    tipo_mime: str
    tamanho_bytes: int = Field(ge=1)
    conteudo_base64: str


class AnalysisRequest(BaseModel):
    solicitante: str = Field(min_length=2)
    departamento: str = ""
    tipo_documento: Literal[
        "atestado_medico",
        "certificado_ensino_medio",
        "historico_escolar",
    ]
    descricao: str = ""
    arquivo: DocumentFile


class Finding(BaseModel):
    titulo: str
    status: Literal["encontrado", "nao_encontrado", "pendente", "alerta"]
    detalhe: str


class AnalysisResponse(BaseModel):
    protocolo: str
    status: Literal["rascunho_tecnico", "ia_indisponivel", "analisado"]
    probabilidade_fraude: int
    resumo: str
    dados_chave: list[Finding]
    verificacoes_oficiais: list[Finding]
    alertas: list[str]
    fatores_score: list[str]
    proximos_passos: list[str]
    motor_extracao: str
    texto_extraido: str


ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}
MAX_FILE_SIZE = 10 * 1024 * 1024


@app.get("/")
def home():
    return {"msg": "API estruturada", "service": "Verify API"}


@app.post("/analises/documento", response_model=AnalysisResponse)
def analyze_document(payload: AnalysisRequest, request: Request):
    corr_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    file = payload.arquivo
    
    logger.info(f"[{corr_id}] Recepcao: Arquivo '{file.nome}' recebido. Tamanho: {file.tamanho_bytes} bytes. Extensao/MIME: {file.tipo_mime}.")

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
        corr_id=corr_id,
    )

    veredicto_final = "Falso/Alerta" if report.probabilidade_fraude >= 60 else "Veridico/Seguro"
    logger.info(f"[{corr_id}] Veredito: {veredicto_final}. Probabilidade de fraude: {report.probabilidade_fraude}%. Fatores: {', '.join(report.fatores_score)}")

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
