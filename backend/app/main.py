import base64
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
import json
import os
import uuid
import base64
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# ================= CONFIG =================
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


@app.get("/")
def home():
    return {"msg": "API estruturada", "service": "Verify API"}


@app.post("/analises/documento", response_model=AnalysisResponse)
def analyze_document(payload: AnalysisRequest):
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= MODELS =================
class ArquivoInput(BaseModel):
    nome: str
    tipo_mime: str
    tamanho_bytes: int
    conteudo_base64: str

class AnaliseRequest(BaseModel):
    solicitante: str
    departamento: str | None = None
    tipo_documento: str
    descricao: str | None = None
    arquivo: ArquivoInput

# ================= UTILS =================
def validar_cnpj_real(cnpj: str):
    cnpj_limpo = "".join(filter(str.isdigit, str(cnpj)))
    try:
        res = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}", timeout=10)
        if res.status_code == 200:
            d = res.json()
            status = d.get("descricao_situacao_cadastral", "DESCONHECIDA")
            return {"valido": status == "ATIVA", "nome": d.get("razao_social"), "status": status}
        return {"valido": False, "nome": None, "status": "BAIXADO/INATIVO"}
    except:
        return {"valido": False, "nome": None, "status": "ERRO API"}

def gerar_prompt(req: AnaliseRequest):
    return f"""
    Analise este documento ({req.tipo_documento}) pertencente a {req.solicitante}.
    Busque indícios de fraude, montagem, ou inconsistência. Se for histórico/certificado, extraia o CNPJ da instituição.
    
    Retorne APENAS um JSON no exato formato abaixo:
    {{
      "probabilidade_fraude": 0,
      "resumo": "Texto curto explicando a decisão principal.",
      "alertas": ["Lista de strings com alertas de fraude visual encontrados. Deixe vazio se não houver."],
      "dados_chave": [
        {{ "titulo": "Nome no Documento", "status": "encontrado", "detalhe": "Nome extraído" }},
        {{ "titulo": "CNPJ", "status": "encontrado", "detalhe": "Apenas os números" }}
      ],
      "proximos_passos": ["Lista de strings com sugestões do que o analista humano deve checar."]
    }}
    Lembre-se: Use os status permitidos: 'encontrado', 'nao_encontrado', 'pendente', 'alerta'.
    """

# ================= ENDPOINT =================
@app.post("/analises/documento")
async def analisar(req: AnaliseRequest):
    try:
        prompt = gerar_prompt(req)
        
        image_bytes = base64.b64decode(req.arquivo.conteudo_base64)
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=req.arquivo.tipo_mime),
                prompt
            ]
        )
        
        texto = response.text.replace("```json", "").replace("```", "").strip()
        res_ia = json.loads(texto)
        
        probabilidade = res_ia.get("probabilidade_fraude", 0)
        verificacoes = []
        cnpj_extraido = None

        for dado in res_ia.get("dados_chave", []):
            if dado.get("titulo") == "CNPJ" and dado.get("detalhe"):
                cnpj_extraido = dado.get("detalhe")
                break

        if cnpj_extraido and len(str(cnpj_extraido)) > 5:
            val = validar_cnpj_real(cnpj_extraido)
            if val["valido"]:
                verificacoes.append({
                    "titulo": "Consulta Receita Federal (BrasilAPI)",
                    "status": "encontrado",
                    "detalhe": f"CNPJ Ativo: {val['nome']}"
                })
            else:
                probabilidade = max(probabilidade, 85)
                verificacoes.append({
                    "titulo": "Consulta Receita Federal (BrasilAPI)",
                    "status": "alerta",
                    "detalhe": f"Alerta: CNPJ {val['status']}"
                })
        else:
            verificacoes.append({
                "titulo": "Consulta de CNPJ",
                "status": "nao_encontrado",
                "detalhe": "Nenhum CNPJ legível identificado no documento."
            })

        return {
            "protocolo": f"REQ-{uuid.uuid4().hex[:8].upper()}",
            "status": "analisado",
            "probabilidade_fraude": probabilidade,
            "resumo": res_ia.get("resumo", "Análise concluída com sucesso."),
            "dados_chave": res_ia.get("dados_chave", []),
            "verificacoes_oficiais": verificacoes,
            "alertas": res_ia.get("alertas", []),
            "proximos_passos": res_ia.get("proximos_passos", ["Aprovação automática sugerida."])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
