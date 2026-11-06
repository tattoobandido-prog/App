"""
TattooLover - Cotizador de tatuajes
Ejecutar con:  streamlit run tattoolover.py
Instalar con:  pip install streamlit
"""
import urllib.parse
from pathlib import Path

import streamlit as st

# ================== CONFIGURACIÓN ==================
WHATSAPP_NUMBER = "595972815410"  # <-- tu número con código de país, sin + ni espacios
STUDIO_NAME = "TattooLover"
CARPETA_ESTILOS = Path("estilos")  # pon aquí las imágenes de referencia

TAMANOS = ["0 a 5 cm", "5 a 10 cm", "10 a 15 cm", "15 a 20 cm", "20 a 25 cm", "Más de 25 cm"]

# nombre del estilo -> archivo de imagen dentro de la carpeta "estilos"
ESTILOS = {
    "Realismo": "realismo.jpg",
    "Minimalista / Línea fina": "minimalista.jpg",
    "Old School": "old_school.jpg",
    "Blackwork": "blackwork.jpg",
    "Acuarela": "acuarela.jpg",
    "Geométrico": "geometrico.jpg",
    "Tribal": "tribal.jpg",
    "Lettering": "lettering.jpg",
}

# Zonas del cuerpo (vista frontal) -> forma SVG
ZONAS = {
    "Cabeza": '<ellipse cx="100" cy="35" rx="22" ry="27" {s}/>',
    "Cuello": '<rect x="90" y="60" width="20" height="18" {s}/>',
    "Hombro izquierdo": '<ellipse cx="143" cy="92" rx="18" ry="14" {s}/>',
    "Hombro derecho": '<ellipse cx="57" cy="92" rx="18" ry="14" {s}/>',
    "Pecho": '<rect x="70" y="80" width="60" height="45" rx="8" {s}/>',
    "Abdomen": '<rect x="72" y="127" width="56" height="50" rx="8" {s}/>',
    "Brazo izquierdo": '<rect x="148" y="105" width="18" height="55" rx="8" {s}/>',
    "Brazo derecho": '<rect x="34" y="105" width="18" height="55" rx="8" {s}/>',
    "Antebrazo izquierdo": '<rect x="152" y="162" width="16" height="55" rx="8" {s}/>',
    "Antebrazo derecho": '<rect x="32" y="162" width="16" height="55" rx="8" {s}/>',
    "Muslo izquierdo": '<rect x="102" y="180" width="30" height="75" rx="12" {s}/>',
    "Muslo derecho": '<rect x="68" y="180" width="30" height="75" rx="12" {s}/>',
    "Pierna izquierda": '<rect x="105" y="258" width="24" height="75" rx="10" {s}/>',
    "Pierna derecha": '<rect x="71" y="258" width="24" height="75" rx="10" {s}/>',
    "Pie izquierdo": '<ellipse cx="117" cy="345" rx="14" ry="8" {s}/>',
    "Pie derecho": '<ellipse cx="83" cy="345" rx="14" ry="8" {s}/>',
}
EXTRA_ZONAS = ["Espalda", "Costillas", "Mano", "Otra"]


def dibujar_cuerpo(seleccion: str) -> str:
    formas = []
    for nombre, forma in ZONAS.items():
        activo = nombre == seleccion
        fill = "#e63946" if activo else "#d9d9d9"
        estilo = f'fill="{fill}" stroke="#555" stroke-width="1.5"'
        formas.append(forma.format(s=estilo))
    return (
        '<svg viewBox="0 0 200 360" width="220" xmlns="http://www.w3.org/2000/svg">'
        + "".join(formas)
        + "</svg>"
    )


def construir_mensaje(d: dict) -> str:
    lineas = [
        f"*Nueva cotización - {STUDIO_NAME}*",
        f"Nombre: {d['nombre']}",
        f"Teléfono: {d['telefono']}",
        f"Zona del cuerpo: {d['zona']}",
        f"Tamaño: {d['tamano']}",
        f"Estilo: {d['estilo']}",
    ]
    if d["detalle"].strip():
        lineas.append(f"Idea / detalles: {d['detalle'].strip()}")
    return "\n".join(lineas)


# ================== INTERFAZ ==================
st.set_page_config(page_title=STUDIO_NAME, page_icon="🖋️", layout="centered")
st.title(f"🖋️ {STUDIO_NAME}")
st.caption("Pide tu cotización en 4 pasos y recibe respuesta por WhatsApp.")

st.session_state.setdefault("zona", None)
st.session_state.setdefault("tamano", None)
st.session_state.setdefault("estilo", None)

# ---- Paso 1: zona del cuerpo ----
st.header("1. ¿Dónde te lo quieres hacer?")
col_img, col_btn = st.columns([1, 1])
with col_img:
    st.markdown(dibujar_cuerpo(st.session_state["zona"] or ""), unsafe_allow_html=True)
with col_btn:
    for nombre in list(ZONAS) + EXTRA_ZONAS:
        tipo = "primary" if st.session_state["zona"] == nombre else "secondary"
        if st.button(nombre, key=f"zona_{nombre}", type=tipo, use_container_width=True):
            st.session_state["zona"] = nombre
            st.rerun()

# ---- Paso 2: tamaño ----
st.header("2. ¿De qué tamaño?")
cols = st.columns(3)
for i, t in enumerate(TAMANOS):
    tipo = "primary" if st.session_state["tamano"] == t else "secondary"
    if cols[i % 3].button(t, key=f"tam_{t}", type=tipo, use_container_width=True):
        st.session_state["tamano"] = t
        st.rerun()

# ---- Paso 3: estilo ----
st.header("3. Elige un estilo")
cols = st.columns(2)
for i, (nombre, archivo) in enumerate(ESTILOS.items()):
    with cols[i % 2]:
        ruta = CARPETA_ESTILOS / archivo
        if ruta.exists():
            st.image(str(ruta), use_container_width=True)
        else:
            st.info(f"(Agrega la imagen: estilos/{archivo})")
        tipo = "primary" if st.session_state["estilo"] == nombre else "secondary"
        if st.button(nombre, key=f"est_{nombre}", type=tipo, use_container_width=True):
            st.session_state["estilo"] = nombre
            st.rerun()

# ---- Paso 4: datos y envío ----
st.header("4. Tus datos")
nombre = st.text_input("Nombre")
telefono = st.text_input("Tu WhatsApp")
detalle = st.text_area("Cuéntanos tu idea (opcional)")

st.divider()
st.subheader("Resumen")
st.write(f"**Zona:** {st.session_state['zona'] or '—'}")
st.write(f"**Tamaño:** {st.session_state['tamano'] or '—'}")
st.write(f"**Estilo:** {st.session_state['estilo'] or '—'}")

completo = all([st.session_state["zona"], st.session_state["tamano"],
                st.session_state["estilo"], nombre.strip(), telefono.strip()])

if completo:
    mensaje = construir_mensaje({
        "nombre": nombre, "telefono": telefono, "detalle": detalle,
        "zona": st.session_state["zona"], "tamano": st.session_state["tamano"],
        "estilo": st.session_state["estilo"],
    })
    url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
    st.link_button("📲 Enviar cotización por WhatsApp", url, type="primary", use_container_width=True)
else:
    st.warning("Completa zona, tamaño, estilo, nombre y WhatsApp para poder enviar.")
