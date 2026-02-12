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

# 3. Estilos CSS (WhatsApp Style + UI Personalizada)
bin_str = get_base64('TAIYO.jpg')
logo_html = f'data:image/jpg;base64,{bin_str}' if bin_str else ""

st.markdown(f"""
    <style>
    /* Reset y Fondo */
    .block-container {{ padding: 0rem !important; max-width: 100% !important; }}
    .stApp {{ background-color: #000000; color: #FFFFFF; }}
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

    /* Título Grande Centrado debajo de la franja */
    .main-title {{
        color: #FFFFFF; 
        font-family: 'Arial Black', sans-serif; 
        font-size: 42px; 
        text-align: center;
        margin-top: 20px;
        margin-bottom: 10px;
        width: 100%;
    }}

    /* Burbujas tipo WhatsApp */
    .stChatMessage {{ 
        border-radius: 20px !important; 
        padding: 15px !important;
        margin-bottom: 15px !important;
    }}
    
    /* Asistente: Blanco con texto negro */
    [data-testid="stChatMessageAssistant"] {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #DDD;
    }}
    [data-testid="stChatMessageAssistant"] p, [data-testid="stChatMessageAssistant"] h3 {{ 
        color: #000000 !important; 
    }}

    /* Usuario: Verde WhatsApp con texto blanco */
    [data-testid="stChatMessageUser"] {{
        background-color: #25D366 !important;
        color: #FFFFFF !important;
    }}
    [data-testid="stChatMessageUser"] p {{ 
        color: #FFFFFF !important; 
    }}

    .content-wrapper {{ padding-left: 10%; padding-right: 10%; padding-top: 20px; }}
    
    /* Estilo para inputs y selects en modo oscuro */
    .stSelectbox label, .stTextInput label {{ color: white !important; }}
    </style>
    
    <div class="red-banner">
        <img src="{logo_html}" class="logo-img">
    </div>
    <h1 class="main-title">Chatbot SERNISSAN</h1>
    """, unsafe_allow_html=True)

# 4. Memoria del Chat y Estado
if "messages" not in st.session_state:
    st.session_state.messages = []
if "cargo" not in st.session_state:
    st.session_state.cargo = None

# 5. Carga de Datos
SHEET_URL = "https://docs.google.com/spreadsheets/d/1FcQUNjuHkrK3idDJLtgIxqlXTxEQ-M7n/edit?usp=sharing"
df = load_data(SHEET_URL)

def restart_chat():
    st.session_state.messages = []
    st.session_state.cargo = None

with st.container():
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    # Botón de reinicio en la parte superior derecha (opcional)
    if st.session_state.cargo:
        if st.button("🔄 Cambiar de Cargo / Reiniciar"):
            restart_chat()
            st.rerun()

    # PASO 1: Selección de Cargo
    if st.session_state.cargo is None:
        with st.chat_message("assistant"):
            st.markdown("### Hola. Bienvenida al sistema de gestión Taiyo Motors.\nPara comenzar, por favor indícame: **¿En qué cargo estás?**")
        
        if df is not None:
            # Columna G (Responsables) es índice 6
            lista_cargos = sorted(df.iloc[:, 6].dropna().unique().tolist())
            cargo_sel = st.selectbox("", ["Selecciona un cargo..."] + lista_cargos, label_visibility="collapsed")
            
            if cargo_sel != "Selecciona un cargo...":
                st.session_state.cargo = cargo_sel
                bienvenida = f"Perfecto. He cargado el manual SERNISSAN para el cargo: **{cargo_sel}**.\n\n¿Qué hábito o proceso deseas consultar hoy?"
                st.session_state.messages.append({"role": "assistant", "content": bienvenida})
                st.rerun()
    
    # PASO 2: Conversación Activa
    else:
        # Mostrar historial
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input de chat
        if prompt := st.chat_input("Escribe el número del hábito o palabra clave..."):
            # Guardar y mostrar mensaje del usuario
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Lógica de búsqueda
            busqueda = prompt.lower()
            df_filtered = df[df.astype(str).apply(lambda x: busqueda in x.str.lower().values, axis=1)]
            
            # Filtro por cargo (Columna G)
            df_cargo = df_filtered[df_filtered.iloc[:, 6].str.contains(st.session_state.cargo, na=False, case=False)]

            with st.chat_message("assistant"):
                if not df_cargo.empty:
                    respuesta = f"He encontrado estos hábitos asignados a tu cargo (**{st.session_state.cargo}**):"
                    st.markdown(respuesta)
                    st.table(df_cargo)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta})
                elif not df_filtered.empty:
                    respuesta = "No encontré ese término asignado a tu cargo, pero aquí hay resultados generales del manual:"
                    st.markdown(respuesta)
                    st.dataframe(df_filtered)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta})
                else:
                    respuesta = "Lo siento, no encontré información con ese término. Intenta buscar el número del hábito (ej: 115)."
                    st.markdown(respuesta)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta})

    st.markdown('</div>', unsafe_allow_html=True)
