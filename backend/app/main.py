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

app = FastAPI()

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