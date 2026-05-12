"""
testar_api.py
=============
Testes reais do pipeline — adaptado ao endpoint /analises/documento.

COMO USAR:
    1. Backend rodando:
       cd backend && uvicorn app.main:app --reload

    2. Coloque documentos reais em  tests/docs/
       (nomes devem conter: atestado / historico / certificado)
       Extensões aceitas: .pdf, .jpg, .jpeg, .png

    3. Se a pasta estiver vazia, o script gera imagens PNG mínimas
       válidas automaticamente para você ver o pipeline funcionando.

    4. Execute (dentro da pasta backend/):
       python app/testar_api.py

    5. Resultados salvos em tests/resultados/
"""

import base64
import json
import os
import sys
import struct
import urllib.error
import urllib.request
import zlib
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ENDPOINT  = f"{BASE_URL}/analises/documento"

DOCS_DIR    = Path("tests/docs")
RESULTS_DIR = Path("tests/resultados")

MIME_MAP: dict[str, str] = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".pdf":  "application/pdf",
}

DOCUMENT_MAP: dict[str, str] = {
    "atestado":    "atestado_medico",
    "historico":   "historico_escolar",
    "certificado": "certificado_ensino_medio",
}

SEP = "=" * 70


# ---------------------------------------------------------------------------
# Gerador de PNG mínimo válido (sem dependências externas)
# Cria um PNG 1x1 pixel branco com texto embarcado no chunk tEXt
# ---------------------------------------------------------------------------

def _make_png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    length = struct.pack(">I", len(data))
    crc    = struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    return length + chunk_type + data + crc


def generate_test_png(label: str) -> bytes:
    """
    Gera um PNG 1x1 pixel branco com um chunk de texto descritivo.
    É um arquivo PNG 100% válido — não é mock, é um arquivo real mínimo.
    """
    signature = b"\x89PNG\r\n\x1a\n"

    # IHDR: largura=1, altura=1, bit_depth=8, color_type=2 (RGB)
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    ihdr = _make_png_chunk(b"IHDR", ihdr_data)

    # IDAT: um pixel branco RGB (255,255,255) com filtro 0
    raw_row  = b"\x00\xff\xff\xff"
    compressed = zlib.compress(raw_row)
    idat = _make_png_chunk(b"IDAT", compressed)

    # tEXt: metadado com o label do documento
    text_data = b"Comment\x00" + label.encode("latin-1", errors="replace")
    text_chunk = _make_png_chunk(b"tEXt", text_data)

    # IEND
    iend = _make_png_chunk(b"IEND", b"")

    return signature + ihdr + idat + text_chunk + iend


def already_analyzed(doc_path: Path) -> bool:
    """
    Retorna True se já existe um resultado JSON salvo para este documento
    em tests/resultados/, evitando reanálise desnecessária.
    """
    if not RESULTS_DIR.exists():
        return False
    stem = doc_path.stem
    existing = list(RESULTS_DIR.glob(f"{stem}_*.json"))
    return len(existing) > 0


def ensure_test_docs() -> None:
    """
    Se a pasta tests/docs/ estiver vazia ou sem arquivos válidos,
    gera um PNG mínimo real para cada tipo de documento.
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    valid = [
        p for p in DOCS_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in MIME_MAP and p.stat().st_size > 0
    ]
    if valid:
        return

    print("\n⚠️  Nenhum documento real encontrado em tests/docs/")
    print("   Gerando imagens PNG mínimas válidas para teste do pipeline...\n")

    samples = {
        "atestado_teste.png":    "Atestado Medico - Documento de Teste",
        "historico_teste.png":   "Historico Escolar - Documento de Teste",
        "certificado_teste.png": "Certificado Ensino Medio - Documento de Teste",
    }
    for filename, label in samples.items():
        path = DOCS_DIR / filename
        path.write_bytes(generate_test_png(label))
        print(f"   ✅ Gerado: {filename} ({path.stat().st_size} bytes)")

    print(
        "\n   💡 Para testes reais, substitua esses arquivos pelos documentos verdadeiros.\n"
    )


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def resolve_doc_type(filename: str) -> str:
    lower = filename.lower()
    for keyword, doc_type in DOCUMENT_MAP.items():
        if keyword in lower:
            return doc_type
    return "historico_escolar"


def encode_file(path: Path) -> tuple[str, str, int]:
    """Retorna (base64, mime_type, tamanho_bytes)."""
    suffix = path.suffix.lower()
    mime   = MIME_MAP.get(suffix)
    if not mime:
        raise ValueError(f"Extensão '{suffix}' não suportada.")
    raw  = path.read_bytes()
    b64  = base64.b64encode(raw).decode("utf-8")
    return b64, mime, len(raw)


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def save_result(filename: str, result: dict) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"{Path(filename).stem}_{ts}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=4), encoding="utf-8")
    return out


def print_summary(result: dict) -> None:
    status_icon = {
        "analisado":        "✅",
        "rascunho_tecnico": "🟡",
        "ia_indisponivel":  "🔴",
    }.get(result.get("status", ""), "•")

    score = result.get("probabilidade_fraude", 0)
    if score >= 75:
        score_label = f"✅ {score}% — Provavelmente VERÍDICO"
    else:
        score_label = f"🟡 {score}% — Precisa de VERIFICAÇÃO EXTERNA"

    print(f"\n  Status          : {status_icon} {result.get('status', '-')}")
    print(f"  Autenticidade   : {score_label}")
    print(f"  Motor           : {result.get('motor_extracao', '-')}")
    print(f"  Resumo          : {result.get('resumo', '-')}")

    verificacoes = result.get("verificacoes_oficiais", [])
    if verificacoes:
        print(f"\n  Verificações oficiais ({len(verificacoes)}):")
        for v in verificacoes:
            icon = {
                "encontrado":   "✅",
                "alerta":       "⚠️ ",
                "pendente":     "🕐",
                "nao_encontrado": "❌",
            }.get(v["status"], "•")
            print(f"    {icon} {v['titulo']}: {v['detalhe']}")

    alertas = result.get("alertas", [])
    if alertas:
        print(f"\n  Alertas ({len(alertas)}):")
        for a in alertas:
            print(f"    ⚠️  {a}")

    passos = result.get("proximos_passos", [])
    if passos:
        print(f"\n  Próximos passos ({len(passos)}):")
        for p in passos:
            print(f"    → {p}")

    campos = [
        d for d in result.get("dados_chave", [])
        if d["titulo"] not in {
            "Solicitante", "Tipo informado", "Arquivo recebido", "Motor de extracao"
        }
    ]
    encontrados = sum(1 for c in campos if c["status"] == "encontrado")
    print(f"\n  Campos extraídos: {encontrados}/{len(campos)} encontrados")


# ---------------------------------------------------------------------------
# Execução de cada teste
# ---------------------------------------------------------------------------

def check_backend_alive() -> None:
    try:
        urllib.request.urlopen(BASE_URL, timeout=5)
    except urllib.error.HTTPError:
        pass  # servidor respondeu com erro HTTP — está no ar
    except Exception as exc:
        print(f"\n❌ Backend não acessível em {BASE_URL}")
        print(f"   Erro: {exc}")
        print("\n   Execute primeiro:\n   cd backend && uvicorn app.main:app --reload\n")
        sys.exit(1)


def run_test(doc_path: Path, index: int, total: int) -> bool:
    print(f"\n{SEP}")
    print(f"🧪 Teste {index}/{total}: {doc_path.name}")
    print(SEP)

    doc_type = resolve_doc_type(doc_path.name)
    size_kb  = round(doc_path.stat().st_size / 1024, 1)
    print(f"  Tipo detectado  : {doc_type}")
    print(f"  Tamanho         : {size_kb} KB")

    # Codifica o arquivo
    try:
        file_b64, mime_type, size_bytes = encode_file(doc_path)
    except ValueError as exc:
        print(f"  ❌ {exc}")
        return False

    if size_bytes == 0:
        print("  ❌ Arquivo vazio — coloque um documento real em tests/docs/")
        return False

    # Monta o payload exatamente como o main.py espera
    payload = {
        "solicitante": "Teste Automatizado",
        "departamento": "QA",
        "tipo_documento": doc_type,
        "descricao": f"Teste real com arquivo {doc_path.name}",
        "arquivo": {
            "nome": doc_path.name,
            "tipo_mime": mime_type,
            "tamanho_bytes": size_bytes,
            "conteudo_base64": file_b64,
        },
    }

    print("  Enviando para o backend...")
    try:
        result = post_json(ENDPOINT, payload)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"  ❌ Erro HTTP {exc.code}: {body[:500]}")
        return False
    except Exception as exc:
        print(f"  ❌ Erro de conexão: {exc}")
        return False

    print_summary(result)

    out_path = save_result(doc_path.name, result)
    print(f"\n  💾 Resultado salvo em: {out_path}")

    # Validações de sanidade
    passos = result.get("proximos_passos", [])
    checks = [
        ("protocolo presente",        bool(result.get("protocolo"))),
        ("status válido",             result.get("status") in {
                                          "analisado", "rascunho_tecnico", "ia_indisponivel"
                                      }),
        ("probabilidade entre 0-99",  0 <= int(result.get("probabilidade_fraude", -1)) <= 99),
        ("dados_chave é lista",       isinstance(result.get("dados_chave"), list)),
        ("motor_extracao presente",   bool(result.get("motor_extracao"))),
        ("sem passos duplicados",     len(passos) == len(set(passos))),
    ]

    print("\n  Validações de sanidade:")
    passed = True
    for label, ok in checks:
        icon = "✅" if ok else "❌"
        print(f"    {icon} {label}")
        if not ok:
            passed = False

    return passed


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"\n{SEP}")
    print("  SUITE DE TESTES REAIS — Pipeline de Análise de Documentos")
    print(SEP)
    print(f"  Backend   : {BASE_URL}")
    print(f"  Endpoint  : {ENDPOINT}")
    print(f"  Docs      : {DOCS_DIR.resolve()}")
    print(f"  Resultados: {RESULTS_DIR.resolve()}")

    check_backend_alive()

    # Gera arquivos de teste se a pasta estiver vazia
    ensure_test_docs()

    # Coleta documentos válidos, não-vazios e ainda não analisados
    all_docs = sorted([
        p for p in DOCS_DIR.iterdir()
        if p.is_file()
        and p.suffix.lower() in MIME_MAP
        and p.stat().st_size > 0
    ])
    skipped = [p for p in all_docs if already_analyzed(p)]
    docs    = [p for p in all_docs if not already_analyzed(p)]

    if skipped:
        print(f"\n  ⏭️  {len(skipped)} documento(s) ignorado(s) (já analisado(s)):")
        for s in skipped:
            print(f"    • {s.name}")
        print("     Para reanalisar, apague os JSONs em tests/resultados/ e rode novamente.")

    if not docs:
        if skipped:
            print("\n✅ Todos os documentos já foram analisados. Nada a fazer.")
            print("   Apague os JSONs em tests/resultados/ para reanalisar.")
        else:
            print("\n❌ Nenhum documento válido encontrado mesmo após geração automática.")
        sys.exit(0)

    print(f"\n  {len(docs)} documento(s) a analisar:")
    for d in docs:
        print(f"    • {d.name}  ({round(d.stat().st_size / 1024, 1)} KB)")

    # Executa os testes
    results: list[tuple[str, bool]] = []
    for i, doc in enumerate(docs, 1):
        passed = run_test(doc, i, len(docs))
        results.append((doc.name, passed))

    # Relatório final
    print(f"\n{SEP}")
    print("📋 RELATÓRIO FINAL")
    print(SEP)
    passed_count = sum(1 for _, ok in results if ok)
    for name, ok in results:
        icon = "✅" if ok else "❌"
        print(f"  {icon} {name}")
    print(f"\n  Resultado: {passed_count}/{len(results)} testes passaram")

    if passed_count < len(results):
        print("\n  💡 Para testes mais completos, coloque documentos reais em tests/docs/")
        print("     O OCR e o Gemini só extraem dados úteis de documentos com conteúdo real.")

    print(f"{SEP}\n")
    sys.exit(0 if passed_count == len(results) else 1)


if __name__ == "__main__":
    main()