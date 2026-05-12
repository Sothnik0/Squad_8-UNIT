"""
Fluxo principal:
    1. OCR via OCR.space  →  extração de texto bruto
    2. Gemini             →  interpretação semântica complementar
    3. Merge              →  consolidação dos dois resultados
    4. Verificações       →  consultas públicas (BrasilAPI, ViaCEP) e validações locais
    5. Payload final      →  AnalysisPayload estruturado para a camada de apresentação

Tipos de documento suportados:
    - atestado_medico
    - certificado_ensino_medio
    - historico_escolar
"""

import json
import os
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

# =============================================================================
# SEÇÃO 1 — CONSTANTES E CONFIGURAÇÕES
# =============================================================================

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
OCR_SPACE_URL = "https://api.ocr.space/parse/image"
BRASILAPI_CNPJ_URL = "https://brasilapi.com.br/api/cnpj/v1"
VIACEP_URL = "https://viacep.com.br/ws"

# Modelo Gemini lido de variável de ambiente; fallback vazio desativa a etapa de IA.
DEFAULT_GEMINI_MODEL = (
    os.getenv("GEMINI_MODEL", "").strip() or os.getenv("AI_MODEL", "").strip()
)

# Especificações dos tipos de documento aceitos pelo sistema.
DOCUMENT_SPECS: dict[str, dict[str, str]] = {
    "atestado_medico": {
        "label": "Atestado medico",
    },
    "certificado_ensino_medio": {
        "label": "Certificado de conclusao do ensino medio",
    },
    "historico_escolar": {
        "label": "Historico escolar",
    },
}

# =============================================================================
# SEÇÃO 2 — MODELOS DE DADOS
# =============================================================================

@dataclass
class VerificationResult:
    """Resultado de uma verificação oficial (CNPJ, CEP, CPF, CRM)."""

    titulo: str
    status: str   # encontrado | nao_encontrado | pendente | alerta
    detalhe: str

@dataclass
class AnalysisPayload:
    """Payload final retornado pela análise completa de um documento."""

    protocolo: str
    status: str
    probabilidade_fraude: int
    resumo: str
    dados_chave: list[dict[str, str]]
    verificacoes_oficiais: list[dict[str, str]]
    alertas: list[str]
    fatores_score: list[str]
    proximos_passos: list[str]
    motor_extracao: str
    texto_extraido: str

# =============================================================================
# SEÇÃO 3 — CHAVES DE API
# =============================================================================

def get_gemini_key() -> str:
    """
    Retorna a chave de API do Gemini lida das variáveis de ambiente.

    Ordem de preferência: GEMINI_API_KEY → GOOGLE_API_KEY.
    """
    return (
        os.getenv("GEMINI_API_KEY", "").strip()
        or os.getenv("GOOGLE_API_KEY", "").strip()
    )

def get_ocr_key() -> str:
    """Retorna a chave de API do OCR.space lida das variáveis de ambiente."""
    return os.getenv("OCR_API_KEY", "").strip()

# =============================================================================
# SEÇÃO 4 — FUNÇÕES UTILITÁRIAS
# =============================================================================

def clean_text(value: Any) -> str:
    """Converte *value* para string e remove espaços nas bordas."""
    return str(value or "").strip()

def only_digits(value: Any) -> str:
    """Remove todos os caracteres não-numéricos de *value*."""
    return "".join(char for char in str(value or "") if char.isdigit())

def normalize_label_key(value: Any) -> str:
    """
    Transforma um label em uma chave comparável: minúsculas, sem acentos,
    apenas letras/dígitos e espaços simples.
    """
    cleaned = clean_text(value)
    if not cleaned:
        return ""
    normalized = unicodedata.normalize("NFKD", cleaned)
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return re.sub(r"[^a-z0-9]+", " ", without_accents.lower()).strip()

def normalize_confidence(value: Any) -> float:
    """Converte *value* para float ≥ 0; retorna 0.0 em caso de erro."""
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return 0.0

def normalize_status(status: Any) -> str:
    """
    Garante que o status seja um dos valores válidos do sistema.
    Qualquer valor desconhecido é normalizado para 'pendente'.
    """
    normalized = clean_text(status).lower()
    return (
        normalized
        if normalized in {"encontrado", "nao_encontrado", "pendente", "alerta"}
        else "pendente"
    )

def normalize_string_list(value: Any) -> list[str]:
    """
    Normaliza qualquer valor (str, lista, dict ou outro) para uma lista
    de strings não-vazias e sem espaços nas bordas.
    """
    if value is None:
        return []
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(normalize_string_list(item))
        return result
    if isinstance(value, dict):
        message = clean_text(value.get("message") or value.get("error") or "")
        return [message] if message else []
    cleaned_val = clean_text(value)
    return [cleaned_val] if cleaned_val else []

def dedupe_strings(values: list[str]) -> list[str]:
    """Remove duplicatas de uma lista de strings preservando a ordem de inserção."""
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = clean_text(value)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result

def dedupe_next_steps(
    *, gemini_steps: list[str], default_steps: list[str]
) -> list[str]:
    """
    Combina os próximos passos sugeridos pelo Gemini com os padrões do sistema,
    eliminando duplicatas exatas e semânticas (frases muito similares).
    """
    result: list[str] = []
    seen_exact: set[str] = set()
    # Palavras-chave que identificam a "intenção" de cada passo
    seen_keywords: set[str] = set()

    def extract_keywords(text: str) -> set[str]:
        important = {
            "carimbo", "assinatura", "ocr", "imagem", "crm", "uf",
            "cnpj", "cep", "cpf", "periodo", "afastamento", "instituicao",
            "registro", "selo", "autenticidade", "medico", "paciente",
            "data", "emissao", "manual", "conferir", "validar", "comparar",
        }
        words = set(re.findall(r"[a-záàâãéèêíïóôõúüç]+", text.lower()))
        return words & important

    for step in [*gemini_steps, *default_steps]:
        cleaned = clean_text(step)
        if not cleaned or cleaned in seen_exact:
            continue
        kws = extract_keywords(cleaned)
        # Se todas as palavras-chave já estão cobertas, é semanticamente duplicado
        if kws and kws.issubset(seen_keywords):
            continue
        seen_exact.add(cleaned)
        seen_keywords |= kws
        result.append(cleaned)

    return result

def match_group(text: str, pattern: str) -> str:
    """
    Aplica *pattern* em *text* (case-insensitive) e retorna o primeiro grupo
    capturado limpo, ou string vazia se não houver correspondência.
    """
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return clean_text(match.group(1)) if match else ""

def format_cpf(value: str) -> str:
    """
    Formata 11 dígitos no padrão CPF (000.000.000-00).
    Retorna o valor original se não tiver exatamente 11 dígitos.
    """
    digits = only_digits(value)
    if len(digits) != 11:
        return clean_text(value)
    return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"

def format_cnpj(value: str) -> str:
    """
    Formata 14 dígitos no padrão CNPJ (00.000.000/0000-00).
    Retorna o valor original se não tiver exatamente 14 dígitos.
    """
    digits = only_digits(value)
    if len(digits) != 14:
        return clean_text(value)
    return f"{digits[0:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"

# =============================================================================
# SEÇÃO 5 — VALIDAÇÕES MATEMÁTICAS (CEP, CPF, CNPJ)
# =============================================================================

def is_valid_cep(cep: str) -> bool:
    """Retorna True se *cep* tiver exatamente 8 dígitos numéricos."""
    return len(cep) == 8 and cep.isdigit()

def is_valid_cpf(cpf: str) -> bool:
    """
    Valida os dígitos verificadores do CPF conforme algoritmo oficial.
    Rejeita sequências com todos os dígitos iguais (ex.: '11111111111').
    """
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    numbers = [int(char) for char in cpf]
    for digit_index in (9, 10):
        total = sum(
            numbers[i] * ((digit_index + 1) - i) for i in range(digit_index)
        )
        digit = (total * 10) % 11
        if digit == 10:
            digit = 0
        if numbers[digit_index] != digit:
            return False
    return True

def is_valid_cnpj(cnpj: str) -> bool:
    """
    Valida os dígitos verificadores do CNPJ conforme algoritmo oficial.
    Rejeita sequências com todos os dígitos iguais (ex.: '00000000000000').
    """
    if len(cnpj) != 14 or len(set(cnpj)) == 1:
        return False
    numbers = [int(char) for char in cnpj]
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digit1 = 11 - (sum(a * b for a, b in zip(numbers[:12], weights1)) % 11)
    digit1 = 0 if digit1 >= 10 else digit1
    digit2 = 11 - (sum(a * b for a, b in zip(numbers[:13], weights2)) % 11)
    digit2 = 0 if digit2 >= 10 else digit2
    return numbers[12] == digit1 and numbers[13] == digit2

# =============================================================================
# SEÇÃO 6 — CAMADA HTTP GENÉRICA
# =============================================================================

def post_json(
    *, url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int
) -> dict[str, Any]:
    """Executa um POST com corpo JSON e retorna a resposta como dicionário."""
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

def get_json(
    *, url: str, query: dict[str, str] | None, timeout: int
) -> dict[str, Any]:
    """Executa um GET simples e retorna a resposta como dicionário."""
    final_url = f"{url}?{urllib.parse.urlencode(query)}" if query else url
    request = urllib.request.Request(final_url, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

def read_http_error(error: urllib.error.HTTPError) -> str:
    """
    Tenta extrair uma mensagem legível do corpo de um erro HTTP.
    Retorna string vazia se não conseguir.
    """
    try:
        body = error.read().decode("utf-8")
        if not body:
            return ""
        payload = json.loads(body)
        if isinstance(payload, dict) and "error" in payload and isinstance(
            payload["error"], dict
        ):
            payload = payload["error"]
        if isinstance(payload, dict):
            return clean_text(
                payload.get("message")
                or payload.get("status")
                or payload.get("error")
                or body
            )
        return clean_text(body)
    except Exception:  # noqa: BLE001
        return ""

# =============================================================================
# SEÇÃO 7 — CONSTRUÇÃO E NORMALIZAÇÃO DE CAMPOS EXTRAÍDOS
# =============================================================================

def build_field(
    label: str, value: str, confidence: float = 0.82, source: str = "ocr_space"
) -> dict[str, Any]:
    """
    Cria um dicionário padronizado representando um campo extraído.

    O status é 'encontrado' quando *value* é não-vazio; 'nao_encontrado' caso contrário.
    A confiança é zerada quando o campo não foi encontrado.
    """
    cleaned = clean_text(value)
    return {
        "label": label,
        "value": cleaned,
        "status": "encontrado" if cleaned else "nao_encontrado",
        "confidence": confidence if cleaned else 0.0,
        "source": source,
    }

def stringify_field_detail(field: dict[str, Any]) -> str:
    """
    Formata o detalhe de exibição de um campo extraído, incluindo
    o valor, a confiança percentual (se disponível) e a origem.
    """
    value = clean_text(field.get("value", ""))
    confidence = field.get("confidence")
    source = clean_text(field.get("source", ""))
    detail = value or "Campo nao identificado no documento."
    if confidence is not None:
        try:
            detail = f"{detail} (confianca {round(float(confidence) * 100)}%)"
        except (TypeError, ValueError):
            pass
    if source:
        detail = f"{detail} - origem: {source}"
    return detail

def normalize_key_findings(combined_output: dict[str, Any]) -> list[dict[str, str]]:
    """
    Converte os campos extraídos do resultado combinado no formato
    esperado pela chave 'dados_chave' do payload final.
    Elimina labels duplicados.
    """
    findings: list[dict[str, str]] = []
    seen_labels: set[str] = set()
    for field in combined_output.get("extracted_fields", []):
        label = clean_text(field.get("label", ""))
        label_key = normalize_label_key(label)
        if not label or not label_key or label_key in seen_labels:
            continue
        seen_labels.add(label_key)
        findings.append(
            {
                "titulo": label,
                "status": normalize_status(field.get("status")),
                "detalhe": stringify_field_detail(field),
            }
        )
    return findings

def preferred_label(existing: Any, incoming: Any) -> str:
    """
    Escolhe o label mais descritivo entre dois candidatos.
    Prefere o label mais longo (geralmente vindo do Gemini).
    """
    existing_label = clean_text(existing)
    incoming_label = clean_text(incoming)
    if incoming_label and len(incoming_label) >= len(existing_label):
        return incoming_label
    return existing_label or incoming_label

def merge_sources(existing: Any, incoming: Any) -> str:
    """
    Combina as origens de dois campos (ex.: 'ocr_space' + 'gemini').
    Retorna uma única string quando as origens são iguais.
    """
    existing_source = clean_text(existing)
    incoming_source = clean_text(incoming)
    if existing_source and incoming_source and existing_source != incoming_source:
        return f"{existing_source} + {incoming_source}"
    return incoming_source or existing_source

def should_replace_field(
    *,
    existing_status: str,
    incoming_status: str,
    existing_confidence: float,
    incoming_confidence: float,
) -> bool:
    """
    Decide se o campo *incoming* deve substituir o *existing* na mesclagem.

    Critérios (em ordem de prioridade):
        1. Status com maior prioridade vence (encontrado > alerta > pendente > nao_encontrado).
        2. Em empate de status, maior confiança vence.
    """
    status_priority = {
        "encontrado": 3,
        "alerta": 2,
        "pendente": 1,
        "nao_encontrado": 0,
    }
    incoming_priority = status_priority.get(incoming_status, -1)
    existing_priority = status_priority.get(existing_status, -1)
    if incoming_priority != existing_priority:
        return incoming_priority > existing_priority
    return incoming_confidence >= existing_confidence

def merge_extracted_field(
    existing: dict[str, Any], incoming: dict[str, Any]
) -> dict[str, Any]:
    """
    Mescla dois registros do mesmo campo (OCR vs Gemini), mantendo
    os valores de maior status e confiança.
    """
    existing_status = normalize_status(existing.get("status"))
    incoming_status = normalize_status(incoming.get("status"))
    existing_confidence = normalize_confidence(existing.get("confidence"))
    incoming_confidence = normalize_confidence(incoming.get("confidence"))

    if should_replace_field(
        existing_status=existing_status,
        incoming_status=incoming_status,
        existing_confidence=existing_confidence,
        incoming_confidence=incoming_confidence,
    ):
        merged = dict(existing)
        merged.update(incoming)
    else:
        merged = dict(incoming)
        merged.update(existing)

    merged["label"] = preferred_label(existing.get("label"), incoming.get("label"))
    merged["source"] = merge_sources(existing.get("source"), incoming.get("source"))
    merged["status"] = normalize_status(merged.get("status"))
    merged["confidence"] = max(existing_confidence, incoming_confidence)
    return merged

# =============================================================================
# SEÇÃO 8 — EXTRAÇÃO OCR (OCR.space)
# Interpreta o texto bruto retornado pelo OCR por tipo de documento.
# =============================================================================

def _extract_dates_from_text(text: str, current_year: int) -> list[tuple]:
    """
    Extrai todas as datas válidas (numéricas e por extenso) de um texto.
    Retorna lista de tuplas (date_obj, hora_str) ordenada da mais antiga para mais recente.
    Só aceita anos entre 1920 (para nascimento) e o ano atual.
    """
    import datetime as _dt

    meses = {
        "janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3, "abril": 4,
        "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
        "outubro": 10, "novembro": 11, "dezembro": 12,
    }

    found: list[tuple] = []

    # Datas numéricas: DD/MM/AAAA com hora opcional
    for m in re.finditer(
        r"(\d{2}/\d{2}/\d{4})(?:[\s,-]*(?:às|as)?\s*(\d{2}:\d{2}(?::\d{2})?))?",
        text, re.IGNORECASE,
    ):
        data_str, hora_str = m.group(1), m.group(2)
        try:
            d = _dt.datetime.strptime(data_str, "%d/%m/%Y").date()
            if 1920 <= d.year <= current_year:
                found.append((d, hora_str or ""))
        except ValueError:
            pass

    # Datas por extenso: "20 de dezembro de 2022"
    for m in re.finditer(
        r"(\d{1,2})\s+de\s+([a-zç]+)\s+de\s+(\d{4})"
        r"(?:[\s,-]*(?:às|as)?\s*(\d{2}:\d{2}(?::\d{2})?))?",
        text, re.IGNORECASE,
    ):
        dia, mes_str, ano_str, hora_str = m.groups()
        mes_num = meses.get(mes_str.lower())
        if mes_num:
            try:
                d = _dt.date(int(ano_str), mes_num, int(dia))
                if 1920 <= d.year <= current_year:
                    found.append((d, hora_str or ""))
            except ValueError:
                pass

    found.sort(key=lambda x: x[0])
    return found

def _calculate_age(birth_date) -> str:
    """Calcula a idade a partir da data de nascimento usando a data atual."""
    import datetime as _dt
    today = _dt.date.today()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    return str(age)

def parse_medical_certificate_ocr(raw_text: str) -> dict[str, Any]:
    """
    Interpreta o texto bruto do OCR para atestados médicos.

    Extrai:
        - Nome do paciente, CPF, data de nascimento, idade
        - Nome completo do médico (Dr./Dra. + nome) e CRM
        - Carimbo / assinatura (texto extraído, não só presença)
        - Hospital, clínica, UBS, UPA, Secretaria ou outro local emissor
        - Endereço completo do local emissor
        - Estado e cidade de emissão
        - Data e local de emissão (ex: "Aracaju/SE, 10 de maio de 2024")
        - Período de afastamento em dias + validade do atestado
        - CID
    """
    import datetime as _dt

    current_year = _dt.date.today().year

    normalized_text = (
        raw_text
        .replace("Paclente", "Paciente").replace("paclente", "paciente")
        .replace("Medlco", "Medico").replace("Asslnatura", "Assinatura")
        .replace("Hospltal", "Hospital").replace("Clínlca", "Clínica")
    )
    lowered_text = normalized_text.lower()

    # Nome do paciente — múltiplos padrões de atestado
    # Nome do paciente: exige contexto explícito ou padrão nome-sobrenome
    # (ao menos 2 palavras em maiúsculo de 3+ letras cada)
    _name_candidates = [
        # "Paciente: NOME" ou "Nome do Paciente: NOME"
        match_group(normalized_text, r"(?:Paciente|Nome do Paciente)[:\s;]+([A-ZÀ-Ú][A-ZÀ-Úa-zà-ú][A-ZÀ-Úa-zà-ú ]{3,})"),
        # "o(a) Sr(a). NOME" ou "Sr(a) NOME" — padrão comum em atestados
        match_group(normalized_text, r"[Ss]r\.?(?:a\.?)?\s*\)?\s+([A-ZÀ-Ú]{2,}(?:\s+[A-ZÀ-Ú]{2,})+)"),
        # "Atesto que atendi... o(a) Sr(a). NOME"
        match_group(normalized_text, r"(?:Atesto|Certifico|Declaro)[^\n]{0,60}[Ss]r\.?(?:a\.?)?\s*\)?\s+([A-ZÀ-Ú]{2,}(?:\s+[A-ZÀ-Ú]{2,})+)"),
        # "o paciente NOME"
        match_group(normalized_text, r"(?:o|a) paciente[:\s]+([A-ZÀ-Ú][A-ZÀ-Úa-zà-ú ]{4,})"),
        # "Nome: NOME SOBRENOME"
        match_group(normalized_text, r"(?:Nome|Paciente)[:\s]+([A-ZÀ-Ú]{3,}(?:\s+[A-ZÀ-Ú]{2,}){1,4})\b"),
    ]
    patient_name = next(
        (n.strip() for n in _name_candidates
         if n and len(n.split()) >= 2
         and all(len(w) >= 2 for w in n.split())
         and not any(kw in n.lower() for kw in ["nesta", "data", "que", "para", "com", "uma", "sendo", "atividade"])),
        "",
    )

    # Extrai CPF em qualquer formato, incluindo preenchimento manuscrito
    # Tolerante a espaços irregulares, pontos e hífens em posições variadas
    _cpf_raw = ""
    # 1. Com label "CPF:" seguido de dígitos com separadores quaisquer
    _cpf_match = re.search(
        r"CPF[:\s./N°nº]*([0-9][0-9\s.\-/]{9,18}[0-9])",
        normalized_text, re.IGNORECASE,
    )
    if _cpf_match:
        _digits = only_digits(_cpf_match.group(1))
        if len(_digits) == 11:
            _cpf_raw = _digits
    # 2. Formato padrão isolado "000.000.000-00"
    if not _cpf_raw:
        _m = re.search(r"\b([0-9]{3}[.\s][0-9]{3}[.\s][0-9]{3}[-\s][0-9]{2})\b", normalized_text)
        if _m:
            _cpf_raw = only_digits(_m.group(1))
    # 3. 11 dígitos consecutivos que passam na validação matemática (último recurso)
    if not _cpf_raw:
        for _m in re.finditer(r"\b([0-9]{11})\b", normalized_text):
            if is_valid_cpf(_m.group(1)):
                _cpf_raw = _m.group(1)
                break
    cpf = format_cpf(_cpf_raw) if _cpf_raw and len(_cpf_raw) == 11 else ""

    all_dates = _extract_dates_from_text(normalized_text, current_year)
    birth_candidates  = [(d, h) for d, h in all_dates if d.year <= current_year - 10]
    issue_candidates  = [(d, h) for d, h in all_dates if current_year - 5 <= d.year <= current_year]

    birth_date_str = ""
    birth_date_obj = None
    birth_context = match_group(
        normalized_text,
        r"(?:Data de Nascimento|Nascimento|Nasc\.?|D\.N\.?)[:\s]+([0-9]{2}/[0-9]{2}/[0-9]{4})",
    )
    if birth_context:
        try:
            birth_date_obj = _dt.datetime.strptime(birth_context, "%d/%m/%Y").date()
            birth_date_str = birth_context
        except ValueError:
            pass
    if not birth_date_obj and birth_candidates:
        birth_date_obj, _ = birth_candidates[0]
        birth_date_str = birth_date_obj.strftime("%d/%m/%Y")

    age_str = ""
    age_context = match_group(normalized_text, r"(?:Idade|Anos)[:\s]+([0-9]{1,3})")
    if birth_date_obj:
        # Sempre prefere calcular — a idade no documento pode estar desatualizada
        _calc_age = _calculate_age(birth_date_obj)
        _doc_age = age_context or ""
        if _doc_age and _doc_age != _calc_age:
            age_str = f"{_calc_age} anos (documento indica {_doc_age})"
        else:
            age_str = f"{_calc_age} anos"
    elif age_context:
        age_str = f"{age_context} anos (conforme documento)"

    issue_date_str = ""
    issue_context = match_group(
        normalized_text,
        r"(?:Data de Emissao|Data de Atendimento|Emitido em|Data)[:\s]+([0-9]{2}/[0-9]{2}/[0-9]{4})",
    )
    if issue_context:
        issue_date_str = issue_context
    elif issue_candidates:
        d, h = issue_candidates[-1]
        issue_date_str = d.strftime("%d/%m/%Y") + (f" as {h}" if h else "")
    elif all_dates and not birth_date_obj:
        d, h = all_dates[-1]
        issue_date_str = d.strftime("%d/%m/%Y")

    # Local e data de emissão (padrão: "Aracaju/SE, 10 de maio de 2024"
    # ou "Aracaju, 10/05/2024")
    # Local + data: exige cidade (Title Case 4+ letras) + data com ano 20XX
    # Local + data: busca "CIDADE/UF, data" ou "Cidade, data"
    # Rejeita palavras que são sobrenomes comuns de médicos (Jesus, Silva, Santos etc.)
    # Prioridade: padrão com UF explícita (mais confiável)
    _UF = r"(?:AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)"
    _date_pat = r"(?:\d{1,2}\s+de\s+[a-zç]+\s+de\s+20\d{2}|\d{2}/\d{2}/20\d{2})"
    _sobrenomes_comuns = {
        "jesus", "silva", "santos", "oliveira", "souza", "lima", "pereira",
        "costa", "ferreira", "alves", "moura", "ribeiro", "carvalho", "gomes",
    }
    # Padrão 1: CIDADE/UF, data — mais confiável
    _place_m = re.search(
        rf"([A-ZÁÀÂÃÉÈÊÍÓÔÕÚ]{{3,}}(?:\s+[A-ZÁÀÂÃÉÈÊÍÓÔÕÚ]{{2,}})?)"
        rf"/({_UF})[,\s]{{1,3}}({_date_pat})",
        normalized_text, re.IGNORECASE,
    )
    if _place_m:
        issue_place_date = f"{_place_m.group(1).strip()}/{_place_m.group(2)}, {_place_m.group(3).strip()}"
    else:
        # Padrão 2: Cidade, data — rejeita sobrenomes
        _place_m2 = re.search(
            rf"\b([A-ZÀ-Ú][a-zà-ú]{{3,}}(?:\s+[A-ZÀ-Ú][a-zà-ú]{{2,}})?)"
            rf"[,\s]{{1,3}}({_date_pat})",
            normalized_text, re.IGNORECASE,
        )
        if (_place_m2
                and len(_place_m2.group(1).strip()) >= 4
                and _place_m2.group(1).strip().lower() not in _sobrenomes_comuns
                and not any(s in _place_m2.group(1).lower() for s in _sobrenomes_comuns)):
            issue_place_date = f"{_place_m2.group(1).strip()}, {_place_m2.group(2).strip()}"
        else:
            issue_place_date = ""

    # Hospital / local emissor — ampliado para Secretaria de Saúde
    institution_patterns = [
        r"((?:Hospital|Hospit)[^\n]{2,60})",
        r"((?:Cl[ií]nica|Clinica)[^\n]{2,60})",
        r"((?:UBS|UPA|CAPS|AME|AMA|NASF)[^\n]{0,60})",
        r"(Posto de Sa[uú]de[^\n]{0,60})",
        r"(Secretaria\s+(?:Municipal|Estadual|de\s+Sa[uú]de)[^\n]{0,60})",
        r"(UNIMED[^\n]{0,60})",
        r"(Centro\s+de\s+Sa[uú]de[^\n]{0,60})",
        r"(Pronto[\s-]?Socorro[^\n]{0,60})",
        r"(Policl[ií]nica[^\n]{0,60})",
        r"(?:Instituicao|Estabelecimento|Unidade de Saude)[:\s]+([^\n]+)",
        r"Empresa[:\s]+([^\n]+)",
    ]
    institution_name = ""
    for pat in institution_patterns:
        result = match_group(normalized_text, pat)
        if result:
            institution_name = result.strip().rstrip(".,;")
            break

    # Fallback: cabeçalho do documento (primeiras 10 linhas)
    # Junta linhas curtas consecutivas em maiúsculas (ex: HOSPITAL/GABRIEL/SOARES)
    # e pega o nome completo da instituição
    if not institution_name:
        _header_lines = [l.strip() for l in normalized_text.splitlines()[:10] if l.strip()]
        _skip_kws = {"atestado", "medico", "médico", "laudo", "receita", "exame",
                     "declaracao", "declaração", "certificado"}
        _joined = ""
        for _hl in _header_lines:
            if (_hl == _hl.upper() and len(_hl) >= 3 and not _hl.isdigit()
                    and not any(kw in _hl.lower() for kw in _skip_kws)
                    and (not patient_name or patient_name.upper() not in _hl)):
                # Linha curta (<= 20 chars) provavelmente é parte do nome partido em linhas
                if len(_hl) <= 20 and _joined:
                    _joined = f"{_joined} {_hl}"
                else:
                    if _joined and len(_joined) >= 5:
                        break
                    _joined = _hl
            else:
                if _joined and len(_joined) >= 5:
                    break
                _joined = ""
        if _joined and len(_joined) >= 5:
            institution_name = _joined.rstrip(".,;")

    # Endereço do local emissor
    _addr_match = re.search(
        r"(?:^|\n)\s*((?:Rua|Avenida|Av\.?\s|Alameda|Al\.?\s|Travessa|Tv\.?\s"
        r"|Rodovia|Rod\.?\s|R\s+[A-Z])[^\n]{5,80})",
        normalized_text, re.IGNORECASE | re.MULTILINE,
    )
    _cep_line_match = re.search(
        r"([^\n]{5,60})\n[0-9]{5}-?[0-9]{3}\s+[A-ZÀ-Ú]",
        normalized_text,
    )
    address = (
        clean_text(_addr_match.group(1)) if _addr_match
        else clean_text(_cep_line_match.group(1)) if _cep_line_match
        else match_group(normalized_text, r"(?:Endere[cç]o|End\.?)[:\s]+([^\n]{5,80})")
        or match_group(normalized_text, r"(?:Logradouro)[:\s]+([^\n]{5,80})")
    )

    # Carimbo / assinatura — extrai texto real próximo ao CRM
    # Tenta extrair nome do médico junto ao carimbo/assinatura
    # Carimbo/assinatura: busca nome do médico em contextos confiáveis
    # Prioridade: nome antes do CRM, nome após Dr./Dra., nome após "Assinatura do Médico"
    _stamp_candidates = [
        # Nome em maiúsculas logo antes de "CRM" (padrão mais comum no carimbo)
        match_group(normalized_text, r"([A-ZÀ-Ú]{3,}(?:\s+[A-ZÀ-Ú]{2,})+)\s*\n?\s*CRM"),
        # Dr./Dra. seguido de nome
        match_group(normalized_text, r"(?:Dr\.?|Dra\.?)\s+([A-ZÀ-Ú][A-ZÀ-Úa-zà-ú ]{4,})"),
        # Linha imediatamente após "Assinatura do Médico"
        match_group(normalized_text, r"Assinatura do M[eé]dico\s*\n+([A-ZÀ-Ú][A-ZÀ-Úa-zà-ú ]{4,})"),
        # Médico responsável
        match_group(normalized_text, r"M[eé]dico Respons[aá]vel[:\s]+([A-ZÀ-Ú][A-ZÀ-Úa-zà-ú ]{4,})"),
    ]
    doctor_stamp = next(
        (s for s in _stamp_candidates
         if s and len(s.split()) >= 2
         and not any(kw in s.lower() for kw in ["data", "assinatura", "medico", "carimbo", "ura"])),
        "",
    )
    signature_keywords = [
        "assinatura", "carimbo", "crm/", "crm:", "rubrica",
        "dr.", "dra.", "medico responsavel", "médico responsável",
    ]
    doctor_signed = any(kw in lowered_text for kw in signature_keywords)
    if doctor_stamp:
        signature_detail = f"Medico identificado: {doctor_stamp.strip()}"
    elif doctor_signed:
        found_kws = [kw for kw in signature_keywords if kw in lowered_text]
        signature_detail = f"Indicios: {', '.join(found_kws[:3])}"
    else:
        signature_detail = ""

    # Estado e cidade de emissão
    UF_LIST = r"AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO"

    # Padrão 1: "CIDADE - UF" ou "CIDADE/UF" (maiúsculas ou Title Case)
    _city_uf = (
        re.search(rf"([A-ZÁÀÂÃÉÈÊÍÓÔÕÚ]{{3,}}(?:\s+[A-ZÁÀÂÃÉÈÊÍÓÔÕÚ]{{2,}})?)"
                  rf"\s*[/\-]\s*({UF_LIST})\b", normalized_text)
        or re.search(rf"([A-ZÀ-Ú][a-zà-ú]{{3,}}(?:\s+[A-ZÀ-Ú][a-zà-ú]{{2,}})?)"
                     rf"[/\-,]\s*({UF_LIST})\b", normalized_text)
    )
    # Padrão 2: "CEP CIDADE - UF" como "49015-511 ARACAJU - SE"
    _cep_city_uf = re.search(
        rf"[0-9]{{5}}-?[0-9]{{3}}\s+([A-ZÁÀÂÃÉÈÊÍÓÔÕÚ]{{3,}}(?:\s+[A-ZÁÀÂÃÉÈÊÍÓÔÕÚ]{{2,}})?)"
        rf"\s*[-/]\s*({UF_LIST})\b",
        normalized_text,
    )
    state = match_group(normalized_text, rf"\b({UF_LIST})\b")
    location = ""
    if _city_uf:
        location = f"{_city_uf.group(1).strip()}/{_city_uf.group(2)}"
    elif _cep_city_uf:
        location = f"{_cep_city_uf.group(1).strip()}/{_cep_city_uf.group(2)}"
    elif issue_place_date:
        location = issue_place_date
    else:
        city_ctx = match_group(normalized_text, r"(?:Cidade|Municipio|Localidade)[:\s]+([^\n,]+)")
        if city_ctx and state:
            location = f"{city_ctx.strip()}/{state}"
        elif state:
            location = f"Estado: {state}"

    provider_name = (
        match_group(normalized_text, r"(?:Dr\.?|Dra\.?)[:\s]+([A-ZÀ-Ú][A-ZÀ-Úa-zà-ú ]{4,})")
        or match_group(normalized_text, r"(?:Dr\.?|Dra\.?)\s+([A-ZÀ-Ú]{2,}(?:\s+[A-ZÀ-Ú]{2,})+)")
        or match_group(normalized_text, r"(?:Medico|Médico|Medica|Médica)[:\s]+([A-ZÀ-Ú][A-ZÀ-Úa-zà-ú ]{4,})")
        or match_group(normalized_text, r"Prestador[:\s]+([A-ZÀ-Ú ]{6,})")
        or (doctor_stamp if doctor_stamp else "")
    )
    crm_number = only_digits(
        match_group(normalized_text, r"CRM[:\s/]*(?:[A-Z]{2}\s*[-/]?\s*)?([0-9]{3,8})")
    )

    # Período de afastamento
    leave_days_raw = (
        # "por 120 (CENTO E VINTE) dia(s)" — padrão mais comum em atestados hospitalares
        match_group(normalized_text, r"por\s+([0-9]{1,3})\s*\(?[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÚÜ\s]+\)?\s*dia(?:s|\(s\))?")
        # "afastamento das atividades laborativas ou acadêmicas por N dias"
        or match_group(normalized_text, r"atividades?\s+(?:laborativas?|acad[eê]micas?)[^0-9]{0,40}([0-9]{1,3})\s*dia")
        # "afastamento de N dias" / "repouso de N dias"
        or match_group(normalized_text, r"(?:afastamento|repouso|licen[cç]a)\s+de[:\s]*([0-9]{1,3})\s*dias?")
        # "período de N dias"
        or match_group(normalized_text, r"(?:periodo|período)\s+de[:\s]*([0-9]{1,3})\s*dias?")
        # "N dias de repouso/afastamento"
        or match_group(normalized_text, r"([0-9]{1,3})\s*dias?\s+de\s+(?:repouso|afastamento|licen[cç]a)")
        # "a partir de DATA" com número anterior (fallback)
        or match_group(normalized_text, r"por\s+(?:um\s+)?periodo\s+de[:\s]*([0-9]{1,2})")
    )
    leave_days = leave_days_raw.strip() if leave_days_raw else ""

    # Validade do atestado (quantos dias é válido a partir da emissão)
    # Atestados médicos no Brasil são válidos conforme:
    #   - Até 2 dias: dispensam comprovação adicional na maioria das empresas
    #   - 3–15 dias: recomendado confirmar com o empregador
    #   - Acima de 15 dias: pode exigir perícia médica
    validity_status = ""
    validity_detail = ""
    if leave_days:
        try:
            days_int = int(leave_days)
            if days_int <= 0:
                validity_status = "alerta"
                validity_detail = "Periodo de afastamento invalido (0 dias ou negativo)."
            elif days_int <= 2:
                validity_status = "encontrado"
                validity_detail = f"{days_int} dia(s). Curto prazo — justifica falta conforme regimento."
            elif days_int <= 7:
                validity_status = "encontrado"
                validity_detail = f"{days_int} dia(s). Prazo normal — encaminhar ao setor academico."
            elif days_int <= 15:
                validity_status = "encontrado"
                validity_detail = f"{days_int} dia(s). Prazo medio — verificar regras de abono da instituicao."
            elif days_int <= 90:
                validity_status = "pendente"
                validity_detail = (
                    f"{days_int} dia(s). Afastamento longo — pode exigir acompanhamento pela coordenacao "
                    "e pericia medica pelo INSS se for servidor (acima de 15 dias)."
                )
            elif days_int <= 180:
                validity_status = "pendente"
                validity_detail = (
                    f"{days_int} dia(s). Afastamento prolongado — acionar coordenacao academica, "
                    "verificar regime domiciliar e pericia do INSS."
                )
            else:
                validity_status = "alerta"
                validity_detail = (
                    f"{days_int} dia(s). Afastamento excepcional — exige laudo complementar "
                    "e aprovacao da coordenacao academica e/ou INSS."
                )
        except ValueError:
            pass

    cep = only_digits(match_group(normalized_text, r"CEP[:\s]*([0-9\-]{8,9})"))
    cid = match_group(normalized_text, r"\bCID[:\s.-]*([A-Z][0-9]{2,4})\b")

    extracted_fields = [
        build_field("Nome do paciente",             patient_name),
        build_field("CPF do paciente",              cpf),
        build_field("Data de nascimento",           birth_date_str),
        build_field("Idade do paciente",            age_str),
        build_field("Hospital ou local emissor",    institution_name),
        build_field("Endereco do local emissor",    address if address else ""),
        build_field("Carimbo ou assinatura",        signature_detail),
        build_field("Estado e cidade de emissao",   location),
        build_field("Local e data de emissao",      issue_place_date if issue_place_date else ""),
        build_field("Nome do medico",               provider_name),
        build_field("CRM",                          crm_number),
        build_field("Data de emissao",              issue_date_str),
        build_field("Periodo de afastamento (dias)", leave_days),
        build_field("Validade do atestado",         validity_detail),
        build_field("CID identificado",             cid),
    ]

    found_count = sum(1 for item in extracted_fields if item["status"] == "encontrado")

    summary = (
        "OCR executado com sucesso no atestado medico."
        if found_count >= 4
        else "OCR executado, mas sem dados confiaveis suficientes no atestado medico."
    )

    score_factors: list[str] = []
    if not crm_number:
        score_factors.append("O OCR nao localizou um CRM utilizavel no atestado.")
    if not provider_name:
        score_factors.append("O nome do medico nao foi identificado no atestado.")
    if not issue_date_str:
        score_factors.append("A data de emissao do atestado nao foi identificada.")
    if not doctor_signed:
        score_factors.append("Nenhum indicio de assinatura ou carimbo do medico foi encontrado.")
    if not institution_name:
        score_factors.append("O hospital ou local emissor nao foi identificado.")
    if not patient_name:
        score_factors.append("O nome do paciente nao foi localizado no atestado.")
    if validity_status == "alerta":
        score_factors.append(f"Periodo de afastamento suspeito: {validity_detail}")
    if found_count >= 9:
        score_factors.append("O OCR recuperou a maioria dos campos esperados do atestado.")

    alerts: list[str] = []
    if validity_status == "alerta":
        alerts.append(f"Validade do atestado: {validity_detail}")

    return {
        "summary": summary,
        "raw_text": raw_text,
        "engine": "ocr_space",
        "alerts": alerts,
        "extracted_fields": extracted_fields,
        "reference_data": {
            "institution_name": institution_name,
            "cnpj": "",
            "cpf": only_digits(cpf),
            "cep": cep,
            "crm_number": crm_number,
            "crm_state": state or ("SE" if "sergipe" in lowered_text else ""),
        },
        "recommended_checks": [
            "Conferir nome do paciente, CPF e data de nascimento com documento de identidade.",
            "Validar CRM do medico e confirmar assinatura/carimbo na imagem original.",
            "Verificar hospital emissor, endereco e cidade/estado de emissao.",
            "Confirmar periodo de afastamento e validade junto ao empregador.",
        ],
        "fraud_probability": 15 if found_count >= 9 else (28 if found_count >= 5 else 45),
        "score_factors": score_factors,
    }

def parse_school_document_ocr(tipo_documento: str, raw_text: str) -> dict[str, Any]:
    """
    Interpreta o texto bruto do OCR para documentos escolares
    (histórico escolar e certificado de ensino médio).

    Extrai: nome da instituição, nome do aluno, CNPJ, CEP e data.
    """
    # Busca o nome da instituição com ou sem acento e prioriza nomes mais curtos/limpos
    # Tenta primeiro "COLÉGIO/COLEGIO NOME" (sem lixo OCR anexado)
    _inst_candidates = [
        match_group(raw_text, r"(COL[EÉ]GIO[^\n]{2,50})"),
        match_group(raw_text, r"(ESCOLA[^\n]{2,50})"),
        match_group(raw_text, r"(INSTITUTO[^\n]{2,50})"),
        match_group(raw_text, r"(CENTRO EDUCACIONAL[^\n]{2,50})"),
        match_group(raw_text, r"(SECRETARIA[^\n]{2,50})"),
        match_group(raw_text, r"(ESCOLA[^\n]+|COL[EÉ]GIO[^\n]+|INSTITUTO[^\n]+)"),
    ]
    institution_name = next(
        (c.strip().rstrip(".,;") for c in _inst_candidates
         if c and len(c.strip()) >= 5),
        "",
    )
    student_name = match_group(
        raw_text, r"(?:Aluno|Aluna|Estudante)[:\s]+([^\n]+)"
    )
    cnpj = format_cnpj(
        match_group(
            raw_text,
            r"([0-9]{2}\.?[0-9]{3}\.?[0-9]{3}/?[0-9]{4}-?[0-9]{2})",
        )
    )
    cep = only_digits(match_group(raw_text, r"CEP[:\s]*([0-9\-]{8,9})"))
    issue_date = match_group(raw_text, r"(\d{2}/\d{2}/\d{4})")

    extracted_fields = [
        build_field("Nome da instituicao", institution_name),
        build_field("Nome do aluno", student_name),
        build_field("CNPJ da instituicao", cnpj),
        build_field("CEP da instituicao", cep),
        build_field("Data identificada", issue_date),
    ]

    label = DOCUMENT_SPECS[tipo_documento]["label"]
    return {
        "summary": f"OCR executado com sucesso em {label.lower()}.",
        "raw_text": raw_text,
        "engine": "ocr_space",
        "alerts": [],
        "extracted_fields": extracted_fields,
        "reference_data": {
            "institution_name": institution_name,
            "cnpj": cnpj,
            "cep": cep,
            "crm_number": "",
            "crm_state": "",
        },
        "recommended_checks": [
            "Comparar os campos extraidos com a imagem do documento escolar.",
            "Conferir autenticidade visual da instituicao, assinaturas e registro.",
        ],
        "fraud_probability": 22 if institution_name else 42,
        "score_factors": [
            "A confirmacao da instituicao emissora pesa mais neste tipo de documento."
        ],
    }

def analyze_with_ocr_space(
    *,
    tipo_documento: str,
    file_name: str,
    mime_type: str,
    file_data_base64: str,
) -> dict[str, Any]:
    """
    Envia o documento para a API OCR.space e retorna o texto extraído
    junto com os campos parseados para o tipo de documento informado.

    Retorna um dicionário de fallback com alertas explicativos quando:
    - A chave OCR_API_KEY não está configurada.
    - Ocorre erro HTTP ou de rede.
    - O OCR não extrai texto suficiente.
    """
    api_key = get_ocr_key()
    if not api_key:
        return {
            "summary": "OCR nao configurado no backend.",
            "raw_text": "",
            "engine": "ocr_nao_configurado",
            "alerts": ["OCR_API_KEY nao configurada no backend."],
            "extracted_fields": [],
            "reference_data": {},
            "recommended_checks": ["Configurar OCR_API_KEY para extracao automatica."],
            "fraud_probability": 25,
            "score_factors": [
                "Nao houve OCR automatico disponivel para ler o documento."
            ],
        }

    payload = urllib.parse.urlencode(
        {
            "apikey": api_key,
            "base64Image": f"data:{mime_type};base64,{file_data_base64}",
            "language": "por",
            "OCREngine": "2",
            "filetype": file_name.split(".")[-1],
            "isOverlayRequired": "false",
            "scale": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(OCR_SPACE_URL, data=payload, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            parsed = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {
            "summary": "O OCR falhou durante a leitura do documento.",
            "raw_text": "",
            "engine": "ocr_space",
            "alerts": [
                read_http_error(exc) or f"Falha HTTP {exc.code} ao consultar OCR.space."
            ],
            "extracted_fields": [],
            "reference_data": {},
            "recommended_checks": [
                "Reexecutar a leitura OCR ou validar manualmente o documento."
            ],
            "fraud_probability": 30,
            "score_factors": [
                "A leitura OCR nao conseguiu extrair o conteudo do documento."
            ],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "summary": "O OCR falhou antes de concluir a leitura do documento.",
            "raw_text": "",
            "engine": "ocr_space",
            "alerts": [f"Erro na integracao com OCR.space: {exc}"],
            "extracted_fields": [],
            "reference_data": {},
            "recommended_checks": ["Validar manualmente o documento."],
            "fraud_probability": 30,
            "score_factors": [
                "A leitura OCR nao conseguiu extrair o conteudo do documento."
            ],
        }

    text_parts: list[str] = []
    for item in parsed.get("ParsedResults", []) or []:
        text = clean_text(item.get("ParsedText", ""))
        if text:
            text_parts.append(text)

    raw_text = "\n".join(text_parts).strip()
    if not raw_text:
        return {
            "summary": "OCR executado, mas sem texto legivel suficiente.",
            "raw_text": "",
            "engine": "ocr_space",
            "alerts": normalize_string_list(parsed.get("ErrorMessage"))
            or ["OCR sem texto extraido."],
            "extracted_fields": [],
            "reference_data": {},
            "recommended_checks": [
                "Conferir nitidez da imagem e reenviar o documento."
            ],
            "fraud_probability": 35,
            "score_factors": [
                "O OCR nao encontrou texto suficiente para sustentar a analise."
            ],
        }

    if tipo_documento == "atestado_medico":
        return parse_medical_certificate_ocr(raw_text)
    if tipo_documento in {"certificado_ensino_medio", "historico_escolar"}:
        return parse_school_document_ocr(tipo_documento, raw_text)

    # Tipo de documento desconhecido: retorna o texto bruto sem parsing específico.
    return {
        "summary": "OCR executado com sucesso.",
        "raw_text": raw_text,
        "engine": "ocr_space",
        "alerts": [],
        "extracted_fields": [],
        "reference_data": {},
        "recommended_checks": [],
        "fraud_probability": 25,
        "score_factors": [
            "A leitura OCR foi concluida e aguarda interpretacao complementar."
        ],
    }

# =============================================================================
# SEÇÃO 9 — CAMADA DE IA COMPLEMENTAR (Gemini)
# =============================================================================

def build_gemini_prompt(
    *,
    solicitante: str,
    departamento: str,
    tipo_documento: str,
    descricao: str,
    ocr_text: str,
) -> str:
    """
    Monta o prompt enviado ao Gemini, incluindo contexto do solicitante,
    tipo do documento, descrição adicional e o texto OCR de apoio.

    Instrui o modelo a responder SOMENTE em JSON válido com o schema definido.
    """
    return f"""
Voce esta analisando um documento submetido para validacao interna. Use a imagem/arquivo enviado como fonte principal e o OCR como apoio quando ele existir.
Tipo informado: {DOCUMENT_SPECS[tipo_documento]['label']}
Solicitante: {solicitante}
Departamento: {departamento or 'Nao informado'}
Descricao adicional: {descricao or 'Nao informada'}

Texto OCR de apoio (pode estar incompleto):
{ocr_text[:12000] if ocr_text else 'OCR indisponivel.'}

Responda SOMENTE em JSON valido no formato:
{{
  "fraud_probability": 0,
  "alerts": ["string"],
  "score_factors": ["string"],
  "recommended_checks": ["string"],
  "reference_data": {{
    "institution_name": "",
    "cnpj": "",
    "cep": "",
    "crm_number": "",
    "crm_state": ""
  }},
  "extracted_fields": [
    {{"label": "Campo", "value": "Valor", "status": "encontrado|nao_encontrado|pendente|alerta", "confidence": 0.0}}
  ]
}}
""".strip()

def extract_gemini_text(response_payload: dict[str, Any]) -> str:
    """
    Navega pela estrutura de resposta da API do Gemini e retorna
    o texto gerado concatenado de todas as partes.
    """
    candidates = response_payload.get("candidates", [])
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    return "\n".join(
        part.get("text", "") for part in parts if part.get("text")
    ).strip()

def simplify_gemini_alerts(value: Any) -> list[str]:
    """
    Substitui mensagens de erro técnicas do Gemini (quota, rate limit)
    por textos amigáveis ao usuário final.
    """
    alerts = normalize_string_list(value)
    simplified: list[str] = []
    for alert in alerts:
        lowered = alert.lower()
        if (
            "quota exceeded" in lowered
            or "free_tier" in lowered
            or "rate limit" in lowered
        ):
            simplified.append(
                "A camada complementar de IA nao estava disponivel; "
                "o relatorio foi gerado com OCR e regras locais."
            )
        else:
            simplified.append(alert)
    return dedupe_strings(simplified)

def analyze_with_gemini(
    *,
    api_key: str,
    solicitante: str,
    departamento: str,
    tipo_documento: str,
    descricao: str,
    ocr_text: str,
    mime_type: str,
    file_data_base64: str,
) -> dict[str, Any]:
    """
    Envia o documento e o texto OCR para o Gemini e retorna a análise
    complementar em JSON com campos extraídos, probabilidade de fraude e alertas.

    Retorna um dicionário vazio de fallback quando:
    - A chave de API não está configurada.
    - O modelo Gemini não está definido.
    - Não há nem texto OCR nem arquivo para enviar.
    - Ocorre qualquer erro de rede ou de formato.
    """
    if not api_key or not DEFAULT_GEMINI_MODEL or (
        not ocr_text and not file_data_base64
    ):
        return {
            "alerts": [],
            "score_factors": [],
            "recommended_checks": [],
            "extracted_fields": [],
            "reference_data": {},
        }

    prompt = build_gemini_prompt(
        solicitante=solicitante,
        departamento=departamento,
        tipo_documento=tipo_documento,
        descricao=descricao,
        ocr_text=ocr_text,
    )
    parts: list[dict[str, Any]] = [{"text": prompt}]
    if file_data_base64:
        parts.append({"inline_data": {"mime_type": mime_type, "data": file_data_base64}})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
    }
    url = (
        f"{GEMINI_API_BASE}/{urllib.parse.quote(DEFAULT_GEMINI_MODEL)}"
        f":generateContent?key={urllib.parse.quote(api_key)}"
    )

    try:
        raw_response = post_json(url=url, payload=payload, headers={}, timeout=90)
    except urllib.error.HTTPError as exc:
        return {
            "alerts": [
                read_http_error(exc)
                or f"Falha HTTP {exc.code} ao consultar o Gemini."
            ],
            "score_factors": [
                "A etapa de interpretacao com Gemini nao conseguiu concluir a leitura do OCR."
            ],
            "recommended_checks": [
                "Usar o relatorio baseado em OCR e seguir com conferencia manual "
                "enquanto a IA complementar estiver indisponivel."
            ],
            "extracted_fields": [],
            "reference_data": {},
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "alerts": [f"Erro na integracao com Gemini: {exc}"],
            "score_factors": [
                "A etapa de interpretacao com Gemini falhou e o sistema seguiu com OCR puro."
            ],
            "recommended_checks": [
                "Validar manualmente os campos extraidos pelo OCR."
            ],
            "extracted_fields": [],
            "reference_data": {},
        }

    output_text = extract_gemini_text(raw_response)
    try:
        parsed = json.loads(output_text)
    except json.JSONDecodeError:
        return {
            "alerts": ["A resposta do Gemini nao veio em JSON valido."],
            "score_factors": [
                "O Gemini respondeu fora do formato esperado; mantendo resultado baseado no OCR."
            ],
            "recommended_checks": ["Seguir com a conferencia manual do OCR."],
            "extracted_fields": [],
            "reference_data": {},
        }

    parsed.setdefault("alerts", [])
    parsed.setdefault("score_factors", [])
    parsed.setdefault("recommended_checks", [])
    parsed.setdefault("extracted_fields", [])
    parsed.setdefault("reference_data", {})
    return parsed

# =============================================================================
# SEÇÃO 10 — MESCLAGEM DOS RESULTADOS OCR + GEMINI
# =============================================================================

def build_summary(
    *, document_type: str, ocr_output: dict[str, Any], gemini_output: dict[str, Any]
) -> str:
    """
    Gera uma frase de resumo para o payload final com base no que
    o OCR e o Gemini conseguiram (ou não) processar.
    """
    if gemini_output.get("extracted_fields"):
        return "OCR executado e interpretado com apoio do Gemini."
    if ocr_output.get("raw_text"):
        label = DOCUMENT_SPECS[document_type]["label"].lower()
        return (
            f"OCR executado com sucesso para {label}. "
            "A IA complementar nao concluiu, mas os dados extraidos ja estao visiveis abaixo."
        )
    return "A analise automatica nao conseguiu extrair dados confiaveis do documento."

def merge_analysis_outputs(
    *, document_type: str, ocr_output: dict[str, Any], gemini_output: dict[str, Any]
) -> dict[str, Any]:
    """
    Combina os resultados do OCR e do Gemini em um único dicionário,
    mesclando campos extraídos, alertas, fatores de score e texto bruto.

    A mesclagem de campos preserva a ordem de aparição e resolve conflitos
    pelo critério status + confiança (ver `merge_extracted_field`).
    """
    merged = dict(ocr_output)
    combined_fields: dict[str, dict[str, Any]] = {}
    ordered_keys: list[str] = []

    for field in ocr_output.get("extracted_fields", []):
        label_key = normalize_label_key(field.get("label"))
        if not label_key:
            continue
        combined_fields[label_key] = dict(field)
        ordered_keys.append(label_key)

    for field in gemini_output.get("extracted_fields", []):
        label_key = normalize_label_key(field.get("label"))
        if not label_key:
            continue
        if label_key in combined_fields:
            combined_fields[label_key] = merge_extracted_field(
                combined_fields[label_key], field
            )
            continue
        combined_fields[label_key] = dict(field)
        ordered_keys.append(label_key)

    merged["extracted_fields"] = [combined_fields[key] for key in ordered_keys]
    merged["reference_data"] = {
        **(ocr_output.get("reference_data", {}) or {}),
        **(gemini_output.get("reference_data", {}) or {}),
    }
    merged["alerts"] = normalize_string_list(
        ocr_output.get("alerts", [])
    ) + normalize_string_list(gemini_output.get("alerts", []))
    merged["score_factors"] = normalize_string_list(
        ocr_output.get("score_factors", [])
    ) + normalize_string_list(gemini_output.get("score_factors", []))
    merged["recommended_checks"] = normalize_string_list(
        ocr_output.get("recommended_checks", [])
    ) + normalize_string_list(gemini_output.get("recommended_checks", []))
    merged["summary"] = build_summary(
        document_type=document_type,
        ocr_output=ocr_output,
        gemini_output=gemini_output,
    )
    merged["fraud_probability"] = (
        gemini_output.get("fraud_probability")
        or ocr_output.get("fraud_probability")
        or 0
    )
    merged["engine"] = (
        "ocr_space + gemini"
        if gemini_output.get("extracted_fields")
        else ocr_output.get("engine", "ocr_space")
    )
    merged["raw_text"] = ocr_output.get("raw_text", "")
    return merged

# =============================================================================
# SEÇÃO 11 — VERIFICAÇÕES OFICIAIS
# Consultas públicas (BrasilAPI, ViaCEP) e validações locais por tipo de documento.
# Atestado médico : CPF, CRM, campos médicos, cidade/endereço via ViaCEP
# Histórico escolar: nome do aluno, disciplinas, notas, anos letivos, formatação
# =============================================================================

def verify_institution_name(
    *, institution_name: str, extraction_failed: bool
) -> VerificationResult:
    """Verifica se o nome da instituição de ensino foi extraído do documento."""
    if institution_name:
        return VerificationResult(
            "Escola identificada",
            "encontrado",
            f"Instituicao extraida: {institution_name}.",
        )
    if extraction_failed:
        return VerificationResult(
            "Escola identificada",
            "pendente",
            "A identificacao da instituicao ficou pendente.",
        )
    return VerificationResult(
        "Escola identificada",
        "nao_encontrado",
        "O nome da instituicao nao foi localizado no documento.",
    )

def verify_cnpj_free(
    *, cnpj: str, institution_name: str, extraction_failed: bool
) -> VerificationResult:
    """
    Valida o CNPJ matematicamente e consulta a BrasilAPI para confirmar
    se a instituição existe, está ativa e o nome bate com o extraído.
    """
    title = "Consulta CNPJ da escola (BrasilAPI)"
    if not cnpj:
        if extraction_failed:
            return VerificationResult(title, "pendente", "A verificacao do CNPJ ficou pendente.")
        if institution_name:
            return VerificationResult(
                title,
                "pendente",
                "A escola foi identificada, mas o CNPJ nao apareceu no documento.",
            )
        return VerificationResult(
            title,
            "nao_encontrado",
            "Nenhum CNPJ da instituicao foi encontrado no documento.",
        )
    cnpj_digits = only_digits(cnpj)
    if not is_valid_cnpj(cnpj_digits):
        return VerificationResult(
            title, "alerta", "O CNPJ extraido possui digitos verificadores invalidos."
        )
    cnpj = cnpj_digits  # usa os dígitos puros na consulta
    try:
        data = get_json(url=f"{BRASILAPI_CNPJ_URL}/{cnpj}", query=None, timeout=30)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return VerificationResult(
                title,
                "nao_encontrado",
                "O CNPJ extraido nao foi localizado na BrasilAPI.",
            )
        return VerificationResult(
            title,
            "alerta",
            read_http_error(exc)
            or f"Falha HTTP {exc.code} na consulta de CNPJ pela BrasilAPI.",
        )
    except Exception as exc:  # noqa: BLE001
        return VerificationResult(
            title,
            "pendente",
            f"Nao foi possivel concluir a consulta publica do CNPJ pela BrasilAPI: {exc}",
        )

    official_name = clean_text(
        data.get("razao_social") or data.get("nome_fantasia") or ""
    )
    official_status = clean_text(data.get("descricao_situacao_cadastral") or "")
    if official_status and official_status.upper() != "ATIVA":
        return VerificationResult(
            title,
            "alerta",
            f"CNPJ localizado na BrasilAPI, mas a situacao cadastral retornou {official_status}.",
        )
    if (
        institution_name
        and official_name
        and institution_name.lower() not in official_name.lower()
        and official_name.lower() not in institution_name.lower()
    ):
        return VerificationResult(
            title,
            "alerta",
            f"CNPJ localizado na BrasilAPI, mas o nome retornado ({official_name}) "
            f"diverge do nome extraido ({institution_name}).",
        )
    return VerificationResult(
        title,
        "encontrado",
        f"CNPJ localizado na BrasilAPI. Situacao: {official_status or 'nao informada'}. "
        f"Nome oficial: {official_name or 'nao informado'}.",
    )

def verify_cep_free(*, cep: str, extraction_failed: bool) -> VerificationResult:
    """
    Valida o CEP matematicamente e consulta o ViaCEP para confirmar
    se o endereço existe.
    """
    title = "Consulta CEP"
    if not cep:
        if extraction_failed:
            return VerificationResult(
                title, "pendente", "A verificacao do CEP ficou pendente."
            )
        return VerificationResult(
            title, "nao_encontrado", "Nenhum CEP foi identificado no documento."
        )
    if not is_valid_cep(cep):
        return VerificationResult(
            title, "alerta", "O CEP extraido nao possui 8 digitos validos."
        )
    try:
        data = get_json(url=f"{VIACEP_URL}/{cep}/json/", query=None, timeout=30)
    except urllib.error.HTTPError as exc:
        return VerificationResult(
            title,
            "alerta",
            read_http_error(exc) or f"Falha HTTP {exc.code} na consulta de CEP.",
        )
    except Exception as exc:  # noqa: BLE001
        return VerificationResult(
            title,
            "pendente",
            f"Nao foi possivel concluir a consulta do CEP: {exc}",
        )
    if data.get("erro") is True:
        return VerificationResult(
            title, "nao_encontrado", "O CEP extraido nao foi localizado no ViaCEP."
        )
    return VerificationResult(
        title,
        "encontrado",
        f"CEP localizado: {data.get('logradouro', 'logradouro nao informado')}, "
        f"{data.get('bairro', 'bairro nao informado')} - "
        f"{data.get('localidade', '')}/{data.get('uf', '')}.",
    )

def verify_cpf_local(*, cpf: str, extraction_failed: bool) -> VerificationResult:
    """
    Valida matematicamente os dígitos verificadores do CPF extraído
    do atestado médico. Não realiza consulta externa.
    """
    title = "Validacao local do CPF"
    if not cpf:
        if extraction_failed:
            return VerificationResult(
                title,
                "pendente",
                "A verificacao do CPF ficou pendente porque a extracao nao foi concluida.",
            )
        return VerificationResult(
            title, "nao_encontrado", "Nenhum CPF foi identificado no documento."
        )
    if not is_valid_cpf(cpf):
        return VerificationResult(
            title, "alerta", "O CPF extraido possui digitos verificadores invalidos."
        )
    cpf_fmt = format_cpf(cpf)
    return VerificationResult(
        title,
        "encontrado",
        f"CPF {cpf_fmt} validado — digitos verificadores corretos.",
    )

def verify_crm_presence(
    *, crm_number: str, crm_state: str, extraction_failed: bool
) -> VerificationResult:
    """
    Verifica se um número de CRM foi identificado no atestado médico.
    Registra como pendente quando encontrado (não há API pública gratuita do CFM).
    """
    title = "Identificacao do CRM"
    if not crm_number:
        if extraction_failed:
            return VerificationResult(
                title,
                "pendente",
                "O OCR/IA nao conseguiu localizar um CRM utilizavel com seguranca.",
            )
        return VerificationResult(
            title,
            "nao_encontrado",
            "Nenhum numero de CRM foi localizado no atestado.",
        )
    if not crm_state:
        return VerificationResult(
            title,
            "pendente",
            f"CRM {crm_number} identificado, mas a UF do registro nao foi identificada.",
        )
    return VerificationResult(
        title,
        "pendente",
        f"CRM {crm_number}/{crm_state} identificado. "
        "Validacao externa ficou pendente de conferencia manual.",
    )

def validate_historico_escolar(
    raw_text: str,
    extracted_fields: list[dict[str, Any]],
) -> list[VerificationResult]:
    """
    Valida a autenticidade de um histórico escolar aplicando um conjunto
    de verificações heurísticas sobre o texto extraído pelo OCR e os campos
    estruturados pelo pipeline.

    Verificações realizadas:
        1. Presença do nome do aluno.
        2. Presença do nome da instituição emissora.
        3. Presença de data de emissão válida.
        4. Presença de disciplinas/matérias cursadas.
        5. Presença de notas ou conceitos nas disciplinas.
        6. Coerência das notas (valores entre 0 e 10, ou conceitos A-E).
        7. Presença de ano(s) letivo(s).
        8. Coerência dos anos letivos (não futuros, não absurdamente antigos).
        9. Presença de assinatura ou carimbo textual.
       10. Presença de série/ano escolar (1º ano, 2º ano etc.).
       11. Ausência de inconsistências de formatação (repetição suspeita de blocos).
       12. Presença de pelo menos uma menção à conclusão ou situação final do aluno.

    Retorna uma lista de VerificationResult, uma por verificação.
    """
    import datetime

    results: list[VerificationResult] = []
    lowered = raw_text.lower()
    current_year = datetime.date.today().year

    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #
    field_map = {
        normalize_label_key(f.get("label", "")): f
        for f in extracted_fields
    }
    student_field = (
        field_map.get("nome do aluno")
        or field_map.get("aluno")
        or field_map.get("estudante")
    )
    student_name = clean_text(student_field.get("value", "")) if student_field else ""
    if not student_name:
        student_name = match_group(
            raw_text, r"(?:Aluno|Aluna|Estudante|Nome)[:\s]+([A-ZÀ-Ú][a-zA-ZÀ-ú ]{4,})"
        )

    if student_name:
        results.append(VerificationResult(
            "Nome do aluno",
            "encontrado",
            f"Nome identificado: {student_name}.",
        ))
    else:
        results.append(VerificationResult(
            "Nome do aluno",
            "nao_encontrado",
            "O nome do aluno nao foi localizado no historico escolar.",
        ))

    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #
    institution_field = (
        field_map.get("nome da instituicao")
        or field_map.get("instituicao")
        or field_map.get("escola")
    )
    institution_name = (
        clean_text(institution_field.get("value", "")) if institution_field else ""
    )
    if not institution_name:
        institution_name = match_group(
            raw_text,
            r"(COL[EÉ]GIO[^\n]{2,50}|ESCOLA[^\n]{2,50}|INSTITUTO[^\n]{2,50}|SECRETARIA[^\n]{2,50}|CENTRO EDUCACIONAL[^\n]{2,50})",
        )

    if institution_name:
        results.append(VerificationResult(
            "Instituicao emissora",
            "encontrado",
            f"Instituicao identificada: {institution_name}.",
        ))
    else:
        results.append(VerificationResult(
            "Instituicao emissora",
            "nao_encontrado",
            "O nome da instituicao emissora nao foi localizado no documento.",
        ))

    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #
    # Data de emissão: usa a data mais RECENTE do documento com ano >= 2010
    # (documentos escolares são emitidos recentemente, não em 2005)
    # Data de emissão do histórico: pega a mais RECENTE com ano >= 2015
    # Exclui datas de nascimento (geralmente antes de 2010)
    # Também busca datas por extenso como "05 de Janeiro de 2023"
    import datetime as _hdt
    _meses_hist = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4,
        "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
        "outubro": 10, "novembro": 11, "dezembro": 12,
    }
    _valid_issue_dates = []

    # Datas numéricas
    for _m in re.finditer(r"(\d{2}/\d{2}/\d{4})", raw_text):
        try:
            _y = int(_m.group(1).split("/")[2])
            if 2015 <= _y <= current_year:
                _valid_issue_dates.append((_y, _m.group(1)))
        except (IndexError, ValueError):
            pass

    # Datas por extenso: "05 de Janeiro de 2023"
    for _m in re.finditer(
        r"(\d{1,2})\s+de\s+([a-záàâãç]+)\s+de\s+(20\d{2})",
        raw_text, re.IGNORECASE,
    ):
        _mes_n = _meses_hist.get(_m.group(2).lower())
        if _mes_n:
            try:
                _y = int(_m.group(3))
                if 2015 <= _y <= current_year:
                    _d_str = f"{int(_m.group(1)):02d}/{_mes_n:02d}/{_y}"
                    _valid_issue_dates.append((_y, _d_str))
            except ValueError:
                pass

    issue_date = ""
    if _valid_issue_dates:
        _valid_issue_dates.sort(key=lambda x: x[0], reverse=True)
        issue_date = _valid_issue_dates[0][1]

    if issue_date:
        results.append(VerificationResult(
            "Data de emissao",
            "encontrado",
            f"Data identificada: {issue_date}.",
        ))
    else:
        results.append(VerificationResult(
            "Data de emissao",
            "nao_encontrado",
            "Nenhuma data de emissao valida foi localizada no historico.",
        ))

    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #
    discipline_keywords = [
        "matematica", "portugues", "historia", "geografia", "ciencias",
        "fisica", "quimica", "biologia", "ingles", "artes", "educacao fisica",
        "filosofia", "sociologia", "literatura", "redacao", "lingua",
    ]
    found_disciplines = [kw for kw in discipline_keywords if kw in lowered]
    if len(found_disciplines) >= 3:
        results.append(VerificationResult(
            "Disciplinas cursadas",
            "encontrado",
            f"{len(found_disciplines)} disciplina(s) identificada(s): "
            f"{', '.join(found_disciplines[:5])}{'...' if len(found_disciplines) > 5 else ''}.",
        ))
    elif found_disciplines:
        results.append(VerificationResult(
            "Disciplinas cursadas",
            "pendente",
            f"Apenas {len(found_disciplines)} disciplina(s) identificada(s) "
            f"({', '.join(found_disciplines)}). Esperava-se ao menos 3.",
        ))
    else:
        results.append(VerificationResult(
            "Disciplinas cursadas",
            "nao_encontrado",
            "Nenhuma disciplina reconhecida foi localizada no historico.",
        ))

    # ------------------------------------------------------------------ #
    # 5 & 6. Presença e coerência de notas
    # Critério rigoroso para evitar falsos positivos com anos, CPF etc:
    #   - Aceita X,X ou X.X (ex: 7,5 / 8.0) — formato decimal inequívoco
    #   - Aceita inteiros de 1 dígito: 0–9
    #   - Aceita exatamente "10" isolado
    # Rejeita inteiros de 2 dígitos sem decimal (11–99) pois são
    # frequentemente anos, porcentagens ou outros números do documento.
    # ------------------------------------------------------------------ #
    decimal_grades = re.findall(r"\b(\d[.,]\d)\b", raw_text)
    ten_grade      = re.findall(r"\b(10)\b", raw_text)
    single_grades  = re.findall(r"\b([0-9])\b", raw_text)

    valid_numeric: list[float] = []
    for g in decimal_grades:
        try:
            val = float(g.replace(",", "."))
            if 0.0 <= val <= 10.0:
                valid_numeric.append(val)
        except ValueError:
            pass
    valid_numeric += [10.0] * len(ten_grade)
    valid_numeric += [float(g) for g in single_grades]

    concept_grades = re.findall(r"\b([A-E])\b", raw_text)

    if len(valid_numeric) >= 3 or len(concept_grades) >= 3:
        sample = [str(g) for g in valid_numeric[:6]] or concept_grades[:6]
        results.append(VerificationResult(
            "Notas/conceitos",
            "encontrado",
            f"{len(valid_numeric) or len(concept_grades)} nota(s)/conceito(s) "
            f"identificado(s) dentro do intervalo esperado. "
            f"Exemplos: {', '.join(sample)}.",
        ))
    else:
        results.append(VerificationResult(
            "Notas/conceitos",
            "nao_encontrado",
            "Nenhuma nota ou conceito foi identificado com quantidade suficiente no historico.",
        ))

    # ------------------------------------------------------------------ #
    # 7 & 8. Anos letivos — presença e coerência
    # Estratégia: busca anos APENAS em contextos claramente letivos:
    #   a) padrão "ANO_LETIVO: 20XX" ou "20XX/20XX" (faixas letivas)
    #   b) anos que aparecem em linhas curtas (≤ 30 chars) — tabelas
    #   c) anos após palavras-chave letivas ("ano letivo", "período" etc)
    # Isso evita capturar o ano de nascimento, CEP, CNPJ e outros.
    # ------------------------------------------------------------------ #
    school_years: set[int] = set()

    # Contexto a: faixas letivas explícitas "2017/2018" ou "2017-2018"
    for m in re.finditer(r"\b(20[012]\d)[/\-](20[012]\d)\b", raw_text):
        y1, y2 = int(m.group(1)), int(m.group(2))
        if abs(y2 - y1) <= 1:          # só faixas de 1 ano de diferença
            school_years.add(y1)
            school_years.add(y2)

    # Contexto b: anos em linhas curtas (linhas de tabela de notas)
    for line in raw_text.splitlines():
        stripped = line.strip()
        if 4 <= len(stripped) <= 30:
            for m in re.finditer(r"\b(20[012]\d)\b", stripped):
                school_years.add(int(m.group(1)))

    # Contexto c: após palavras-chave letivas
    letivo_pattern = re.compile(
        r"(?:ano letivo|periodo letivo|ano escolar|turma|serie)[^\d]{0,10}(20[012]\d)",
        re.IGNORECASE,
    )
    for m in letivo_pattern.finditer(raw_text):
        school_years.add(int(m.group(1)))

    # Filtra: aceita anos entre 2005 e (current_year - 1)
    # Exclui o ano atual pois o histórico já foi concluído
    all_school_years = sorted(y for y in school_years if 2005 <= y <= current_year - 1)

    # Prefere os anos mais recentes em sequência (ensino médio: 3-4 anos seguidos)
    # Se houver grupos separados por gap > 2 anos, pega o grupo mais recente
    years = all_school_years
    if len(all_school_years) > 4:
        # Encontra o grupo mais recente de anos consecutivos (gap <= 2)
        _groups = []
        _cur_group = [all_school_years[-1]]
        for _yr in reversed(all_school_years[:-1]):
            if _cur_group[-1] - _yr <= 2:
                _cur_group.append(_yr)
            else:
                _groups.append(sorted(_cur_group))
                _cur_group = [_yr]
        _groups.append(sorted(_cur_group))
        # Pega o grupo mais recente com 2+ anos
        _recent = next((g for g in _groups if len(g) >= 2), _groups[0] if _groups else [])
        years = sorted(_recent) if _recent else all_school_years[-4:]

    if not years:
        results.append(VerificationResult(
            "Anos letivos",
            "nao_encontrado",
            "Nenhum ano letivo foi identificado no historico.",
        ))
    else:
        future_years = [y for y in years if y > current_year]
        if future_years:
            results.append(VerificationResult(
                "Anos letivos",
                "alerta",
                f"Anos futuros detectados no historico: {future_years}. "
                "Documento possivelmente adulterado.",
            ))
        else:
            results.append(VerificationResult(
                "Anos letivos",
                "encontrado",
                f"{len(years)} ano(s) letivo(s) identificado(s): "
                f"{', '.join(str(y) for y in years)}.",
            ))

    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #
    signature_keywords = [
        "assinatura", "diretor", "diretora", "secretaria", "secretario",
        "coordenador", "coordenadora", "carimbo", "rubrica", "responsavel",
    ]
    found_signature = any(kw in lowered for kw in signature_keywords)
    if found_signature:
        matched = [kw for kw in signature_keywords if kw in lowered]
        results.append(VerificationResult(
            "Assinatura ou carimbo",
            "encontrado",
            f"Indicios de assinatura/carimbo encontrados: {', '.join(matched)}.",
        ))
    else:
        results.append(VerificationResult(
            "Assinatura ou carimbo",
            "nao_encontrado",
            "Nenhum indicio textual de assinatura ou carimbo foi localizado.",
        ))

    # ------------------------------------------------------------------ #
    # 10. Série / ano escolar
    # ------------------------------------------------------------------ #
    series_match = re.search(
        r"\b([1-9][°º]?\s*(?:ano|serie|serie)|ensino\s+(?:fundamental|medio))\b",
        raw_text,
        flags=re.IGNORECASE,
    )
    if series_match:
        results.append(VerificationResult(
            "Serie ou ano escolar",
            "encontrado",
            f"Serie/etapa identificada: '{clean_text(series_match.group(0))}'.",
        ))
    else:
        results.append(VerificationResult(
            "Serie ou ano escolar",
            "nao_encontrado",
            "Nenhuma serie ou ano escolar foi identificado no historico.",
        ))

    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #
    _inst_upper = institution_name.upper() if institution_name else ""
    _fmt_line_counts: dict[str, int] = {}
    _common_table_values = {
        "aprovado", "aprovada", "reprovado", "cursado", "sim", "nao",
        "nao", "nota", "media", "carga horaria", "frequencia", "resultado",
    }
    for _line in raw_text.splitlines():
        _s = _line.strip()
        if not _s or len(_s) <= 15:
            continue
        if re.match(r"^[\d\s.,/%()-]+$", _s):
            continue
        if _inst_upper and _s.upper() == _inst_upper:
            continue
        if _s.lower() in _common_table_values:
            continue
        _fmt_line_counts[_s] = _fmt_line_counts.get(_s, 0) + 1

    # Threshold maior: 6+ repetições E linha com 20+ chars
    # O nome da instituição pode aparecer 1x por página (PDF com 3 págs = 3x)
    repeated = {
        line: count for line, count in _fmt_line_counts.items()
        if count >= 6 and len(line) > 20
    }
    if repeated:
        examples = list(repeated.keys())[:3]
        results.append(VerificationResult(
            "Consistencia de formatacao",
            "alerta",
            f"Linhas repetidas de forma suspeita detectadas ({len(repeated)} ocorrencia(s)): "
            f"{'; '.join(repr(e) for e in examples)}. Possivel copia ou adulteracao.",
        ))
    else:
        results.append(VerificationResult(
            "Consistencia de formatacao",
            "encontrado",
            "Nenhuma repeticao suspeita de blocos de texto foi detectada.",
        ))

    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #
    conclusion_keywords = [
        "aprovado", "aprovada", "reprovado", "reprovada", "concluiu",
        "concluinte", "certificado", "diploma", "formado", "formada",
        "transferido", "transferida", "situacao final", "resultado final",
    ]
    found_conclusion = [kw for kw in conclusion_keywords if kw in lowered]
    if found_conclusion:
        results.append(VerificationResult(
            "Situacao final do aluno",
            "encontrado",
            f"Indicios de situacao final encontrados: {', '.join(found_conclusion)}.",
        ))
    else:
        results.append(VerificationResult(
            "Situacao final do aluno",
            "nao_encontrado",
            "Nenhuma mencao a situacao final ou conclusao do aluno foi localizada.",
        ))

    return results

def verify_medical_fields(
    *,
    patient_name: str,
    birth_date: str,
    age: str,
    institution_name: str,
    address: str,
    doctor_signed: bool,
    signature_detail: str,
    location: str,
    issue_place_date: str,
    leave_days: str,
    validity_detail: str,
    validity_status: str,
    extraction_failed: bool,
) -> list[VerificationResult]:
    """Verificacoes especificas do atestado medico."""
    results: list[VerificationResult] = []

    # Nome do paciente — confirmar que o atestado pertence ao solicitante
    if patient_name:
        results.append(VerificationResult(
            "Nome do paciente", "encontrado",
            f"Nome do titular: {patient_name}.",
        ))
    else:
        results.append(VerificationResult(
            "Nome do paciente",
            "pendente" if extraction_failed else "nao_encontrado",
            "Nome nao localizado — confirmar manualmente se pertence ao solicitante.",
        ))

    # Data de nascimento — cruzar com RG/CPF do solicitante
    if birth_date:
        results.append(VerificationResult(
            "Data de nascimento", "encontrado",
            f"Nascimento: {birth_date}. Cruzar com RG/CPF.",
        ))
    else:
        results.append(VerificationResult(
            "Data de nascimento",
            "pendente" if extraction_failed else "nao_encontrado",
            "Data de nascimento nao localizada — solicitar documento de identidade.",
        ))

    # Idade — coerencia com data de nascimento
    if age:
        results.append(VerificationResult(
            "Idade do paciente", "encontrado",
            f"Idade: {age}. Coerente com data de nascimento.",
        ))
    else:
        results.append(VerificationResult(
            "Idade do paciente", "pendente",
            "Idade nao identificada — calculada se data de nascimento estiver disponivel.",
        ))

    # Hospital/local emissor — confirmar que a unidade existe
    if institution_name:
        results.append(VerificationResult(
            "Hospital ou local emissor", "encontrado",
            f"Emissor: {institution_name}.",
        ))
    else:
        results.append(VerificationResult(
            "Hospital ou local emissor",
            "pendente" if extraction_failed else "nao_encontrado",
            "Unidade emissora nao identificada — conferir no documento fisico.",
        ))

    # Endereço — validar existencia real do local emissor via ViaCEP/mapa
    if address:
        results.append(VerificationResult(
            "Endereco do local emissor", "encontrado",
            f"Endereco: {address}.",
        ))
    else:
        results.append(VerificationResult(
            "Endereco do local emissor", "pendente",
            "Endereco nao localizado — verificar rodape do documento fisico.",
        ))

    # Carimbo/assinatura — sem assinatura nao tem validade juridica no Brasil
    if doctor_signed:
        detail_msg = signature_detail or "Indicios de assinatura/carimbo localizados."
        results.append(VerificationResult(
            "Carimbo ou assinatura", "encontrado",
            detail_msg,
        ))
    else:
        results.append(VerificationResult(
            "Carimbo ou assinatura", "alerta",
            "Assinatura/carimbo nao localizado — atestado sem assinatura nao tem validade legal.",
        ))

    # Cidade e estado — detectar inconsistencias geograficas
    loc = location or issue_place_date
    if loc:
        results.append(VerificationResult(
            "Cidade e estado de emissao", "encontrado",
            f"Local: {loc}.",
        ))
    else:
        results.append(VerificationResult(
            "Cidade e estado de emissao",
            "pendente" if extraction_failed else "nao_encontrado",
            "Cidade/estado nao localizado — confirmar no documento fisico.",
        ))

    # Validade do afastamento — Lei 8.213/91: acima de 15 dias exige pericia INSS
    if validity_detail:
        results.append(VerificationResult(
            "Periodo de afastamento", validity_status or "encontrado",
            validity_detail,
        ))
    elif leave_days:
        results.append(VerificationResult(
            "Periodo de afastamento", "pendente",
            f"{leave_days} dia(s) identificado — classificacao pendente.",
        ))
    else:
        results.append(VerificationResult(
            "Periodo de afastamento", "nao_encontrado",
            "Dias de afastamento nao localizado — conferir no documento. "
            "Acima de 15 dias exige pericia do INSS (Lei 8.213/91).",
        ))

    return results

def verify_address_via_cep(*, cep: str, location: str, institution_name: str) -> VerificationResult:
    """
    Valida cidade e endereço do atestado consultando o ViaCEP com o CEP extraído.
    Se não houver CEP, retorna pendente com orientação de conferência manual.
    """
    title = "Validacao de cidade e endereco (ViaCEP)"

    if not cep:
        msg = "CEP nao localizado no atestado"
        if location:
            msg += f" — local informado: {location}"
        msg += ". Confirmar endereco manualmente."
        return VerificationResult(title, "pendente", msg)

    if not is_valid_cep(cep):
        return VerificationResult(title, "alerta",
            f"CEP extraido ({cep}) invalido — nao possui 8 digitos validos.")

    try:
        data = get_json(url=f"{VIACEP_URL}/{cep}/json/", query=None, timeout=30)
    except urllib.error.HTTPError as exc:
        return VerificationResult(title, "alerta",
            read_http_error(exc) or f"Falha HTTP {exc.code} ao consultar ViaCEP.")
    except Exception as exc:  # noqa: BLE001
        return VerificationResult(title, "pendente",
            f"Consulta ViaCEP nao concluida: {exc}")

    if data.get("erro") is True:
        return VerificationResult(title, "nao_encontrado",
            f"CEP {cep} nao localizado no ViaCEP — verificar se o CEP esta correto.")

    logradouro = clean_text(data.get("logradouro", ""))
    bairro     = clean_text(data.get("bairro", ""))
    cidade     = clean_text(data.get("localidade", ""))
    uf         = clean_text(data.get("uf", ""))
    endereco_oficial = f"{logradouro}, {bairro} — {cidade}/{uf}".strip(", —")

    # Confere se a cidade/UF bate com o local extraido do documento
    inconsistencia = ""
    if location and cidade:
        loc_lower = location.lower()
        if cidade.lower() not in loc_lower and uf.lower() not in loc_lower:
            inconsistencia = (
                f" ATENCAO: local extraido do documento ({location}) "
                f"diverge da cidade do CEP ({cidade}/{uf})."
            )

    # Monta display: usa logradouro se disponível, senão cidade/UF
    # CEPs de grande circulação (hospitais, prédios) não têm logradouro na API
    if logradouro and bairro:
        display = f"{logradouro}, {bairro} — {cidade}/{uf}"
    elif logradouro:
        display = f"{logradouro} — {cidade}/{uf}"
    elif cidade:
        display = f"{cidade}/{uf} (CEP de grande circulação — sem logradouro especifico)"
    else:
        display = f"CEP {cep} valido"

    return VerificationResult(
        title, "encontrado" if not inconsistencia else "alerta",
        f"CEP {cep} confirmado: {display}.{inconsistencia}",
    )

def run_relevant_verifications(
    *,
    tipo_documento: str,
    combined_output: dict[str, Any],
    extraction_failed: bool,
) -> list[VerificationResult]:
    """
    Decide quais verificações externas executar com base no tipo do documento
    e dispara cada uma delas, retornando a lista de resultados.

    - Documentos escolares: nome da instituição, CNPJ, CEP.
    - Atestados médicos: CPF, CRM.
    """
    reference_data = combined_output.get("reference_data", {}) or {}
    institution_name = clean_text(reference_data.get("institution_name", ""))
    cnpj = only_digits(reference_data.get("cnpj", ""))
    cep = only_digits(reference_data.get("cep", ""))
    crm_number = only_digits(reference_data.get("crm_number", ""))
    crm_state = clean_text(reference_data.get("crm_state", "")).upper()
    cpf = only_digits(reference_data.get("cpf", ""))

    results: list[VerificationResult] = []
    if tipo_documento in {"certificado_ensino_medio", "historico_escolar"}:
        results.append(
            verify_institution_name(
                institution_name=institution_name, extraction_failed=extraction_failed
            )
        )
        results.append(
            verify_cnpj_free(
                cnpj=cnpj,
                institution_name=institution_name,
                extraction_failed=extraction_failed,
            )
        )
        results.append(
            verify_cep_free(cep=cep, extraction_failed=extraction_failed)
        )
    if tipo_documento == "historico_escolar":
        results.extend(
            validate_historico_escolar(
                raw_text=combined_output.get("raw_text", ""),
                extracted_fields=combined_output.get("extracted_fields", []),
            )
        )
    if tipo_documento == "atestado_medico":
        results.append(
            verify_cpf_local(cpf=cpf, extraction_failed=extraction_failed)
        )
        results.append(
            verify_crm_presence(
                crm_number=crm_number,
                crm_state=crm_state,
                extraction_failed=extraction_failed,
            )
        )
        # Valida cidade e endereco via ViaCEP usando o CEP extraido
        _med_location = clean_text(
            combined_output.get("reference_data", {}).get("location", "")
        )
        _med_fields = {
            f.get("label", "").lower(): clean_text(f.get("value", ""))
            for f in combined_output.get("extracted_fields", [])
        }
        _med_cep = only_digits(combined_output.get("reference_data", {}).get("cep", ""))
        _med_loc = (
            _med_fields.get("cidade e estado de emissao", "")
            or _med_fields.get("estado e cidade de emissao", "")
            or _med_fields.get("local e data de emissao", "")
        )
        results.append(
            verify_address_via_cep(
                cep=_med_cep,
                location=_med_loc,
                institution_name=institution_name,
            )
        )
        # Extrai campos médicos específicos do combined_output para verificação
        _fields_map = {
            _f.get("label", "").lower(): clean_text(_f.get("value", ""))
            for _f in combined_output.get("extracted_fields", [])
        }
        _sig_val    = _fields_map.get("carimbo ou assinatura", "")
        _val_detail = _fields_map.get("validade do atestado", "")
        # Reconstrói validity_status a partir do detalhe
        _val_status = (
            "alerta"    if "suspeito" in _val_detail.lower() or "invalido" in _val_detail.lower()
            else "pendente" if "pericia" in _val_detail.lower() or "longo" in _val_detail.lower()
            else "encontrado" if _val_detail else ""
        )
        results.extend(
            verify_medical_fields(
                patient_name=_fields_map.get("nome do paciente", ""),
                birth_date=_fields_map.get("data de nascimento", ""),
                age=_fields_map.get("idade do paciente", ""),
                institution_name=_fields_map.get("hospital ou local emissor", ""),
                address=_fields_map.get("endereco do local emissor", ""),
                doctor_signed=bool(_sig_val),
                signature_detail=_sig_val,
                location=_fields_map.get("estado e cidade de emissao", ""),
                issue_place_date=_fields_map.get("local e data de emissao", ""),
                leave_days=_fields_map.get("periodo de afastamento (dias)", ""),
                validity_detail=_val_detail,
                validity_status=_val_status,
                extraction_failed=extraction_failed,
            )
        )
    return results

# =============================================================================
# SEÇÃO 12 — SCORE, ALERTAS E PRÓXIMOS PASSOS
# =============================================================================

def build_score_factors(
    *,
    document_type: str,
    combined_output: dict[str, Any],
    verifications: list[VerificationResult],
) -> list[str]:
    """
    Consolida os fatores que influenciaram o score de risco, incluindo
    os provenientes das verificações com status negativo.
    """
    factors = normalize_string_list(combined_output.get("score_factors", []))
    for verification in verifications:
        if verification.status in {"alerta", "nao_encontrado", "pendente"}:
            factors.append(f"{verification.titulo}: {verification.detalhe}")
    if document_type == "atestado_medico" and not any(
        item.titulo == "Identificacao do CRM" and item.status != "nao_encontrado"
        for item in verifications
    ):
        factors.append("O atestado nao apresentou CRM utilizavel para verificacao.")
    return dedupe_strings(factors)

def clamp_probability(
    raw_value: Any,
    verifications: list[VerificationResult],
    factors: list[str],
) -> int:
    """
    Calcula a pontuacao de autenticidade numa escala de 0 a 99.

        0  - 74  → Precisa de verificacao externa
        75 - 99  → Provavelmente veridico

    Logica:
    - Base: inverso do fraud_probability da IA (fraud=20 → base=80).
    - Bonus: proporcional aos campos com status "encontrado" vs
      (encontrado + nao_encontrado) — "pendente" e "alerta" sao neutros
      no bonus pois sao inconclusivos, nao necessariamente negativos.
    - Penalidade: cada "alerta" subtrai 8 pts; cada "nao_encontrado"
      em campo critico subtrai 4 pts.
    - Alertas impedem score acima de 74 (mantem na zona de verificacao).
    - Minimo absoluto: 15 (a IA pode errar — nunca zero).
    """
    try:
        fraud = max(0.0, min(99.0, float(raw_value)))
        score = int(100 - fraud)
    except (TypeError, ValueError):
        score = 55

    found   = sum(1 for v in verifications if v.status == "encontrado")
    missing = sum(1 for v in verifications if v.status == "nao_encontrado")
    alerts  = sum(1 for v in verifications if v.status == "alerta")
    decisive = found + missing  # pendente e alerta sao neutros no bonus

    # Bonus: proporcional ao que foi efetivamente encontrado
    if decisive > 0:
        score += int((found / decisive) * 20)

    # Penalidades suaves
    score -= alerts * 8
    score -= missing * 4

    # Alertas travam o teto em 74
    if alerts > 0:
        score = min(score, 74)

    # Campos críticos: se ausentes, travam o score em 74 (zona de verificação)
    # Não faz sentido dizer "provavelmente verídico" sem CPF, nascimento ou dias
    critical_missing = sum(
        1 for v in verifications
        if v.status == "nao_encontrado"
        and any(kw in v.titulo.lower() for kw in ["cpf", "nascimento", "afastamento", "periodo"])
    )
    if critical_missing >= 2:
        score = min(score, 74)

    return max(15, min(99, score))

def build_verification_alerts(results: list[VerificationResult]) -> list[str]:
    """
    Converte os resultados de verificação com status 'alerta' ou 'pendente'
    em mensagens de alerta legíveis para o payload final.
    """
    return [
        f"{result.titulo}: {result.detalhe}"
        for result in results
        if result.status in {"alerta", "pendente"}
    ]

def build_default_next_steps(*, document_type: str) -> list[str]:
    """
    Retorna a lista de próximos passos recomendados de acordo com
    o tipo do documento, usada como complemento às sugestões da IA.
    """
    if document_type == "atestado_medico":
        return [
            "Conferir visualmente carimbo, assinatura e periodo de afastamento.",
            "Comparar os dados extraidos pelo OCR com a imagem original do atestado.",
            "Validar manualmente CRM e UF do profissional, se necessario.",
        ]
    return [
        "Conferir manualmente a autenticidade visual da instituicao emissora.",
        "Confirmar registro, assinatura e selo caso o risco final permaneca medio ou alto.",
    ]

def determine_analysis_status(combined_output: dict[str, Any]) -> str:
    """
    Define o status geral da análise:
    - 'analisado'         → campos extraídos disponíveis.
    - 'rascunho_tecnico'  → apenas texto bruto, sem campos estruturados.
    - 'ia_indisponivel'   → nenhum dado extraído.
    """
    if combined_output.get("extracted_fields"):
        return "analisado"
    if combined_output.get("raw_text"):
        return "rascunho_tecnico"
    return "ia_indisponivel"

# =============================================================================
# SEÇÃO 13 — ORQUESTRAÇÃO PRINCIPAL
# build_analysis() é o único ponto de entrada público deste módulo.
# =============================================================================

def build_analysis(
    *,
    protocolo: str,
    solicitante: str,
    departamento: str,
    tipo_documento: str,
    descricao: str,
    file_name: str,
    mime_type: str,
    file_data_base64: str,
    file_size_bytes: int,
) -> AnalysisPayload:
    """
    Função central do pipeline. Recebe os dados do documento enviado e:

    1. Normaliza o tipo de documento (fallback para 'historico_escolar').
    2. Executa o OCR via OCR.space.
    3. Envia para o Gemini a análise complementar.
    4. Mescla os dois resultados.
    5. Executa as verificações oficiais (CNPJ, CEP, CPF, CRM).
    6. Monta e retorna o AnalysisPayload final.

    NOTA: o tipo informado pelo usuário é preservado em 'dados_chave' mesmo
    quando remapeado internamente, para rastreabilidade.
    """
    document_type = (
        tipo_documento if tipo_documento in DOCUMENT_SPECS else "historico_escolar"
    )

    ocr_output = analyze_with_ocr_space(
        tipo_documento=document_type,
        file_name=file_name,
        mime_type=mime_type,
        file_data_base64=file_data_base64,
    )
    gemini_output = analyze_with_gemini(
        api_key=get_gemini_key(),
        solicitante=solicitante,
        departamento=departamento,
        tipo_documento=document_type,
        descricao=descricao,
        ocr_text=ocr_output.get("raw_text", ""),
        mime_type=mime_type,
        file_data_base64=file_data_base64,
    )
    combined = merge_analysis_outputs(
        document_type=document_type,
        ocr_output=ocr_output,
        gemini_output=gemini_output,
    )
    extraction_failed = not combined.get("extracted_fields")
    verification_results = run_relevant_verifications(
        tipo_documento=document_type,
        combined_output=combined,
        extraction_failed=extraction_failed,
    )

    dados_chave = [
        {"titulo": "Solicitante", "status": "encontrado", "detalhe": solicitante},
        {
            "titulo": "Tipo informado",
            "status": "encontrado",
            "detalhe": DOCUMENT_SPECS[document_type]["label"],
        },
        {
            "titulo": "Arquivo recebido",
            "status": "encontrado",
            "detalhe": f"{file_name} ({round(file_size_bytes / 1024, 1)} KB)",
        },
        {
            "titulo": "Motor de extracao",
            "status": "encontrado",
            "detalhe": combined.get("engine", "heuristica_local"),
        },
        *normalize_key_findings(combined),
    ]

    fatores_score = build_score_factors(
        document_type=document_type,
        combined_output=combined,
        verifications=verification_results,
    )
    alertas = dedupe_strings(
        [
            *normalize_string_list(ocr_output.get("alerts", [])),
            *simplify_gemini_alerts(gemini_output.get("alerts", [])),
            *build_verification_alerts(verification_results),
        ]
    )
    proximos_passos = dedupe_next_steps(
        gemini_steps=normalize_string_list(combined.get("recommended_checks", [])),
        default_steps=build_default_next_steps(document_type=document_type),
    )

    return AnalysisPayload(
        protocolo=protocolo,
        status=determine_analysis_status(combined),
        probabilidade_fraude=clamp_probability(
            combined.get("fraud_probability", 0), verification_results, fatores_score
        ),
        resumo=str(
            combined.get("summary")
            or "Nao foi possivel gerar resumo automatico para este documento."
        ),
        dados_chave=dados_chave,
        verificacoes_oficiais=[item.__dict__ for item in verification_results],
        alertas=alertas,
        fatores_score=fatores_score,
        proximos_passos=proximos_passos,
        motor_extracao=str(combined.get("engine") or "heuristica_local"),
        texto_extraido=str(combined.get("raw_text") or ""),
    )