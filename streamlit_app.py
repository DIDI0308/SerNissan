import streamlit as st
import pandas as pd
import base64

# Configuración de la página (Debe ser la primera instrucción de Streamlit)
st.set_page_config(page_title="Chatbot SERNISSAN", page_icon="🚗", layout="wide")

# Función para convertir imagen local a Base64
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# --- ESTILOS PERSONALIZADOS (CSS) ---
bin_str = get_base64_of_bin_file('TAIYO.jpg')
logo_html = f'data:image/jpg;base64,{bin_str}' if bin_str else ""

st.markdown(f"""
    <style>
    /* 1. Eliminar márgenes y paddings de Streamlit para que la franja sea de esquina a esquina */
    .block-container {{
        padding: 0rem 0rem 0rem 0rem !important;
        max-width: 100% !important;
    }}
    
    .stApp {{
        background-color: #000000; /* Fondo Negro */
        color: #FFFFFF; /* Texto Blanco por defecto */
    }}

    /* 2. Ocultar el encabezado por defecto de Streamlit */
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* 3. Franja Roja Superior de esquina a esquina */
    .red-banner {{
        background-color: #C41230; /* Rojo Oficial Taiyo Motors */
        width: 100vw;
        height: 160px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0;
        padding: 0;
    }}

    .logo-img {{
        max-height: 110px;
        width: auto;
    }}

    /* 4. Estilos de texto para modo oscuro */
    h1, h2, h3, p, span, label {{
        color: #FFFFFF !important;
    }}

    /* Estilo para el contenedor del contenido debajo de la franja */
    .content-wrapper {{
        padding: 2rem;
    }}
    </style>
    
    <div class="red-banner">
        <img src="{logo_html}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)

# Contenedor para el resto del contenido con margen lateral
with st.container():
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    # --- ROBOT DE BIENVENIDA ---
    col1, col2 = st.columns([1, 5])
    with col1:
        st.write("") 
        st.title("🤖") 
    with col2:
        st.subheader("¡Bienvenido al Chatbot de SERNISSAN!")
        st.write("Hola, soy tu asistente virtual de mejora continua. Estoy aquí para ayudarte a consultar los hábitos y KPIs de gestión.")

    # --- EXTRACCIÓN DE DATOS ---
    sheet_id = "1FcQUNjuHkrK3idDJLtgIxqlXTxEQ-M7n"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

    @st.cache_data
    def load_data():
        try:
            df = pd.read_csv(url)
            return df
        except Exception as e:
            return None

    df = load_data()

    # --- LÓGICA DEL CHAT ---
    if df is not None:
        st.markdown("---")
        busqueda = st.text_input("Escribe el número del hábito o una palabra clave:")
        
        if busqueda:
            resultado = df[df.astype(str).apply(lambda x: busqueda.lower() in x.str.lower().values, axis=1)]
            if not resultado.empty:
                st.write("### Resultados encontrados:")
                st.dataframe(resultado)
            else:
                st.warning("No encontré información relacionada.")
    else:
        st.error("Error al cargar la base de datos. Revisa el acceso al Google Sheet.")
    
    st.markdown('</div>', unsafe_allow_html=True)
