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

# 3. Estilos CSS (Tablas Centradas, Pequeñas y con Recuadro)
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
    .main-title {{ color: #FFFFFF !important; font-family: 'Arial Black', sans-serif; font-size: 42px; text-align: center; margin-top: 20px; margin-bottom: 5px; width: 100%; }}
    
    .stMarkdown, .stText, p, h1, h2, h3, span, label, .stSelectbox p {{ color: #FFFFFF !important; }}
    .stChatMessage {{ border-radius: 20px !important; padding: 15px !important; margin-bottom: 15px !important; }}
    [data-testid="stChatMessageAssistant"] {{ background-color: #FFFFFF !important; }}
    [data-testid="stChatMessageAssistant"] p, [data-testid="stChatMessageAssistant"] h3, [data-testid="stChatMessageAssistant"] span {{ color: #000000 !important; }}
    [data-testid="stChatMessageUser"] {{ background-color: #25D366 !important; }}
    [data-testid="stChatMessageUser"] p {{ color: #FFFFFF !important; }}

    /* FORMATO DE TABLA CENTRADA Y AJUSTADA */
    .table-container {{
        display: flex;
        justify-content: center;
        width: 100%;
        margin: 20px 0;
    }}
    .styled-table {{
        border-collapse: collapse;
        margin: auto;
        font-size: 0.85em; /* Tamaño reducido para mejor ajuste */
        font-family: sans-serif;
        width: 90%;
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #444;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.05);
    }}
    .styled-table thead tr {{
        background-color: #C41230;
        color: #ffffff;
        text-align: center;
    }}
    .styled-table th, .styled-table td {{
        padding: 8px 12px;
        border: 1px solid #444; /* Recuadro */
        text-align: center;
        white-space: normal !important; /* Ajuste automático de texto */
        word-wrap: break-word;
    }}
    
    .content-wrapper {{ padding-left: 10%; padding-right: 10%; padding-top: 10px; }}
    .stButton>button {{ background-color: #C41230 !important; color: white !important; border-radius: 10px; font-weight: bold; }}
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
    
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        if st.button("Actualizar Datos / Cambiar Cargo"):
            restart_chat()
            st.rerun()

    st.write("---")

    if st.session_state.cargo is None:
        with st.chat_message("assistant"):
            st.markdown("### Hola. Bienvenida al sistema de gestión de Taiyo Motors.\nPara brindarte la información de tu área, por favor selecciona: **¿En qué cargo estás?**")
        
        if df is not None:
            lista_cargos_limpia = extraer_cargos_unicos(df)
            cargo_sel = st.selectbox("Cargos disponibles:", ["Selecciona un cargo..."] + lista_cargos_limpia, label_visibility="collapsed")
            
            if cargo_sel != "Selecciona un cargo...":
                st.session_state.cargo = cargo_sel
                # Filtrado automático al seleccionar cargo
                df_cargo_inicial = df[df.iloc[:, 6].str.contains(cargo_sel, na=False, case=True)]
                
                msj_bienvenida = f"Perfecto. He cargado el manual para el cargo: **{cargo_sel}**."
                st.session_state.messages.append({"role": "assistant", "content": msj_bienvenida})
                
                if not df_cargo_inicial.empty:
                    st.session_state.messages.append({"role": "assistant", "content": "Aquí tienes tus hábitos y procesos asignados:", "data": df_cargo_inicial})
                
                st.rerun()
    
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "data" in message:
                    # Botón para descargar la tabla a Excel (CSV)
                    csv_data = message["data"].to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Descargar esta tabla para Excel", data=csv_data, file_name=f'habitos_{st.session_state.cargo}.csv', mime='text/csv')
                    # Renderizado de tabla con formato HTML
                    st.markdown(f'<div class="table-container">{message["data"].to_html(index=False, classes="styled-table")}</div>', unsafe_allow_html=True)

        if prompt := st.chat_input("Escribe el nombre del proceso o número de hábito..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            busqueda = prompt.lower()
            df_filtered = df[df.astype(str).apply(lambda x: busqueda in x.str.lower().values, axis=1)]
            df_cargo = df_filtered[df_filtered.iloc[:, 6].str.contains(st.session_state.cargo, na=False, case=True)]

            with st.chat_message("assistant"):
                if not df_cargo.empty:
                    texto = f"Resultados para tu cargo (**{st.session_state.cargo}**):"
                    st.markdown(texto)
                    csv_res = df_cargo.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Descargar resultados", data=csv_res, file_name='busqueda_sernissan.csv', mime='text/csv')
                    st.markdown(f'<div class="table-container">{df_cargo.to_html(index=False, classes="styled-table")}</div>', unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": texto, "data": df_cargo})
                elif not df_filtered.empty:
                    texto = "Resultados generales encontrados:"
                    st.markdown(texto)
                    st.markdown(f'<div class="table-container">{df_filtered.to_html(index=False, classes="styled-table")}</div>', unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": texto, "data": df_filtered})
                else:
                    msj = "No encontré información relacionada. Intenta con otra palabra clave."
                    st.markdown(msj)
                    st.session_state.messages.append({"role": "assistant", "content": msj})

    st.markdown('</div>', unsafe_allow_html=True)
