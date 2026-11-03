"""Personajes secundarios con acabado "3D de plastilina" (render propio con numpy).

Cada pieza del personaje es un elipsoide 3D (cabeza, nariz, orejas, barba…). Se calcula su
profundidad píxel a píxel (z-buffer), su normal y se ilumina con una luz principal, luz
ambiente, brillo especular y luz de contorno. Encima se añaden texturas (pelo, barba
rizada, tela, piel), oclusión ambiental (sombras en los huecos) y detalles 2D (boca,
arrugas, gafas).

render(personaje, t, boca, parpado, mira, tam) → imagen RGBA (numpy) lista para imshow.
"""
import numpy as np

LUZ = np.array([-0.45, 0.55, 0.70])
LUZ = LUZ / np.linalg.norm(LUZ)


# ----------------------------------------------------------------- utilidades
def _ruido(forma, celdas, semilla):
    """Ruido suave (value noise) del tamaño `forma`."""
    rng = np.random.default_rng(semilla)
    g = rng.random((celdas + 1, celdas + 1))
    h, w = forma
    y = np.linspace(0, celdas, h, endpoint=False)
    x = np.linspace(0, celdas, w, endpoint=False)
    y0, x0 = y.astype(int), x.astype(int)
    fy, fx = (y - y0)[:, None], (x - x0)[None, :]
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]
    b = g[y0][:, x0 + 1]
    c = g[y0 + 1][:, x0]
    d = g[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def _fbm(forma, semilla, base=6, octavas=4):
    r, amp, tot = 0, 1.0, 0
    for k in range(octavas):
        r = r + amp * _ruido(forma, base * 2 ** k, semilla + k)
        tot += amp
        amp *= 0.5
    return r / tot


def _caja(img, k):
    """Desenfoque rápido (caja) de tamaño k."""
    if k < 1:
        return img
    c = np.cumsum(np.pad(img, ((k + 1, k), (0, 0)), mode="edge"), 0)
    img = (c[2 * k + 1:] - c[:-2 * k - 1]) / (2 * k + 1)
    c = np.cumsum(np.pad(img, ((0, 0), (k + 1, k)), mode="edge"), 1)
    return (c[:, 2 * k + 1:] - c[:, :-2 * k - 1]) / (2 * k + 1)


def _hex(c):
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)])


class Escena:
    def __init__(self, tam=520):
        self.n = tam
        lin = np.linspace(-1.0, 1.0, tam)
        self.X, self.Y = np.meshgrid(lin, -lin * 1.1)
        self.Z = np.full((tam, tam), -9.0)
        self.N = np.zeros((tam, tam, 3))
        self.C = np.zeros((tam, tam, 3))
        self.ID = np.full((tam, tam), -1)
        self.material = []        # (brillo, intensidad especular, textura)

    def elipsoide(self, c, r, color, rot=0.0, brillo=12, esp=0.12, textura=None,
                  recorte=None):
        """c=(x,y,z), r=(a,b,cz). rot: giro en el plano de la imagen (grados).
        recorte: función (X, Y) → máscara booleana para dibujar solo una parte."""
        ang = np.radians(rot)
        dx, dy = self.X - c[0], self.Y - c[1]
        u = dx * np.cos(ang) + dy * np.sin(ang)
        v = -dx * np.sin(ang) + dy * np.cos(ang)
        q = 1 - (u / r[0]) ** 2 - (v / r[1]) ** 2
        m = q > 0
        if recorte is not None:
            m &= recorte(self.X, self.Y)
        z = np.where(m, c[2] + r[2] * np.sqrt(np.clip(q, 0, None)), -9)
        delante = m & (z > self.Z)
        if not delante.any():
            return
        nu, nv, nz = u / r[0] ** 2, v / r[1] ** 2, (z - c[2]) / r[2] ** 2
        nx = nu * np.cos(ang) - nv * np.sin(ang)
        ny = nu * np.sin(ang) + nv * np.cos(ang)
        N = np.stack([nx, ny, nz], -1)
        N /= np.linalg.norm(N, axis=-1, keepdims=True) + 1e-9
        self.Z[delante] = z[delante]
        self.N[delante] = N[delante]
        self.C[delante] = _hex(color)
        self.ID[delante] = len(self.material)
        self.material.append((brillo, esp, textura, (u, v)))

    def sombrear(self):
        n = self.n
        dif = np.clip(self.N @ LUZ, 0, 1)
        borde = (1 - np.clip(self.N[..., 2], 0, 1)) ** 3
        col = self.C.copy()
        espec = np.zeros((n, n))
        for k, (brillo, esp, tex, (u, v)) in enumerate(self.material):
            m = self.ID == k
            if not m.any():
                continue
            if tex == "pelo":           # mechones finos
                fb = _fbm((n, n), 11 + k, base=8)
                hebra = 0.5 + 0.5 * np.sin(u * 140 + fb * 9)
                col[m] *= (0.7 + 0.35 * hebra[m])[:, None]
            elif tex == "rizo":         # barba / pelo rizado
                fb = _fbm((n, n), 21 + k, base=22, octavas=3)
                col[m] *= (0.62 + 0.55 * fb[m])[:, None]
            elif tex == "tela":
                fb = _fbm((n, n), 31 + k, base=40, octavas=2)
                col[m] *= (0.93 + 0.1 * fb[m])[:, None]
            elif tex == "piel":
                fb = _fbm((n, n), 41 + k, base=30, octavas=3)
                col[m] *= (0.95 + 0.08 * fb[m])[:, None]
            r = 2 * (self.N[..., 2:3] * self.N) - np.array([0, 0, 1])  # reflejo de la vista
            espec[m] = esp * np.clip((self.N @ LUZ)[m], 0, 1) ** brillo
        # oclusión ambiental: zonas más hundidas que su entorno, más oscuras
        prof = np.where(self.ID >= 0, self.Z, -1)
        ao = np.clip((_caja(prof, 6) - prof) * 2.2, 0, 0.55)
        luz = 0.38 + 0.72 * dif - ao
        img = col * luz[..., None] + espec[..., None] + 0.18 * borde[..., None] * \
            np.array([0.6, 0.75, 1.0])
        # calidez en las sombras (efecto "piel / plastilina")
        img += (1 - dif)[..., None] * np.array([0.05, 0.0, -0.02]) * (self.ID >= 0)[..., None]
        alpha = (self.ID >= 0).astype(float)
        rgba = np.dstack([np.clip(img, 0, 1), alpha])
        return rgba

    # detalles 2D sobre la imagen ya sombreada
    def mancha(self, img, c, r, color, alpha=1.0, rot=0.0, suave=0.02):
        ang = np.radians(rot)
        dx, dy = self.X - c[0], self.Y - c[1]
        u = dx * np.cos(ang) + dy * np.sin(ang)
        v = -dx * np.sin(ang) + dy * np.cos(ang)
        d = np.sqrt((u / r[0]) ** 2 + (v / r[1]) ** 2)
        a = np.clip((1 - d) / (suave / min(r)), 0, 1) * alpha
        img[..., :3] = img[..., :3] * (1 - a[..., None]) + _hex(color) * a[..., None]
        img[..., 3] = np.maximum(img[..., 3], a)

    def aro(self, img, c, r, grosor, color, alpha=1.0):
        d = np.sqrt(((self.X - c[0]) / r[0]) ** 2 + ((self.Y - c[1]) / r[1]) ** 2)
        a = np.clip(1 - np.abs(d - 1) / (grosor / min(r)), 0, 1) * alpha
        img[..., :3] = img[..., :3] * (1 - a[..., None]) + _hex(color) * a[..., None]
        img[..., 3] = np.maximum(img[..., 3], a)

    def linea(self, img, p0, p1, grosor, color, alpha=1.0):
        p0, p1 = np.array(p0), np.array(p1)
        d = p1 - p0
        t = np.clip(((self.X - p0[0]) * d[0] + (self.Y - p0[1]) * d[1]) / (d @ d), 0, 1)
        dist = np.hypot(self.X - p0[0] - t * d[0], self.Y - p0[1] - t * d[1])
        a = np.clip(1 - dist / grosor, 0, 1) ** 0.6 * alpha
        img[..., :3] = img[..., :3] * (1 - a[..., None]) + _hex(color) * a[..., None]


def _ojo(E, img_ops, c, r, iris, mira, parpado, piel, z_par=0.03, ojeras=None):
    """Globo ocular + párpado superior. Iris, pupila y brillo se pintan después."""
    E.elipsoide(c, (r, r * 0.8, r * 0.9), "#F4F1EC", brillo=40, esp=0.5)
    abierto = np.clip(parpado, 0.05, 1)
    corte = c[1] + r * 0.8 * (2 * abierto * 0.72 - 1)
    E.elipsoide((c[0], c[1] + 0.005, c[2] + z_par), (r * 1.12, r * 0.95, r * 0.9), piel,
                textura="piel", recorte=lambda X, Y: Y > corte)
    img_ops.append(("iris", (c[0] + mira[0] * r * 0.35, c[1] + mira[1] * r * 0.25), r, iris,
                    corte))


def _pintar_ojos(E, img, ops):
    for tipo, c, r, iris, corte in ops:
        visible = E.Y <= corte
        dist = np.hypot(E.X - c[0], E.Y - c[1])
        for rad, col, a in ((r * 0.55, iris, 1.0), (r * 0.25, "#0B0B0E", 1.0)):
            m = np.clip((rad - dist) / 0.006, 0, 1) * visible * (E.ID >= 0)
            # degradado del iris
            tono = _hex(col) * (0.7 + 0.5 * np.clip(dist / rad, 0, 1))[..., None]
            img[..., :3] = img[..., :3] * (1 - m[..., None]) + tono * m[..., None]
        brillo = np.hypot(E.X - c[0] + r * 0.18, E.Y - c[1] - r * 0.2)
        m = np.clip((r * 0.11 - brillo) / 0.005, 0, 1) * visible
        img[..., :3] = img[..., :3] * (1 - m[..., None]) + m[..., None]


# ----------------------------------------------------------------------- PACO
def paco(t=0.0, boca=0.0, parpado=1.0, mira=(0.3, 0.0), tam=520):
    """El cuñado (60 y pico): entradas canosas, bigote gris, gafas de leer, polo rojo."""
    PIEL, PIEL_R, CANA = "#E2A882", "#D98A6C", "#C9CCD1"
    E = Escena(tam)
    ops = []
    # cuerpo y cuello
    E.elipsoide((0, -1.15, -0.4), (0.95, 0.62, 0.45), "#B0283A", textura="tela", esp=0.05)
    E.elipsoide((0.0, -0.55, -0.15), (0.17, 0.2, 0.2), PIEL, textura="piel")
    E.elipsoide((-0.15, -0.66, -0.02), (0.16, 0.06, 0.07), "#8E1F2E", rot=-28, textura="tela")
    E.elipsoide((0.15, -0.66, -0.02), (0.16, 0.06, 0.07), "#8E1F2E", rot=28, textura="tela")
    # cabeza, orejas, papada y mofletes
    for sx in (-1, 1):
        E.elipsoide((sx * 0.4, 0.02, -0.08), (0.08, 0.13, 0.06), PIEL_R, textura="piel")
    E.elipsoide((0, 0.08, 0), (0.4, 0.52, 0.38), PIEL, textura="piel", esp=0.1)
    E.elipsoide((0, -0.36, 0.02), (0.22, 0.1, 0.24), PIEL, textura="piel")
    for sx in (-1, 1):
        E.elipsoide((sx * 0.2, -0.14, 0.26), (0.13, 0.12, 0.12), PIEL, textura="piel")
    # pelo canoso a los lados y detrás (entradas)
    for sx in (-1, 1):
        E.elipsoide((sx * 0.34, 0.26, 0.04), (0.11, 0.2, 0.18), CANA, textura="pelo",
                    rot=sx * 15, esp=0.15, brillo=20)
    # ojos (algo caídos) y cejas pobladas
    for sx in (-1, 1):
        _ojo(E, ops, (sx * 0.15, 0.12, 0.3), 0.055, "#5B3A22", mira, parpado * 0.8, PIEL)
        E.elipsoide((sx * 0.16, 0.24 + (0.03 if sx > 0 else 0), 0.34), (0.1, 0.03, 0.04),
                    CANA, rot=-sx * 8, textura="pelo")
    # nariz grande y bigote
    E.elipsoide((0, -0.02, 0.4), (0.075, 0.12, 0.1), PIEL_R, textura="piel", esp=0.18)
    for sx in (-1, 1):
        E.elipsoide((sx * 0.1, -0.14, 0.38), (0.13, 0.055, 0.06), CANA, rot=sx * 12,
                    textura="pelo", esp=0.1)
    img = E.sombrear()
    _pintar_ojos(E, img, ops)
    # boca
    ab = 0.012 + 0.05 * boca
    E.mancha(img, (0, -0.24), (0.1, 0.03 + ab * 0.8), "#B9705F", alpha=0.7, suave=0.04)
    E.mancha(img, (0, -0.24), (0.085, ab), "#4A1D22")
    if boca > 0.3:
        E.mancha(img, (0, -0.24 + ab * 0.55), (0.06, 0.012), "#F2EEE6")
    # arrugas
    for k in range(3):
        y = 0.38 + 0.05 * k
        E.linea(img, (-0.16, y), (0.16, y + 0.005), 0.006, "#A86F4F", 0.5)
    for sx in (-1, 1):
        E.linea(img, (sx * 0.23, 0.13), (sx * 0.28, 0.16), 0.005, "#A86F4F", 0.6)
        E.linea(img, (sx * 0.23, 0.1), (sx * 0.28, 0.09), 0.005, "#A86F4F", 0.6)
    # gafas de leer en la punta de la nariz
    for sx in (-1, 1):
        E.aro(img, (sx * 0.12, -0.03), (0.09, 0.055), 0.012, "#2A2D33")
    E.linea(img, (-0.03, -0.02), (0.03, -0.02), 0.01, "#2A2D33")
    return img


# --------------------------------------------------------------- PROFESOR VOLTIO
def voltio(t=0.0, boca=0.0, parpado=1.0, mira=(0.0, 0.1), tam=520):
    """Científico loco: calva alargada, mechones y barba pelirrojos, lupa de relojero en un
    ojo, pajarita morada y bata verde."""
    PIEL, PIEL_R, ROJO = "#EBC2A0", "#E0A487", "#C8541E"
    E = Escena(tam)
    ops = []
    E.elipsoide((0, -1.18, -0.4), (0.92, 0.6, 0.45), "#4FAE80", textura="tela", esp=0.05)
    for sx in (-1, 1):   # solapas
        E.elipsoide((sx * 0.2, -0.78, 0.0), (0.09, 0.25, 0.05), "#3C8E66", rot=sx * 20,
                    textura="tela")
    E.elipsoide((0, -0.58, -0.1), (0.15, 0.18, 0.18), PIEL, textura="piel")
    # cabeza alargada y orejas
    for sx in (-1, 1):
        E.elipsoide((sx * 0.36, 0.05, -0.08), (0.08, 0.13, 0.06), PIEL_R, textura="piel")
    E.elipsoide((0, 0.18, 0), (0.36, 0.6, 0.36), PIEL, textura="piel", esp=0.35, brillo=30)
    # mechones laterales disparados
    for sx in (-1, 1):
        for k in range(6):
            E.elipsoide((sx * (0.38 + 0.035 * k), 0.24 + 0.05 * k, -0.06 - 0.01 * k),
                        (0.15, 0.028, 0.03), "#D8622A" if k % 2 else ROJO,
                        rot=sx * (10 + 12 * k), textura="pelo", esp=0.15, brillo=18)
    # barba enorme y rizada
    E.elipsoide((0, -0.3, 0.12), (0.4, 0.34, 0.3), ROJO, textura="rizo", esp=0.05)
    for sx in (-1, 1):
        E.elipsoide((sx * 0.27, -0.18, 0.1), (0.16, 0.2, 0.2), ROJO, textura="rizo")
    # pajarita
    for sx in (-1, 1):
        E.elipsoide((sx * 0.09, -0.62, 0.22), (0.09, 0.055, 0.05), "#6A2BB0", rot=sx * 15,
                    esp=0.3, brillo=25)
    E.elipsoide((0, -0.62, 0.26), (0.035, 0.035, 0.03), "#8E4DD8", esp=0.3)
    # ojos: izquierdo normal, derecho tras la lupa (más grande)
    _ojo(E, ops, (-0.14, 0.15, 0.3), 0.055, "#3E7FB8", mira, parpado, PIEL)
    _ojo(E, ops, (0.15, 0.15, 0.36), 0.095, "#3E7FB8", mira, parpado, PIEL, z_par=0.04)
    for sx, alto in ((-1, 0.27), (1, 0.31)):
        E.elipsoide((sx * 0.15, alto, 0.34), (0.1, 0.03, 0.04), ROJO, rot=-sx * 15,
                    textura="pelo")
    E.elipsoide((0, 0.02, 0.38), (0.06, 0.1, 0.09), PIEL_R, textura="piel", esp=0.2)
    img = E.sombrear()
    _pintar_ojos(E, img, ops)
    # lupa de relojero: aro grueso metálico + cinta
    E.aro(img, (0.15, 0.15), (0.13, 0.13), 0.025, "#3A3F4B")
    E.aro(img, (0.15, 0.15), (0.115, 0.115), 0.006, "#9AA5B4")
    E.linea(img, (0.27, 0.2), (0.38, 0.32), 0.02, "#3A3F4B")
    # boca dentro de la barba
    ab = 0.03 + 0.06 * boca
    E.mancha(img, (0, -0.16), (0.13, ab + 0.025), "#B86A55", alpha=0.8, suave=0.04)
    E.mancha(img, (0, -0.16), (0.11, ab), "#4A1D22")
    E.mancha(img, (0, -0.16 + ab * 0.5), (0.085, 0.016), "#F2EEE6")
    return img
