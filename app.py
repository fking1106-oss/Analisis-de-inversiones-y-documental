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
# NORMALIZACIÓN DEL TEXTO AVANZADA
# ============================================================

def normalizar_texto(texto):
    if texto is None:
        return ""

    texto = str(texto).lower().strip()

    # Eliminar HTML o etiquetas extrañas
    texto = re.sub(r"<[^>]+>", " ", texto)

    # Quitar tildes y caracteres diacríticos
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

    # Normalizar espacios múltiples y puntuación excesiva
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto


# ============================================================
# DICCIONARIOS AMPLIADOS DE INVERSIÓN Y DOCUMENTAL
# ============================================================

VERBOS_INVERSION = [
    r"\breparar\b", r"\breparacion\b", r"\breparaciones\b",
    r"\breemplazar\b", r"\breemplazo\b", r"\bcambiar\b", r"\bcambio\b",
    r"\bsustituir\b", r"\bsustitucion\b", r"\binstalar\b", r"\binstalacion\b",
    r"\bmontar\b", r"\bmontaje\b", r"\bconstruir\b", r"\bconstruccion\b",
    r"\badecuar\b", r"\badecuacion\b", r"\bremodelar\b", r"\bremodelacion\b",
    r"\breubicar\b", r"\breubicacion\b", r"\bretirar\b", r"\bderribar\b",
    r"\bfabricar\b", r"\bfabricacion\b", r"\badquirir\b", r"\badquisicion\b",
    r"\bcomprar\b", r"\bcompra\b", r"\bsuministrar\b", r"\bsuministro\b",
    r"\bimplementar\b", r"\bdotar\b", r"\bdotacion\b", r"\bampliar\b",
    r"\bampliacion\b", r"\bcomprar(ia)?\b", r"\binvertir\b", r"\binversion\b"
]

OBJETOS_INVERSION = [
    r"\bequipo(s)?\b", r"\bmaquina(s)?\b", r"\bmaquinaria(s)?\b",
    r"\binfraestructura\b", r"\bpiso(s)?\b", r"\bbaldosa(s)?\b",
    r"\bpared(es)?\b", r"\btecho(s)?\b", r"\bpuerta(s)?\b",
    r"\bpuerta tipo cortina\b", r"\bcortina(s)?\b", r"\blamina(s)?\b",
    r"\bluminaria(s)?\b", r"\blampara(s)?\b", r"\bacrilico(s)?\b",
    r"\btanque(s)?\b", r"\bfiltro(s)?\b", r"\biman(es)?\b",
    r"\bisocubo(s)?\b", r"\bcontenedor(es)?\b", r"\bestiba(s)?\b",
    r"\bescalera(s)?\b", r"\bdrenaje(s)?\b", r"\bcanal(es)?\b",
    r"\brecubrimiento(s)?\b", r"\bpintura sanitaria\b",
    r"\brecubrimiento anticorrosivo\b", r"\baire acondicionado\b",
    r"\bmontacarga(s)?\b", r"\bdetector de metales\b",
    r"\bcontrol fisico\b", r"\bcierres automaticos\b",
    r"\bpuertas rapidas\b", r"\bcomputador(es)?\b", r"\blaptop(s)?\b",
    r"\bservidor(es)?\b", r"\bvehiculo(s)?\b", r"\bcamion(es)?\b",
    r"\bherramienta(s)?\b", r"\bmobile(s)?\b", r"\bdispositivo(s)?\b",
    r"\bactivo(s)?\b", r"\bbodega(s)?\b", r"\boficina(s)?\b",
    r"\bplanta(s)?\b", r"\bedificio(s)?\b", r"\blocal(es)?\b"
]

VERBOS_DOCUMENTALES = [
    r"\bactualizar\b", r"\bactualizacion\b", r"\bincluir\b", r"\bincluyendo\b",
    r"\bcrear\b", r"\bcreacion\b", r"\bdiseñar\b", r"\bdiseño\b",
    r"\bdocumentar\b", r"\bdocumentacion\b", r"\bestablecer\b",
    r"\bestablecer criterios\b", r"\bdefinir\b", r"\bdefinicion\b",
    r"\brevisar\b", r"\brevision\b", r"\bverificar\b", r"\bverificacion\b",
    r"\bevaluar\b", r"\bevaluacion\b", r"\banalizar\b", r"\banalisis\b",
    r"\bsolicitar\b", r"\bgestionar\b", r"\bgarantizar\b", r"\bcapacitar\b",
    r"\bcapacitacion\b", r"\bentrenar\b", r"\bentrenamiento\b",
    r"\bsensibilizar\b", r"\bsensibilizacion\b", r"\bsocializar\b",
    r"\bsocializacion\b", r"\bdivulgar\b", r"\bdivulgacion\b",
    r"\bprogramar\b", r"\bprogramacion\b", r"\bplanificar\b",
    r"\bplanificacion\b", r"\bfortalecer\b", r"\bregistrar\b",
    r"\bcompletar\b", r"\bformalizar\b", r"\brecopilar\b",
    r"\bmonitorear\b", r"\bseguimiento\b", r"\brealizar seguimiento\b",
    r"\belaborar\b", r"\belaboracion\b", r"\bredactar\b", r"\bredaccion\b",
    r"\bformular\b", r"\bformulacion\b", r"\bstructurar\b", r"\bestructuracion\b",
    r"\bconsensuar\b", r"\bconcertar\b", r"\bnotificar\b", r"\bcomunicar\b"
]

OBJETOS_DOCUMENTALES = [
    r"\bprocedimiento(s)?\b", r"\bformato(s)?\b", r"\bmatriz\b",
    r"\bmatrices\b", r"\bmanual(es)?\b", r"\bprograma(s)?\b",
    r"\bplan(es)? de accion\b", r"\bcronograma(s)?\b", r"\bmetodologia(s)?\b",
    r"\bcriterio(s)?\b", r"\bestudio(s)?\b", r"\bauditoria(s)?\b",
    r"\bcapacitacion\b", r"\bentrenamiento\b", r"\bsensibilizacion\b",
    r"\bsocializacion\b", r"\bdivulgacion\b", r"\bdocumentacion\b",
    r"\bregistro(s)?\b", r"\binforme(s)?\b", r"\bevidencia(s)?\b",
    r"\bpolitica(s)?\b", r"\bobjetivo(s)?\b", r"\bperfil(es)? de cargo\b",
    r"\blistado(s)?\b", r"\bmatriz legal\b", r"\bmatriz de peligros\b",
    r"\bmatriz de proveedores\b", r"\banalisis haccp\b", r"\btrazabilidad\b",
    r"\bindicador(es)?\b", r"\bplan de crisis\b", r"\bplan de inspeccion\b",
    r"\bactas?\b", r"\bcorreo(s)?\b", r"\bmemorando(s)?\b",
    r"\bcircular(es)?\b", r"\bpresentacion(es)?\b", r"\btabla(s)?\b"
]


# ============================================================
# FUNCIÓN AUXILIAR DE VALIDACIÓN DE PATRONES
# ============================================================

def contiene_patron(texto, patrones):
    for patron in patrones:
        if re.search(patron, texto):
            return True
    return False


# ============================================================
# CLASIFICADOR PRINCIPAL DE ALTA PRECISIÓN
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
    # 1. PATRONES FÍSICOS FUERTES (INVERSIÓN DIRECTA ALTA)
    # --------------------------------------------------------
    patrones_fisicos_fuertes = [
        r"\b(reparar|reemplazar|cambiar|instalar|adecuar|construir|ampliar|adquirir|comprar|implementar)\b.*\b(piso|baldosa|pared|techo|puerta|lamina|acrilico|tanque|drenaje|canal|filtro|iman|isocubo|estiba|equipo|maquina|maquinaria|vehiculo|computador|laptop|servidor|aire acondicionado|luminaria|lampara|bodega|oficina|planta|edificio|herramienta)\b",
        r"\b(compra|adquisicion|construccion|remodelacion|adecuacion|instalacion|montaje)\b.*\b(de|del|para)\b",
        r"\bnueva bodega\b", r"\bnueva oficina\b", r"\bnueva planta\b"
    ]

    if contiene_patron(texto, patrones_fisicos_fuertes):
        # Verificar si hay contradicción documental explícita al inicio
        if not (texto.startswith("revisar") or texto.startswith("actualizar") or texto.startswith("documentar") or texto.startswith("informe")):
            return {
                "clasificacion": "INVERSIÓN",
                "confianza": 98,
                "motivo": "Alta correspondencia con adquisición, intervención física de infraestructura, activos o maquinaria."
            }

    # --------------------------------------------------------
    # 2. PATRONES DOCUMENTALES FUERTES (GESTIÓN / ADMINISTRATIVO)
    # --------------------------------------------------------
    patrones_documentales_fuertes = [
        r"\b(elaborar|actualizar|redactar|revisar|verificar|evaluar|analizar|documentar|establecer|definir|crear|diseñar|gestionar|socializar|capacitar|divulgar|monitorear|programar|planificar)\b.*\b(informe|procedimiento|manual|formato|matriz|politica|documento|registro|cronograma|plan|indicador|acta|presentacion|capacitacion|auditoria|estudio|analisis)\b",
        r"\binforme mensual\b", r"\bprocedimiento de\b", r"\bmanual de\b", r"\bmatriz de\b"
    ]

    if contiene_patron(texto, patrones_documentales_fuertes):
        return {
            "clasificacion": "DOCUMENTAL",
            "confianza": 96,
            "motivo": "Identificación precisa de actividad documental, administrativa, informe, procedimiento o control."
        }

    # --------------------------------------------------------
    # 3. CRUCE POR VERBO + OBJETO (INVERSIÓN)
    # --------------------------------------------------------
    tiene_verbo_inv = contiene_patron(texto, VERBOS_INVERSION)
    tiene_objeto_inv = contiene_patron(texto, OBJETOS_INVERSION)

    if tiene_verbo_inv and tiene_objeto_inv:
        return {
            "clasificacion": "INVERSIÓN",
            "confianza": 92,
            "motivo": "Coincidencia simultánea de verbo de inversión y objeto físico o activo susceptible de mejora."
        }

    # --------------------------------------------------------
    # 4. CRUCE POR VERBO + OBJETO (DOCUMENTAL)
    # --------------------------------------------------------
    tiene_verbo_doc = contiene_patron(texto, VERBOS_DOCUMENTALES)
    tiene_objeto_doc = contiene_patron(texto, OBJETOS_DOCUMENTALES)

    if tiene_verbo_doc and tiene_objeto_doc:
        return {
            "clasificacion": "DOCUMENTAL",
            "confianza": 90,
            "motivo": "Coincidencia simultánea de verbo de gestión/creación y documento u objeto administrativo."
        }

    # --------------------------------------------------------
    # 5. VERBOS SUELTOS DE ALTA CERTEZA DOCUMENTAL O INVERSIÓN
    # --------------------------------------------------------
    if tiene_verbo_doc:
        return {
            "clasificacion": "DOCUMENTAL",
            "confianza": 82,
            "motivo": "El verbo principal de la acción apunta inequívocamente a un proceso administrativo o documental."
        }

    if tiene_verbo_inv:
        return {
            "clasificacion": "INVERSIÓN",
            "confianza": 80,
            "motivo": "El verbo principal sugiere una intervención física o provisión de recursos materiales."
        }

    # --------------------------------------------------------
    # 6. REVISIÓN MANUAL REDUCIDA (ÚLTIMO RECURSO)
    # --------------------------------------------------------
    return {
        "clasificacion": "REVISIÓN MANUAL",
        "confianza": 50,
        "motivo": "La descripción carece de verbos u objetos estándar claros; requiere validación experta."
    }


# ============================================================
# INTEGRACIÓN DE IA (GEMINI API)
# ============================================================

def clasificar_con_ia(descripcion, api_key=""):
    """
    Clasifica una descripción de actividad utilizando la API de Gemini (gemini-3-flash-preview)
    con un esquema estructurado (JSON).
    """
    import json
    import urllib.request
    import urllib.error

    system_prompt = (
        "Eres un analista financiero y experto en gestión de proyectos corporativos. "
        "Tu tarea es clasificar la descripción de una actividad empresarial en una de estas tres categorías exactas:\n"
        "1. INVERSIÓN: Adquisición de activos, equipos, maquinaria, tecnología, construcción, remodelación, infraestructura o reparaciones físicas.\n"
        "2. DOCUMENTAL: Informes, manuales, procedimientos, formatos, políticas, capacitación, actas o gestión administrativa/documental.\n"
        "3. REVISIÓN MANUAL: Si es completamente ambigua o no encaja claramente en ninguna de las anteriores.\n\n"
        "Devuelve la respuesta estrictamente en formato JSON."
    )

    user_query = f"Clasifica la siguiente actividad: '{descripcion}'"

    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "clasificacion": {
                        "type": "STRING",
                        "enum": ["INVERSIÓN", "DOCUMENTAL", "REVISIÓN MANUAL"]
                    },
                    "confianza": {
                        "type": "INTEGER",
                        "description": "Porcentaje de confianza de 0 a 100"
                    },
                    "motivo": {
                        "type": "STRING",
                        "description": "Breve explicación del motivo de la clasificación"
                    }
                },
                "propertyOrdering": ["clasificacion", "confianza", "motivo"]
            }
        }
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(payload).encode('utf-8')

    # Reintentos con retroceso exponencial simple
    import time
    delay = 1
    for intento in range(3):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                candidate = result.get('candidates', [{}])[0]
                part_text = candidate.get('content', {}).get('parts', [{}])[0].get('text', '{}')
                parsed = json.loads(part_text)
                return {
                    "clasificacion": parsed.get("clasificacion", "REVISIÓN MANUAL"),
                    "confianza": parsed.get("confianza", 85),
                    "motivo": parsed.get("motivo", "Clasificado mediante Inteligencia Artificial (Gemini).")
                }
        except Exception as e:
            if intento == 2:
                # Si falla la IA, hacemos fallback al motor de reglas local
                res_local = clasificar_accion(descripcion)
                res_local["motivo"] += " (Fallback local por error de API)."
                return res_local
            time.sleep(delay)
            delay *= 2


# ============================================================
# INTERFAZ DE STREAMLIT
# ============================================================

st.sidebar.title("⚙️ Panel de Control")
st.sidebar.info(
    "Sube tu archivo Excel (`.xlsx`) o CSV corporativo con las descripciones de actividades para comenzar el análisis automático."
)

# Opciones de motor de clasificación
modo_motor = st.sidebar.radio(
    "Selecciona el Motor de Clasificación:",
    ["Motor de Reglas (NLP Local)", "Inteligencia Artificial (Gemini API)"]
)

api_key_input = ""
if modo_motor == "Inteligencia Artificial (Gemini API)":
    api_key_input = st.sidebar.text_input(
        "API Key de Gemini (Opcional)", 
        type="password", 
        placeholder="Déjalo en blanco si usas el entorno por defecto",
        help="Si Canvas provee la API key automáticamente en runtime, puedes dejar este campo vacío."
    )

uploaded_file = st.sidebar.file_uploader(
    "Cargar archivo de datos", 
    type=["xlsx", "csv"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Criterios de Clasificación")
st.sidebar.markdown("""
- **INVERSIÓN:** Equipos, infraestructura, construcción, remodelación, maquinaria, activos, tecnología y reparaciones físicas.
- **DOCUMENTAL:** Informes, manuales, procedimientos, formatos, políticas, capacitación y gestión administrativa.
- **REVISIÓN MANUAL:** Casos altamente ambiguos.
""")

st.title("📊 Clasificador Inteligente de Actividades Empresariales")
st.markdown(f"Clasifica de forma automática tus actividades corporativas en **INVERSIÓN**, **DOCUMENTAL** o **REVISIÓN MANUAL** utilizando **{modo_motor}**.")

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
            with st.spinner(f"Analizando descripciones con {modo_motor}..."):
                resultados = []
                confianzas = []
                motivos = []
                
                for item in df[selected_column]:
                    if modo_motor == "Inteligencia Artificial (Gemini API)":
                        res = clasificar_con_ia(item, api_key=api_key_input)
                    else:
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
                file_name="actividades_clasificadas_ia.xlsx",
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
    
    st.dataframe(sample_df, use_keyword=True if 'use_keyword' in locals() else True, use_container_width=True)
    
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
