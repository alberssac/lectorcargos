import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image
import pandas as pd
from datetime import datetime
import json

# 1. Configuración de página e Icono
st.set_page_config(page_title="Scanner Cargos", page_icon="📸")

st.write("### Modelos disponibles para tu API Key:")

# Esta es la función que pide el error:
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        st.write(f"Nombre: `{m.name}`")

# 2. Configuración de la IA (Solución al error 404)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Usamos la versión estable del modelo
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")
# 3. Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📸 Extractor de Cargos")
procesador = st.text_input("Procesado por:", "Usuario")

# 4. Selección de origen (GALERÍA POR DEFECTO)
opcion = st.radio("Origen de imagen:", ["Galería/Archivos", "Cámara"], horizontal=True)

if opcion == "Galería/Archivos":
    foto = st.file_uploader("Selecciona el cargo desde tus fotos", type=["jpg", "jpeg", "png"])
else:
    foto = st.camera_input("Toma la foto con la cámara")

if foto:
    img = Image.open(foto)
    st.image(img, caption="Imagen cargada", width=300)
    
    if st.button("🚀 Procesar y Guardar"):
        with st.spinner("Leyendo datos con IA..."):
            try:
                # Instrucciones precisas para Perú
                prompt = """
                Analiza este 'Cargo de Recepción'. Extrae los datos y responde 
                SOLO con un objeto JSON con estas llaves:
                "Nombre", "DNI", "Cargo", "Mesa", "Distrito", "Direccion", "Notas".
                Si no ves algo, pon "N/A".
                """
                
                # Generar contenido
                response = model.generate_content([prompt, img])
                
                # Limpiar la respuesta (quitar ```json si la IA los pone)
                res_text = response.text.replace('```json', '').replace('```', '').strip()
                datos_json = json.loads(res_text)
                
                # 5. Guardar en Google Sheets
                # IMPORTANTE: Verifica que tu hoja se llame "Sheet1" o cámbialo aquí
                df_existente = conn.read(worksheet="Sheet1")
                
                nuevo_registro = {
                    "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Procesador": procesador,
                    "Nombre": datos_json.get("Nombre", "N/A"),
                    "DNI": datos_json.get("DNI", "N/A"),
                    "Cargo": datos_json.get("Cargo", "N/A"),
                    "Mesa": datos_json.get("Mesa", "N/A"),
                    "Distrito": datos_json.get("Distrito", "N/A"),
                    "Direccion": datos_json.get("Direccion", "N/A"),
                    "Notas": datos_json.get("Notas", "N/A")
                }
                
                df_final = pd.concat([df_existente, pd.DataFrame([nuevo_registro])], ignore_index=True)
                conn.update(worksheet="Sheet1", data=df_final)
                
                st.success("✅ ¡Guardado en Google Sheets!")
                st.json(datos_json)
                st.balloons()
                
            except Exception as e:
                st.error(f"Detalle técnico: {e}")
