import streamlit as st
import pandas as pd
import base64
import re

st.set_page_config(page_title="APP SerNissan", page_icon="🚗", layout="wide")

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

def extraer_cargos_unicos(columna_df):
    try:
        raw_cargos = columna_df.dropna().unique().tolist()
        cargos_procesados = set()
        for celda in raw_cargos:
            partes = re.split(r',|\sy\s|\.|\n', str(celda))
            for p in partes:
                limpio = p.strip()
                if limpio and len(limpio) > 2:
                    cargos_procesados.add(limpio[0].upper() + limpio[1:])
        return sorted(list(cargos_procesados))
    except: return []

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
    
    /* Estilo de los Botones: Fondo Rojo, Texto Blanco, Borde ROJO */
    .stButton>button {{
        background-color: #C41230 !important;
        color: #FFFFFF !important;
        border-radius: 10px;
        border: 2px solid #C41230 !important; /* BORDE ROJO AQUI */
        font-weight: bold;
        width: 100%;
        height: 45px;
    }}
    .stButton>button:hover {{
        background-color: #A00F27 !important;
        border: 2px solid #FFFFFF !important; /* Borde cambia a blanco al pasar el mouse para feedback visual */
    }}

    .table-container {{ display: flex; justify-content: center; width: 100%; margin: 20px 0; }}
    .styled-table {{ border-collapse: collapse; margin: auto; font-size: 0.8em; width: 95%; background-color: #1a1a1a; color: white; border: 1px solid #C41230; }}
    .styled-table thead tr {{ background-color: #C41230; color: #ffffff; text-align: center; }}
    .styled-table th, .styled-table td {{ padding: 6px 10px; border: 1px solid #444; text-align: center; white-space: normal !important; word-wrap: break-word; }}
    
    .content-wrapper {{ padding: 10px 5%; }}
    .welcome-msg {{ font-size: 20px; font-weight: bold; margin-bottom: 15px; border-left: 5px solid #C41230; padding-left: 15px; }}
    </style>
    
    <div class="red-banner"><img src="{logo_html}" class="logo-img"></div>
    <h1 class="main-title">APP SerNissan</h1>
    """, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1FcQUNjuHkrK3idDJLtgIxqlXTxEQ-M7n/edit?usp=sharing"
df_master = load_data(SHEET_URL)

with st.container():
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    col_up, _ = st.columns([1, 3])
    with col_up:
        if st.button("ACTUALIZAR"):
            st.cache_data.clear()
            st.rerun()

    st.write("---")

    if df_master is not None:
        st.markdown('<p class="welcome-msg">Hola, bienvenido a la app de consultas sobre SerNissan</p>', unsafe_allow_html=True)

        df_temp = df_master.copy()
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            cargos_op = extraer_cargos_unicos(df_master.iloc[:, 6])
            cargo_f = st.selectbox("CARGO", ["Seleccionar..."] + cargos_op)
            if cargo_f != "Seleccionar...":
                df_temp = df_temp[df_temp.iloc[:, 6].str.contains(cargo_f, na=False, case=True)]

        with col2:
            pgi_op = sorted(df_temp.iloc[:, 0].dropna().unique().astype(str).tolist())
            pgi_f = st.selectbox("N° PGI", ["Seleccionar..."] + pgi_op)
            if pgi_f != "Seleccionar...":
                df_temp = df_temp[df_temp.iloc[:, 0].astype(str) == pgi_f]

        with col3:
            mv_op = sorted(df_temp.iloc[:, 2].dropna().unique().astype(str).tolist())
            mv_f = st.selectbox("MOMENTO DE VERDAD", ["Seleccionar..."] + mv_op)
            if mv_f != "Seleccionar...":
                df_temp = df_temp[df_temp.iloc[:, 2].astype(str) == mv_f]

        with col4:
            hab_op = sorted(df_temp.iloc[:, 3].dropna().unique().astype(str).tolist())
            hab_f = st.selectbox("N° HÁBITO", ["Seleccionar..."] + hab_op)
            if hab_f != "Seleccionar...":
                df_temp = df_temp[df_temp.iloc[:, 3].astype(str) == hab_f]

        st.write("")
        
        if st.button("BUSCAR"):
            if cargo_f != "Seleccionar..." or pgi_f != "Seleccionar..." or mv_f != "Seleccionar..." or hab_f != "Seleccionar...":
                if not df_temp.empty:
                    st.success(f"Se encontraron {len(df_temp)} registros.")
                    csv = df_temp.to_csv(index=False).encode('utf-8')
                    st.download_button(label="Exportar", data=csv, file_name='consulta_sernissan.csv', mime='text/csv')
                    st.markdown(f'<div class="table-container">{df_temp.to_html(index=False, classes="styled-table")}</div>', unsafe_allow_html=True)
                else:
                    st.error("No existen datos para la combinación seleccionada.")
            else:
                st.warning("Por favor, selecciona al menos un filtro antes de buscar.")

    st.markdown('</div>', unsafe_allow_html=True)
