import streamlit as st
import pandas as pd
import base64
import re

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

# Función para limpiar y separar cargos únicos
def extraer_cargos_unicos(df):
    try:
        # Seleccionamos la columna G (índice 6)
        columna_responsables = df.iloc[:, 6].dropna().astype(str)
        
        cargos_set = set()
        for celda in columna_responsables:
            # Reemplazamos la "y" por una coma para estandarizar el separador
            # Luego separamos por comas o puntos
            partes = re.split(r',|\sy\s|\.', celda)
            for p in partes:
                limpio = p.strip().capitalize() # Limpiamos espacios y estandarizamos
                if limpio and len(limpio) > 3: # Evitamos textos vacíos o muy cortos
                    cargos_set.add(limpio)
        
        return sorted(list(cargos_set))
    except:
        return ["Error al leer cargos"]

# 3. Estilos CSS (WhatsApp Style + Modo Oscuro)
bin_str = get_base64('TAIYO.jpg')
logo_html = f'data:image/jpg;base64,{bin_str}' if bin_str else ""

st.markdown(f"""
    <style>
    .block-container {{ padding: 0rem !important; max-width: 100% !important; }}
    .stApp {{ background-color: #000000 !important; color: #FFFFFF !important; }}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    .red-banner {{
        background-color: #C41230; 
        width: 100vw; height: 120px;
        display: flex; justify-content: center; align-items: center;
        margin: 0; padding: 0;
    }}
    .logo-img {{ max-height: 80px; }}
    .main-title {{
        color: #FFFFFF !important; font-family: 'Arial Black'; font-size: 42px; 
        text-align: center; margin-top: 20px;
    }}

    /* Burbujas de Chat */
    [data-testid="stChatMessageAssistant"] {{ background-color: #FFFFFF !important; color: #000000 !important; }}
    [data-testid="stChatMessageAssistant"] p {{ color: #000000 !important; }}
    [data-testid="stChatMessageUser"] {{ background-color: #25D366 !important; color: #FFFFFF !important; }}
    
    .content-wrapper {{ padding: 2rem 10%; }}
    .stButton>button {{ background-color: #C41230 !important; color: white !important; }}
    </style>
    
    <div class="red-banner">
        <img src="{logo_html}" class="logo-img">
    </div>
    <h1 class="main-title">Chatbot SERNISSAN</h1>
    """, unsafe_allow_html=True)

# 4. Inicialización y Carga
if "messages" not in st.session_state: st.session_state.messages = []
if "cargo" not in st.session_state: st.session_state.cargo = None

SHEET_URL = "https://docs.google.com/spreadsheets/d/1FcQUNjuHkrK3idDJLtgIxqlXTxEQ-M7n/edit?usp=sharing"
df = load_data(SHEET_URL)

def restart_chat():
    st.session_state.messages = []
    st.session_state.cargo = None

# 5. Interfaz
with st.container():
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    if st.session_state.cargo:
        if st.button("🔄 Cambiar de Cargo"):
            restart_chat()
            st.rerun()

    if st.session_state.cargo is None:
        with st.chat_message("assistant"):
            st.markdown("### Hola. Bienvenida a Taiyo Motors.\nPor favor, selecciona tu cargo específico:")
        
        if df is not None:
            cargos_limpios = extraer_cargos_unicos(df)
            cargo_sel = st.selectbox("", ["Selecciona..."] + cargos_limpios, label_visibility="collapsed")
            
            if cargo_sel != "Selecciona...":
                st.session_state.cargo = cargo_sel
                msj = f"Configurado para: **{cargo_sel}**. ¿Qué proceso deseas consultar?"
                st.session_state.messages.append({"role": "assistant", "content": msj})
                st.rerun()
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Escribe el hábito o palabra clave..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            # Búsqueda
            busqueda = prompt.lower()
            mask = df.astype(str).apply(lambda x: busqueda in x.str.lower().values, axis=1)
            df_filtered = df[mask]
            
            # Filtro por cargo seleccionado en la columna de responsables
            df_cargo = df_filtered[df_filtered.iloc[:, 6].str.contains(st.session_state.cargo, na=False, case=False)]

            with st.chat_message("assistant"):
                if not df_cargo.empty:
                    st.table(df_cargo)
                elif not df_filtered.empty:
                    st.markdown("Resultados generales fuera de tu cargo:")
                    st.dataframe(df_filtered)
                else:
                    st.markdown("No hay resultados. Intenta con otra palabra.")

    st.markdown('</div>', unsafe_allow_html=True)
