import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from datetime import datetime
# Nota: Para Google Sheets usaremos gspread o st.connection

# Configuración de la IA
genai.configure(api_key="TU_GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📸 Extractor de Cargos - Pro")
procesador = st.text_input("Nombre del Procesador", "Usuario Principal")

# Captura de imagen desde iPhone
foto = st.camera_input("Toma una foto del cargo")

if foto:
    img = Image.open(foto)
    st.image(img, caption="Imagen capturada", width=300)
    
    if st.button("Procesar y Guardar"):
        with st.spinner("La IA está leyendo el documento..."):
            # Prompt específico para tu documento
            prompt = """
            Analiza esta imagen de un 'Cargo de Recepción'. Extrae los siguientes campos en formato texto:
            - Nombre completo del Señor(a)
            - DNI
            - Cargo
            - Mesa de Sufragio
            - Distrito
            - Dirección completa
            - Notas manuscritas (si las hay)
            Responde solo con los datos separados por comas.
            """
            
            response = model.generate_content([prompt, img])
            datos = response.text.split(",") # Simplificación para el ejemplo
            
            # Crear el registro
            nuevo_registro = {
                "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Procesador": procesador,
                "Datos": response.text
            }
            
            # Aquí conectarías con tu Google Sheet
            st.success("¡Datos extraídos con éxito!")
            st.write(response.text)
            
            # Botón para descargar el Excel local si no quieres usar la nube aún
            df = pd.DataFrame([nuevo_registro])
            st.download_button("Descargar Excel Temporal", df.to_csv(), "registro.csv")
