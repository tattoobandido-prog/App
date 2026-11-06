"""
TattooLover - Cotizador de tatuajes
Ejecutar con:  streamlit run tattoolover.py
Instalar con:  pip install streamlit
"""
import urllib.parse
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# ================== CONFIGURACIÓN ==================
WHATSAPP_NUMBER = "595972815410"  # <-- tu número con código de país, sin + ni espacios
STUDIO_NAME = "TattooLover"
BASE = Path(__file__).parent
CARPETA_ESTILOS = BASE / "estilos"  # pon aquí las fotos de ejemplo de cada estilo

TAMANOS = ["0 a 5 cm", "5 a 10 cm", "10 a 15 cm", "15 a 20 cm", "20 a 25 cm", "Más de 25 cm"]

# nombre del estilo -> nombre del archivo de foto (sin extensión) en la carpeta "estilos"
# Sirve .jpg, .jpeg, .png o .webp
ESTILOS = {
    "Realismo": "realismo",
    "Minimalista / Línea fina": "minimalista",
    "Old School": "old_school",
    "Blackwork": "blackwork",
    "Acuarela": "acuarela",
    "Geométrico": "geometrico",
    "Tribal": "tribal",
    "Lettering": "lettering",
}
EXTENSIONES = [".jpg", ".jpeg", ".png", ".webp"]

# Muñequito interactivo (HTML/SVG en componentes/cuerpo/index.html)
_cuerpo = components.declare_component("cuerpo", path=str(BASE / "componentes" / "cuerpo"))

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');

[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse at 50% -10%, rgba(225,6,0,.38), transparent 55%),
    radial-gradient(ellipse at 100% 100%, rgba(225,6,0,.16), transparent 45%),
    repeating-linear-gradient(45deg, rgba(255,255,255,.018) 0 2px, transparent 2px 14px),
    #0b0b0b;
  background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stHeaderActionElements"] { display: none; }

.tl-hero { text-align: center; padding: 8px 0 6px; }
.tl-titulo {
  font-family: 'UnifrakturMaguntia', serif !important; font-size: 68px !important; line-height: 1.1; margin: 0;
  color: #fff; text-shadow: 0 0 18px rgba(225,6,0,.75), 0 3px 0 #7a0000;
}
.tl-sub { color: #cfcfcf; margin-top: 10px; font-size: 17px; }
.tl-linea { height: 2px; margin: 18px auto 4px; width: 70%;
  background: linear-gradient(90deg, transparent, #e10600, transparent); }

h2 { font-size: 1.55rem !important; border-left: 4px solid #e10600; padding-left: 12px !important; margin-top: 28px !important; }
h2 .tl-num { color: #e10600; }

.stButton > button, .stLinkButton > a { border-radius: 999px; font-weight: 600; }
.stButton > button p { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.stButton > button[kind="secondary"] { background: #141414; border: 1px solid #3a3a3a; color: #fff; }
.stButton > button[kind="secondary"]:hover { border-color: #e10600; color: #fff; }
.stButton > button[kind="primary"], .stLinkButton > a[kind="primary"] { box-shadow: 0 0 16px rgba(225,6,0,.5); }

.tl-card-vacia {
  aspect-ratio: 4 / 3; border-radius: 12px; display: flex; align-items: center; justify-content: center;
  text-align: center; padding: 10px; margin-bottom: 8px; font-size: 20px; color: #fff;
  font-family: 'UnifrakturMaguntia', serif;
  background: radial-gradient(circle at 30% 20%, rgba(225,6,0,.35), transparent 60%), #151515;
  border: 1px solid #2e2e2e;
}
/* estilos: siempre 2 por fila, también en celular */
[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 12px !important; }
[data-testid="stColumn"] { min-width: 0 !important; width: 50% !important; flex: 1 1 50% !important; }
[data-testid="stImage"] img { border-radius: 12px; aspect-ratio: 4 / 3; object-fit: cover; }

.tl-resumen { background: #141414; border: 1px solid #2e2e2e; border-radius: 14px; padding: 14px 18px; }
.tl-resumen div { padding: 4px 0; }
.tl-resumen b { color: #ff3b30; }
</style>
"""


def foto_estilo(archivo: str):
    for ext in EXTENSIONES:
        ruta = CARPETA_ESTILOS / f"{archivo}{ext}"
        if ruta.exists():
            return ruta
    return None


def construir_mensaje(d: dict) -> str:
    lineas = [
        f"*Nueva cotización - {STUDIO_NAME}*",
        f"Nombre: {d['nombre']}",
        f"Teléfono: {d['telefono']}",
        f"Zona del cuerpo: {d['zona']} ({d['lado'].lower()})",
        f"Tamaño: {d['tamano']}",
        f"Estilo: {d['estilo']}",
    ]
    if d["detalle"].strip():
        lineas.append(f"Idea / detalles: {d['detalle'].strip()}")
    return "\n".join(lineas)


def titulo(num: int, texto: str):
    st.markdown(f'## <span class="tl-num">{num}.</span> {texto}', unsafe_allow_html=True)


# ================== INTERFAZ ==================
st.set_page_config(page_title=STUDIO_NAME, page_icon="🖋️", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(
    f'<div class="tl-hero"><div class="tl-titulo">{STUDIO_NAME}</div>'
    '<div class="tl-sub">Pide tu cotización en 4 pasos y recibe respuesta por WhatsApp</div>'
    '<div class="tl-linea"></div></div>',
    unsafe_allow_html=True,
)

st.session_state.setdefault("estilo", None)

# ---- Paso 1: zona del cuerpo ----
titulo(1, "¿Dónde te lo quieres hacer?")
sel = _cuerpo(key="cuerpo", default=None) or {}
lado = sel.get("lado") or "Frente"
zona = sel.get("zona")

# ---- Paso 2: tamaño ----
titulo(2, "¿De qué tamaño?")
tamano = st.pills("Tamaño", TAMANOS, key="tamano", label_visibility="collapsed")

# ---- Paso 3: estilo ----
titulo(3, "Elige un estilo")
items = list(ESTILOS.items())
for fila in range(0, len(items), 2):  # filas de 2 para que en celular quede en orden
    cols = st.columns(2)
    for col, (nombre, archivo) in zip(cols, items[fila:fila + 2]):
        with col:
            ruta = foto_estilo(archivo)
            if ruta:
                st.image(str(ruta), use_container_width=True)
            else:
                st.markdown(f'<div class="tl-card-vacia">{nombre}</div>', unsafe_allow_html=True)
            tipo = "primary" if st.session_state["estilo"] == nombre else "secondary"
            if st.button(nombre, key=f"est_{nombre}", type=tipo, use_container_width=True):
                st.session_state["estilo"] = nombre
                st.rerun()

# ---- Paso 4: datos y envío ----
titulo(4, "Tus datos")
nombre = st.text_input("Nombre")
telefono = st.text_input("Tu WhatsApp")
detalle = st.text_area("Cuéntanos tu idea (opcional)")

estilo = st.session_state["estilo"]
st.markdown(
    '<div class="tl-resumen">'
    f'<div><b>Zona:</b> {f"{zona} ({lado.lower()})" if zona else "—"}</div>'
    f'<div><b>Tamaño:</b> {tamano or "—"}</div>'
    f'<div><b>Estilo:</b> {estilo or "—"}</div>'
    '</div>',
    unsafe_allow_html=True,
)
st.write("")

completo = all([zona, tamano, estilo, nombre.strip(), telefono.strip()])

if completo:
    mensaje = construir_mensaje({
        "nombre": nombre, "telefono": telefono, "detalle": detalle,
        "zona": zona, "lado": lado, "tamano": tamano, "estilo": estilo,
    })
    url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
    st.link_button("📲 Enviar cotización por WhatsApp", url, type="primary", use_container_width=True)
else:
    st.warning("Completa zona, tamaño, estilo, nombre y WhatsApp para poder enviar.")
