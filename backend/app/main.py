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
    especificacoes = {
        "atestado": "Extraia: Nome do médico, CRM, dias de afastamento e CID (se houver).",
        "historico": "Extraia: Média Global/CRA, Disciplinas Pendentes e Data de Emissão.",
        "certificado": "Extraia: Carga Horária total, Data de Conclusão e Nome do Curso.",
        "rg": "Extraia: Número do RG, Data de Expedição e Naturalidade."
    }

    tipo_lower = req.tipo_documento.lower()
    diretriz_especifica = "Extraia os dados identificadores principais."
    
    for chave, valor in especificacoes.items():
        if chave in tipo_lower:
            diretriz_especifica = valor
            break

    return f"""
    Analise a autenticidade deste documento ({req.tipo_documento}) de {req.solicitante}.
    FOCO PRINCIPAL: Identificar indícios de montagem, edições de texto, inconsistência de fontes ou fraudes visuais.
    
    TAREFA ADICIONAL: 
    1. {diretriz_especifica}
    2. Identifique SEMPRE o CNPJ da instituição emissora (se houver) para validação.

    Retorne APENAS um JSON no formato:
    {{
      "probabilidade_fraude": 0,
      "resumo": "Explicação curta da análise.",
      "alertas": ["Lista de alertas visuais de fraude encontrados."],
      "dados_chave": [
        {{ "titulo": "Nome no Documento", "status": "encontrado", "detalhe": "Valor" }},
        {{ "titulo": "CNPJ", "status": "encontrado", "detalhe": "Somente números" }},
        {{ "titulo": "Dado Extra", "status": "encontrado", "detalhe": "Valor do dado extraído" }}
      ],
      "proximos_passos": ["O que o analista deve conferir."]
    }}
    Status permitidos: 'encontrado', 'nao_encontrado', 'pendente', 'alerta'.
    """

# ================= ENDPOINT =================
@app.post("/analises/documento")
async def analisar(req: AnaliseRequest):
    try:
        prompt = gerar_prompt(req)
        image_bytes = base64.b64decode(req.arquivo.conteudo_base64)
        
        response = client.models.generate_content(
            model='gemini-2.0-flash', #
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=req.arquivo.tipo_mime),
                prompt
            ]
        )
        
        texto = response.text.strip()
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
        
        res_ia = json.loads(texto)
        
        probabilidade = res_ia.get("probabilidade_fraude", 0)
        verificacoes = []
        cnpj_extraido = next((d.get("detalhe") for d in res_ia.get("dados_chave", []) if d.get("titulo") == "CNPJ"), None)

        if cnpj_extraido and len(str(cnpj_extraido)) >= 11:
            val = validar_cnpj_real(cnpj_extraido)
            status_verificacao = "encontrado" if val["valido"] else "alerta"
            if not val["valido"]: probabilidade = max(probabilidade, 85)
            
            verificacoes.append({
                "titulo": "Consulta Receita Federal (BrasilAPI)",
                "status": status_verificacao,
                "detalhe": f"{val['nome'] or 'CNPJ'} - {val['status']}"
            })
        else:
            verificacoes.append({
                "titulo": "Consulta de CNPJ",
                "status": "nao_encontrado",
                "detalhe": "CNPJ não identificado ou inválido para consulta automática."
            })

        return {
            "protocolo": f"REQ-{uuid.uuid4().hex[:8].upper()}",
            "status": "analisado",
            "probabilidade_fraude": probabilidade,
            "resumo": res_ia.get("resumo", "Análise concluída."),
            "dados_chave": res_ia.get("dados_chave", []),
            "verificacoes_oficiais": verificacoes,
            "alertas": res_ia.get("alertas", []),
            "proximos_passos": res_ia.get("proximos_passos", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
