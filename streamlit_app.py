import streamlit as st
import pandas as pd
import base64

# Configuración de la página
st.set_page_config(page_title="Chatbot SERNISSAN", page_icon="🚗", layout="wide")

# Función para convertir imagen local a Base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- ESTILOS PERSONALIZADOS (CSS) ---
# Intentamos cargar el logo, si no existe todavía, usamos un placeholder
try:
    bin_str = get_base64_of_bin_file('TAIYOO.jpg')
    logo_html = f'data:image/jpg;base64,{bin_str}'
except FileNotFoundError:
    logo_html = "" # Se mantiene vacío hasta que subas el archivo

st.markdown(f"""
    <style>
    /* Eliminar espacios en blanco superiores */
    .block-container {{
        padding-top: 0rem;
        padding-bottom: 0rem;
    }}
    
    .stAppHeader {{
        display: none;
    }}

    /* Franja Roja Superior */
    .red-banner {{
        background-color: #C41230; /* Rojo Oficial Taiyo Motors */
        width: 100%;
        height: 150px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }}

    .logo-img {{
        max-height: 100px;
    }}
    </style>
    
    <div class="red-banner">
        <img src="{logo_html}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)

# --- ROBOT DE BIENVENIDA ---
col1, col2 = st.columns([1, 5])

with col1:
    st.write("") # Espaciador
    st.title("🤖") 

with col2:
    st.subheader("¡Bienvenido al Chatbot de SERNISSAN!")
    st.info("Hola, soy tu asistente virtual de mejora continua. Estoy aquí para ayudarte a consultar los hábitos y KPIs de gestión.")

# --- EXTRACCIÓN DE DATOS ---
sheet_id = "1FcQUNjuHkrK3idDJLtgIxqlXTxEQ-M7n"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error al conectar con la tabla: {e}")
        return None

df = load_data()

# --- LÓGICA DEL CHAT ---
if df is not None:
    st.success("Base de datos de hábitos SERNISSAN cargada correctamente.")
    
    # Campo de búsqueda para el usuario
    busqueda = st.text_input("Escribe el número del hábito o una palabra clave (ej. '115' o 'limpieza'):")
    
    if busqueda:
        # Filtrar en la columna 'Hábito' o 'Nº Hábito' (Ajustar según nombres exactos de tu tabla)
        resultado = df[df.astype(str).apply(lambda x: busqueda.lower() in x.str.lower().values, axis=1)]
        
        if not resultado.empty:
            st.write("### Resultados encontrados:")
            st.dataframe(resultado)
        else:
            st.warning("No encontré información relacionada con esa búsqueda.")
else:
    st.warning("Por favor, verifica que el Google Sheet tenga acceso público.")
