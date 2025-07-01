# 💼 ClientHunt AI – API inteligente de busca de oportunidades + assistente modular com IA
==========================================================================================

ClientHunt AI é uma API completa e modular voltada para a **busca inteligente de oportunidades em tempo real** — como **empregos, estágios e bolsas de estudo** — em fontes públicas como LinkedIn e Indeed. O sistema conta com um **assistente IA integrado** e um **painel interativo feito com [Flet](https://flet.dev/)** para facilitar o uso, visualização e testes em tempo real.

---

## 🌐 API Online
----------------

A API está disponível publicamente em:  
🔗 https://minha-api.riberto2006.workers.dev/  
📘 Documentação Swagger: https://minha-api.riberto2006.workers.dev/docs

---

## 🚀 Funcionalidades principais
-------------------------------

### 🔍 `/search_jobs`
----------------------

Endpoint para busca de vagas em tempo real com base em diversos critérios como:

- Nome da vaga (ex: `desenvolvedor`, `marketing`)
- Localidade (país e cidade)
- Tipo de trabalho (remoto, híbrido, presencial)
- Data da publicação

A busca é flexível: mesmo que nenhuma vaga exata seja encontrada, o sistema tenta sugerir **oportunidades semelhantes**, inclusive de outras regiões ou datas mais antigas, priorizando **utilidade real**.

---

### 🧠 `/chat`
----------------

Endpoint para interações com um assistente IA (baseado em ChatGPT/Gemini) que pode:

- Interpretar comandos em linguagem natural  
- Ajudar a filtrar ou formatar buscas  
- Integrar com sistemas externos (bots, dashboards, sites)  
- Ser personalizado para nichos específicos (TI, freelancers, bolsas, etc.)

---

## 📊 Painel interativo com Flet (Python)
-----------------------------------------

O repositório inclui um **painel de controle feito com Flet**, que permite:

- Inserir parâmetros para testar os endpoints  
- Visualizar os resultados em tempo real  
- Prototipar aplicações baseadas na API de forma rápida e visual

---

## ⚙️ Casos de uso sugeridos
----------------------------

- Bots para envio automático de vagas  
- Plataformas de recomendação de oportunidades  
- Sistemas de alerta personalizados com IA  
- Ferramentas para recrutadores, estudantes e freelancers  
- Assistentes virtuais que entendem comandos de voz ou texto

---

## 🔧 Status do projeto
-----------------------

Este é um **MVP funcional**, em constante evolução. Recursos futuros planejados:

- Geração de voz e imagem com IA  
- Novas fontes de dados  

---

## 📁 Estrutura do repositório
------------------------------

```bash
├── chat_AI.py   # Exemplos de uso
├── painel.py    # Painel interativo com Flet
├── vagas.py     # Exemplos de uso
├── requirements.txt     # Dependências
└── README.md            # Esta documentação
