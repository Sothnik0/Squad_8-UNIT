import base64
import requests
import json

# Configurações
URL_API = "http://127.0.0.1:8000/analises/documento"

# Usando um serviço de imagens para desenvolvedores (nunca bloqueia). 
# Essa imagem vai estar escrita "Documento Falso Teste"
URL_IMAGEM_TESTE = "https://dummyimage.com/600x800/eeeeee/000000.png&text=Documento+Falso+Teste"

def testar_api():
    print("Baixando imagem de teste da internet...")
    
    try:
        # Adicionamos um cabeçalho para fingir que somos o Google Chrome
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        img_response = requests.get(URL_IMAGEM_TESTE, headers=headers)
        img_response.raise_for_status() 
        
        encoded_string = base64.b64encode(img_response.content).decode('utf-8')
    except Exception as e:
        print(f"❌ Erro ao baixar a imagem da web: {e}")
        return

    # Monta o payload
    payload = {
        "solicitante": "Carlos (Teste Backend)",
        "departamento": "TI - Squad 8",
        "tipo_documento": "Certificado / Cartão CNPJ",
        "descricao": "Teste de validação da IA via script com imagem da web",
        "arquivo": {
            "nome": "imagem_falsa_teste.png",
            "tipo_mime": "image/png",
            "tamanho_bytes": len(encoded_string),
            "conteudo_base64": encoded_string
        }
    }

    print("Enviando requisição para o seu FastAPI (isso pode levar alguns segundos)...")
    
    try:
        response = requests.post(URL_API, json=payload)
    except requests.exceptions.ConnectionError:
        print("❌ Erro de Conexão: O seu servidor FastAPI (uvicorn) não está rodando. Inicie ele primeiro!")
        return

    print("\n" + "="*50)
    if response.status_code == 200:
        print("✅ SUCESSO! A IA respondeu o seguinte JSON:")
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
    else:
        print(f"❌ ERRO {response.status_code}:")
        print(response.text)
    print("="*50 + "\n")

if __name__ == "__main__":
    testar_api()