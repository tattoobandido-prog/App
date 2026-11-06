"""
Genera index.html (en la raíz del proyecto): la versión de Tattoo Lovers como página web simple
(sin Streamlit). Reutiliza el muñeco de componentes/cuerpo/index.html y la
lista de estilos de tattoolover.py.

Ejecutar desde la carpeta del proyecto:  python3 web/generar.py
"""
import ast
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
WEB = BASE / "web"

# ---- datos de tattoolover.py ----
codigo = (BASE / "tattoolover.py").read_text(encoding="utf-8")
arbol = ast.parse(codigo)
datos = {}
for nodo in arbol.body:
    if isinstance(nodo, ast.Assign) and isinstance(nodo.targets[0], ast.Name):
        nombre = nodo.targets[0].id
        if nombre in {"WHATSAPP_NUMBER", "STUDIO_NAME", "TAMANOS", "ESTILOS", "EXTENSIONES"}:
            datos[nombre] = ast.literal_eval(nodo.value)

estilos = []
for nombre, archivo in datos["ESTILOS"].items():
    foto = next((f"estilos/{archivo}{ext}" for ext in datos["EXTENSIONES"]
                 if (BASE / "estilos" / f"{archivo}{ext}").exists()), None)
    estilos.append({"nombre": nombre, "foto": foto})

# ---- muñeco ----
comp = (BASE / "componentes" / "cuerpo" / "index.html").read_text(encoding="utf-8")
css = re.search(r"<style>(.*?)</style>", comp, re.S).group(1)
css = re.sub(r"^\s*html, body \{.*?\}\n", "", css, flags=re.M)
css = re.sub(r"^\s*\* \{.*?\}\n", "", css, flags=re.M)
css = re.sub(r"^\s*:root \{.*?\}\n", "", css, flags=re.M)
cuerpo_html = re.search(r'(<div class="wrap">.*?</div>\s*)\n<script>', comp, re.S).group(1)
cuerpo_html = cuerpo_html.replace('class="wrap"', 'class="cuerpo-wrap"', 1)
css = css.replace(".wrap ", ".cuerpo-wrap ")
js = re.search(r"<script>(.*?)</script>", comp, re.S).group(1)
js = js.split("// ---------- conexión con Streamlit ----------")[0]
js = re.sub(r"function send\(type, extra\) \{.*?\n\}",
            "function send(type, extra) {\n"
            "  if (type === \"streamlit:setComponentValue\" && window.alCambiarCuerpo) window.alCambiarCuerpo(extra.value);\n"
            "}", js, flags=re.S)
js = "(function () {\n" + js + "\ndibujar();\n})();"

plantilla = (WEB / "plantilla.html").read_text(encoding="utf-8")
html = (plantilla
        .replace("/*__CSS_CUERPO__*/", css)
        .replace("<!--__CUERPO__-->", cuerpo_html)
        .replace("/*__JS_CUERPO__*/", js)
        .replace("__DATOS__", json.dumps({
            "whatsapp": datos["WHATSAPP_NUMBER"],
            "estudio": datos["STUDIO_NAME"],
            "tamanos": datos["TAMANOS"],
            "estilos": estilos,
        }, ensure_ascii=False)))
(BASE / "index.html").write_text(html, encoding="utf-8")
print("index.html listo:", len(html), "bytes")
