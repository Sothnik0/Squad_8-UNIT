import json
import os
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


GEMINI_API_BASE = 'https://generativelanguage.googleapis.com/v1beta/models'
OCR_SPACE_URL = 'https://api.ocr.space/parse/image'
CNPJA_URL = 'https://open.cnpja.com/office'
VIACEP_URL = 'https://viacep.com.br/ws'
DEFAULT_GEMINI_MODEL = os.getenv('AI_MODEL', os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-lite'))


DOCUMENT_SPECS = {
    'atestado_medico': {
        'label': 'Atestado medico',
    },
    'certificado_ensino_medio': {
        'label': 'Certificado de conclusao do ensino medio',
    },
    'historico_escolar': {
        'label': 'Historico escolar',
    },
    'diploma': {
        'label': 'Diploma de graduacao/ensino superior',
    },
}


@dataclass
class VerificationResult:
    titulo: str
    status: str
    detalhe: str


@dataclass
class AnalysisPayload:
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
    document_type = tipo_documento if tipo_documento in DOCUMENT_SPECS else 'historico_escolar'

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
        ocr_text=ocr_output.get('raw_text', ''),
        mime_type=mime_type,
        file_data_base64=file_data_base64,
    )
    combined = merge_analysis_outputs(document_type=document_type, ocr_output=ocr_output, gemini_output=gemini_output)
    extraction_failed = not combined.get('extracted_fields')
    verification_results = run_relevant_verifications(
        tipo_documento=document_type,
        combined_output=combined,
        extraction_failed=extraction_failed,
    )

    dados_chave = [
        {'titulo': 'Solicitante', 'status': 'encontrado', 'detalhe': solicitante},
        {'titulo': 'Tipo informado', 'status': 'encontrado', 'detalhe': DOCUMENT_SPECS[document_type]['label']},
        {
            'titulo': 'Arquivo recebido',
            'status': 'encontrado',
            'detalhe': f'{file_name} ({round(file_size_bytes / 1024, 1)} KB)',
        },
        {'titulo': 'Motor de extracao', 'status': 'encontrado', 'detalhe': combined.get('engine', 'heuristica_local')},
        *normalize_key_findings(combined),
    ]

    fatores_score = build_score_factors(document_type=document_type, combined_output=combined, verifications=verification_results)
    alertas = dedupe_strings([
        *normalize_string_list(ocr_output.get('alerts', [])),
        *simplify_gemini_alerts(gemini_output.get('alerts', [])),
        *build_verification_alerts(verification_results),
    ])
    proximos_passos = list(dict.fromkeys([
        *normalize_string_list(combined.get('recommended_checks', [])),
        *build_default_next_steps(document_type=document_type),
    ]))

    return AnalysisPayload(
        protocolo=protocolo,
        status=determine_analysis_status(combined),
        probabilidade_fraude=clamp_probability(combined.get('fraud_probability', 0), verification_results, fatores_score),
        resumo=str(combined.get('summary') or 'Nao foi possivel gerar resumo automatico para este documento.'),
        dados_chave=dados_chave,
        verificacoes_oficiais=[item.__dict__ for item in verification_results],
        alertas=alertas,
        fatores_score=fatores_score,
        proximos_passos=proximos_passos,
        motor_extracao=str(combined.get('engine') or 'heuristica_local'),
        texto_extraido=str(combined.get('raw_text') or ''),
    )


def get_gemini_key() -> str:
    return (
        os.getenv('GEMINI_API_KEY', '').strip()
        or os.getenv('GOOGLE_API_KEY', '').strip()
        or os.getenv('OPENAI_API_KEY', '').strip()
    )


def get_ocr_key() -> str:
    return os.getenv('OCR_API_KEY', '').strip()


def analyze_with_ocr_space(*, tipo_documento: str, file_name: str, mime_type: str, file_data_base64: str) -> dict[str, Any]:
    api_key = get_ocr_key()
    if not api_key:
        return {
            'summary': 'OCR nao configurado no backend.',
            'raw_text': '',
            'engine': 'ocr_nao_configurado',
            'alerts': ['OCR_API_KEY nao configurada no backend.'],
            'extracted_fields': [],
            'reference_data': {},
            'recommended_checks': ['Configurar OCR_API_KEY para extracao automatica.'],
            'fraud_probability': 25,
            'score_factors': ['Nao houve OCR automatico disponivel para ler o documento.'],
        }

    payload = urllib.parse.urlencode({
        'apikey': api_key,
        'base64Image': f'data:{mime_type};base64,{file_data_base64}',
        'language': 'por',
        'OCREngine': '2',
        'filetype': file_name.split('.')[-1],
        'isOverlayRequired': 'false',
        'scale': 'true',
    }).encode('utf-8')
    request = urllib.request.Request(OCR_SPACE_URL, data=payload, method='POST')
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            parsed = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        return {
            'summary': 'O OCR falhou durante a leitura do documento.',
            'raw_text': '',
            'engine': 'ocr_space',
            'alerts': [read_http_error(exc) or f'Falha HTTP {exc.code} ao consultar OCR.space.'],
            'extracted_fields': [],
            'reference_data': {},
            'recommended_checks': ['Reexecutar a leitura OCR ou validar manualmente o documento.'],
            'fraud_probability': 30,
            'score_factors': ['A leitura OCR nao conseguiu extrair o conteudo do documento.'],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            'summary': 'O OCR falhou antes de concluir a leitura do documento.',
            'raw_text': '',
            'engine': 'ocr_space',
            'alerts': [f'Erro na integracao com OCR.space: {exc}'],
            'extracted_fields': [],
            'reference_data': {},
            'recommended_checks': ['Validar manualmente o documento.'],
            'fraud_probability': 30,
            'score_factors': ['A leitura OCR nao conseguiu extrair o conteudo do documento.'],
        }

    text_parts = []
    for item in parsed.get('ParsedResults', []) or []:
        text = clean_text(item.get('ParsedText', ''))
        if text:
            text_parts.append(text)

    raw_text = '\n'.join(text_parts).strip()
    if not raw_text:
        return {
            'summary': 'OCR executado, mas sem texto legivel suficiente.',
            'raw_text': '',
            'engine': 'ocr_space',
            'alerts': normalize_string_list(parsed.get('ErrorMessage')) or ['OCR sem texto extraido.'],
            'extracted_fields': [],
            'reference_data': {},
            'recommended_checks': ['Conferir nitidez da imagem e reenviar o documento.'],
            'fraud_probability': 35,
            'score_factors': ['O OCR nao encontrou texto suficiente para sustentar a analise.'],
        }

    if tipo_documento == 'atestado_medico':
        return parse_medical_certificate_ocr(raw_text)
    if tipo_documento in {'certificado_ensino_medio', 'historico_escolar'}:
        return parse_school_document_ocr(tipo_documento, raw_text)
    if tipo_documento == 'diploma':
        return parse_diploma_ocr(raw_text)
        
    return {
        'summary': 'OCR executado com sucesso.',
        'raw_text': raw_text,
        'engine': 'ocr_space',
        'alerts': [],
        'extracted_fields': [],
        'reference_data': {},
        'recommended_checks': [],
        'fraud_probability': 25,
        'score_factors': ['A leitura OCR foi concluida e aguarda interpretacao complementar.'],
    }

def parse_medical_certificate_ocr(raw_text: str) -> dict[str, Any]:
    normalized_text = raw_text.replace('Paclente', 'Paciente').replace('paclente', 'paciente')
    patient_name = match_group(normalized_text, 'Paciente[:;\\s]+([A-ZÀ-Ú ]{6,})') or match_group(normalized_text, 'o paciente[:;\\s]+([A-ZÀ-Ú ]{6,})')
    cpf = format_cpf(match_group(normalized_text, 'CPF[:\\s]+([0-9.\\-]{11,14})'))
    provider_name = match_group(normalized_text, 'Prestador[:\\s]+([A-ZÀ-Ú ]{6,})')
    crm_number = only_digits(match_group(normalized_text, 'CRM[:\\s]*(?:SE\\s*)?([0-9]{3,8})'))
    leave_days = match_group(normalized_text, 'periodo de[:\\s]*([0-9]{1,2})') or match_group(normalized_text, 'por um periodo de[:\\s]*([0-9]{1,2})')
    issue_date = match_group(normalized_text, '(\\d{2}/\\d{2}/\\d{4})')
    cid = match_group(normalized_text, '\\b([A-Z][0-9]{2,4})\\b')
    institution_name = match_group(normalized_text, 'Empresa[:\\s]+([^\\n]+)') or match_group(normalized_text, '(UNIMED[^\\n]+)')
    cep = only_digits(match_group(normalized_text, 'CEP[:\\s]*([0-9\\-]{8,9})'))
    lowered_text = normalized_text.lower()
    doctor_signed = 'assinatura do m' in lowered_text or 'crm/se' in lowered_text

    extracted_fields = [
        build_field('Nome do paciente', patient_name),
        build_field('CPF do paciente', cpf),
        build_field('Instituicao emissora', institution_name),
        build_field('Nome do medico', provider_name),
        build_field('CRM', crm_number),
        build_field('Data identificada', issue_date),
        build_field('Periodo de afastamento (dias)', leave_days),
        build_field('CID identificado', cid),
        build_field('Assinatura ou referencia ao medico', 'Presente' if doctor_signed else ''),
    ]

    found_count = sum(1 for item in extracted_fields if item['status'] == 'encontrado')
    summary = 'OCR executado com sucesso no atestado medico.' if found_count else 'OCR executado, mas sem dados confiaveis suficientes no atestado medico.'
    score_factors = []
    if not crm_number:
        score_factors.append('O OCR nao localizou um CRM utilizavel no atestado.')
    if not provider_name:
        score_factors.append('O nome do medico nao apareceu com clareza suficiente no OCR.')
    if not issue_date:
        score_factors.append('A data principal do documento nao foi identificada com seguranca.')
    if not doctor_signed:
        score_factors.append('O OCR nao encontrou indicios textuais claros de assinatura ou identificacao do medico.')
    if found_count >= 6:
        score_factors.append('O OCR conseguiu recuperar boa parte dos campos esperados do atestado.')

    return {
        'summary': summary,
        'raw_text': raw_text,
        'engine': 'ocr_space',
        'alerts': [],
        'extracted_fields': extracted_fields,
        'reference_data': {
            'institution_name': institution_name,
            'cnpj': '',
            'cep': cep,
            'crm_number': crm_number,
            'crm_state': 'SE' if 'crm/se' in lowered_text or 'sergipe' in lowered_text else '',
        },
        'recommended_checks': [
            'Comparar os campos extraidos pelo OCR com a imagem original do atestado.',
            'Conferir manualmente carimbo, assinatura, periodo de afastamento e nome do paciente.',
        ],
        'fraud_probability': 18 if found_count >= 6 else 38,
        'score_factors': score_factors,
    }


def parse_school_document_ocr(tipo_documento: str, raw_text: str) -> dict[str, Any]:
    institution_name = match_group(raw_text, r'(ESCOLA[^\n]+|COLEGIO[^\n]+|INSTITUTO[^\n]+|SECRETARIA[^\n]+)')
    student_name = match_group(raw_text, r'(?:Aluno|Aluna|Estudante)[:\s]+([^\n]+)')
    cnpj = format_cnpj(match_group(raw_text, r'([0-9]{2}\.?[0-9]{3}\.?[0-9]{3}/?[0-9]{4}-?[0-9]{2})'))
    cep = only_digits(match_group(raw_text, 'CEP[:\\s]*([0-9\\-]{8,9})'))
    issue_date = match_group(raw_text, '(\\d{2}/\\d{2}/\\d{4})')

    extracted_fields = [
        build_field('Nome da instituicao', institution_name),
        build_field('Nome do aluno', student_name),
        build_field('CNPJ da instituicao', cnpj),
        build_field('CEP da instituicao', cep),
        build_field('Data identificada', issue_date),
    ]

    label = DOCUMENT_SPECS[tipo_documento]['label']
    return {
        'summary': f'OCR executado com sucesso em {label.lower()}.',
        'raw_text': raw_text,
        'engine': 'ocr_space',
        'alerts': [],
        'extracted_fields': extracted_fields,
        'reference_data': {
            'institution_name': institution_name,
            'cnpj': cnpj,
            'cep': cep,
            'crm_number': '',
            'crm_state': '',
        },
        'recommended_checks': [
            'Comparar os campos extraidos com a imagem do documento escolar.',
            'Conferir autenticidade visual da instituicao, assinaturas e registro.',
        ],
        'fraud_probability': 22 if institution_name else 42,
        'score_factors': ['A confirmacao da instituicao emissora pesa mais neste tipo de documento.'],
    }


def parse_diploma_ocr(raw_text: str) -> dict[str, Any]:
    institution_name = match_group(raw_text, r'(UNIVERSIDADE[^\n]+|FACULDADE[^\n]+|INSTITUTO SUPERIOR[^\n]+|CENTRO UNIVERSITÁRIO[^\n]+)')
    graduate_name = match_group(raw_text, r'(?:conferiu o grau de|diplomado|conferido a|nome do aluno|graduado)[:\s]*([A-ZÀ-Ú ]{6,})')
    course_name = match_group(raw_text, r'(?:no curso de|bacharel em|licenciado em|tecnólogo em)[:\s]*([^\n,.]*)')
    
    cnpj = format_cnpj(match_group(raw_text, r'([0-9]{2}\.?[0-9]{3}\.?[0-9]{3}/?[0-9]{4}-?[0-9]{2})'))
    cep = only_digits(match_group(raw_text, 'CEP[:\\s]*([0-9\\-]{8,9})'))
    issue_date = match_group(raw_text, '(\\d{2}/\\d{2}/\\d{4})')
    registration_code = match_group(raw_text, r'(?:registro|sob o nº|livro[:\s]*[A-Z0-9\-]+)')

    extracted_fields = [
        build_field('Nome da instituicao emissora', institution_name),
        build_field('Nome do diplomado', graduate_name),
        build_field('Curso', course_name),
        build_field('CNPJ da instituicao', cnpj),
        build_field('CEP da instituicao', cep),
        build_field('Data de emissao/colacao', issue_date),
        build_field('Dados de registro/livro', registration_code),
    ]

    found_count = sum(1 for item in extracted_fields if item['status'] == 'encontrado')
    summary = 'OCR executado com sucesso no diploma.' if found_count >= 4 else 'OCR executado, mas poucos dados estruturados foram identificados no diploma.'
    
    score_factors = []
    if not institution_name:
        score_factors.append('O OCR nao identificou o nome da instituicao de ensino superior.')
    if not graduate_name:
        score_factors.append('Nao foi possivel isolar o nome do diplomado de forma automatica pelo OCR.')
    if not registration_code:
        score_factors.append('Indicios de registro interno (livro/folha) nao foram detectados no texto plano.')

    return {
        'summary': summary,
        'raw_text': raw_text,
        'engine': 'ocr_space',
        'alerts': [],
        'extracted_fields': extracted_fields,
        'reference_data': {
            'institution_name': institution_name,
            'cnpj': cnpj,
            'cep': cep,
            'crm_number': '',
            'crm_state': '',
        },
        'recommended_checks': [
            'Verificar se o curso e a instituicao estao devidamente reconhecidos no portal e-MEC.',
            'Conferir as assinaturas do reitor e secretario academico no verso do documento.',
        ],
        'fraud_probability': 20 if found_count >= 4 else 40,
        'score_factors': score_factors,
    }


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
    if not api_key or (not ocr_text and not file_data_base64):
        return {'alerts': [], 'score_factors': [], 'recommended_checks': [], 'extracted_fields': [], 'reference_data': {}}

    prompt = build_gemini_prompt(
        solicitante=solicitante,
        departamento=departamento,
        tipo_documento=tipo_documento,
        descricao=descricao,
        ocr_text=ocr_text,
    )
    parts = [{'text': prompt}]
    if file_data_base64:
        parts.append({'inline_data': {'mime_type': mime_type, 'data': file_data_base64}})
    payload = {
        'contents': [{'parts': parts}],
        'generationConfig': {'responseMimeType': 'application/json', 'temperature': 0.2},
    }
    url = f"{GEMINI_API_BASE}/{urllib.parse.quote(DEFAULT_GEMINI_MODEL)}:generateContent?key={urllib.parse.quote(api_key)}"

    try:
        raw_response = post_json(url=url, payload=payload, headers={}, timeout=90)
    except urllib.error.HTTPError as exc:
        return {
            'alerts': [read_http_error(exc) or f'Falha HTTP {exc.code} ao consultar o Gemini.'],
            'score_factors': ['A etapa de interpretacao com Gemini nao conseguiu concluir a leitura do OCR.'],
            'recommended_checks': ['Usar o relatorio baseado em OCR e seguir com conferencia manual enquanto a IA complementar estiver indisponivel.'],
            'extracted_fields': [],
            'reference_data': {},
        }
    except Exception as exc:  # noqa: BLE001
        return {
            'alerts': [f'Erro na integracao com Gemini: {exc}'],
            'score_factors': ['A etapa de interpretacao com Gemini falhou e o sistema seguiu com OCR puro.'],
            'recommended_checks': ['Validar manualmente os campos extraidos pelo OCR.'],
            'extracted_fields': [],
            'reference_data': {},
        }

    output_text = extract_gemini_text(raw_response)
    try:
        parsed = json.loads(output_text)
    except json.JSONDecodeError:
        return {
            'alerts': ['A resposta do Gemini nao veio em JSON valido.'],
            'score_factors': ['O Gemini respondeu fora do formato esperado; mantendo resultado baseado no OCR.'],
            'recommended_checks': ['Seguir com a conferencia manual do OCR.'],
            'extracted_fields': [],
            'reference_data': {},
        }

    parsed.setdefault('alerts', [])
    parsed.setdefault('score_factors', [])
    parsed.setdefault('recommended_checks', [])
    parsed.setdefault('extracted_fields', [])
    parsed.setdefault('reference_data', {})
    return parsed


def merge_analysis_outputs(*, document_type: str, ocr_output: dict[str, Any], gemini_output: dict[str, Any]) -> dict[str, Any]:
    merged = dict(ocr_output)
    combined_fields: dict[str, dict[str, Any]] = {}
    ordered_keys: list[str] = []

    for field in ocr_output.get('extracted_fields', []):
        label_key = normalize_label_key(field.get('label'))
        if not label_key:
            continue
        combined_fields[label_key] = dict(field)
        ordered_keys.append(label_key)

    for field in gemini_output.get('extracted_fields', []):
        label_key = normalize_label_key(field.get('label'))
        if not label_key:
            continue
        if label_key in combined_fields:
            combined_fields[label_key] = merge_extracted_field(combined_fields[label_key], field)
            continue
        combined_fields[label_key] = dict(field)
        ordered_keys.append(label_key)

    merged['extracted_fields'] = [combined_fields[key] for key in ordered_keys]
    merged['reference_data'] = {**(ocr_output.get('reference_data', {}) or {}), **(gemini_output.get('reference_data', {}) or {})}
    merged['alerts'] = normalize_string_list(ocr_output.get('alerts', [])) + normalize_string_list(gemini_output.get('alerts', []))
    merged['score_factors'] = normalize_string_list(ocr_output.get('score_factors', [])) + normalize_string_list(gemini_output.get('score_factors', []))
    merged['recommended_checks'] = normalize_string_list(ocr_output.get('recommended_checks', [])) + normalize_string_list(gemini_output.get('recommended_checks', []))
    merged['summary'] = build_summary(document_type=document_type, ocr_output=ocr_output, gemini_output=gemini_output)
    merged['fraud_probability'] = gemini_output.get('fraud_probability') or ocr_output.get('fraud_probability') or 0
    merged['engine'] = 'ocr_space + gemini' if gemini_output.get('extracted_fields') else ocr_output.get('engine', 'ocr_space')
    merged['raw_text'] = ocr_output.get('raw_text', '')
    return merged

def build_summary(*, document_type: str, ocr_output: dict[str, Any], gemini_output: dict[str, Any]) -> str:
    if gemini_output.get('extracted_fields'):
        return 'OCR executado e interpretado com apoio do Gemini.'
    if ocr_output.get('raw_text'):
        return f"OCR executado com sucesso para {DOCUMENT_SPECS[document_type]['label'].lower()}. A IA complementar nao concluiu, mas os dados extraidos ja estao visiveis abaixo."
    return 'A analise automatica nao conseguiu extrair dados confiaveis do documento.'


def build_gemini_prompt(*, solicitante: str, departamento: str, tipo_documento: str, descricao: str, ocr_text: str) -> str:
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
    "crm_state": "",
    "course_name": "",      
    "registration_code": ""
  }},
  "extracted_fields": [
    {{"label": "Campo", "value": "Valor", "status": "encontrado|nao_encontrado|pendente|alerta", "confidence": 0.0}}
  ]]
}}
""".strip()


def determine_analysis_status(combined_output: dict[str, Any]) -> str:
    if combined_output.get('extracted_fields'):
        return 'analisado'
    if combined_output.get('raw_text'):
        return 'rascunho_tecnico'
    return 'ia_indisponivel'


def run_relevant_verifications(*, tipo_documento: str, combined_output: dict[str, Any], extraction_failed: bool) -> list[VerificationResult]:
    reference_data = combined_output.get('reference_data', {}) or {}
    institution_name = clean_text(reference_data.get('institution_name', ''))
    cnpj = only_digits(reference_data.get('cnpj', ''))
    cep = only_digits(reference_data.get('cep', ''))
    crm_number = only_digits(reference_data.get('crm_number', ''))
    crm_state = clean_text(reference_data.get('crm_state', '')).upper()

    results: list[VerificationResult] = []
    
    if tipo_documento in {'certificado_ensino_medio', 'historico_escolar', 'diploma'}:
        results.append(verify_institution_name(institution_name=institution_name, extraction_failed=extraction_failed))
        results.append(verify_cnpj_free(cnpj=cnpj, institution_name=institution_name, extraction_failed=extraction_failed))
        results.append(verify_cep_free(cep=cep, extraction_failed=extraction_failed))
    if tipo_documento == 'atestado_medico':
        results.append(verify_crm_presence(crm_number=crm_number, crm_state=crm_state, extraction_failed=extraction_failed))
    return results


def verify_institution_name(*, institution_name: str, extraction_failed: bool) -> VerificationResult:
    if institution_name:
        return VerificationResult('Escola/Instituicao identificada', 'encontrado', f'Instituicao extraida: {institution_name}.')
    if extraction_failed:
        return VerificationResult('Escola/Instituicao identificada', 'pendente', 'A identificacao da instituicao ficou pendente.')
    return VerificationResult('Escola/Instituicao identificada', 'nao_encontrado', 'O nome da instituicao nao foi localizado no documento.')


def verify_cnpj_free(*, cnpj: str, institution_name: str, extraction_failed: bool) -> VerificationResult:
    title = 'Consulta CNPJ da escola/instituicao'
    if not cnpj:
        if extraction_failed:
            return VerificationResult(title, 'pendente', 'A verificacao do CNPJ ficou pendente.')
        if institution_name:
            return VerificationResult(title, 'pendente', 'A instituicao foi identificada, mas o CNPJ nao apareceu no documento.')
        return VerificationResult(title, 'nao_encontrado', 'Nenhum CNPJ da instituicao foi encontrado no documento.')
    if not is_valid_cnpj(cnpj):
        return VerificationResult(title, 'alerta', 'O CNPJ extraido possui digitos verificadores invalidos.')
    try:
        data = get_json(url=f'{CNPJA_URL}/{cnpj}', query=None, timeout=30)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return VerificationResult(title, 'nao_encontrado', 'O CNPJ extraido nao foi localizado na base publica consultada.')
        return VerificationResult(title, 'alerta', read_http_error(exc) or f'Falha HTTP {exc.code} na consulta de CNPJ.')
    except Exception as exc:  # noqa: BLE001
        return VerificationResult(title, 'pendente', f'Nao foi possivel concluir a consulta publica do CNPJ: {exc}')

    official_name = clean_text(data.get('company', {}).get('name') or data.get('alias') or data.get('name') or '')
    if institution_name and official_name and institution_name.lower() not in official_name.lower() and official_name.lower() not in institution_name.lower():
        return VerificationResult(title, 'alerta', f'CNPJ localizado, mas o nome retornado ({official_name}) diverge do nome extraido ({institution_name}).')
    return VerificationResult(title, 'encontrado', f"CNPJ localizado na base publica. Nome oficial: {official_name or 'nao informado'}.")


def verify_cep_free(*, cep: str, extraction_failed: bool) -> VerificationResult:
    title = 'Consulta CEP'
    if not cep:
        if extraction_failed:
            return VerificationResult(title, 'pendente', 'A verificacao do CEP ficou pendente.')
        return VerificationResult(title, 'nao_encontrado', 'Nenhum CEP foi identificado no documento.')
    if not is_valid_cep(cep):
        return VerificationResult(title, 'alerta', 'O CEP extraido nao possui 8 digitos validos.')
    try:
        data = get_json(url=f'{VIACEP_URL}/{cep}/json/', query=None, timeout=30)
    except urllib.error.HTTPError as exc:
        return VerificationResult(title, 'alerta', read_http_error(exc) or f'Falha HTTP {exc.code} na consulta de CEP.')
    except Exception as exc:  # noqa: BLE001
        return VerificationResult(title, 'pendente', f'Nao foi possivel concluir a consulta do CEP: {exc}')
    if data.get('erro') is True:
        return VerificationResult(title, 'nao_encontrado', 'O CEP extraido nao foi localizado no ViaCEP.')
    return VerificationResult(title, 'encontrado', f"CEP localizado: {data.get('logradouro', 'logradouro nao informado')}, {data.get('bairro', 'bairro nao informado')} - {data.get('localidade', '')}/{data.get('uf', '')}.")


def verify_crm_presence(*, crm_number: str, crm_state: str, extraction_failed: bool) -> VerificationResult:
    title = 'Identificacao do CRM'
    if not crm_number:
        if extraction_failed:
            return VerificationResult(title, 'pendente', 'O OCR/IA nao conseguiu localizar um CRM utilizavel com seguranca.')
        return VerificationResult(title, 'nao_encontrado', 'Nenhum numero de CRM foi localizado no atestado.')
    if not crm_state:
        return VerificationResult(title, 'pendente', f'CRM {crm_number} identificado, mas a UF do registro nao foi identificada.')
    return VerificationResult(title, 'pendente', f'CRM {crm_number}/{crm_state} identificado. Validacao externa ficou pendente de conferencia manual.')


def build_score_factors(*, document_type: str, combined_output: dict[str, Any], verifications: list[VerificationResult]) -> list[str]:
    factors = normalize_string_list(combined_output.get('score_factors', []))
    for verification in verifications:
        if verification.status in {'alerta', 'nao_encontrado', 'pendente'}:
            factors.append(f'{verification.titulo}: {verification.detalhe}')
    if document_type == 'atestado_medico' and not any(item.titulo == 'Identificacao do CRM' and item.status != 'nao_encontrado' for item in verifications):
        factors.append('O atestado nao apresentou CRM utilizavel para verificacao.')
    return dedupe_strings(factors)


def build_default_next_steps(*, document_type: str) -> list[str]:
    if document_type == 'atestado_medico':
        return [
            'Conferir visualmente carimbo, assinatura e periodo de afastamento.',
            'Comparar os dados extraidos pelo OCR com a imagem original do atestado.',
            'Validar manualmente CRM e UF do profissional, se necessario.',
        ]
    if document_type == 'diploma':
        return [
            'Verificar a regularidade do curso e da faculdade no portal oficial e-MEC.',
            'Conferir carimbos de registro, folhas de livro no verso e assinaturas da reitoria.',
            'Garantir equivalencia cadastral se o diploma for de instituicao internacional revalidada.',
        ]
    return [
        'Conferir manualmente a autenticidade visual da instituicao emissora.',
        'Confirmar registro, assinatura e selo caso o risco final permaneca medio ou alto.',
    ]

def normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(normalize_string_list(item))
        return result
    if isinstance(value, dict):
        message = clean_text(value.get('message') or value.get('error') or '')
        return [message] if message else []
    cleaned = clean_text(value)
    return [cleaned] if cleaned else []


def normalize_key_findings(combined_output: dict[str, Any]) -> list[dict[str, str]]:
    findings = []
    seen_labels = set()
    for field in combined_output.get('extracted_fields', []):
        label = clean_text(field.get('label', ''))
        label_key = normalize_label_key(label)
        if not label or not label_key or label_key in seen_labels:
            continue
        seen_labels.add(label_key)
        findings.append({'titulo': label, 'status': normalize_status(field.get('status')), 'detalhe': stringify_field_detail(field)})
    return findings


def stringify_field_detail(field: dict[str, Any]) -> str:
    value = clean_text(field.get('value', ''))
    confidence = field.get('confidence')
    source = clean_text(field.get('source', ''))
    detail = value or 'Campo nao identificado no documento.'
    if confidence is not None:
        try:
            detail = f'{detail} (confianca {round(float(confidence) * 100)}%)'
        except (TypeError, ValueError):
            pass
    if source:
        detail = f'{detail} - origem: {source}'
    return detail


def normalize_status(status: Any) -> str:
    normalized = clean_text(status).lower()
    return normalized if normalized in {'encontrado', 'nao_encontrado', 'pendente', 'alerta'} else 'pendente'


def clamp_probability(raw_value: Any, verifications: list[VerificationResult], factors: list[str]) -> int:
    try:
        probability = int(float(raw_value))
    except (TypeError, ValueError):
        probability = 0
    if any(item.status == 'alerta' for item in verifications):
        probability = max(probability, 60)
    if any(item.status == 'nao_encontrado' for item in verifications):
        probability = max(probability, 45)
    if len(factors) >= 4:
        probability = max(probability, 35)
    return max(0, min(99, probability))


def build_verification_alerts(results: list[VerificationResult]) -> list[str]:
    return [f'{result.titulo}: {result.detalhe}' for result in results if result.status in {'alerta', 'pendente'}]


def post_json(*, url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int) -> dict[str, Any]:
    body = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json', **headers}, method='POST')
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def get_json(*, url: str, query: dict[str, str] | None, timeout: int) -> dict[str, Any]:
    final_url = f"{url}?{urllib.parse.urlencode(query)}" if query else url
    request = urllib.request.Request(final_url, method='GET')
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def extract_gemini_text(response_payload: dict[str, Any]) -> str:
    candidates = response_payload.get('candidates', [])
    if not candidates:
        return ''
    parts = candidates[0].get('content', {}).get('parts', [])
    return '\n'.join(part.get('text', '') for part in parts if part.get('text')).strip()


def read_http_error(error: urllib.error.HTTPError) -> str:
    try:
        body = error.read().decode('utf-8')
        if not body:
            return ''
        payload = json.loads(body)
        if isinstance(payload, dict) and 'error' in payload and isinstance(payload['error'], dict):
            payload = payload['error']
        if isinstance(payload, dict):
            return clean_text(payload.get('message') or payload.get('status') or payload.get('error') or body)
        return clean_text(body)
    except Exception:  # noqa: BLE001
        return ''


def build_field(label: str, value: str, confidence: float = 0.82, source: str = 'ocr_space') -> dict[str, Any]:
    cleaned = clean_text(value)
    return {
        'label': label,
        'value': cleaned,
        'status': 'encontrado' if cleaned else 'nao_encontrado',
        'confidence': confidence if cleaned else 0.0,
        'source': source,
    }


def match_group(text: str, pattern: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return clean_text(match.group(1)) if match else ''


def only_digits(value: Any) -> str:
    return ''.join(char for char in str(value or '') if char.isdigit())


def clean_text(value: Any) -> str:
    return str(value or '').strip()


def normalize_label_key(value: Any) -> str:
    cleaned = clean_text(value)
    if not cleaned:
        return ''
    normalized = unicodedata.normalize('NFKD', cleaned)
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r'[^a-z0-9]+', ' ', without_accents.lower()).strip()


def merge_extracted_field(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    existing_status = normalize_status(existing.get('status'))
    incoming_status = normalize_status(incoming.get('status'))
    existing_confidence = normalize_confidence(existing.get('confidence'))
    incoming_confidence = normalize_confidence(incoming.get('confidence'))

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

    merged['label'] = preferred_label(existing.get('label'), incoming.get('label'))
    merged['source'] = merge_sources(existing.get('source'), incoming.get('source'))
    merged['status'] = normalize_status(merged.get('status'))
    merged['confidence'] = max(existing_confidence, incoming_confidence)
    return merged


def should_replace_field(*, existing_status: str, incoming_status: str, existing_confidence: float, incoming_confidence: float) -> bool:
    status_priority = {
        'encontrado': 3,
        'alerta': 2,
        'pendente': 1,
        'nao_encontrado': 0,
    }
    incoming_priority = status_priority.get(incoming_status, -1)
    existing_priority = status_priority.get(existing_status, -1)
    if incoming_priority != existing_priority:
        return incoming_priority > existing_priority
    return incoming_confidence >= existing_confidence


def normalize_confidence(value: Any) -> float:
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return 0.0


def preferred_label(existing: Any, incoming: Any) -> str:
    existing_label = clean_text(existing)
    incoming_label = clean_text(incoming)
    if incoming_label and len(incoming_label) >= len(existing_label):
        return incoming_label
    return existing_label or incoming_label


def merge_sources(existing: Any, incoming: Any) -> str:
    existing_source = clean_text(existing)
    incoming_source = clean_text(incoming)
    if existing_source and incoming_source and existing_source != incoming_source:
        return f'{existing_source} + {incoming_source}'
    return incoming_source or existing_source


def format_cpf(value: str) -> str:
    digits = only_digits(value)
    if len(digits) != 11:
        return clean_text(value)
    return f'{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}'


def format_cnpj(value: str) -> str:
    digits = only_digits(value)
    if len(digits) != 14:
        return clean_text(value)
    return f'{digits[0:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}'


def simplify_gemini_alerts(value: Any) -> list[str]:
    alerts = normalize_string_list(value)
    simplified = []
    for alert in alerts:
        lowered = alert.lower()
        if 'quota exceeded' in lowered or 'free_tier' in lowered or 'rate limit' in lowered:
            simplified.append('A camada complementar de IA nao estava disponivel; o relatorio foi gerado com OCR e regras locais.')
        else:
            simplified.append(alert)
    return dedupe_strings(simplified)

def dedupe_strings(values: list[str]):
    result = []
    seen = set()
    for value in values:
        cleaned = clean_text(value)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


def is_valid_cep(cep: str) -> bool:
    return len(cep) == 8 and cep.isdigit()


def is_valid_cnpj(cnpj: str) -> bool:
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