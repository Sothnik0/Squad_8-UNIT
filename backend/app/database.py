import os
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor, Json

logger = logging.getLogger("uvicorn.error")

DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize connection pool
pool = None

def init_db():
    global pool
    if not DATABASE_URL:
        logger.error("DATABASE_URL is not set in environment variables!")
        return
    try:
        pool = ThreadedConnectionPool(1, 10, dsn=DATABASE_URL)
        logger.info("Database connection pool initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database connection pool: {e}")

@contextmanager
def get_db_cursor():
    global pool
    if not pool:
        init_db()
    if not pool:
        raise Exception("Database connection pool is not initialized.")
    conn = pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        pool.putconn(conn)

def save_analysis(payload: dict) -> None:
    DOC_TYPE_MAP = {
        "atestado_medico": 1,
        "certificado_ensino_medio": 2,
        "diploma": 3,
        "historico_escolar": 4
    }
    
    tipo_doc_id = DOC_TYPE_MAP.get(payload.get("tipo_documento"), 1)
    
    query = """
        INSERT INTO analyses (
            protocolo, solicitante, departamento, tipo_documento, descricao,
            status, probabilidade_fraude, resumo, dados_chave, verificacoes_oficiais,
            alertas, fatores_score, proximos_passos, motor_extracao, texto_extraido, criado_em
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (protocolo) DO UPDATE SET
            status = EXCLUDED.status,
            probabilidade_fraude = EXCLUDED.probabilidade_fraude,
            resumo = EXCLUDED.resumo,
            dados_chave = EXCLUDED.dados_chave,
            verificacoes_oficiais = EXCLUDED.verificacoes_oficiais,
            alertas = EXCLUDED.alertas,
            fatores_score = EXCLUDED.fatores_score,
            proximos_passos = EXCLUDED.proximos_passos,
            motor_extracao = EXCLUDED.motor_extracao,
            texto_extraido = EXCLUDED.texto_extraido;
    """
    
    with get_db_cursor() as cur:
        cur.execute(query, (
            payload["protocolo"],
            payload["solicitante"],
            payload.get("departamento") or "",
            tipo_doc_id,
            payload.get("descricao") or "",
            payload["status"],
            payload["probabilidade_fraude"],
            payload["resumo"],
            Json(payload["dados_chave"]),
            Json(payload["verificacoes_oficiais"]),
            Json(payload["alertas"]),
            Json(payload["fatores_score"]),
            Json(payload["proximos_passos"]),
            payload.get("motor_extracao") or "",
            payload.get("texto_extraido") or "",
            datetime.now(timezone.utc)
        ))

def get_analyses() -> list[dict]:
    query = """
        SELECT a.protocolo, a.solicitante, a.departamento, a.tipo_documento,
               d.nome as tipo_documento_nome, a.descricao, a.status,
               a.probabilidade_fraude, a.resumo, a.dados_chave, a.verificacoes_oficiais,
               a.alertas, a.fatores_score, a.proximos_passos, a.motor_extracao,
               a.texto_extraido, a.criado_em
        FROM analyses a
        LEFT JOIN document_types d ON a.tipo_documento = d.id
        ORDER BY a.criado_em DESC;
    """
    with get_db_cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        results = []
        for r in rows:
            item = dict(r)
            if item.get("criado_em"):
                item["criado_em"] = item["criado_em"].isoformat()
            results.append(item)
        return results

def update_analysis_status(protocolo: str, status: str) -> bool:
    query = """
        UPDATE analyses
        SET status = %s
        WHERE protocolo = %s;
    """
    with get_db_cursor() as cur:
        cur.execute(query, (status, protocolo))
        return cur.rowcount > 0
