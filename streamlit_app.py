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

# 3. Estilos CSS (Tablas Centradas, Recuadro Rojo, Texto Pequeño)
bin_str = get_base64('TAIYOO.jpg')
logo_html = f'data:image/jpg;base64,{bin_str}' if bin_str else ""

st.markdown(f"""
    <style>
    .block-container {{ padding: 0rem !important; max-width: 100% !important; }}
    .stApp {{ background-color: #000000 !important; color: #FFFFFF !important; }}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .red-banner {{ background-color: #C41230; width: 100vw; height: 120px; display: flex; justify-content: center; align-items: center; margin: 0; padding: 0; }}
    .logo-img {{ max-height: 80px; }}
    .main-title {{ color: #FFFFFF !important; font-family: 'Arial Black', sans-serif; font-size: 42px; text-align: center; margin-top: 20px; width: 100%; }}
    .stMarkdown, .stText, p, h1, h2, h3, span, label, .stSelectbox p {{ color: #FFFFFF !important; }}
    .stChatMessage {{ border-radius: 20px !important; padding: 15px !important; margin-bottom: 15px !important; }}
    [data-testid="stChatMessageAssistant"] {{ background-color: #FFFFFF !important; }}
    [data-testid="stChatMessageAssistant"] p, [data-testid="stChatMessageAssistant"] span {{ color: #000000 !important; }}
    [data-testid="stChatMessageUser"] {{ background-color: #25D366 !important; }}
    [data-testid="stChatMessageUser"] p {{ color: #FFFFFF !important; }}
    .table-container {{ display: flex; justify-content: center; width: 100%; margin: 20px 0; }}
    .styled-table {{ border-collapse: collapse; margin: auto; font-size: 0.8em; font-family: sans-serif; width: 95%; background-color: #1a1a1a; color: white; border: 1px solid #C41230; }}
    .styled-table thead tr {{ background-color: #C41230; color: #ffffff; text-align: center; }}
    .styled-table th, .styled-table td {{ padding: 6px 10px; border: 1px solid #444; text-align: center; white-space: normal !important; word-wrap: break-word; }}
    .content-wrapper {{ padding: 10px 5%; }}
    .stButton>button {{ background-color: #C41230 !important; color: white !important; border-radius: 10px; font-weight: bold; width: 100%; }}
    </style>
    <div class="red-banner"><img src="{logo_html}" class="logo-img"></div>
    <h1 class="main-title">Chatbot SERNISSAN</h1>
    """, unsafe_allow_html=True)

# 4. Memoria y Datos
if "messages" not in st.session_state: st.session_state.messages = []
if "cargo" not in st.session_state: st.session_state.cargo = None

SHEET_URL = "https://docs.google.com/spreadsheets/d/1FcQUNjuHkrK3idDJLtgIxqlXTxEQ-M7n/edit?usp=sharing"
df = load_data(SHEET_URL)

def restart_chat():
    st.session_state.messages = []
    st.session_state.cargo = None

# 5. Interfaz Principal
with st.container():
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    # --- LAS CUATRO CASILLAS DE BÚSQUEDA ---
    col_cargo, col_pgi, col_mv, col_hab = st.columns([1, 1, 1, 1])
    
    if df is not None:
        with col_cargo:
            lista_cargos = extraer_cargos_unicos(df)
            cargo_sel = st.selectbox("CARGO", ["Seleccionar Cargo..."] + lista_cargos, label_visibility="visible")
        with col_pgi:
            opciones_pgi = ["Seleccionar PGI..."] + sorted(df.iloc[:, 0].dropna().unique().astype(str).tolist())
            pgi_input = st.selectbox("N° PGI", opciones_pgi, label_visibility="visible")
        with col_mv:
            opciones_mv = ["Seleccionar MV..."] + sorted(df.iloc[:, 2].dropna().unique().astype(str).tolist())
            mv_input = st.selectbox("MOMENTO DE VERDAD", opciones_mv, label_visibility="visible")
        with col_hab:
            opciones_hab = ["Seleccionar Hábito..."] + sorted(df.iloc[:, 3].dropna().unique().astype(str).tolist())
            hab_input = st.selectbox("N° HÁBITO", opciones_hab, label_visibility="visible")

    # Botón de reinicio pequeño debajo
    if st.button("🔄 REINICIAR CONSULTAS"):
        restart_chat()
        st.rerun()

    # Lógica de detección de filtros
    if df is not None:
        df_final = df.copy()
        aplicar_filtro = False

        if cargo_sel != "Seleccionar Cargo...":
            df_final = df_final[df_final.iloc[:, 6].str.contains(cargo_sel, na=False, case=True)]
            st.session_state.cargo = cargo_sel
            aplicar_filtro = True
        
        if pgi_input != "Seleccionar PGI...":
            df_final = df_final[df_final.iloc[:, 0].astype(str) == pgi_input]
            aplicar_filtro = True
            
        if mv_input != "Seleccionar MV...":
            df_final = df_final[df_final.iloc[:, 2].astype(str) == mv_input]
            aplicar_filtro = True
            
        if hab_input != "Seleccionar Hábito...":
            df_final = df_final[df_final.iloc[:, 3].astype(str) == hab_input]
            aplicar_filtro = True

        if aplicar_filtro and not df_final.empty:
            st.session_state.messages.append({"role": "assistant", "content": "Resultados de búsqueda según filtros seleccionados:", "data": df_final})

    st.write("---")

    # 6. Conversación y Resultados
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "data" in message:
                csv_data = message["data"].to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Descargar tabla para Excel", data=csv_data, file_name='reporte_sernissan.csv', mime='text/csv', key=f"dl_{hash(str(message['data']))}")
                st.markdown(f'<div class="table-container">{message["data"].to_html(index=False, classes="styled-table")}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Escribe una palabra clave para buscar en todo el manual..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        busqueda = prompt.lower()
        df_filtered = df[df.astype(str).apply(lambda x: busqueda in x.str.lower().values, axis=1)]
        
        with st.chat_message("assistant"):
            if not df_filtered.empty:
                st.markdown("Resultados generales de la búsqueda:")
                st.session_state.messages.append({"role": "assistant", "content": "Resultados de búsqueda libre:", "data": df_filtered})
            else:
                st.write("No encontré información con ese término.")

    st.markdown('</div>', unsafe_allow_html=True)
