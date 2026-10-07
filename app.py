import streamlit as st
import pandas as pd
import numpy as np
import re
import unicodedata
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

# ============================================================
# NORMALIZACIÓN DEL TEXTO
# ============================================================

def normalizar_texto(texto):
    if texto is None:
        return ""

    texto = str(texto).lower().strip()

    # Eliminar HTML
    texto = re.sub(r"<[^>]+>", " ", texto)

    # Quitar tildes
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

    # Normalizar espacios
    texto = re.sub(r"\s+", " ", texto)

    return texto


# ============================================================
# PALABRAS / EXPRESIONES DE INVERSIÓN
# ============================================================

VERBOS_INVERSION = [
    r"\breparar\b",
    r"\breparacion\b",
    r"\breparaciones\b",
    r"\breemplazar\b",
    r"\breemplazo\b",
    r"\bcambiar\b",
    r"\bcambio\b",
    r"\bsustituir\b",
    r"\bsustitucion\b",
    r"\binstalar\b",
    r"\binstalacion\b",
    r"\bmontar\b",
    r"\bmontaje\b",
    r"\bconstruir\b",
    r"\bconstruccion\b",
    r"\badecuar\b",
    r"\badecuacion\b",
    r"\bremodelar\b",
    r"\bremodelacion\b",
    r"\breubicar\b",
    r"\breubicacion\b",
    r"\bretirar\b",
    r"\bderribar\b",
    r"\bfabricar\b",
    r"\bfabricacion\b",
    r"\badquirir\b",
    r"\badquisicion\b",
    r"\bcomprar\b",
    r"\bcompra\b",
    r"\bsuministrar\b",
    r"\bsuministro\b",
    r"\bimplementar\b"
]


OBJETOS_INVERSION = [
    r"\bequipo(s)?\b",
    r"\bmaquina(s)?\b",
    r"\bmaquinaria\b",
    r"\binfraestructura\b",
    r"\bpiso(s)?\b",
    r"\bbaldosa(s)?\b",
    r"\bpared(es)?\b",
    r"\btecho(s)?\b",
    r"\bpuerta(s)?\b",
    r"\bpuerta tipo cortina\b",
    r"\bcortina(s)?\b",
    r"\btecho\b",
    r"\blamina(s)?\b",
    r"\bluminaria(s)?\b",
    r"\blampara(s)?\b",
    r"\bacrilico\b",
    r"\bacrilicos\b",
    r"\btanque(s)?\b",
    r"\bfiltro(s)?\b",
    r"\biman(es)?\b",
    r"\bisocubo(s)?\b",
    r"\bcontenedor(es)?\b",
    r"\bestiba(s)?\b",
    r"\bescalera(s)?\b",
    r"\bdrenaje(s)?\b",
    r"\bcanal(es)?\b",
    r"\btecho\b",
    r"\brecubrimiento\b",
    r"\bpintura sanitaria\b",
    r"\brecubrimiento anticorrosivo\b",
    r"\baire acondicionado\b",
    r"\bmontacarga(s)?\b",
    r"\bdetector de metales\b",
    r"\bcontrol fisico\b",
    r"\bcierres automaticos\b",
    r"\bpuertas rapidas\b"
]


# ============================================================
# EXPRESIONES DOCUMENTALES
# ============================================================

VERBOS_DOCUMENTALES = [
    r"\bactualizar\b",
    r"\bactualizacion\b",
    r"\bincluir\b",
    r"\bincluyendo\b",
    r"\bcrear\b",
    r"\bcreacion\b",
    r"\bdiseñar\b",
    r"\bdiseño\b",
    r"\bdocumentar\b",
    r"\bdocumentacion\b",
    r"\bestablecer\b",
    r"\bestablecer criterios\b",
    r"\bdefinir\b",
    r"\bdefinicion\b",
    r"\brevisar\b",
    r"\brevision\b",
    r"\bverificar\b",
    r"\bverificacion\b",
    r"\bevaluar\b",
    r"\bevaluacion\b",
    r"\banalizar\b",
    r"\banalisis\b",
    r"\bsolicitar\b",
    r"\bgestionar\b",
    r"\bgarantizar\b",
    r"\bcapacitar\b",
    r"\bcapacitacion\b",
    r"\bentrenar\b",
    r"\bentrenamiento\b",
    r"\bsensibilizar\b",
    r"\bsensibilizacion\b",
    r"\bsocializar\b",
    r"\bsocializacion\b",
    r"\bdivulgar\b",
    r"\bdivulgacion\b",
    r"\bprogramar\b",
    r"\bprogramacion\b",
    r"\bplanificar\b",
    r"\bplanificacion\b",
    r"\bimplementar\b",
    r"\bfortalecer\b",
    r"\bregistrar\b",
    r"\bcompletar\b",
    r"\bformalizar\b",
    r"\brecopilar\b",
    r"\bmonitorear\b",
    r"\bseguimiento\b",
    r"\brealizar seguimiento\b"
]


OBJETOS_DOCUMENTALES = [
    r"\bprocedimiento(s)?\b",
    r"\bprocedimientos\b",
    r"\bformato(s)?\b",
    r"\bmatriz\b",
    r"\bmatrices\b",
    r"\bmanual(es)?\b",
    r"\bprograma(s)?\b",
    r"\bplan(es)? de accion\b",
    r"\bplan de accion\b",
    r"\bcronograma(s)?\b",
    r"\bmetodologia\b",
    r"\bmetodologias\b",
    r"\bcriterio(s)?\b",
    r"\banalisis\b",
    r"\bestudio(s)?\b",
    r"\bevaluacion\b",
    r"\bauditoria(s)?\b",
    r"\bcapacitacion\b",
    r"\bentrenamiento\b",
    r"\bsensibilizacion\b",
    r"\bsocializacion\b",
    r"\bdivulgacion\b",
    r"\bdocumentacion\b",
    r"\bregistro(s)?\b",
    r"\binforme(s)?\b",
    r"\bevidencia(s)?\b",
    r"\bpolitica\b",
    r"\bobjetivo(s)?\b",
    r"\bperfil(es)? de cargo\b",
    r"\blistado\b",
    r"\bmatriz legal\b",
    r"\bmatriz de peligros\b",
    r"\bmatriz de proveedores\b",
    r"\banalisis haccp\b",
    r"\btrazabilidad\b",
    r"\bindicador(es)?\b",
    r"\bplan de crisis\b",
    r"\bplan de inspeccion\b"
]


# ============================================================
# FUNCIÓN AUXILIAR
# ============================================================

def contiene_patron(texto, patrones):
    for patron in patrones:
        if re.search(patron, texto):
            return True
    return False


# ============================================================
# CLASIFICADOR PRINCIPAL
# ============================================================

def clasificar_accion(descripcion):
    texto = normalizar_texto(descripcion)

    if not texto:
        return {
            "clasificacion": "REVISIÓN MANUAL",
            "confianza": 0,
            "motivo": "La descripción está vacía."
        }

    # --------------------------------------------------------
    # 1. INVERSIÓN DIRECTA
    # --------------------------------------------------------
    patrones_fisicos_fuertes = [
        r"\breparar\b.*\b(piso|baldosa|pared|techo|puerta|lamina|acrilico|tanque|drenaje|canal)\b",
        r"\breemplazar\b.*\b(piso|baldosa|pared|techo|puerta|lamina|filtro|iman|isocubo|estiba|equipo)\b",
        r"\bcambiar\b.*\b(piso|baldosa|pared|techo|puerta|lamina|acrilico|equipo|filtro)\b",
        r"\binstalar\b.*\b(equipo|aire acondicionado|lampara|luminaria|puerta|cortina|filtro)\b",
        r"\badecuar\b.*\b(area|espacio|infraestructura|planta|zona)\b",
        r"\bconstruir\b.*\b(area|espacio|infraestructura|planta|zona|bodega)\b",
        r"\badquirir\b.*\b(equipo|maquina|maquinaria|herramienta|estiba|contenedor)\b",
        r"\bcomprar\b.*\b(equipo|maquina|maquinaria|herramienta|estiba|contenedor|computadores|computador|laptop|vehiculo)\b"
    ]

    if contiene_patron(texto, patrones_fisicos_fuertes):
        return {
            "clasificacion": "INVERSIÓN",
            "confianza": 95,
            "motivo": "Se identifica una intervención física, reparación, reemplazo, instalación o adquisición de un activo/equipamiento."
        }

    # --------------------------------------------------------
    # 2. EXCEPCIONES DOCUMENTALES
    # --------------------------------------------------------
    if contiene_patron(texto, [
        r"\bactualizar\b",
        r"\bincluir\b",
        r"\bdocumentar\b",
        r"\bestablecer\b",
        r"\bdefinir\b",
        r"\bcrear\b.*\b(formato|matriz|procedimiento|cronograma|programa)\b",
        r"\bdiseñar\b.*\b(sistema|metodologia|procedimiento|formato)\b",
        r"\bcapacitar\b",
        r"\bcapacitacion\b",
        r"\bsensibilizar\b",
        r"\bsocializar\b",
        r"\bdivulgar\b",
        r"\bsolicitar\b",
        r"\bgestionar\b",
        r"\bregistrar\b",
        r"\bverificar\b",
        r"\brevisar\b",
        r"\brevision\b",
        r"\bevaluar\b",
        r"\bevaluacion\b",
        r"\banalizar\b",
        r"\banalisis\b",
        r"\bplanificar\b",
        r"\bprogramar\b",
        r"\bmonitorear\b",
        r"\bseguimiento\b"
    ]):
        return {
            "clasificacion": "DOCUMENTAL",
            "confianza": 92,
            "motivo": "La acción corresponde principalmente a gestión, documentación, revisión, capacitación, seguimiento o control administrativo."
        }

    # --------------------------------------------------------
    # 3. INVERSIÓN POR VERBO + OBJETO
    # --------------------------------------------------------
    tiene_verbo_inversion = contiene_patron(texto, VERBOS_INVERSION)
    tiene_objeto_inversion = contiene_patron(texto, OBJETOS_INVERSION)

    if tiene_verbo_inversion and tiene_objeto_inversion:
        return {
            "clasificacion": "INVERSIÓN",
            "confianza": 90,
            "motivo": "Se identifica una acción física asociada a infraestructura, equipos, maquinaria o elementos físicos."
        }

    # --------------------------------------------------------
    # 4. DOCUMENTAL POR VERBO + OBJETO
    # --------------------------------------------------------
    tiene_verbo_documental = contiene_patron(texto, VERBOS_DOCUMENTALES)
    tiene_objeto_documental = contiene_patron(texto, OBJETOS_DOCUMENTALES)

    if tiene_verbo_documental and tiene_objeto_documental:
        return {
            "clasificacion": "DOCUMENTAL",
            "confianza": 90,
            "motivo": "Se identifica una actividad documental, administrativa, de gestión, seguimiento o capacitación."
        }

    # --------------------------------------------------------
    # 5. ACCIONES DOCUMENTALES GENERALES
    # --------------------------------------------------------
    if tiene_verbo_documental:
        return {
            "clasificacion": "DOCUMENTAL",
            "confianza": 80,
            "motivo": "El verbo principal corresponde a una actividad de gestión o control."
        }

    # --------------------------------------------------------
    # 6. ACCIONES FÍSICAS GENERALES
    # --------------------------------------------------------
    if tiene_verbo_inversion:
        return {
            "clasificacion": "INVERSIÓN",
            "confianza": 75,
            "motivo": "El verbo indica una intervención física o adquisición."
        }

    # --------------------------------------------------------
    # 7. REVISIÓN MANUAL
    # --------------------------------------------------------
    return {
        "clasificacion": "REVISIÓN MANUAL",
        "confianza": 40,
        "motivo": "No se encontró evidencia suficiente para clasificar automáticamente la acción."
    }


# ============================================================
# INTERFAZ DE STREAMLIT
# ============================================================

st.sidebar.title("⚙️ Panel de Control")
st.sidebar.info(
    "Sube tu archivo Excel (`.xlsx`) o CSV corporativo con las descripciones de actividades para comenzar el análisis automático basado en reglas de NLP."
)

uploaded_file = st.sidebar.file_uploader(
    "Cargar archivo de datos", 
    type=["xlsx", "csv"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Criterios de Clasificación")
st.sidebar.markdown("""
- **INVERSIÓN:** Equipos, infraestructura, construcción, remodelación, maquinaria, activos y reparaciones físicas.
- **DOCUMENTAL:** Informes, manuales, procedimientos, formatos, políticas, capacitación y gestión de archivos.
- **REVISIÓN MANUAL:** Casos ambiguos o sin términos clave concluyentes.
""")

st.title("📊 Clasificador Inteligente de Actividades Empresariales")
st.markdown("Clasifica de forma automática tus actividades corporativas en **INVERSIÓN**, **DOCUMENTAL** o **REVISIÓN MANUAL** mediante motores avanzados de expresiones regulares (Regex) y normalización lingüística.")

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success(f"¡Archivo '{uploaded_file.name}' cargado exitosamente! ({len(df)} filas encontradas)")
        
        columns = df.columns.tolist()
        selected_column = st.selectbox(
            "Selecciona la columna que contiene la descripción de las actividades:",
            columns
        )
        
        if st.button("🚀 Analizar y Clasificar Actividades"):
            with st.spinner("Analizando descripciones de actividades..."):
                resultados = []
                confianzas = []
                motivos = []
                
                for item in df[selected_column]:
                    res = clasificar_accion(item)
                    resultados.append(res["clasificacion"])
                    confianzas.append(res["confianza"])
                    motivos.append(res["motivo"])
                
                df['Clasificación Automática'] = resultados
                df['Confianza (%)'] = confianzas
                df['Motivo / Detalle'] = motivos
            
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
