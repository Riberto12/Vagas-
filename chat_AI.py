# -*- coding: utf-8 -*-
# Acima: Declara a codificação do arquivo como UTF-8 para garantir compatibilidade.

import requests
import json
import time

# URL base da sua API
BASE_URL = "https://minha-api.riberto2006.workers.dev/"

# --- Chave de API para teste ---
# Certifique-se de que esta chave corresponde a uma chave válida definida no seu auth.py
VALID_CHAT_KEY = "chave-de-teste" # Usando uma chave PRO para garantir acesso total

# --- Função para fazer requisições ao endpoint /chat ---
def fazer_requisicao_chat(message: str, api_key: str):
    """
    Envia uma mensagem para o endpoint /chat da API e retorna a resposta.
    """
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    url = f"{BASE_URL}/chat"
    payload = {"message": message}

    print(f"\n--- Enviando mensagem para o assistente de IA... ---")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Levanta um erro para códigos de status HTTP 4xx/5xx
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"\nOops! Algo deu errado na comunicação com o assistente de IA: {http_err}")
        try:
            error_detail = response.json().get('detail', 'Detalhe não disponível.')
            print(f"Detalhes do erro da API: {error_detail}")
            if "Muitas requisições" in error_detail:
                print("Parece que o limite de requisições foi atingido. Tente novamente em breve!")
            elif "inválida" in error_detail or "expirada" in error_detail:
                print("Sua chave de API está inválida ou expirada. Verifique-a e tente novamente!")
        except json.JSONDecodeError:
            print(f"Resposta da API (erro - não JSON): {response.text}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"\nErro de Conexão: Parece que o servidor está offline ou sua internet está com problemas. Detalhe: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"\nErro de Timeout: A requisição demorou demais para responder. Detalhe: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"\nOcorreu um erro inesperado na requisição: {req_err}")
    return None

# --- Função principal para interagir com a AI ---
def interagir_com_ai(api_key: str):
    """
    Permite ao usuário digitar mensagens e receber respostas do assistente de IA.
    """
    print("\n--- Bem-vindo ao Chat com o Assistente de IA! ---")
    print("Digite sua mensagem ou 'sair' para encerrar.")

    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() == 'sair':
            print("Encerrando o chat. Até a próxima!")
            break
        
        if not user_input.strip():
            print("Por favor, digite algo para o assistente de IA.")
            continue

        resposta_ai = fazer_requisicao_chat(user_input, api_key)
        if resposta_ai and 'response' in resposta_ai:
            print(f"Assistente: {resposta_ai['response']}")
        else:
            print("Assistente: Não foi possível obter uma resposta no momento. Por favor, tente novamente.")
        
        time.sleep(1) # Pequena pausa para simular uma interação mais natural

# --- Execução do Script ---
if __name__ == "__main__":
    interagir_com_ai(VALID_CHAT_KEY)
