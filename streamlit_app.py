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

def extraer_cargos_unicos(df):
    try:
        raw_cargos = df.iloc[:, 6].dropna().unique().tolist()
        cargos_procesados = set()
        for celda in raw_cargos:
            partes = re.split(r',|\sy\s|\.|\n', str(celda))
            for p in partes:
                limpio = p.strip()
                if limpio and len(limpio) > 2:
                    cargos_procesados.add(limpio[0].upper() + limpio[1:])
        return sorted(list(cargos_procesados))
    except Exception as e:
        return [f"Error al procesar cargos: {e}"]

# 3. Estilos CSS (Tablas con Recuadro y Texto Ajustado)
bin_str = get_base64('TAIYOO.jpg')
logo_html = f'data:image/jpg;base64,{bin_str}' if bin_str else ""

st.markdown(f"""
    <style>
    /* Reset y Fondo */
    .block-container {{ padding: 0rem !important; max-width: 100% !important; }}
    .stApp {{ background-color: #000000 !important; color: #FFFFFF !important; }}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Encabezado Institucional */
    .red-banner {{ background-color: #C41230; width: 100vw; height: 120px; display: flex; justify-content: center; align-items: center; margin: 0; padding: 0; }}
    .logo-img {{ max-height: 80px; }}
    .main-title {{ color: #FFFFFF !important; font-family: 'Arial Black', sans-serif; font-size: 42px; text-align: center; margin-top: 20px; margin-bottom: 5px; width: 100%; }}
    
    /* Texto General */
    .stMarkdown, .stText, p, h1, h2, h3, span, label, .stSelectbox p {{ color: #FFFFFF !important; }}
    
    /* Burbujas de Chat */
    .stChatMessage {{ border-radius: 20px !important; padding: 15px !important; margin-bottom: 15px !important; }}
    [data-testid="stChatMessageAssistant"] {{ background-color: #FFFFFF !important; color: #000000 !important; }}
    [data-testid="stChatMessageAssistant"] p, [data-testid="stChatMessageAssistant"] span {{ color: #000000 !important; }}
    [data-testid="stChatMessageUser"] {{ background-color: #25D366 !important; }}
    [data-testid="stChatMessageUser"] p {{ color: #FFFFFF !important; }}

    /* DISEÑO DE TABLA CON RECUADRO Y AJUSTE DE TEXTO */
    .styled-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 0.9em;
        font-family: sans-serif;
        min-width: 400px;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #C41230; /* Borde rojo Taiyo */
    }}
    .styled-table thead tr {{
        background-color: #C41230;
        color: #ffffff;
        text-align: left;
    }}
    .styled-table th, .styled-table td {{
        padding: 12px 15px;
        border: 1px solid #444; /* Líneas de recuadro */
        white-space: normal !important; /* Ajuste automático de texto */
        word-wrap: break-word;
    }}
    .content-wrapper {{ padding: 20px 10%; }}
    .stButton>button {{ background-color: #C41230 !important; color: white !important; border-radius: 10px; font-weight: bold; }}
    </style>
    
    <div class="red-banner"><img src="{logo_html}" class="logo-img"></div>
    <h1 class="main-title">Chatbot SERNISSAN</h1>
    """, unsafe_allow_html=True)

# 4. Memoria y Datos
if "messages" not in st.session_state: st.session_state.messages = []
if "cargo" not in st.session_state: st.session_state.cargo = None

SHEET_URL = "https://docs.google.com/spreadsheets/d/1FcQUNjuHkrK3idDJLtgIxqlXTxEQ-0M7n/edit?usp=sharing"
df = load_data(SHEET_URL)

def restart_chat():
    st.session_state.messages = []
    st.session_state.cargo = None

# 5. Estructura Principal
with st.container():
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    if st.button("🔄 Actualizar / Cambiar Cargo"):
        restart_chat()
        st.rerun()

    st.write("---")

    if st.session_state.cargo is None:
        with st.chat_message("assistant"):
            st.markdown("### Hola. Bienvenida al portal de procesos Taiyo Motors.\nSelecciona tu cargo para visualizar tus hábitos:")
        
        if df is not None:
            cargos = extraer_cargos_unicos(df)
            cargo_sel = st.selectbox("Cargos:", ["Selecciona..."] + cargos, label_visibility="collapsed")
            
            if cargo_sel != "Selecciona...":
                st.session_state.cargo = cargo_sel
                # Filtro inicial por cargo
                df_inicial = df[df.iloc[:, 6].str.contains(cargo_sel, na=False, case=True)]
                
                st.session_state.messages.append({"role": "assistant", "content": f"Acceso concedido para: **{cargo_sel}**."})
                if not df_inicial.empty:
                    st.session_state.messages.append({"role": "assistant", "content": "Tus responsabilidades asignadas:", "data": df_inicial})
                st.rerun()
    
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
                if "data" in m:
                    # Renderizamos la tabla con HTML personalizado para control total del formato
                    st.markdown(m["data"].to_html(index=False, classes="styled-table"), unsafe_allow_html=True)

        if prompt := st.chat_input("Busca un hábito o palabra clave..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            busqueda = prompt.lower()
            df_filtered = df[df.astype(str).apply(lambda x: busqueda in x.str.lower().values, axis=1)]
            df_cargo = df_filtered[df_filtered.iloc[:, 6].str.contains(st.session_state.cargo, na=False, case=True)]

            with st.chat_message("assistant"):
                if not df_cargo.empty:
                    st.markdown(f"Resultados para **{st.session_state.cargo}**:")
                    st.markdown(df_cargo.to_html(index=False, classes="styled-table"), unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": "Resultados filtrados:", "data": df_cargo})
                else:
                    st.markdown("No encontré coincidencias específicas. Intenta con otra palabra.")
    
    st.markdown('</div>', unsafe_allow_html=True)
