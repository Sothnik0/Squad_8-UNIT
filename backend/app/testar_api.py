import base64
import requests
import json

# ================= CONFIG =================
URL_API = "http://127.0.0.1:8000/analises/documento"
URL_IMAGEM_TESTE = "https://dummyimage.com/600x800/eeeeee/000000.png&text=Documento+Falso+Teste"
# ==========================================

def testar_api():
    print("⏳ [1/3] Baixando imagem de teste da internet...")
    
    try:
        # Adicionamos um cabeçalho para fingir que somos o navegador e evitar bloqueios
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        img_response = requests.get(URL_IMAGEM_TESTE, headers=headers)
        img_response.raise_for_status() 
        
        # Converte os bytes da imagem baixada para uma string Base64
        encoded_string = base64.b64encode(img_response.content).decode('utf-8')
        print("✅ Imagem baixada e convertida para Base64 com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao baixar a imagem da web: {e}")
        return

    # Monta o pacote de dados exatamente como o Pydantic do backend exige
    payload = {
        "solicitante": "Eduardo (Teste Backend)",
        "departamento": "TI - Squad 8",
        "tipo_documento": "Documento Teste OpenAI",
        "descricao": "Teste de validação da API usando ChatGPT Pro (GPT-4o)",
        "arquivo": {
            "nome": "imagem_falsa_teste.png",
            "tipo_mime": "image/png",
            "tamanho_bytes": len(encoded_string),
            "conteudo_base64": encoded_string
        }
    }

    print("\n🚀 [2/3] Enviando requisição para o seu FastAPI...")
    print("🧠 A IA da OpenAI está analisando a imagem (isso pode levar uns 5 a 15 segundos)...")
    
    try:
        # O timeout evita que o script fique travado para sempre se a API cair
        response = requests.post(URL_API, json=payload, timeout=60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO DE CONEXÃO:")
        print("O seu servidor FastAPI não está rodando.")
        print("Abra outro terminal e rode: uvicorn app.main:app --reload")
        return
    except requests.exceptions.Timeout:
        print("\n❌ ERRO DE TIMEOUT: A OpenAI demorou muito para responder. Tente novamente.")
        return

    print("\n" + "="*60)
    print("📊 [3/3] RESULTADO DA ANÁLISE")
    print("="*60)
    
    if response.status_code == 200:
        print("✅ SUCESSO! O ChatGPT respondeu o seguinte JSON:\n")
        # Imprime o JSON formatado e indentado para ficar fácil de ler
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
    else:
        print(f"❌ ERRO {response.status_code} NO BACKEND:")
        try:
            print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        except:
            print(response.text)
            
    print("="*60 + "\n")

if __name__ == "__main__":
    testar_api()