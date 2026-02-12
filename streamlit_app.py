import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Chatbot SERNISSAN", page_icon="🚗", layout="wide")

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stAppHeader {
        background-color: #C41230; /* Rojo Taiyo Motors */
        height: 120px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        background-color: #C41230;
        padding: 20px;
    }
    .welcome-text {
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        color: #333;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO CON FRANJA ROJA Y LOGO ---
# Nota: He usado la URL directa de la imagen que subiste para el logo
st.markdown("""
    <div class="logo-container">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Taiyo_Motors_Logo.png/400px-Taiyo_Motors_Logo.png" width="120">
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- ROBOT DE BIENVENIDA ---
col1, col2 = st.columns([1, 4])

with col1:
    st.markdown("🤖") # Puedes reemplazar por una imagen de un robot si prefieres

with col2:
    st.subheader("¡Bienvenido al Chatbot de SERNISSAN!")
    st.write("Hola, soy tu asistente virtual de mejora continua. Estoy aquí para ayudarte a consultar los hábitos y KPIs de gestión.")

# --- EXTRACCIÓN DE DATOS ---
# Convertimos el link de Google Sheets a formato de exportación CSV para pandas
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

# --- ESPACIO PARA EL CHAT ---
if df is not None:
    st.success("Base de datos de hábitos SERNISSAN cargada correctamente.")
    # Aquí irá la lógica de consulta que programaremos después
else:
    st.warning("Asegúrate de que el Google Sheet tenga acceso 'Cualquier persona con el enlace'.")
