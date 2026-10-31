"""Robot presentador del canal @hacerlointeligente, con esqueleto articulado.

Articulaciones: cadera, 2 vértebras, cuello, cabeza; por brazo: hombro, codo, muñeca,
3 dedos de 2 falanges y pulgar; por pierna: cadera, rodilla y tobillo (con cinemática
inversa para que los pies se queden en el suelo).

El movimiento imita a un robot de verdad: cada articulación es un "servo" que llega a su
posición con un pequeño rebote, y en una cadena (hombro → codo → muñeca → dedos) cada
articulación arranca unos milisegundos después de la anterior.

Unidades "robot": mide unas 2 unidades de alto, con el centro visual en (0, 0).
Convención de ángulos (grados): 0 = colgando hacia abajo; en los brazos, positivo = hacia
fuera del cuerpo (cada lado en espejo). Codo, muñeca: positivo = se dobla hacia dentro.
"""
import numpy as np
from matplotlib.patches import Circle, Polygon

# ------------------------------------------------------------------ paleta
BLANCO = "#EEF3F8"
BLANCO2 = "#C9D4E0"
AZUL = "#3D8BD9"
AZUL2 = "#25639F"
ARTIC = "#4B5563"     # carcasa de las articulaciones
ARTIC2 = "#9AA5B4"    # eje de la articulación
METAL = "#2B323D"
VISOR = "#0D1219"
LED = "#4CC9F0"
NUCLEO = "#FFD23F"
TINTA = "#10151D"

# ------------------------------------------------------------------ medidas
CADERA_Y = -0.16
HOMBRO_X, HOMBRO_Y = 0.30, 0.40
BRAZO, ANTEBRAZO = 0.30, 0.27
MUSLO, ESPINILLA = 0.36, 0.36
PIE_X, TOBILLO_Y = 0.19, -0.90


# ------------------------------------------------------------------ poses
def _brazos(h, c, m, d, p, i=None):
    return dict(h=h, c=c, m=m, d=d, p=p, i=d if i is None else i)


def _pose(der, izq=None, torso=0.0, cab=0.0, bob=0.0, cuello=0.0, ojos=0.0, luz=1.0):
    izq = izq or der
    out = dict(torso=torso, cab=cab, bob=bob, cuello=cuello, ojos=ojos, luz=luz)
    for lado, b in (("d", der), ("i", izq)):
        for k, v in b.items():
            out[k + lado] = v
    return out


REPOSO = _brazos(10, 18, 6, 0.35, 0.25)
POSES = {
    "apagado": _pose(_brazos(4, 4, 0, 0.55, 0.3), bob=-0.09, cuello=-0.07, cab=-4, luz=0.0),
    "reposo": _pose(REPOSO),
    "saludo": _pose(_brazos(100, -78, 0, 0.0, 0.0), REPOSO, cab=6, ojos=0.3),
    "explica": _pose(_brazos(28, -92, -10, 0.1, 0.05), _brazos(28, -92, -10, 0.1, 0.05)),
    "senala": _pose(_brazos(132, -6, -8, 0.9, 0.7, i=0.0), REPOSO, torso=-4, cab=8, ojos=0.8),
    "piensa": _pose(_brazos(-30, 150, -10, 0.85, 0.5), _brazos(18, 55, 10, 0.5, 0.3),
                    cab=10, ojos=-0.6),
    "pulgar": _pose(_brazos(32, 120, -8, 1.0, 0.0), REPOSO, cab=-5, ojos=0.0),
}
# retraso (s) de cada articulación dentro de su cadena: así se mueve "por partes"
RETRASO = {"h": 0.0, "c": 0.07, "m": 0.14, "d": 0.2, "p": 0.2, "i": 0.2,
           "torso": 0.0, "bob": 0.0, "cuello": 0.05, "cab": 0.1, "ojos": 0.12, "luz": 0.25}


def servo(x, rebote=1.1):
    """Llega rápido y se pasa un poco antes de asentarse (easeOutBack)."""
    x = np.clip(x, 0.0, 1.0)
    return 1 + (rebote + 1) * (x - 1) ** 3 + rebote * (x - 1) ** 2


def pose_en(t, guion, boca=0.0):
    """guion: [(t_inicio, nombre_pose, duración_transición)], ordenado por tiempo."""
    i = max(k for k, (tk, _n, _d) in enumerate(guion) if tk <= t) if t >= guion[0][0] else 0
    t_i, nombre, dur = guion[i]
    destino = POSES[nombre]
    origen = POSES[guion[i - 1][1]] if i > 0 else destino
    pose = {}
    for k, v in destino.items():
        clave = k[:-1] if k[:-1] in RETRASO and len(k) == 2 else k
        x = (t - t_i - RETRASO.get(clave, 0.0)) / dur
        pose[k] = origen[k] + (v - origen[k]) * servo(x)
    a = np.clip((t - t_i - 0.3) / 0.3, 0, 1)  # los gestos "vivos" entran tras la transición

    # ---- gestos con movimiento propio
    if nombre == "saludo":
        pose["md"] += a * 24 * np.sin(2 * np.pi * 2.3 * (t - t_i))
        pose["hd"] += a * 4 * np.sin(2 * np.pi * 1.15 * (t - t_i))
    if nombre == "explica":
        # movimiento lento y suave de manos mientras habla (sin tirones)
        a = 0.5 - 0.5 * np.cos(np.pi * np.clip((t - t_i - 0.3) / 1.2, 0, 1))
        for lado, fase in (("d", 0.0), ("i", 2.1)):
            pose["h" + lado] += a * 3.5 * np.sin(2 * np.pi * 0.28 * t + fase)
            pose["c" + lado] += a * 6 * np.sin(2 * np.pi * 0.35 * t + fase + 0.6)
            pose["m" + lado] += a * 5 * np.sin(2 * np.pi * 0.4 * t + fase + 1.2)
    if nombre == "senala":
        pose["hd"] += a * 2.5 * np.sin(2 * np.pi * 0.7 * t)

    # ---- vida en reposo: "respira" y gira la cabeza a golpes, como un servo
    if nombre != "apagado":
        pose["bob"] += 0.010 * np.sin(2 * np.pi * 0.45 * t)
        golpe = np.floor(t / 2.6)
        rng = np.random.default_rng(int(golpe) + 11)
        objetivo = rng.choice([-5, -2, 0, 3, 6])
        previo = np.random.default_rng(int(golpe) + 10).choice([-5, -2, 0, 3, 6])
        pose["cab"] += previo + (objetivo - previo) * servo((t - golpe * 2.6) / 0.18, 0.6)
        pose["ojos"] += 0.25 * np.sign(objetivo - previo) * np.exp(-(t - golpe * 2.6) * 3)
    return pose


# ------------------------------------------------------------------ geometría
def _dir(ang):
    a = np.radians(ang)
    return np.array([np.sin(a), -np.cos(a)])


def _rot(p, c, ang):
    a = np.radians(ang)
    ca, sa = np.cos(a), np.sin(a)
    v = np.asarray(p, float) - c
    return c + np.array([ca * v[0] - sa * v[1], sa * v[0] + ca * v[1]])


def _ik(cadera, tobillo, l1, l2, signo):
    """Rodilla de una pierna de 2 huesos (se dobla hacia fuera según `signo`)."""
    v = tobillo - cadera
    d = min(np.linalg.norm(v), l1 + l2 - 1e-4)
    u = v / (np.linalg.norm(v) + 1e-9)
    a = np.arccos(np.clip((l1 ** 2 + d ** 2 - l2 ** 2) / (2 * l1 * d), -1, 1))
    ca, sa = np.cos(a * signo), np.sin(a * signo)
    w = np.array([ca * u[0] - sa * u[1], sa * u[0] + ca * u[1]])
    return cadera + l1 * w


class Robot:
    def __init__(self, ax):
        self.ax = ax

    # ---------------------------------------------------------- primitivas
    def _tr(self, p):
        return (self.cx + p[0] * self.s, self.cy + p[1] * self.s)

    def _lw(self, w):
        x0 = self.ax.transData.transform((0, 0))[0]
        x1 = self.ax.transData.transform((self.s, 0))[0]
        return w * abs(x1 - x0) * 72 / self.ax.figure.dpi / 129.6

    def _poli(self, pts, color, borde=1.8, **kw):
        self.ax.add_patch(Polygon([self._tr(p) for p in pts], closed=True, fc=color,
                                  ec=TINTA if borde else "none", lw=self._lw(borde),
                                  joinstyle="round", **kw))

    def _circ(self, p, r, color, borde=1.8, **kw):
        self.ax.add_patch(Circle(self._tr(p), r * self.s, fc=color,
                                 ec=TINTA if borde else "none", lw=self._lw(borde), **kw))

    def _capsula(self, a, b, r0, r1=None, color=BLANCO, borde=1.8, **kw):
        r1 = r0 if r1 is None else r1
        a, b = np.asarray(a, float), np.asarray(b, float)
        d = b - a
        ang = np.arctan2(d[1], d[0])
        pts = [a + r0 * np.array([np.cos(t), np.sin(t)])
               for t in np.linspace(ang + np.pi / 2, ang + 3 * np.pi / 2, 10)]
        pts += [b + r1 * np.array([np.cos(t), np.sin(t)])
                for t in np.linspace(ang - np.pi / 2, ang + np.pi / 2, 10)]
        self._poli(pts, color, borde, **kw)

    def _caja(self, c, w, h, ang, color, r=0.04, borde=1.8, centro_giro=None, **kw):
        """Rectángulo redondeado centrado en c, girado `ang` grados alrededor de centro_giro."""
        c = np.asarray(c, float)
        pts = []
        for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
                           (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
            for t in np.radians(np.linspace(a0, a0 + 90, 6)):
                pts.append(c + [cx + r * np.cos(t), cy + r * np.sin(t)])
        g = c if centro_giro is None else np.asarray(centro_giro, float)
        self._poli([_rot(p, g, ang) for p in pts], color, borde, **kw)

    def _articulacion(self, p, r):
        self._circ(p, r, ARTIC)
        self._circ(p, r * 0.55, ARTIC2, borde=0)
        self._circ(p, r * 0.2, METAL, borde=0)

    # ---------------------------------------------------------- partes
    def _brazo(self, pose, lado, sx):
        """sx = +1 brazo a la derecha de la pantalla, -1 a la izquierda (espejo)."""
        h, c, m = pose["h" + lado], pose["c" + lado], pose["m" + lado]
        hombro = self.hombros[lado]
        a_brazo = self.torso_ang + sx * h
        codo = hombro + BRAZO * _dir(a_brazo)
        a_ante = a_brazo - sx * c
        muneca = codo + ANTEBRAZO * _dir(a_ante)
        a_mano = a_ante - sx * m

        self._capsula(hombro, codo, 0.065, 0.055, BLANCO)
        # pistón hidráulico del brazo
        n = _dir(a_brazo + 90) * 0.045 * sx
        self._capsula(hombro + n + _dir(a_brazo) * 0.06, codo + n * 0.6 - _dir(a_brazo) * 0.05,
                      0.012, 0.012, METAL, borde=0)
        self._capsula(codo, muneca, 0.055, 0.05, AZUL)
        self._capsula(codo + _dir(a_ante) * 0.06, muneca - _dir(a_ante) * 0.06, 0.018,
                      color=AZUL2, borde=0)
        self._mano(muneca, a_mano, pose["d" + lado], pose["p" + lado], pose["i" + lado], sx)
        self._articulacion(codo, 0.05)
        self._articulacion(muneca, 0.035)
        self._articulacion(hombro, 0.075)

    def _mano(self, muneca, ang, curl, pulgar, indice, sx):
        palma_c = muneca + _dir(ang) * 0.065
        self._caja(palma_c, 0.12, 0.1, ang, BLANCO, r=0.03)
        base = muneca + _dir(ang) * 0.11
        # 3 dedos: índice (lado del pulgar), corazón y anular; 2 falanges cada uno
        for k, (off, abre) in enumerate(((-0.04, -12), (0.0, 0), (0.04, 12))):
            c = indice if k == 0 else curl
            p0 = base + _dir(ang + 90) * off * sx
            a1 = ang + sx * abre - sx * 75 * c
            p1 = p0 + _dir(a1) * 0.05
            a2 = a1 - sx * 85 * c
            p2 = p1 + _dir(a2) * 0.04
            self._capsula(p0, p1, 0.016, color=BLANCO2)
            self._capsula(p1, p2, 0.014, color=BLANCO2)
        # pulgar
        p0 = muneca + _dir(ang) * 0.04 + _dir(ang + 90) * (-0.06) * sx
        a1 = ang - sx * 55 + sx * 50 * pulgar
        p1 = p0 + _dir(a1) * 0.05
        a2 = a1 + sx * 50 * pulgar
        p2 = p1 + _dir(a2) * 0.04
        self._capsula(p0, p1, 0.018, color=BLANCO2)
        self._capsula(p1, p2, 0.015, color=BLANCO2)

    def _piernas(self, cadera_c):
        for sx in (-1, 1):
            cadera = cadera_c + np.array([0.13 * sx, -0.04])
            tobillo = np.array([PIE_X * sx, TOBILLO_Y])
            rodilla = _ik(cadera, tobillo, MUSLO, ESPINILLA, signo=sx)
            self._capsula(cadera, rodilla, 0.085, 0.07, BLANCO)
            self._capsula(cadera + np.array([0.05 * sx, -0.05]),
                          rodilla + np.array([0.04 * sx, 0.06]), 0.012, color=METAL, borde=0)
            self._capsula(rodilla, tobillo, 0.07, 0.06, AZUL)
            # bota
            self._caja(tobillo + np.array([0.015 * sx, -0.055]), 0.2, 0.11, 0, BLANCO, r=0.05)
            self._caja(tobillo + np.array([0.015 * sx, -0.1]), 0.2, 0.035, 0, AZUL2, r=0.015)
            self._articulacion(rodilla, 0.06)
            self._articulacion(tobillo, 0.04)
            self._articulacion(cadera, 0.065)

    def _cabeza(self, cuello, ang, pose, boca, t):
        c = cuello + _dir(ang + 180) * 0.29
        luz = float(np.clip(pose["luz"], 0, 1))  # el servo puede pasarse de 1

        def R(p):
            return _rot(np.asarray(p, float) + c, c, ang)

        def caja(dx, dy, w, h, color, r=0.04, borde=1.8, **kw):
            self._caja(c + [dx, dy], w, h, ang, color, r=r, borde=borde, centro_giro=c, **kw)

        # módulos laterales (orejas) y antena
        for sx in (-1, 1):
            self._circ(R([0.345 * sx, 0.0]), 0.08, ARTIC)
            self._circ(R([0.345 * sx, 0.0]), 0.048, LED if luz > 0.5 else METAL, borde=0,
                       alpha=0.5 + 0.5 * luz)
        punta = R([0.22, 0.48])
        self._capsula(R([0.19, 0.27]), punta, 0.012, color=ARTIC2)
        self._circ(punta, 0.035, NUCLEO if (t % 1.2) < 0.6 and luz > 0.5 else ARTIC)
        # casco
        caja(0, 0.0, 0.68, 0.58, BLANCO, r=0.22)
        caja(0, 0.23, 0.34, 0.12, AZUL, r=0.05)
        # visor y ojos LED
        caja(0, 0.03, 0.56, 0.22, VISOR, r=0.09)
        if luz > 0.05:
            parp = 0.15 if (t % 3.3) < 0.12 else 1.0
            ox = 0.04 * np.clip(pose["ojos"], -1, 1)
            for sx in (-1, 1):
                caja(0.115 * sx + ox, 0.035, 0.095, 0.095 * parp, LED, r=0.035, borde=0,
                     alpha=min(1.0, luz))
        self._poli([R([-0.2, 0.11]), R([-0.08, 0.11]), R([-0.16, -0.05]), R([-0.24, -0.05])],
                   "#FFFFFF", borde=0, alpha=0.12)
        # boca: rejilla con barras LED tipo ecualizador que siguen a la voz
        caja(0, -0.17, 0.26, 0.09, VISOR, r=0.03)
        rng = np.random.default_rng(int(t * 30))
        for k, dx in enumerate(np.linspace(-0.08, 0.08, 5)):
            alto = 0.012 + (0.055 * boca * (0.55 + 0.45 * rng.random()) if boca > 0.05 else 0)
            alto *= (1.0 - 0.25 * abs(k - 2) / 2)
            caja(dx, -0.17, 0.022, alto, LED, r=0.008, borde=0, alpha=min(1.0, 0.4 + luz))

    # ---------------------------------------------------------- dibujo completo
    def dibujar(self, t, pose, cx, cy, s, boca=0.0):
        for a in list(self.ax.patches):
            a.remove()
        self.cx, self.cy, self.s = cx, cy, s
        self.torso_ang = pose["torso"]

        pelvis = np.array([0.0, CADERA_Y + pose["bob"]])
        self._piernas(pelvis)
        # pelvis
        self._caja(pelvis + [0, -0.02], 0.36, 0.14, 0, AZUL, r=0.05)
        # columna: 3 vértebras que siguen la inclinación del torso
        base = pelvis + [0, 0.06]
        pecho_c = _rot(base + [0, 0.32], base, self.torso_ang)
        for k in range(3):
            p = _rot(base + [0, 0.05 + 0.065 * k], base, self.torso_ang * (k + 1) / 4)
            self._caja(p, 0.2 - 0.015 * k, 0.05, self.torso_ang * (k + 1) / 4, METAL, r=0.02)
        # pecho
        pts = [[-0.3, 0.13], [0.3, 0.13], [0.27, -0.06], [0.0, -0.17], [-0.27, -0.06]]
        self._poli([_rot(pecho_c + p, pecho_c, self.torso_ang) for p in pts], BLANCO)
        self._caja(pecho_c + [0, -0.01], 0.22, 0.1, self.torso_ang, AZUL, r=0.03,
                   centro_giro=pecho_c)
        brillo = 0.55 + 0.45 * np.sin(2 * np.pi * 1.2 * t) if pose["luz"] > 0.5 else 0.15
        self._circ(_rot(pecho_c + [0, -0.01], pecho_c, self.torso_ang), 0.035, NUCLEO,
                   alpha=brillo)
        self.hombros = {lado: _rot(pecho_c + [HOMBRO_X * sx, 0.1], pecho_c, self.torso_ang)
                        for lado, sx in (("d", 1), ("i", -1))}
        # cuello (2 discos) y cabeza
        cuello = _rot(pecho_c + [0, 0.17 + pose["cuello"]], pecho_c, self.torso_ang)
        self._caja(cuello + [0, -0.02], 0.1, 0.06, self.torso_ang, METAL, r=0.02)
        self._articulacion(cuello + [0, 0.02], 0.04)
        self._cabeza(cuello + [0, 0.02], self.torso_ang + pose["cab"], pose, boca, t)
        # brazos (por delante del cuerpo)
        self._brazo(pose, "i", -1)
        self._brazo(pose, "d", 1)
