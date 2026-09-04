# MANUAL DE IDENTIDAD — KRENN·IQ · v1.0

**Fuente única de verdad.** Derivado del código vivo (`kreniq-shell.css` de krenniq.com + capas.krenniq.com).
Los tres sitios beben de **`tokens.css`** (este folder). Ningún diseño re-deriva el canon de memoria: se lee de aquí.

> **El problema que esto resuelve:** ya existe un canon coherente — vive en el CSS de krenniq + capas, idénticos
> entre sí — pero nunca se escribió, así que cada diseño nuevo se desvía un poco. **Atlas se desvió entero**
> (otra paleta). La solución no es rediseñar: es fijar el canon una vez y alinear Atlas a él.

---

## 1. La marca en una frase
**Krenn·IQ = inteligencia que conoce los límites de lo que sabe — y lo dice.** Veredictos deterministas,
evidencia trazable, cero sobre-afirmación. Dos productos, una disciplina: **CAPAS** (¿la evidencia licencia la
afirmación?) y **Atlas** (¿necesitas QPU o basta una laptop?).

## 2. El símbolo (lo canónico — fijado)
**"Red de Transiciones 3D"** (`logo_kreniq_volum_trico.html`): constelación de nodos unidos por aristas que rota
lento sobre negro puro. Aristas gruesas magenta-rosa y teal forman una estrella; nodos ámbar/dorado de tamaños
distintos; malla fina de fondo. Es un **grafo de transiciones** — la metáfora literal del producto (estados,
aristas, caminos).

**Reglas de uso (no negociables):**
- Vive **siempre sobre `#050507`** (negro). Tres tratamientos válidos, ningún otro:
  1. **Héroe full-bleed** a opacidad ~0.65 con velo radial encima (`.bg-logo` + `.bg-veil` en tokens.css) — como krenniq.com.
  2. **Fondo de sección** más velado.
  3. **Mark estático** `krenniq-logo.png` 32×32 en navbar.
- NO se recolorea · NO se aplana a ícono lineal · NO se pone sobre fondo claro.

## 3. Color (tokens canónicos — en `tokens.css`)
| Token | Valor | Uso |
|---|---|---|
| `--bg` | `#050507` | negro base, **único** fondo |
| `--border` | `rgba(255,255,255,0.08)` | **NEUTRO**, nunca teñido de cian |
| `--text` / `--muted` | `.88` / `.44` blanco | cuerpo / secundario |
| `--pink` | `#e8185d` | **PRIMARIO de marca + acción** |
| `--pink2` | `#c4125a` | sombra del botón |
| `--violet` | `#a855f7` | 2º color del degradado de titular |
| `--accent` | `#4f5ef7` | índigo, acento secundario (links/badges) |
| `--green` | `#48bb78` | éxito · ACCEPT · CPU |
| `--amber` | `#f6ad55` | **solo** alerta · HOLD (NO color de acción) |

**Degradados oficiales (solo estos dos):** Titular `linear-gradient(135deg,#e8185d,#a855f7)` → en 1–2 palabras
clave del H1, nunca frases enteras. Botón `linear-gradient(135deg,#e8185d,#c4125a)`.
**Prohibido:** el teal/cian `#00e5ff` y el ámbar como primario (ambos de Atlas) se eliminan.

## 4. Tipografía
Una sola familia: **Inter**. Escala: **H1** ~49px/900/`-0.03em`/lh1.05 · **H2** ~33px/900 · **H3** 17px/800 ·
**Eyebrow** 11px/700 UPPERCASE/`+0.12em` en color de sección (rosa el principal) · **Cuerpo** 16px/400 `--text`.

## 5. Layout y geometría
`--col:1200px` · `--gutter:48px` · `--nav-h:60px` · tarjetas `--radius:14px` · botones `7px` (padding 9×20, 13px/700).
Tarjetas: `background:rgba(10,10,18,.75)`, borde `rgba(255,255,255,.10)`, **sin box-shadow** (la profundidad la dan
el borde + el fondo flotante).

## 6. Navegación (IA común)
Navbar 60px: izq la marca (mark 32px + "PRODUCTO / BY KRENN-IQ"); centro links con el activo como **pill**; der
**EN/ES + un único CTA rosa**. Cross-links obligatorios entre las tres propiedades (Home · CAPAS · Atlas). **Un
solo CTA primario por barra.**

## 7. Voz y tono
Inglés base, ES toggle (bilingüe real, mismo registro). Firmas: *"decide on numbers, not noise"*, *"your model
proposes; CAPAS disposes"*, *"knows what it knows, owns what it doesn't"*. Sobrio, técnico, honesto sobre el
alcance — **siempre un bloque "Honest scope"** (`.honest`). Nunca vender "supremacy". Cada número público es
re-derivable o marcado como estimación.

## 8. Anatomía canónica de página
Eyebrow rosa → H1 con 1–2 palabras en degradado → subtítulo `--muted` → fila de CTAs (1 primario rosa +
secundarios outline) → bloque demo/evidencia en `.card` → secciones con eyebrow + H2 + grid de `.card`. Fondo:
logo 3D flotante velado, siempre.

---

## 9. ATLAS — divergencia medida → fix exacto (lo que rompe el canon hoy)
| Atlas hoy (`webui.py :root`) | Canon | Acción |
|---|---|---|
| `--bg:#07070b` | `#050507` | reemplazar |
| `--accent:#f5a623` (ámbar primario, 4 usos) | `--pink:#e8185d` | primario pasa a rosa |
| `--blue/--teal:#00e5ff` (7 usos) | — | **eliminar** (no existe en canon) |
| `--border:rgba(0,229,255,.18)` (cian) | `rgba(255,255,255,0.08)` | borde neutro |
| `--green:#34d399` | `#48bb78` | alinear |
| `#e61062` (rosa corrido, 3 usos) · `#e8185d` (0 usos) | `#e8185d` | corregir el rosa |
| ámbar como acción | ámbar = solo alerta `#f6ad55` | reclasificar |

## 10. EL ENCARGO (una sola barrida, sin más iteración)
> *Adopta `tokens.css` + `BRAND_KRENNIQ.md` como única fuente de verdad. Alinea `atlas.krenniq.com` al canon
> **sin tocar su funcionalidad ni su contenido**: reemplaza el bloque `:root` de Atlas por los tokens canónicos
> (elimina `--blue/--teal:#00e5ff`; primario de ámbar `#f5a623` → `--pink:#e8185d`; `--bg` `#07070b`→`#050507`;
> bordes `rgba(0,229,255,.18)`→`rgba(255,255,255,0.08)`; ámbar solo como alerta). Aplica la escala Inter
> (H1 900/-0.03em), radios (botón 7px, tarjeta 14px), navbar 60px con pill activo y CTA rosa único, y el
> degradado de titular `#e8185d→#a855f7` solo en palabras clave. Conserva el logo 3D flotante en los tres
> sitios. No introduzcas paletas, fuentes, sombras ni gradientes fuera de los listados. Entrega un solo
> `tokens.css` compartido + diff por sitio.*

**Resultado:** un documento, tres sitios que beben del mismo `tokens.css`, y Atlas deja de ser el primo que
pinta distinto.
