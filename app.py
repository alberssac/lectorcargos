import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image
import pandas as pd
from datetime import datetime
import json

# 1. Configuración de la página e Icono
st.set_page_config(page_title="Scanner Cargos", page_icon="📸")

# 2. Configuración de API (asegúrate de tener GEMINI_API_KEY en Secrets)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

# 3. Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📸 Extractor de Cargos")
procesador = st.text_input("Procesado por:", "Usuario")

# 4. Selección de origen
opcion = st.radio("Origen de imagen:", ["Cámara", "Galería/Archivos"], horizontal=True)

if opcion == "Cámara":
    foto = st.camera_input("Toma la foto")
else:
    foto = st.file_uploader("Sube el archivo", type=["jpg", "jpeg", "png"])

if foto:
    # Mostramos una previsualización
    img = Image.open(foto)
    st.image(img, caption="Imagen cargada", width=300)
    
    if st.button("🚀 Procesar y Guardar"):
        with st.spinner("Leyendo datos..."):
            try:
                # EL FIX: Convertimos la imagen a un formato que Gemini acepte sin errores
                prompt = """
                Analiza este 'Cargo de Recepción' peruano.
                Extrae: Nombre, DNI, Cargo, Mesa, Distrito, Direccion, Notas.
                Responde únicamente con un objeto JSON. Si no encuentras un dato, pon 'No detectado'.
                """
                
                # Enviamos la imagen directamente
                response = model.generate_content([prompt, img])
                
                # Limpiamos la respuesta para obtener el JSON
                texto_respuesta = response.text.replace('```json', '').replace('```', '').strip()
                datos_json = json.loads(texto_respuesta)
                
                # 5. Guardar en Google Sheets
                # Leemos lo que ya existe
                df_existente = conn.read(worksheet="Sheet1") # Ajusta al nombre de tu hoja
                
                # Creamos la nueva fila
                nuevo_registro = {
                    "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Procesador": procesador,
                    "Nombre": datos_json.get("Nombre"),
                    "DNI": datos_json.get("DNI"),
                    "Cargo": datos_json.get("Cargo"),
                    "Mesa": datos_json.get("Mesa"),
                    "Distrito": datos_json.get("Distrito"),
                    "Direccion": datos_json.get("Direccion"),
                    "Notas": datos_json.get("Notas")
                }
                
                # Concatenamos y actualizamos
                df_final = pd.concat([df_existente, pd.DataFrame([nuevo_registro])], ignore_index=True)
                conn.update(worksheet="Sheet1", data=df_final)
                
                st.success("✅ Guardado en Google Sheets con éxito")
                st.json(datos_json) # Muestra lo que leyó
                st.balloons()
                
            except Exception as e:
                st.error(f"Hubo un detalle: {e}")
                st.info("Tip: Asegúrate de que la foto sea clara y que el API Key esté bien configurado.")
