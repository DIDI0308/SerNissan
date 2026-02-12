import streamlit as st
import pandas as pd
import base64

# 1. Configuración de la página
st.set_page_config(page_title="Chatbot SERNISSAN", page_icon="🚗", layout="wide")

# 2. Funciones de Apoyo
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except: return None

@st.cache_data(ttl=0) 
def load_data(sheet_url):
    try:
        csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')
        df = pd.read_csv(csv_url)
        return df
    except: return None

# 3. Estilos CSS (Texto Blanco, Fondo Negro y Botones)
bin_str = get_base64('TAIYO.jpg')
logo_html = f'data:image/jpg;base64,{bin_str}' if bin_str else ""

st.markdown(f"""
    <style>
    /* Reset y Fondo General */
    .block-container {{ padding: 0rem !important; max-width: 100% !important; }}
    .stApp {{ background-color: #000000 !important; color: #FFFFFF !important; }}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Franja Roja Superior */
    .red-banner {{
        background-color: #C41230; 
        width: 100vw; height: 120px;
        display: flex; justify-content: center; align-items: center;
        margin: 0; padding: 0;
    }}
    .logo-img {{ max-height: 80px; }}

    /* Título Grande Centrado */
    .main-title {{
        color: #FFFFFF !important; 
        font-family: 'Arial Black', sans-serif; 
        font-size: 42px; 
        text-align: center;
        margin-top: 20px;
        margin-bottom: 5px;
        width: 100%;
    }}

    /* Forzar color de texto blanco en toda la app */
    .stMarkdown, .stText, p, h1, h2, h3, span, label {{
        color: #FFFFFF !important;
    }}

    /* Burbujas tipo WhatsApp */
    .stChatMessage {{ 
        border-radius: 20px !important; 
        padding: 15px !important;
        margin-bottom: 15px !important;
    }}
    
    /* Asistente: Fondo Blanco / Texto Negro (Clásico de WA) */
    [data-testid="stChatMessageAssistant"] {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }}
    [data-testid="stChatMessageAssistant"] p, [data-testid="stChatMessageAssistant"] h3, [data-testid="stChatMessageAssistant"] span {{ 
        color: #000000 !important; 
    }}

    /* Usuario: Verde WhatsApp / Texto Blanco */
    [data-testid="stChatMessageUser"] {{
        background-color: #25D366 !important;
    }}
    [data-testid="stChatMessageUser"] p {{ 
        color: #FFFFFF !important; 
    }}

    /* Contenedor de Contenido */
    .content-wrapper {{ padding-left: 10%; padding-right: 10%; padding-top: 10px; }}

    /* Estilo del botón de actualizar (Fijo arriba) */
    .stButton>button {{
        background-color: #C41230 !important;
        color: white !important;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }}
    </style>
    
    <div class="red-banner">
        <img src="{logo_html}" class="logo-img">
    </div>
    <h1 class="main-title">Chatbot SERNISSAN</h1>
    """, unsafe_allow_html=True)

# 4. Inicialización de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []
if "cargo" not in st.session_state:
    st.session_state.cargo = None

# 5. Carga de Datos desde Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1FcQUNjuHkrK3idDJLtgIxqlXTxEQ-M7n/edit?usp=sharing"
df = load_data(SHEET_URL)

def restart_chat():
    st.session_state.messages = []
    st.session_state.cargo = None

# 6. Interfaz Principal
with st.container():
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    # BOTÓN DE ACTUALIZAR (Siempre visible)
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        if st.button("🔄 Actualizar Datos / Cambiar Cargo"):
            restart_chat()
            st.rerun()

    st.write("---")

    # FLUJO DEL CHAT
    if st.session_state.cargo is None:
        with st.chat_message("assistant"):
            st.markdown("### Hola. Bienvenida al sistema de gestión de Taiyo Motors.\nPara brindarte la información de tu área, por favor selecciona: **¿En qué cargo estás?**")
        
        if df is not None:
            # Columna G (Responsables) es índice 6
            lista_cargos = sorted(df.iloc[:, 6].dropna().unique().tolist())
            cargo_sel = st.selectbox("Cargos disponibles:", ["Selecciona un cargo..."] + lista_cargos, label_visibility="collapsed")
            
            if cargo_sel != "Selecciona un cargo...":
                st.session_state.cargo = cargo_sel
                msj_bienvenida = f"Perfecto. He cargado el manual para el cargo: **{cargo_sel}**.\n\n¿Qué hábito o proceso deseas consultar?"
                st.session_state.messages.append({"role": "assistant", "content": msj_bienvenida})
                st.rerun()
    
    else:
        # Mostrar historial de conversación
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Entrada de texto del chat
        if prompt := st.chat_input("Escribe el nombre del proceso o número de hábito..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Búsqueda en el DataFrame
            busqueda = prompt.lower()
            df_filtered = df[df.astype(str).apply(lambda x: busqueda in x.str.lower().values, axis=1)]
            
            # Filtro por cargo (Columna G)
            df_cargo = df_filtered[df_filtered.iloc[:, 6].str.contains(st.session_state.cargo, na=False, case=False)]

            with st.chat_message("assistant"):
                if not df_cargo.empty:
                    texto_resp = f"Resultados encontrados para tu cargo (**{st.session_state.cargo}**):"
                    st.markdown(texto_resp)
                    st.table(df_cargo)
                    st.session_state.messages.append({"role": "assistant", "content": f"{texto_resp}\n(Tabla mostrada en pantalla)"})
                elif not df_filtered.empty:
                    texto_resp = "No encontré ese término en tu cargo, pero aquí tienes resultados generales:"
                    st.markdown(texto_resp)
                    st.dataframe(df_filtered)
                    st.session_state.messages.append({"role": "assistant", "content": f"{texto_resp}\n(Datos generales mostrados)"})
                else:
                    texto_resp = "Lo siento, no encontré información relacionada. Intenta con una palabra clave diferente."
                    st.markdown(texto_resp)
                    st.session_state.messages.append({"role": "assistant", "content": texto_resp})

    st.markdown('</div>', unsafe_allow_html=True)
