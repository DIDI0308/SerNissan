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

# 3. Estilos CSS (Estética WhatsApp + Marca Taiyo)
bin_str = get_base64('TAIYO.jpg')
logo_html = f'data:image/jpg;base64,{bin_str}' if bin_str else ""

st.markdown(f"""
    <style>
    /* Reset de márgenes */
    .block-container {{ padding: 0rem !important; max-width: 100% !important; }}
    .stApp {{ background-color: #000000; }}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Encabezado */
    .red-banner {{
        background-color: #C41230; 
        width: 100vw; height: 140px;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        margin: 0; padding: 0;
    }}
    .logo-img {{ max-height: 70px; margin-bottom: 5px; }}
    .main-title {{
        color: white; font-family: 'Arial'; font-weight: bold; font-size: 24px; margin: 0;
    }}

    /* Estilo tipo WhatsApp */
    .stChatMessage {{ 
        border-radius: 15px !important; 
        padding: 15px !important;
        margin-bottom: 15px !important;
        max-width: 80%;
    }}
    
    /* Burbuja del Asistente (Blanca con texto negro) */
    [data-testid="stChatMessageAssistant"] {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        margin-right: auto;
    }}
    [data-testid="stChatMessageAssistant"] p {{ color: #000000 !important; }}

    /* Burbuja del Usuario (Verde WhatsApp) */
    [data-testid="stChatMessageUser"] {{
        background-color: #25D366 !important;
        color: #FFFFFF !important;
        margin-left: auto;
    }}
    [data-testid="stChatMessageUser"] p {{ color: #FFFFFF !important; }}

    .content-wrapper {{ padding: 2rem; }}
    
    /* Ajuste de tablas en modo oscuro */
    .stTable {{ background-color: #1A1A1A; border-radius: 10px; }}
    </style>
    
    <div class="red-banner">
        <img src="{logo_html}" class="logo-img">
        <p class="main-title">Chatbot SERNISSAN</p>
    </div>
    """, unsafe_allow_html=True)

# 4. Memoria del Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "cargo" not in st.session_state:
    st.session_state.cargo = None

# 5. Carga de Datos Online
SHEET_URL = "https://docs.google.com/spreadsheets/d/1FcQUNjuHkrK3idDJLtgIxqlXTxEQ-M7n/edit?usp=sharing"
df = load_data(SHEET_URL)

with st.container():
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    # PASO 1: Selección de Cargo
    if st.session_state.cargo is None:
        with st.chat_message("assistant"):
            st.markdown("Hola. Bienvenido al portal de Excelencia Nissan. **¿En qué cargo estás?**")
        
        if df is not None:
            # Columna G (Responsables) es el índice 6
            lista_cargos = sorted(df.iloc[:, 6].dropna().unique().tolist())
            cargo_sel = st.selectbox("Elige tu cargo para filtrar los hábitos:", [""] + lista_cargos)
            
            if cargo_sel != "":
                st.session_state.cargo = cargo_sel
                st.session_state.messages.append({"role": "assistant", "content": f"Entendido. Mostrando información para: **{cargo_sel}**. ¿Qué hábito o proceso deseas consultar hoy?"})
                st.rerun()
    
    # PASO 2: Interfaz de Chat Estilo WhatsApp
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Escribe el nombre del proceso o número de hábito..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Búsqueda en vivo
            busqueda = prompt.lower()
            df_filtered = df[df.astype(str).apply(lambda x: busqueda in x.str.lower().values, axis=1)]
            
            # Filtro por cargo
            df_cargo = df_filtered[df_filtered.iloc[:, 6].str.contains(st.session_state.cargo, na=False, case=False)]

            with st.chat_message("assistant"):
                if not df_cargo.empty:
                    st.markdown(f"Aquí tienes los detalles encontrados para tu rol:")
                    st.table(df_cargo)
                elif not df_filtered.empty:
                    st.markdown("Encontré coincidencias generales en el manual (fuera de tu cargo asignado):")
                    st.dataframe(df_filtered)
                else:
                    st.markdown("No encontré información relacionada en el manual SERNISSAN. Intenta con otra palabra clave.")
            
            st.session_state.messages.append({"role": "assistant", "content": "Búsqueda finalizada."})

    st.markdown('</div>', unsafe_allow_html=True)
