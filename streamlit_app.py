import streamlit as st
import pandas as pd
import base64

# 1. Configuración de la página (Layout total)
st.set_page_config(page_title="Chat SERNISSAN", page_icon="🚗", layout="wide")

# 2. Funciones de Apoyo (Imagen y Datos)
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except: return None

@st.cache_data(ttl=0) # ttl=0 asegura que si editas el Excel, el chat vea el cambio al refrescar
def load_data(sheet_url):
    try:
        # Transformamos el link para lectura directa sin perder el formato online
        csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')
        df = pd.read_csv(csv_url)
        return df
    except: return None

# 3. Estilos CSS (Fondo Negro, Franja de esquina a esquina, Texto Blanco)
bin_str = get_base64('TAIYO.jpg')
logo_html = f'data:image/jpg;base64,{bin_str}' if bin_str else ""

st.markdown(f"""
    <style>
    .block-container {{ padding: 0rem !important; max-width: 100% !important; }}
    .stApp {{ background-color: #000000; color: #FFFFFF; }}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    .red-banner {{
        background-color: #C41230; 
        width: 100vw; height: 140px;
        display: flex; justify-content: center; align-items: center;
        margin: 0; padding: 0;
    }}
    .logo-img {{ max-height: 90px; }}
    .content-wrapper {{ padding: 2.5rem; color: white; }}
    
    /* Estilo de burbujas de chat */
    .stChatMessage {{ background-color: #1A1A1A !important; border-radius: 15px; padding: 10px; margin-bottom: 10px; }}
    </style>
    
    <div class="red-banner">
        <img src="{logo_html}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)

# 4. Inicialización de sesión (Memoria del Chat)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "cargo" not in st.session_state:
    st.session_state.cargo = None

# --- CARGA DE DATOS ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1FcQUNjuHkrK3idDJLtgIxqlXTxEQ-M7n/edit?usp=sharing"
df = load_data(SHEET_URL)

with st.container():
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    # 5. PASO 1: Preguntar el Cargo (Solo si no se ha seleccionado)
    if st.session_state.cargo is None:
        st.chat_message("assistant").write("Hola. Para darte una atención personalizada de SERNISSAN, por favor dime: **¿En qué cargo estás?**")
        
        if df is not None:
            # Extraemos cargos únicos de la Columna G (Responsables)
            # Nota: Asumimos que la Columna G es la 7ma columna (index 6) o se llama 'Responsables'
            try:
                lista_cargos = sorted(df.iloc[:, 6].dropna().unique().tolist())
                cargo_seleccionado = st.selectbox("Selecciona tu cargo de la lista:", [""] + lista_cargos)
                
                if cargo_seleccionado != "":
                    st.session_state.cargo = cargo_seleccionado
                    st.session_state.messages.append({"role": "assistant", "content": f"Perfecto. He configurado el sistema para el cargo: **{cargo_seleccionado}**."})
                    st.rerun()
            except:
                st.error("No se pudo leer la columna de responsables. Revisa la estructura del Excel.")
    
    # 6. PASO 2: Interfaz de Chat (Solo aparece tras elegir cargo)
    else:
        # Mostrar historial de mensajes
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input del usuario
        if prompt := st.chat_input("Escribe el número de hábito o proceso que buscas..."):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Lógica de búsqueda en el DataFrame
            # Filtramos por el cargo seleccionado Y por el término buscado
            busqueda = prompt.lower()
            df_filtered = df[df.astype(str).apply(lambda x: busqueda in x.str.lower().values, axis=1)]
            
            # Priorizamos mostrar los que corresponden a su cargo
            df_cargo = df_filtered[df_filtered.iloc[:, 6].str.contains(st.session_state.cargo, na=False, case=False)]

            with st.chat_message("assistant"):
                if not df_cargo.empty:
                    st.markdown(f"He encontrado estos hábitos específicos para tu rol como **{st.session_state.cargo}**:")
                    st.table(df_cargo)
                elif not df_filtered.empty:
                    st.markdown("Encontré información, aunque no parece estar asignada directamente a tu cargo:")
                    st.dataframe(df_filtered)
                else:
                    st.markdown("Lo siento, no encontré información con ese término en el manual SERNISSAN.")
            
            st.session_state.messages.append({"role": "assistant", "content": "Resultados de búsqueda mostrados."})

    st.markdown('</div>', unsafe_allow_html=True)
