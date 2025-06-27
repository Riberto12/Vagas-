import flet as ft
import asyncio
import pandas as pd
import requests # <--- ADICIONADO: Para fazer requisições HTTP
import json     # <--- ADICIONADO: Para manipular dados JSON

# --- Configurações Iniciais ---
SPACE_BACKGROUND_URL = "background.jpeg"

SPACE_COLORS = {
    "background": "#0F0F2B",
    "surface": "#1A1A3A",
    "primary": "#8E2DE2",
    "primary_dark": "#4A00B7",
    "accent": "#FFD700",
    "text": "#E0E0FF",
    "border": "#4C4C6C",
    "error": "#FF4500",
}

current_mode = "chat_ai"
# Variáveis globais para a busca de vagas
all_found_jobs = []
current_job_index = 0

async def main(page: ft.Page):
    page.title = "Assistente Espacial de IA e Vagas"
    page.vertical_alignment = ft.MainAxisAlignment.START # Voltar ao padrão para que o chat role
    page.window_width = 800
    page.window_height = 900
    page.window_min_width = 700
    page.window_min_height = 800
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.bgcolor = SPACE_COLORS["background"]

    try:
        page.appbar = ft.AppBar(
            title=ft.Text("🚀 Space AI & Job Finder 🛰️", color=SPACE_COLORS["text"], weight=ft.FontWeight.BOLD),
            bgcolor=SPACE_COLORS["surface"],
            center_title=True,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.CHAT,
                    tooltip="Modo Chat com IA",
                    on_click=lambda e: switch_mode("chat_ai"),
                    icon_color=SPACE_COLORS["accent"]
                ),
                ft.IconButton(
                    icon=ft.Icons.WORK,
                    tooltip="Modo Busca de Vagas",
                    on_click=lambda e: switch_mode("job_search"),
                    icon_color=SPACE_COLORS["accent"]
                ),
            ]
        )

        background_image_control = ft.Image(
            src=SPACE_BACKGROUND_URL,
            fit=ft.ImageFit.COVER,
            expand=True
        )

        welcome_message_ref = ft.Ref[ft.Text]()
        chat_history_ref = ft.Ref[ft.Column]()
        chat_input_field_ref = ft.Ref[ft.TextField]()
        send_button_ref = ft.Ref[ft.FloatingActionButton]()
        job_search_form_ref = ft.Ref[ft.Column]()
        
        # --- ADICIONADO: Refs para os novos campos da API ---
        api_url_field_ref = ft.Ref[ft.TextField]()
        api_key_field_ref = ft.Ref[ft.TextField]()
        
        job_title_field_ref = ft.Ref[ft.TextField]()
        job_country_field_ref = ft.Ref[ft.TextField]()
        job_location_field_ref = ft.Ref[ft.TextField]()
        job_remote_dropdown_ref = ft.Ref[ft.Dropdown]()
        job_hours_field_ref = ft.Ref[ft.TextField]()
        job_search_button_ref = ft.Ref[ft.ElevatedButton]()
        new_search_button_ref = ft.Ref[ft.ElevatedButton]()
        job_navigation_buttons_ref = ft.Ref[ft.Row]() 

        page.add(
            ft.Stack(
                [
                    background_image_control,
                    ft.Column(
                        [
                            ft.Container(
                                expand=True,
                                padding=ft.padding.only(left=20, right=20, top=20, bottom=10),
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "Bem-vindo, explorador espacial! Escolha entre conversar com a IA ou buscar vagas.",
                                            color=SPACE_COLORS["text"],
                                            size=16,
                                            text_align=ft.TextAlign.CENTER,
                                            italic=True,
                                            visible=True,
                                            ref=welcome_message_ref
                                        ),
                                        ft.Column(
                                            [],
                                            expand=True,
                                            spacing=10,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            scroll=ft.ScrollMode.ADAPTIVE, 
                                            ref=chat_history_ref
                                        ),
                                        ft.Row(
                                            [
                                                ft.TextField(
                                                    hint_text="Digite sua mensagem ou comando...",
                                                    expand=True,
                                                    border_radius=15,
                                                    border_color=SPACE_COLORS["border"],
                                                    focused_border_color=SPACE_COLORS["primary"],
                                                    text_style=ft.TextStyle(color=SPACE_COLORS["text"]),
                                                    hint_style=ft.TextStyle(color=ft.Colors.with_opacity(0.6, SPACE_COLORS["text"])),
                                                    filled=True,
                                                    bgcolor=SPACE_COLORS["surface"],
                                                    cursor_color=SPACE_COLORS["accent"],
                                                    ref=chat_input_field_ref
                                                ),
                                                ft.FloatingActionButton(
                                                    icon=ft.Icons.SEND,
                                                    on_click=None,
                                                    bgcolor=SPACE_COLORS["primary"],
                                                    shape=ft.CircleBorder(),
                                                    ref=send_button_ref
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.END,
                                            spacing=10,
                                            visible=True
                                        ),
                                        ft.Column(
                                            [
                                                # --- ADICIONADO: Campos para URL e Chave da API ---
                                                ft.TextField(
                                                    label="URL da API (Endpoint de busca)",
                                                    hint_text="ex: http://seuservidor.com/search_jobs",
                                                    border_radius=10, border_color=SPACE_COLORS["border"], focused_border_color=SPACE_COLORS["primary"],
                                                    text_style=ft.TextStyle(color=SPACE_COLORS["text"]), label_style=ft.TextStyle(color=SPACE_COLORS["text"]),
                                                    filled=True, bgcolor=SPACE_COLORS["surface"], cursor_color=SPACE_COLORS["accent"],
                                                    ref=api_url_field_ref
                                                ),
                                                ft.TextField(
                                                    label="Sua Chave de API (X-API-Key)",
                                                    password=True,
                                                    can_reveal_password=True,
                                                    border_radius=10, border_color=SPACE_COLORS["border"], focused_border_color=SPACE_COLORS["primary"],
                                                    text_style=ft.TextStyle(color=SPACE_COLORS["text"]), label_style=ft.TextStyle(color=SPACE_COLORS["text"]),
                                                    filled=True, bgcolor=SPACE_COLORS["surface"], cursor_color=SPACE_COLORS["accent"],
                                                    ref=api_key_field_ref
                                                ),
                                                ft.Divider(height=10, color=ft.Colors.TRANSPARENT), # Espaçador
                                                
                                                ft.TextField(
                                                    label="Título da Vaga (ex: Analista de Dados)",
                                                    border_radius=10, border_color=SPACE_COLORS["border"], focused_border_color=SPACE_COLORS["primary"],
                                                    text_style=ft.TextStyle(color=SPACE_COLORS["text"]), label_style=ft.TextStyle(color=SPACE_COLORS["text"]),
                                                    filled=True, bgcolor=SPACE_COLORS["surface"], cursor_color=SPACE_COLORS["accent"],
                                                    ref=job_title_field_ref
                                                ),
                                                ft.TextField(
                                                    label="País (em inglês, ex: brazil, usa)",
                                                    border_radius=10, border_color=SPACE_COLORS["border"], focused_border_color=SPACE_COLORS["primary"],
                                                    text_style=ft.TextStyle(color=SPACE_COLORS["text"]), label_style=ft.TextStyle(color=SPACE_COLORS["text"]),
                                                    filled=True, bgcolor=SPACE_COLORS["surface"], cursor_color=SPACE_COLORS["accent"],
                                                    ref=job_country_field_ref
                                                ),
                                                ft.TextField(
                                                    label="Localidade (cidade ou 'Home Office')",
                                                    border_radius=10, border_color=SPACE_COLORS["border"], focused_border_color=SPACE_COLORS["primary"],
                                                    text_style=ft.TextStyle(color=SPACE_COLORS["text"]), label_style=ft.TextStyle(color=SPACE_COLORS["text"]),
                                                    filled=True, bgcolor=SPACE_COLORS["surface"], cursor_color=SPACE_COLORS["accent"],
                                                    ref=job_location_field_ref
                                                ),
                                                ft.Dropdown(
                                                    label="Tipo de Trabalho",
                                                    options=[
                                                        ft.dropdown.Option("Ambos"),
                                                        ft.dropdown.Option("Remoto"),
                                                        ft.dropdown.Option("Presencial"),
                                                    ],
                                                    border_radius=10, border_color=SPACE_COLORS["border"], focused_border_color=SPACE_COLORS["primary"],
                                                    label_style=ft.TextStyle(color=SPACE_COLORS["text"]), text_style=ft.TextStyle(color=SPACE_COLORS["text"]),
                                                    filled=True, bgcolor=SPACE_COLORS["surface"],
                                                    value="Ambos",
                                                    ref=job_remote_dropdown_ref
                                                ),
                                                ft.TextField(
                                                    label="Horas atrás (0 para 'Hoje')",
                                                    keyboard_type=ft.KeyboardType.NUMBER,
                                                    border_radius=10, border_color=SPACE_COLORS["border"], focused_border_color=SPACE_COLORS["primary"],
                                                    text_style=ft.TextStyle(color=SPACE_COLORS["text"]), label_style=ft.TextStyle(color=SPACE_COLORS["text"]),
                                                    filled=True, bgcolor=SPACE_COLORS["surface"], cursor_color=SPACE_COLORS["accent"],
                                                    ref=job_hours_field_ref
                                                ),
                                                ft.ElevatedButton(
                                                    "🚀 Buscar Vagas",
                                                    on_click=None,
                                                    bgcolor=SPACE_COLORS["primary"],
                                                    color=SPACE_COLORS["text"],
                                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                                    ref=job_search_button_ref
                                                )
                                            ],
                                            spacing=15,
                                            visible=False,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ref=job_search_form_ref
                                        ),
                                        ft.Row(
                                            [
                                                ft.ElevatedButton(
                                                    "◀️ Anterior",
                                                    on_click=None,
                                                    bgcolor=SPACE_COLORS["primary_dark"],
                                                    color=SPACE_COLORS["text"],
                                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                                    data="previous"
                                                ),
                                                ft.ElevatedButton(
                                                    "Próxima ▶️",
                                                    on_click=None,
                                                    bgcolor=SPACE_COLORS["primary_dark"],
                                                    color=SPACE_COLORS["text"],
                                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                                    data="next"
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=20,
                                            visible=False, 
                                            ref=job_navigation_buttons_ref
                                        ),
                                        ft.ElevatedButton(
                                            "🔄 Nova Busca / Voltar ao Chat",
                                            on_click=lambda e: switch_mode(current_mode),
                                            bgcolor=SPACE_COLORS["accent"],
                                            color=SPACE_COLORS["background"],
                                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                            visible=False,
                                            ref=new_search_button_ref
                                        )
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    expand=True
                                )
                            ),
                        ],
                        expand=True
                    )
                ],
                expand=True
            )
        )
    except Exception as e:
        page.add(ft.Text(f"ERRO CRÍTICO: Falha ao iniciar a UI. Detalhes: {e}", color=ft.Colors.RED_500, size=20))
        page.update()
        print(f"DEBUG: Erro crítico na inicialização da página: {e}")
        return

    # --- Funções Auxiliares para Mensagens ---
    def add_message(sender: str, message: str, color: str = SPACE_COLORS["text"]):
        message_margin_bottom = 15
        message_bubble_width = min(page.window_width * 0.75, 600) 

        try:
            message_content_controls = []
            message_container_bg = SPACE_COLORS["surface"]
            alignment = ft.MainAxisAlignment.START 
            message_text_color = color 

            if sender == "Você":
                alignment = ft.MainAxisAlignment.END
                message_container_bg = SPACE_COLORS["primary_dark"]
                message_text_color = ft.Colors.WHITE
            elif sender == "Assistente":
                alignment = ft.MainAxisAlignment.START
                message_container_bg = SPACE_COLORS["surface"]
                message_text_color = SPACE_COLORS["text"]
            elif sender == "Sistema":
                alignment = ft.MainAxisAlignment.CENTER
                message_container_bg = SPACE_COLORS["surface"]
                message_text_color = SPACE_COLORS["accent"]
            elif sender == "ERRO":
                alignment = ft.MainAxisAlignment.CENTER
                message_container_bg = SPACE_COLORS["error"]
                message_text_color = ft.Colors.WHITE
            
            display_message = str(message) if message is not None else "Mensagem Vazia (DEBUG)"

            if sender != "Sistema" or ("Processando" not in display_message and "Buscando vagas" not in display_message and "Bem-vindo" not in display_message):
                message_content_controls.append(ft.Text(f"**{sender}:**", size=11, color=message_text_color, weight=ft.FontWeight.BOLD))
            
            message_content_controls.append(ft.Text(display_message, color=message_text_color, size=14, selectable=True, text_align=ft.TextAlign.START))


            chat_history_ref.current.controls.append(
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                message_content_controls,
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                            ),
                            padding=ft.padding.symmetric(vertical=10, horizontal=15),
                            margin=ft.margin.only(bottom=message_margin_bottom),
                            bgcolor=message_container_bg,
                            border_radius=15,
                            width=message_bubble_width,
                            alignment=ft.alignment.top_left,
                            ink=False
                        )
                    ],
                    alignment=alignment,
                    wrap=False 
                )
            )
            page.update()
            if chat_history_ref.current:
                 chat_history_ref.current.scroll_to(offset=-1, duration=500)
        except Exception as e:
            print(f"DEBUG: Erro crítico ao tentar adicionar mensagem '{message}' à UI: {e}")
            page.add(ft.Text(f"Erro interno de UI (add_message): {e}", color=ft.Colors.RED_500))
            page.update()

    def show_loading(message: str):
        add_message("Sistema", message, color=SPACE_COLORS["accent"])
        page.update()

    def hide_loading():
        try:
            if chat_history_ref.current.controls and isinstance(chat_history_ref.current.controls[-1], ft.Row):
                container_content_column = chat_history_ref.current.controls[-1].controls[0].content
                if isinstance(container_content_column, ft.Column) and len(container_content_column.controls) > 1:
                    sender_text_control = container_content_column.controls[0]
                    message_text_control = container_content_column.controls[1]
                    
                    if isinstance(sender_text_control, ft.Text) and "Sistema:" in sender_text_control.value and \
                       isinstance(message_text_control, ft.Text) and \
                       ("Processando" in message_text_control.value or "Buscando vagas" in message_text_control.value):
                        chat_history_ref.current.controls.pop()
                        page.update()
        except Exception as e:
            print(f"DEBUG: Erro ao esconder mensagem de loading: {e}")

    def show_error(message: str):
        error_display_message = str(message) if message else "Erro desconhecido. Verifique o console."
        add_message("ERRO", error_display_message, color=SPACE_COLORS["error"])

    # --- Nova função para mostrar descrição completa em um diálogo (Reintroduzida) ---
    def show_full_description(e, description_text):
        print(f"DEBUG: Descrição recebida para 'Ver Mais...' (primeiros 200 caracteres): {description_text[:200]}...")
        print(f"DEBUG: Comprimento total da descrição recebida: {len(description_text)} caracteres.")

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Descrição Completa da Vaga", color=SPACE_COLORS["text"]),
            content=ft.Container(
                content=ft.Column(
                    [
                        # Usando ft.Markdown aqui para renderizar a descrição completa com formatação
                        ft.Markdown(
                            description_text, 
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            selectable=True,
                            # Adicione on_tap_link se houver links dentro da descrição
                            on_tap_link=lambda e: page.launch_url(e.data),
                        ),
                    ],
                    scroll=ft.ScrollMode.ADAPTIVE, 
                    expand=True 
                ),
                width=page.window_width * 0.8, 
                height=page.window_height * 0.7, 
                padding=10,
                bgcolor=SPACE_COLORS["surface"],
                border_radius=10,
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda e: close_dialog(page)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=SPACE_COLORS["surface"],
            shape=ft.RoundedRectangleBorder(radius=15),
        )
        page.dialog.open = True
        page.update()

    def close_dialog(page):
        page.dialog.open = False
        page.update()

    # --- Função para exibir uma única vaga ---
    def display_single_job(job_data_list, index):
        global current_job_index
        chat_history_ref.current.controls.clear() 
        page.update()

        if not job_data_list or index < 0 or index >= len(job_data_list):
            add_message("Sistema", "Não há mais vagas para exibir.", color=SPACE_COLORS["accent"])
            job_navigation_buttons_ref.current.visible = False
            return

        job = job_data_list[index]
        max_card_width = min(page.window_width * 0.8, 700) 

        try:
            title_text = job.get('title', 'Título não disponível')
            company_text = job.get('company', 'Empresa não disponível')
            location_text = job.get('location', 'Localização não disponível')
            is_remote_text = 'Sim ✅' if job.get('is_remote') else 'Não ❌'
            date_posted_text = job.get('date_posted', 'Data não disponível')
            full_description = job.get('description', 'Descrição não disponível') 
            job_type_text = job.get('job_type', 'Não disponível') 
            salary_text = job.get('salary', 'Não disponível')

            display_description = full_description
            if len(full_description) > 250: 
                display_description = full_description[:250] + "..."

            job_url = job.get('job_url')

            card_content_controls = [
                ft.Text(f"💼 **{title_text}**", size=16, weight=ft.FontWeight.BOLD, color=SPACE_COLORS["text"])
            ]

            if job_url and isinstance(job_url, str) and job_url.strip().startswith('http'):
                card_content_controls.append(ft.Markdown(
                    f"🔗 [Link da Vaga]({job_url})",
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    on_tap_link=lambda e: page.launch_url(e.data),
                    selectable=True,
                ))
            else:
                card_content_controls.append(ft.Text("🔗 Link da Vaga: Não disponível ou inválido", size=12, color=ft.Colors.with_opacity(0.8, SPACE_COLORS["text"])))

            card_content_controls.extend([
                ft.Text(f"🏢 Empresa: {company_text}", size=12, color=SPACE_COLORS["text"]),
                ft.Text(f"📍 Localização: {location_text}", size=12, color=SPACE_COLORS["text"]),
                ft.Text(f"🌍 Remoto: {is_remote_text}", size=12, color=SPACE_COLORS["text"]),
                ft.Text(f"📅 Postado: {date_posted_text}", size=12, color=SPACE_COLORS["text"]),
                ft.Text(f"💰 Salário: {salary_text}", size=12, color=SPACE_COLORS["text"]), 
                ft.Text(f"🏷️ Tipo de Vaga: {job_type_text}", size=12, color=SPACE_COLORS["text"]), 
                ft.Text(f"📝 Descrição:\n{display_description}", size=12, color=ft.Colors.with_opacity(0.9, SPACE_COLORS["text"]), selectable=True)
            ])

            if len(full_description) > 250: 
                card_content_controls.append(
                    ft.TextButton(
                        "Ver Mais...",
                        on_click=lambda e, desc=full_description: show_full_description(e, desc),
                        style=ft.ButtonStyle(color=SPACE_COLORS["accent"])
                    )
                )
            
            chat_history_ref.current.controls.append(
                ft.Row(
                    [
                        ft.Card(
                            content=ft.Container(
                                ft.Column(card_content_controls, spacing=5, horizontal_alignment=ft.CrossAxisAlignment.START),
                                padding=ft.padding.all(15),
                                bgcolor=SPACE_COLORS["surface"],
                                border_radius=15,
                                border=ft.border.all(1, SPACE_COLORS["primary_dark"]),
                                width=max_card_width 
                            ),
                            elevation=5,
                            margin=ft.margin.only(bottom=15)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER, 
                    expand=True 
                )
            )
            page.update()

            # Habilita/Desabilita botões de navegação
            job_navigation_buttons_ref.current.controls[0].disabled = (index == 0) # Anterior
            job_navigation_buttons_ref.current.controls[1].disabled = (index >= len(job_data_list) - 1) # Próxima
            job_navigation_buttons_ref.current.visible = True
            
            page.update()
            
        except Exception as ex_card:
            print(f"DEBUG: ERRO CRÍTICO ao renderizar Card da vaga {index+1}: {type(ex_card).__name__}: {ex_card}. Dados parciais da vaga: {job.keys()}")
            show_error(f"ERRO INTERNO NA EXIBIÇÃO: Falha ao exibir vaga {index+1}. Verifique o console para detalhes.")
            job_navigation_buttons_ref.current.visible = False
            page.update()

    # --- Funções para Navegação de Vagas ---
    def navigate_jobs(e):
        global current_job_index, all_found_jobs
        
        if e.control.data == "next":
            current_job_index += 1
        elif e.control.data == "previous":
            current_job_index -= 1
        
        display_single_job(all_found_jobs, current_job_index)


    # --- Funções de Lógica (Chat e Busca de Vagas) ---
    async def send_message_chat(e):
        user_message = chat_input_field_ref.current.value.strip()
        chat_input_field_ref.current.value = ""
        page.update()

        if not user_message:
            return

        welcome_message_ref.current.visible = False
        add_message("Você", user_message)
        show_loading("...")
        
        # --- MODIFICADO: Lógica do chat desativada ---
        hide_loading()
        add_message("Assistente", "A função de Chat com a IA foi desativada nesta versão.")
        page.update()
    
    async def search_jobs_gui(e):
        global all_found_jobs, current_job_index 

        # --- MODIFICADO: Obter valores dos campos da API ---
        api_url = api_url_field_ref.current.value.strip()
        api_key = api_key_field_ref.current.value.strip()

        title = job_title_field_ref.current.value.strip()
        country = job_country_field_ref.current.value.strip()
        location = job_location_field_ref.current.value.strip()
        is_remote_str = job_remote_dropdown_ref.current.value
        hours_ago_str = job_hours_field_ref.current.value.strip()

        print(f"DEBUG: Iniciando busca com: Título='{title}', País='{country}', Localidade='{location}', Remoto='{is_remote_str}', Horas='{hours_ago_str}'")

        # --- MODIFICADO: Validação dos campos da API ---
        if not api_url or not api_key:
            show_error("ERRO DE VALIDAÇÃO: A URL e a Chave de API são obrigatórias!")
            page.update()
            return

        if not title or not country:
            show_error("ERRO DE VALIDAÇÃO: Título da vaga e País são obrigatórios para a busca!")
            page.update()
            return

        hours_ago = None
        if hours_ago_str:
            try:
                hours_ago = int(hours_ago_str)
                if hours_ago < 0:
                    show_error("ERRO DE VALIDAÇÃO: Horas atrás deve ser um número positivo ou 0.")
                    page.update()
                    return
            except ValueError:
                show_error("ERRO DE VALIDAÇÃO: 'Horas atrás' deve ser um número inteiro válido (ex: 0 para hoje, 24 para 24h atrás).")
                print(f"DEBUG: ValueError para horas_ago_str: '{hours_ago_str}'")
                page.update()
                return

        chat_history_ref.current.controls.clear()
        welcome_message_ref.current.visible = False
        add_message("Sistema", "📡 Conectando à API e buscando vagas... isso pode levar um momento.")
        page.update()

        # --- MODIFICADO: Função interna para chamada de API e transformação de dados ---
        def fetch_and_transform_jobs():
            headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
            payload = {
                "search_term": title,
                "location": location,
                "country": country,
                "is_remote": is_remote_str,
                "hours_old": hours_ago if hours_ago is not None else 0
            }
            try:
                response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=45)
                response.raise_for_status()
                api_response_data = response.json()

                if not api_response_data or 'jobs' not in api_response_data:
                    return {"error": "Resposta da API inválida ou não contém a chave 'jobs'."}

                transformed_jobs = []
                for job in api_response_data.get('jobs', []):
                    # Formata o salário a partir dos múltiplos campos da API
                    salary_text = "Não disponível"
                    salary_from = job.get('salary_from')
                    salary_to = job.get('salary_to')
                    salary_avg = job.get('salary_avg')
                    salary_unit = job.get('salary_unit')
                    
                    if salary_avg:
                        salary_text = f"~ {salary_avg}"
                    elif salary_from and salary_to:
                        salary_text = f"{salary_from} - {salary_to}"
                    elif salary_from:
                        salary_text = f"A partir de {salary_from}"
                    
                    if salary_unit and salary_text != "Não disponível":
                         salary_text += f" ({salary_unit})"

                    # Transforma o dicionário da API para o formato esperado pela UI
                    transformed_job = {
                        'title': job.get('title', 'N/A'),
                        'company': job.get('company', 'N/A'),
                        'location': job.get('location', 'N/A'),
                        'is_remote': job.get('is_remote', False) or (job.get('work_from_home_type') == 'Remoto'),
                        'date_posted': job.get('date_posted', 'N/A'),
                        'description': job.get('description', 'Descrição não disponível.'),
                        'job_type': job.get('job_type', 'N/A'),
                        'salary': salary_text,
                        'job_url': job.get('job_url')
                    }
                    transformed_jobs.append(transformed_job)
                
                return transformed_jobs

            except requests.exceptions.HTTPError as http_err:
                error_detail = "Detalhe não disponível."
                try:
                    error_detail = http_err.response.json().get('detail', http_err.response.text)
                except json.JSONDecodeError:
                    error_detail = http_err.response.text
                return {"error": f"Erro HTTP {http_err.response.status_code} da API: {error_detail}"}
            except requests.exceptions.RequestException as req_err:
                return {"error": f"Erro de Conexão com a API: {req_err}"}
            except Exception as e:
                return {"error": f"Ocorreu um erro inesperado: {e}"}

        # Executa a função de rede em uma thread separada
        jobs_data = await asyncio.to_thread(fetch_and_transform_jobs)

        hide_loading()
        
        # --- MODIFICADO: Tratamento da resposta da API ---
        if isinstance(jobs_data, dict) and jobs_data.get("error"):
            show_error(f"ERRO DA API: {jobs_data.get('error')}")
            new_search_button_ref.current.visible = True
            job_navigation_buttons_ref.current.visible = False
        
        elif not isinstance(jobs_data, list):
            show_error(f"ERRO DE DADOS: Formato inesperado recebido. Esperava uma LISTA, recebi: {type(jobs_data).__name__}.")
            new_search_button_ref.current.visible = True
            job_navigation_buttons_ref.current.visible = False
        
        elif not jobs_data:
            show_error("😔 Nenhuma vaga encontrada com os critérios fornecidos.")
            new_search_button_ref.current.visible = True
            job_navigation_buttons_ref.current.visible = False

        else: 
            all_found_jobs = jobs_data 
            current_job_index = 0     
            
            add_message("Sistema", f"🎉 Encontrei {len(all_found_jobs)} vaga(s) para você! Exibindo a primeira...")
            display_single_job(all_found_jobs, current_job_index) 

            job_search_form_ref.current.visible = False
            chat_input_field_ref.current.parent.visible = False
            new_search_button_ref.current.visible = True
            job_navigation_buttons_ref.current.visible = True 
            
            job_navigation_buttons_ref.current.controls[0].on_click = navigate_jobs
            job_navigation_buttons_ref.current.controls[1].on_click = navigate_jobs
            
        page.update()

    def switch_mode(mode: str):
        global current_mode, all_found_jobs, current_job_index
        current_mode = mode
        chat_history_ref.current.controls.clear()
        welcome_message_ref.current.visible = True
        new_search_button_ref.current.visible = False
        job_navigation_buttons_ref.current.visible = False 
        
        all_found_jobs = [] 
        current_job_index = 0 

        chat_input_row = chat_input_field_ref.current.parent

        try:
            if mode == "chat_ai":
                send_button_ref.current.on_click = send_message_chat
                chat_input_field_ref.current.on_submit = send_message_chat 
                chat_input_row.visible = True
                job_search_form_ref.current.visible = False
                page.vertical_alignment = ft.MainAxisAlignment.START # Modo chat, alinha ao topo para scrollar
                page.update()
                add_message("Sistema", "Você está agora no **modo de chat com a IA**. Pergunte-me qualquer coisa!", color=SPACE_COLORS["accent"])
            elif mode == "job_search":
                job_search_button_ref.current.on_click = search_jobs_gui
                chat_input_row.visible = False
                job_search_form_ref.current.visible = True
                page.vertical_alignment = ft.MainAxisAlignment.CENTER # Modo busca, centraliza o formulário ou a vaga
                page.update()
                add_message("Sistema", "Você está no **modo de busca de vagas**. Preencha os campos abaixo para encontrar sua vaga ideal.", color=SPACE_COLORS["accent"])
            page.update()
        except Exception as e:
            print(f"DEBUG: Erro ao trocar de modo: {e}")
            show_error(f"ERRO INTERNO: Falha ao mudar de modo. Tente reiniciar.")
            page.update()

    switch_mode(current_mode)


if __name__ == "__main__":
    ft.app(target=main)
