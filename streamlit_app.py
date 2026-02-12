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

# 3. Estilos CSS (Botones Rojos, Texto Blanco, Tablas Centradas)
bin_str = get_base64('TAIYOO.jpg')
logo_html = f'data:image/jpg;base64,{bin_str}' if bin_str else ""

st.markdown(f"""
    <style>
    .block-container {{ padding: 0rem !important; max-width: 100% !important; }}
    .stApp {{ background-color: #000000 !important; color: #FFFFFF !important; }}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Banner Rojo */
    .red-banner {{ background-color: #C41230; width: 100vw; height: 120px; display: flex; justify-content: center; align-items: center; margin: 0; padding: 0; }}
    .logo-img {{ max-height: 80px; }}
    .main-title {{ color: #FFFFFF !important; font-family: 'Arial Black', sans-serif; font-size: 42px; text-align: center; margin-top: 20px; width: 100%; }}
    
    /* Texto Blanco General */
    .stMarkdown, .stText, p, h1, h2, h3, span, label, .stSelectbox p {{ color: #FFFFFF !important; }}
    
    /* Botones ROJOS con texto BLANCO */
    .stButton>button {{
        background-color: #C41230 !important;
        color: #FFFFFF !important;
        border-radius: 10px;
        border: 1px solid #FFFFFF;
        font-weight: bold;
        width: 100%;
        height: 45px;
    }}
    .stButton>button:hover {{
        background-color: #A00F27 !important;
        border: 1px solid #C41230;
    }}

    /* Estilo de Chat */
    .stChatMessage {{ border-radius: 20px !important; padding: 15px !important; margin-bottom: 15px !important; }}
    [data-testid="stChatMessageAssistant"] {{ background-color: #FFFFFF !important; color: #000000 !important; }}
    [data-testid="stChatMessageAssistant"] p, [data-testid="stChatMessageAssistant"] span {{ color: #000000 !important; }}
    [data-testid="stChatMessageUser"] {{ background-color: #25D366 !important; }}
    
    /* Tabla Centrada y Profesional */
    .table-container {{ display: flex; justify-content: center; width: 100%; margin: 20px 0; }}
    .styled-table {{ border-collapse: collapse; margin: auto; font-size: 0.8em; width: 95%; background-color: #1a1a1a; color: white; border: 1px solid #C41230; }}
    .styled-table thead tr {{ background-color: #C41230; color: #ffffff; text-align: center; }}
    .styled-table th, .styled-table td {{ padding: 6px 10px; border: 1px solid #444; text-align: center; white-space: normal !important; word-wrap: break-word; }}
    
    .content-wrapper {{ padding: 10px 5%; }}
    </style>
    
    <div class="red-banner"><img src="{logo_html}" class="logo-img"></div>
    <h1 class="main-title">Chatbot SERNISSAN</h1>
    """, unsafe_allow_html=True)

# 4. Memoria y Datos
if "messages" not in st.session_state: st.session_state.messages = []

SHEET_URL = "https://docs.google.com/spreadsheets/d/1FcQUNjuHkrK3idDJLtgIxqlXTxEQ-M7n/edit?usp=sharing"
df = load_data(SHEET_URL)

def restart_chat():
    st.session_state.messages = []

# 5. Interfaz Principal
with st.container():
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    # --- BOTÓN ACTUALIZAR ---
    col_up, _ = st.columns([1, 3])
    with col_up:
        if st.button("🔄 ACTUALIZAR TABLA MADRE"):
            restart_chat()
            st.rerun()

    st.write("---")

    # --- LOS 4 FILTROS ---
    col1, col2, col3, col4 = st.columns(4)
    
    if df is not None:
        with col1:
            cargos = extraer_cargos_unicos(df)
            cargo_f = st.selectbox("CARGO", ["Filtrar por Cargo..."] + cargos)
        with col2:
            opciones_pgi = ["Filtrar por PGI..."] + sorted(df.iloc[:, 0].dropna().unique().astype(str).tolist())
            pgi_f = st.selectbox("N° PGI", opciones_pgi)
        with col3:
            opciones_mv = ["Filtrar por MV..."] + sorted(df.iloc[:, 2].dropna().unique().astype(str).tolist())
            mv_f = st.selectbox("MOMENTO DE VERDAD", opciones_mv)
        with col4:
            opciones_hab = ["Filtrar por Hábito..."] + sorted(df.iloc[:, 3].dropna().unique().astype(str).tolist())
            hab_f = st.selectbox("N° HÁBITO", opciones_hab)

    # --- BOTÓN DE BÚSQUEDA ROJO ---
    if st.button("🔍 EJECUTAR BÚSQUEDA FILTRADA"):
        if df is not None:
            res = df.copy()
            activos = []

            if cargo_f != "Filtrar por Cargo...":
                res = res[res.iloc[:, 6].str.contains(cargo_f, na=False, case=True)]
                activos.append(f"Cargo: {cargo_f}")
            if pgi_f != "Filtrar por PGI...":
                res = res[res.iloc[:, 0].astype(str) == pgi_f]
                activos.append(f"PGI: {pgi_f}")
            if mv_f != "Filtrar por MV...":
                res = res[res.iloc[:, 2].astype(str) == mv_f]
                activos.append(f"MV: {mv_f}")
            if hab_f != "Filtrar por Hábito...":
                res = res[res.iloc[:, 3].astype(str) == hab_f]
                activos.append(f"Hábito: {hab_f}")

            if activos:
                if not res.empty:
                    st.session_state.messages.append({"role": "assistant", "content": f"Resultados para: {', '.join(activos)}", "data": res})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": f"Sin resultados para: {', '.join(activos)}"})
            else:
                st.warning("Selecciona al menos un filtro.")

    st.write("---")

    # 6. Chat y Resultados
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if "data" in m:
                csv = m["data"].to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Exportar estos datos a Excel", data=csv, file_name='sernissan_tarija.csv', mime='text/csv', key=f"dl_{hash(str(m['data']))}")
                st.markdown(f'<div class="table-container">{m["data"].to_html(index=False, classes="styled-table")}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("O busca aquí por palabra clave..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        busqueda = prompt.lower()
        df_f = df[df.astype(str).apply(lambda x: busqueda in x.str.lower().values, axis=1)]
        
        with st.chat_message("assistant"):
            if not df_f.empty:
                st.session_state.messages.append({"role": "assistant", "content": f"Resultados de palabra clave '{prompt}':", "data": df_f})
            else:
                st.markdown("No se encontraron coincidencias.")

    st.markdown('</div>', unsafe_allow_html=True)
