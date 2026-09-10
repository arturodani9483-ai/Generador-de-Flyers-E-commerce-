import streamlit as st
import pandas as pd
import os
import io
import re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

st.set_page_config(page_title="Sistema Multiuso & Evaluador", layout="wide", page_icon="🛍️")

DB_LIQUIDEZ_FILE = "base_liquidez_militares.csv"
DB_DICTAMENES_FILE = "dictamenes_giraduria.csv"

# --- FUNCIONES DE LIMPIEZA Y FORMATO ---
def limpiar_ci(val):
    if pd.isna(val) or val is None:
        return ""
    try:
        return str(int(float(val))).strip()
    except:
        return str(val).split('.')[0].replace('.', '').strip()

def limpiar_monto(val):
    if pd.isna(val) or val is None:
        return 0.0
    try:
        return float(val)
    except:
        s = str(val).replace('.', '').replace(',', '.').strip()
        numeros = re.findall(r'[-+]?\d*\.\d+|\d+', s)
        return float(numeros[0]) if numeros else 0.0

def formato_guarani(val):
    try:
        return f"{int(round(val)):,}".replace(',', '.')
    except:
        return "0"

def cargar_liquidez():
    if os.path.exists(DB_LIQUIDEZ_FILE):
        return pd.read_csv(DB_LIQUIDEZ_FILE, dtype=str)
    return pd.DataFrame()

def guardar_liquidez(df):
    df.to_csv(DB_LIQUIDEZ_FILE, index=False)

def cargar_dictamenes():
    if os.path.exists(DB_DICTAMENES_FILE):
        return pd.read_csv(DB_DICTAMENES_FILE, dtype=str)
    return pd.DataFrame(columns=['CEDULA', 'CUOTA_PROPUESTA', 'DICTAMEN_GIRADOR', 'FECHA'])

def guardar_dictamenes(df):
    df.to_csv(DB_DICTAMENES_FILE, index=False)

# --- FUNCIÓN INTELIGENTE DE GENERACIÓN DE FLYER ---
def obtener_color_dominante(img_pil):
    img_small = img_pil.copy().resize((50, 50)).convert('RGB')
    pixels = list(img_small.getdata())
    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)
    return (r, g, b)

def generar_flyer_producto(img_producto, img_logo, titulo, caracteristicas, precio, whatsapp):
    # Lienzo formato 1080x1350 (Ideal Instagram/WhatsApp Status)
    ancho, alto = 1080, 1350
    
    # Detección de color basada en el producto
    color_base = obtener_color_dominante(img_producto)
    
    # Crear fondo estilizado
    flyer = Image.new('RGB', (ancho, alto), color=(18, 18, 24))
    draw = ImageDraw.Draw(flyer)
    
    # Encabezado con color de acento detectado
    draw.rectangle([0, 0, ancho, 180], fill=color_base)
    
    # Pegar Logo si existe
    if img_logo:
        logo = img_logo.copy()
        logo.thumbnail((250, 120))
        flyer.paste(logo, (40, 30), mask=logo.convert('RGBA') if logo.mode == 'RGBA' else None)

    # Procesar e insertar Foto del Producto
    prod_img = img_producto.copy()
    prod_img.thumbnail((900, 550))
    pos_x = (ancho - prod_img.width) // 2
    flyer.paste(prod_img, (pos_x, 220))

    # Tarjeta de Info (Título, Características, Precio)
    draw.rectangle([50, 800, 1030, 1200], fill=(30, 32, 44), outline=color_base, width=4)
    
    # Textos
    draw.text((80, 830), titulo.upper(), fill=(255, 255, 255))
    
    # Características
    y_char = 890
    for linea in caracteristicas.split('\n'):
        if linea.strip():
            draw.text((80, y_char), f"• {linea.strip()}", fill=(200, 205, 215))
            y_char += 35

    # Cuadro de Precio destacado
    draw.rectangle([600, 1070, 1000, 1170], fill=color_base)
    draw.text((620, 1100), f"Gs. {precio}", fill=(255, 255, 255))

    # Pie de página con WhatsApp
    draw.rectangle([0, 1230, ancho, alto], fill=(10, 10, 15))
    draw.text((80, 1260), f"📲 Pedidos al WhatsApp: {whatsapp}", fill=(0, 230, 118))

    return flyer

df_liquidez = cargar_liquidez()
df_dictamenes = cargar_dictamenes()

st.title("🪖 Evaluador Crediticio & 🎨 Generador de Flyers")

# --- BARRA LATERAL DE NAVEGACIÓN ---
st.sidebar.header("⚙️ Menú Principal")
opcion = st.sidebar.radio("Navegación:", [
    "🎨 Generador de Flyers (E-Commerce)",
    "🔍 Simular / Consultar Crédito", 
    "📋 Dictamen del Girador", 
    "📥 Cargar Base Mensual"
])

# --- MÓDULO: GENERADOR DE FLYERS ---
if opcion == "🎨 Generador de Flyers (E-Commerce)":
    st.subheader("🎨 Creador Inteligente de Flyers Publicitarios")
    st.write("Sube la foto de tu producto y tu logo; el sistema adaptará la paleta de colores para resaltar la publicación.")

    col_up1, col_up2 = st.columns(2)
    with col_up1:
        file_producto = st.file_uploader("1. Foto del Producto *", type=["jpg", "jpeg", "png"])
    with col_up2:
        file_logo = st.file_uploader("2. Logo de la Tienda (Opcional)", type=["jpg", "jpeg", "png"])

    st.markdown("---")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        titulo_prod = st.text_input("Nombre / Título del Producto:", placeholder="Ej: Auriculares Inalámbricos Pro")
        caracteristicas_prod = st.text_area("Características principales (Una por línea):", placeholder="Cancelación de ruido\nBatería hasta 24hs\nConexión Bluetooth 5.3")
    with col_t2:
        precio_prod = st.text_input("Precio de Venta (Gs.):", placeholder="Ej: 180.000")
        wa_prod = st.text_input("Número de WhatsApp de Contacto:", placeholder="Ej: 0981 123 456")

    if file_producto and titulo_prod and precio_prod:
        if st.button("🚀 Generar Flyer Automático"):
            try:
                img_prod = Image.open(file_producto)
                img_lg = Image.open(file_logo) if file_logo else None
                
                flyer_resultado = generar_flyer_producto(img_prod, img_lg, titulo_prod, caracteristicas_prod, precio_prod, wa_prod)

                st.markdown("---")
                st.subheader("📸 Vista Previa del Flyer Generado:")
                st.image(flyer_resultado, use_container_width=True)

                # Convertir imagen para descargar
                buf = io.BytesIO()
                flyer_resultado.save(buf, format="PNG")
                byte_im = buf.getvalue()

                st.download_button(
                    label="📥 Descargar Flyer en Alta Calidad (PNG)",
                    data=byte_im,
                    file_name=f"Flyer_{titulo_prod.replace(' ', '_')}.png",
                    mime="image/png",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error al procesar la imagen: {e}")

# --- MÓDULO 1: SIMULAR / CONSULTAR CRÉDITO ---
elif opcion == "🔍 Simular / Consultar Crédito":
    st.subheader("🔍 Buscador de Liquidez por Cédula")
    
    if df_liquidez.empty:
        st.info("👈 La base de datos está vacía. Carga la planilla mensual desde 'Cargar Base Mensual'.")
    else:
        ci_input = st.text_input("Ingresá el Número de Cédula (C.I.):", placeholder="Ej: 1093300").strip().replace('.', '')
        
        if ci_input:
            match = df_liquidez[df_liquidez['emp_ci'].apply(limpiar_ci) == ci_input]
            
            if match.empty:
                st.error(f"No se encontró ningún militar registrado con la C.I. Nº '{ci_input}'.")
            else:
                row = match.iloc[0]
                nombre = row.get('emp_nomape', 'S/N')
                unidad = row.get('UNIDAD', '-')
                categoria = row.get('cat_codigo', '-')

                presupuestado = limpiar_monto(row.get('presupuestado', 0))
                liquido_real = limpiar_monto(row.get('liquido', 0))
                limite_50 = liquido_real / 2.0

                st.markdown("---")
                st.success(f"👤 **Militar:** {nombre} | **C.I.:** {ci_input} | **Categoría:** {categoria}")
                st.info(f"🏛️ **Unidad Militar:** {unidad}")

                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Presupuestado", f"Gs. {formato_guarani(presupuestado)}")
                col_m2.metric("Líquido Real Actual", f"Gs. {formato_guarani(liquido_real)}")
                col_m3.metric("Límite de Cuota (50%)", f"Gs. {formato_guarani(limite_50)}")

                st.markdown("---")
                st.subheader("💳 Evaluación del Nuevo Crédito")
                cuota_solicitada = st.number_input("Ingresá el Monto de la Cuota para el Nuevo Crédito (Gs.):", min_value=0.0, step=50000.0, format="%.0f")

                if cuota_solicitada > 0:
                    diferencia = limite_50 - cuota_solicitada
                    if cuota_solicitada <= limite_50:
                        st.success("✅ **CRÉDITO FACTIBLE (APROBADO)**")
                        st.write(f"La cuota entra dentro del límite del 50%. Margen disponible: **Gs. {formato_guarani(diferencia)}**")
                    else:
                        st.error("⚠️ **RECHAZADO POR LÍMITE DE LIQUIDEZ DEL 50% - HABLAR CON SU GIRADURÍA**")
                        st.write(f"La cuota supera el límite del 50% por **Gs. {formato_guarani(abs(diferencia))}**.")

                dict_match = df_dictamenes[df_dictamenes['CEDULA'].apply(limpiar_ci) == ci_input]
                if not dict_match.empty:
                    st.markdown("---")
                    dict_row = dict_match.iloc[-1]
                    st.warning(f"📌 **Dictamen Registrado por Giraduría ({dict_row['FECHA']}):** {dict_row['DICTAMEN_GIRADOR']}")

# --- MÓDULO 2: DICTAMEN DEL GIRADOR ---
elif opcion == "📋 Dictamen del Girador":
    st.subheader("📋 Módulo de Registro de Dictamen de Giraduría")
    
    if df_liquidez.empty:
        st.info("Carga la base de liquidez primero.")
    else:
        ci_girador = st.text_input("Ingresá la Cédula del Militar para consultar/editar dictamen:", placeholder="Ej: 1093300").strip().replace('.', '')
        
        if ci_girador:
            match = df_liquidez[df_liquidez['emp_ci'].apply(limpiar_ci) == ci_girador]
            
            if match.empty:
                st.error(f"No se encontró la Cédula '{ci_girador}'.")
            else:
                row = match.iloc[0]
                nombre = row.get('emp_nomape', 'S/N')
                unidad = row.get('UNIDAD', '-')
                liquido_real = limpiar_monto(row.get('liquido', 0))
                limite_50 = liquido_real / 2.0

                st.markdown("---")
                st.write("### Datos de Solo Lectura:")
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.text_input("Nombre y Apellido:", value=nombre, disabled=True)
                    st.text_input("Unidad Militar:", value=unidad, disabled=True)
                with col_g2:
                    st.text_input("Cédula N°:", value=ci_girador, disabled=True)
                    st.text_input("Límite de Cuota Máxima (50%):", value=f"Gs. {formato_guarani(limite_50)}", disabled=True)

                st.markdown("---")
                dict_previo = df_dictamenes[df_dictamenes['CEDULA'].apply(limpiar_ci) == ci_girador]
                obs_inicial = dict_previo.iloc[-1]['DICTAMEN_GIRADOR'] if not dict_previo.empty else ""

                with st.form("form_dictamen"):
                    st.subheader("📝 Editar Dictamen / Observación de Giraduría")
                    cuota_evaluando = st.number_input("Monto de Cuota Solicitada (Gs.):", min_value=0.0, step=50000.0, format="%.0f")
                    obs_girador = st.text_area("Observaciones / Respuesta del Girador:", value=obs_inicial, placeholder="Ej: Compra de deuda aprobada / Rechazado definitivo")
                    
                    btn_guardar_dictamen = st.form_submit_button("💾 Guardar Dictamen")

                    if btn_guardar_dictamen:
                        if not obs_girador.strip():
                            st.error("Por favor ingresa una observación para guardar el dictamen.")
                        else:
                            df_dictamenes = df_dictamenes[df_dictamenes['CEDULA'].apply(limpiar_ci) != ci_girador]
                            nuevo_dictamen = pd.DataFrame([{
                                'CEDULA': ci_girador,
                                'CUOTA_PROPUESTA': formato_guarani(cuota_evaluando),
                                'DICTAMEN_GIRADOR': obs_girador.strip(),
                                'FECHA': pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                            }])
                            df_dictamenes = pd.concat([df_dictamenes, nuevo_dictamen], ignore_index=True)
                            guardar_dictamenes(df_dictamenes)
                            st.success("✅ ¡Dictamen guardado con éxito! Se reflejará en la consulta principal.")

# --- MÓDULO 3: CARGAR BASE MENSUAL ---
elif opcion == "📥 Cargar Base Mensual":
    st.subheader("📥 Cargar Base de Liquidez Mensual de Militares")
    archivo = st.file_uploader("Seleccioná la planilla en formato Excel o CSV", type=["xlsx", "xls", "csv"])
    
    if archivo:
        if st.button("⚠️ Procesar e Importar Base de Datos Mensual"):
            try:
                ext = archivo.name.lower().split('.')[-1]
                if ext == 'csv':
                    df_cargado = pd.read_csv(archivo, dtype=str)
                else:
                    xls = pd.ExcelFile(archivo)
                    hoja = xls.sheet_names[3] if len(xls.sheet_names) >= 4 else xls.sheet_names[0]
                    df_cargado = pd.read_excel(xls, sheet_name=hoja, dtype=str)

                if df_cargado.empty:
                    st.warning("No se encontraron datos procesables en el archivo.")
                else:
                    guardar_liquidez(df_cargado)
                    st.success(f"✅ ¡Base de datos importada correctamente! Total de registros procesados: {len(df_cargado):,}")
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")
