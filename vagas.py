# -*- coding: utf-8 -*-
# Acima: Declara a codificação do arquivo como UTF-8 para garantir compatibilidade.

import requests
import json
import time
from datetime import datetime # Para formatação de datas
from typing import Optional # <--- Adicionado: Importa o tipo Optional

# URL base da sua API
BASE_URL = "https://minha-api.riberto2006.workers.dev/"

# --- Chave de API para teste ---
# Certifique-se de que esta chave corresponde à definida no seu auth.py
VALID_FREE_KEY = "chave-de-teste"  

# --- Mapeamento de Chaves para Nomes em Português e Tratamento de Valores ---
# Este dicionário mapeia as chaves do JSON para rótulos mais amigáveis em português
# e define a ordem de apresentação.
JOB_FIELD_TRANSLATIONS = {
    'id': 'ID da Vaga',
    'site': 'Plataforma',
    'job_url': 'Link da Vaga',
    'job_url_direct': 'Link Direto da Candidatura',
    'title': 'Título da Vaga',
    'company': 'Empresa',
    'location': 'Localização',
    'date_posted': 'Data de Publicação',
    'job_type': 'Tipo de Contrato',
    'salary_from': 'Salário Mínimo',
    'salary_to': 'Salário Máximo',
    'salary_unit': 'Unidade Salarial',
    'salary_avg': 'Salário Médio Estimado',
    'salary_hourly': 'Salário por Hora',
    'salary_yearly': 'Salário Anual',
    'description': 'Descrição da Vaga',
    'company_website': 'Website da Empresa',
    'company_description': 'Sobre a Empresa',
    'company_num_employees': 'Número de Funcionários',
    'company_revenue': 'Faturamento da Empresa',
    'skills': 'Habilidades Necessárias',
    'experience_range': 'Nível de Experiência',
    'work_from_home_type': 'Modalidade',
    'company_rating': 'Avaliação da Empresa',
    'company_reviews_count': 'Número de Avaliações',
    'vacancy_count': 'Vagas Abertas na Empresa'
}

# --- Função para fazer requisições à API ---
def fazer_requisicao(endpoint: str, payload: dict, api_key: str, method: str = "POST"):
    """
    Função genérica para fazer uma requisição POST ou GET à API.
    """
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    url = f"{BASE_URL}/{endpoint}"

    try:
        if method.upper() == "POST":
            response = requests.post(url, headers=headers, data=json.dumps(payload))
        elif method.upper() == "GET":
            response = requests.get(url, headers=headers)
        else:
            print("Método HTTP não suportado por esta função.")
            return None

        response.raise_for_status() # Levanta um erro para códigos de status HTTP 4xx/5xx
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"\nOops! Algo deu errado na requisição: {http_err}")
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

# --- Testando o endpoint /search_jobs ---
def buscar_e_exibir_vagas(api_key: str, termo_busca: str, localidade: str, pais: str, is_remota: Optional[str] = None, hours_old: Optional[int] = None):
    print(f"\n##### Buscando vagas de '{termo_busca}' em '{localidade}, {pais}' #####")
    job_payload = {
        "search_term": termo_busca,
        "location": localidade,
        "country": pais,
        "is_remote": is_remota,
        "hours_old": hours_old
    }
    resposta_jobs = fazer_requisicao("search_jobs", job_payload, api_key)

    if resposta_jobs:
        count = resposta_jobs.get('count', 0)
        print(f"\n--- Boas notícias! Encontramos {count} oportunidades incríveis para você! ---")
        if count > 0:
            print("\nConfira os detalhes de cada vaga:")
            for i, job in enumerate(resposta_jobs['jobs']): # Itera sobre todas as vagas
                print(f"\n--- Vaga #{i+1}: {job.get('title', 'Título Desconhecido')} na {job.get('company', 'Empresa Desconhecida')} ---")
                for key in JOB_FIELD_TRANSLATIONS:
                    value = job.get(key)
                    display_key = JOB_FIELD_TRANSLATIONS[key]

                    # Tratamento para "Não disponível"
                    if value is None or (isinstance(value, str) and value.strip().lower() in ['none', 'nan', 'null', '']):
                        display_value = "Não disponível :("
                    elif isinstance(value, (int, float)) and (value == 0 or (hasattr(value, '__array_ufunc__') and (isinstance(value, float) and (value != value or value == float('inf') or value == float('-inf'))))):
                        # Captura floats/ints que podem ser 0 ou valores problemáticos (NaN, Inf)
                        display_value = "Não disponível :("
                    elif key == 'description':
                        # Para a descrição, exibimos apenas um trecho para não sobrecarregar
                        display_value = f"{str(value)[:400]}..." if value != "Não disponível :(" else "Não disponível :("
                    elif key in ['job_url', 'job_url_direct', 'company_website'] and value:
                        display_value = f"Link: {value}"
                    elif key.startswith('salary_') and value != "Não disponível :(":
                        # Formata valores de salário como moeda, se for um número
                        try:
                            numeric_value = float(value)
                            # Formato BR para moeda (ex: 1.234,56)
                            formatted_value = f"{numeric_value:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')

                            salary_unit = job.get('salary_unit', '').lower()
                            if salary_unit == 'yearly' and key == 'salary_yearly':
                                display_value = f"EUR {formatted_value} por Ano"
                            elif salary_unit == 'hourly' and key == 'salary_hourly':
                                display_value = f"EUR {formatted_value} por Hora"
                            elif salary_unit == 'monthly' and key in ['salary_from', 'salary_to', 'salary_avg']:
                                display_value = f"EUR {formatted_value} por Mês"
                            elif salary_unit == 'daily':
                                display_value = f"EUR {formatted_value} por Dia"
                            elif salary_unit == 'weekly':
                                display_value = f"EUR {formatted_value} por Semana"
                            else: # Se a unidade não for clara, apenas mostra o valor com EUR
                                display_value = f"EUR {formatted_value}"
                        except ValueError:
                            display_value = str(value) # Se não for número, mostra como string
                    elif isinstance(value, str) and (value.lower() == 'true' or value.lower() == 'false'):
                        display_value = "Sim" if value.lower() == 'true' else "Não"
                    elif key == 'date_posted' and value != "Não disponível :(":
                        try:
                            # Tenta formatar a data se for uma string ISO
                            dt_object = datetime.fromisoformat(value)
                            display_value = dt_object.strftime("%d/%m/%Y") # Formato dd/mm/yyyy
                        except ValueError:
                            display_value = str(value) # Fallback para string original
                    else:
                        display_value = value

                    # Exibe o campo, a menos que seja um campo de salário secundário com valor "Não disponível"
                    if (display_value != "Não disponível :(" or
                        key in ['title', 'company', 'location', 'job_url', 'date_posted']):
                        print(f"  > {display_key}: {display_value}")
                print("\n" + "="*60 + "\n") # Separador visual mais robusto para cada vaga
        else:
            print("Puxa! :( Não encontramos nenhuma vaga com os critérios que você nos deu. Que tal tentar outros termos?")
    else:
        print("\nParece que não foi possível buscar as vagas no momento. Por favor, tente novamente mais tarde.")

# --- Execução dos Testes ---
if __name__ == "__main__":
    # Teste de busca de vagas com chave PRO válida
    buscar_e_exibir_vagas(VALID_PRO_KEY,
                          termo_busca="Analista de Dados",
                          localidade="Lisboa",
                          pais="portugal",
                          is_remota="Ambos",
                          hours_old=72)

    # Exemplo de busca para "Backend Developer" no Brasil (remoto)
    # time.sleep(5) # Pequena pausa entre as chamadas para não sobrecarregar
    # buscar_e_exibir_vagas(VALID_PRO_KEY,
    #                       termo_busca="Backend Developer",
    #                       localidade="São Paulo",
    #                       pais="brazil",
    #                       is_remota="Remoto",
    #                       hours_old=48)

    print("\n--- Processo de Busca de Vagas Concluído! :) ---")
