import streamlit as st
import pandas as pd
import numpy as np
import re
from io import BytesIO

st.set_page_config(
    page_title="Clasificador Inteligente de Actividades Empresariales",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.15);
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

INVERSION_KEYWORDS = [
    "compra", "adquisición", "adquirir", "construcción", "construir", 
    "remodelación", "remodelar", "adecuación", "adecuar", "mejoramiento", 
    "ampliación", "instalación", "instalar", "implementación", "equipo", 
    "computador", "computadora", "laptop", "servidor", "maquinaria", 
    "vehículo", "automóvil", "herramienta", "activo", "infraestructura", 
    "bodega", "oficina", "tecnología", "sistema", "planta", "inversión"
]

DOCUMENTAL_KEYWORDS = [
    "elaboración", "elaborar", "actualización", "actualizar", "revisión", 
    "revisar", "informe", "procedimiento", "manual", "formato", 
    "política", "registro", "organización", "gestión", "documento", 
    "documental", "acta", "instructivo", "guía", "reporte", "archivo"
]

def classify_activity(text):
    if not isinstance(text, str) or not text.strip():
        return "REVISIÓN MANUAL", 0.0, "Texto vacío o no válido"
    
    text_lower = text.lower()
    
    # Calculate keyword matches with boundary matching
    inv_matches = [kw for kw in INVERSION_KEYWORDS if re.search(r'\b' + kw, text_lower)]
    doc_matches = [kw for kw in DOCUMENTAL_KEYWORDS if re.search(r'\b' + kw, text_lower)]
    
    inv_score = len(set(inv_matches))
    doc_score = len(set(doc_matches))
    
    # Edge case overrides
    if "comprar informe" in text_lower or "adquirir licencia" in text_lower:
        if "licencia" in text_lower:
            return "INVERSIÓN", 0.75, "Adquisición de activo intangible (licencia)"
    
    # Decision logic based on scores
    if inv_score > 0 and doc_score == 0:
        confidence = min(0.65 + (inv_score * 0.12), 0.98)
        return "INVERSIÓN", confidence, f"Términos de inversión detectados: {', '.join(set(inv_matches))}"
    elif doc_score > 0 and inv_score == 0:
        confidence = min(0.65 + (doc_score * 0.12), 0.98)
        return "DOCUMENTAL", confidence, f"Términos documentales detectados: {', '.join(set(doc_matches))}"
    elif inv_score > 0 and doc_score > 0:
        if inv_score > doc_score:
            return "INVERSIÓN", 0.55, "Conflicto de términos, mayor peso en inversión"
        elif doc_score > inv_score:
            return "DOCUMENTAL", 0.55, "Conflicto de términos, mayor peso documental"
        else:
            return "REVISIÓN MANUAL", 0.40, "Conflicto directo entre inversión y documental"
    else:
        return "REVISIÓN MANUAL", 0.20, "Sin palabras clave concluyentes detectadas"

st.sidebar.title("⚙️ Panel de Control")
st.sidebar.info(
    "Sube tu archivo Excel (`.xlsx`) o CSV corporativo con las descripciones de actividades para comenzar el análisis automático."
)

uploaded_file = st.sidebar.file_uploader(
    "Cargar archivo de datos", 
    type=["xlsx", "csv"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Criterios de Clasificación")
st.sidebar.markdown("""
- **INVERSIÓN:** Equipos, infraestructura, construcción, remodelación, maquinaria y activos.
- **DOCUMENTAL:** Informes, manuales, procedimientos, formatos, políticas y gestión de archivos.
- **REVISIÓN MANUAL:** Casos ambiguos o sin términos claros.
""")

st.title("📊 Clasificador Inteligente de Actividades Empresariales")
st.markdown("Clasifica de forma automática tus actividades corporativas en **INVERSIÓN**, **DOCUMENTAL** o **REVISIÓN MANUAL** mediante Procesamiento de Lenguaje Natural (NLP) avanzado.")

if uploaded_file is not None:
    try:
        # Read uploaded file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success(f"¡Archivo '{uploaded_file.name}' cargado exitosamente! ({len(df)} filas encontradas)")
        
        # Column selector
        columns = df.columns.tolist()
        selected_column = st.selectbox(
            "Selecciona la columna que contiene la descripción de las actividades:",
            columns
        )
        
        if st.button("🚀 Analizar y Clasificar Actividades"):
            with st.spinner("Analizando descripciones de actividades..."):
                results = []
                confidences = []
                reasons = []
                
                for item in df[selected_column]:
                    cat, conf, reason = classify_activity(item)
                    results.append(cat)
                    confidences.append(round(conf, 2))
                    reasons.append(reason)
                
                df['Clasificación Automática'] = results
                df['Confianza'] = confidences
                df['Motivo / Detalle'] = reasons
            
            st.toast("¡Clasificación completada con éxito!", icon="✅")
            
            st.markdown("---")
            st.subheader("📈 Resumen Ejecutivo de Resultados")
            
            col1, col2, col3, col4 = st.columns(4)
            total_items = len(df)
            inv_count = (df['Clasificación Automática'] == 'INVERSIÓN').sum()
            doc_count = (df['Clasificación Automática'] == 'DOCUMENTAL').sum()
            rev_count = (df['Clasificación Automática'] == 'REVISIÓN MANUAL').sum()
            
            with col1:
                st.metric("Total Actividades", total_items)
            with col2:
                st.metric("Inversión", f"{inv_count} ({inv_count/total_items*100:.1f}%)")
            with col3:
                st.metric("Documental", f"{doc_count} ({doc_count/total_items*100:.1f}%)")
            with col4:
                st.metric("Revisión Manual", f"{rev_count} ({rev_count/total_items*100:.1f}%)")
            
            st.markdown("---")
            st.subheader("📋 Detalle de Registros Procesados")
            
            filter_option = st.selectbox(
                "Filtrar tabla por categoría:",
                ["Todas", "INVERSIÓN", "DOCUMENTAL", "REVISIÓN MANUAL"]
            )
            
            if filter_option != "Todas":
                filtered_df = df[df['Clasificación Automática'] == filter_option]
            else:
                filtered_df = df
                
            st.dataframe(filtered_df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("💾 Exportar Resultados")
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Clasificacion')
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 Descargar archivo completo en Excel",
                data=processed_data,
                file_name="actividades_clasificadas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.markdown("---")
    st.markdown("### 📥 ¿No tienes un archivo a la mano? Descarga nuestra plantilla de prueba")
    
    sample_data = {
        "ID": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Descripción de la Actividad": [
            "Compra de computadores para el área administrativa.",
            "Construcción de una nueva bodega de almacenamiento.",
            "Elaboración del informe mensual de gestión gerencial.",
            "Actualización del procedimiento de compras y contratación.",
            "Remodelación de oficinas principales del piso 3.",
            "Revisión del manual de procesos de calidad interna.",
            "Adquisición de maquinaria pesada para la nueva planta.",
            "Elaboración de formatos estandarizados de control.",
            "Adecuación de las instalaciones eléctricas.",
            "Reunión de coordinación general de equipo."
        ]
    }
    sample_df = pd.DataFrame(sample_data)
    
    st.dataframe(sample_df, use_container_width=True)
    
    output_sample = BytesIO()
    with pd.ExcelWriter(output_sample, engine='openpyxl') as writer:
        sample_df.to_excel(writer, index=False, sheet_name='Ejemplo')
    sample_bytes = output_sample.getvalue()
    
    st.download_button(
        label="📥 Descargar plantilla de ejemplo (.xlsx)",
        data=sample_bytes,
        file_name="plantilla_actividades_ejemplo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )