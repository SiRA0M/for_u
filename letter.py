import math
import random
import sys
import time
import numpy as np
import pygame

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
TITLE = "Special Letter 💌 3D ASCII Bloom"
WINDOW_WIDTH = 1050
WINDOW_HEIGHT = 880
FPS = 60

COLOR_BG = (0, 0, 0)

# Envelope Colors
COL_BORDER = (248, 222, 205)
COL_PAPER_MAIN = (235, 172, 132)
COL_PAPER_SHADOW = (175, 108, 78)
COL_PAPER_HIGHLIGHT = (255, 230, 198)
COL_GLOW_PURPLE = (155, 100, 235)

# Wax Seal Colors
COL_SEAL_BRIGHT = (255, 55, 145)
COL_SEAL_CORE = (255, 15, 105)
COL_SEAL_OUTER = (210, 25, 88)
COL_SEAL_SPECULAR = (255, 215, 240)

COL_POLLEN_GOLD = (255, 235, 140)
COL_STARDUST = (255, 255, 255)
COL_PINK_LIGHT = (255, 170, 220)

ASCII_CHARS_DENSE = ["8", "%", "&", "#", "S", "B", "w", "m", "Z", "X", "Q", "0"]
ASCII_CHARS_MED = ["o", "*", "a", "s", "z", "x", "e", "u", "r", "n", "v"]


# ==============================================================================
# PURE ASCII REPLAY ICON BUTTON
# ==============================================================================
class AsciiReplayButton:
    """Pure ASCII typography replay badge at bottom-left."""
    ICON_LINES = [
        " .----. ",
        "/  <-- \\",
        "\\      /",
        " '----' "
    ]

    def __init__(self, x=45, y=WINDOW_HEIGHT - 95):
        self.x = x
        self.y = y
        self.char_w = 9.5
        self.char_h = 15.0
        self.w = int(len(self.ICON_LINES[0]) * self.char_w) + 12
        self.h = int(len(self.ICON_LINES) * self.char_h) + 10
        self.rect = pygame.Rect(x - 6, y - 5, self.w, self.h)
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface, font):
        if self.is_hovered:
            col_fg = (255, 235, 180)
            col_accent = (255, 80, 160)
            col_bg = (35, 20, 45)
            col_border = (200, 120, 220)
        else:
            col_fg = (210, 180, 235)
            col_accent = (180, 100, 210)
            col_bg = (20, 14, 28)
            col_border = (80, 55, 105)

        pygame.draw.rect(surface, col_bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, col_border, self.rect, 1, border_radius=8)

        for r_idx, line in enumerate(self.ICON_LINES):
            py = self.y + r_idx * self.char_h
            for c_idx, ch in enumerate(line):
                if ch != " ":
                    px = self.x + c_idx * self.char_w
                    color = col_accent if ch in ["<", "-"] else col_fg
                    t_surf = font.render(ch, True, color)
                    surface.blit(t_surf, (int(px), int(py)))


# ==============================================================================
# 2D ENVELOPE GENERATOR
# ==============================================================================
class Envelope2D:
    def __init__(self, cx, cy, width=760.0, height=450.0):
        self.cx = cx
        self.cy = cy
        self.w = width
        self.h = height

        self.char_w = 9.0
        self.char_h = 14.8
        self.cols = int(self.w / self.char_w)
        self.rows = int(self.h / self.char_h)

        self.left = cx - width / 2.0
        self.top = cy - height / 2.0

        self.cells = []
        self._build_envelope()

    def _build_envelope(self):
        rng = random.Random(42)

        for r in range(self.rows):
            y = self.top + r * self.char_h
            ny = r / (self.rows - 1)

            for c in range(self.cols):
                x = self.left + c * self.char_w
                nx = c / (self.cols - 1)

                is_top = (r == 0)
                is_bot = (r == self.rows - 1)
                is_left = (c == 0)
                is_right = (c == self.cols - 1)

                dx = abs(nx - 0.5) * 2.0
                top_flap_crease = abs(ny - (1.0 - dx) * 0.5) < 0.032 and ny <= 0.52
                bot_flap_crease = abs((1.0 - ny) - (1.0 - dx) * 0.5) < 0.032 and ny >= 0.48

                seal_dx = (x - self.cx) / 36.0
                seal_dy = (y - self.cy) / 32.0
                sy = -seal_dy - 0.15
                sx = seal_dx
                heart_eq = (sx * sx + sy * sy - 1.0) ** 3 - sx * sx * (sy ** 3)
                is_seal = heart_eq <= 0.05
                is_seal_edge = abs(heart_eq) <= 0.12

                if is_top or is_bot:
                    char = "/" if (c % 2 == 0) else "\\"
                    color = COL_BORDER
                elif is_left:
                    char = "\\"
                    color = COL_BORDER
                elif is_right:
                    char = "/"
                    color = (205, 175, 245)
                elif is_seal:
                    if is_seal_edge:
                        char = rng.choice(["♥", "#", "@", "%"])
                        color = COL_SEAL_OUTER
                    elif sy > 0.3 and sx < 0.1:
                        char = rng.choice(["*", "+", "♥"])
                        color = COL_SEAL_SPECULAR
                    else:
                        char = rng.choice(["♥", "@", "#", "8", "%"])
                        color = rng.choice([COL_SEAL_BRIGHT, COL_SEAL_CORE])
                elif top_flap_crease or bot_flap_crease:
                    char = "/" if (nx > 0.5) else "\\"
                    color = COL_PAPER_HIGHLIGHT
                else:
                    if ny < (1.0 - dx) * 0.5:
                        char = rng.choice(ASCII_CHARS_DENSE)
                        base_col = COL_PAPER_MAIN
                    else:
                        char = rng.choice(ASCII_CHARS_DENSE if ny < 0.74 else ASCII_CHARS_MED)
                        base_col = COL_PAPER_MAIN if ny < 0.74 else COL_PAPER_SHADOW

                    jitter = rng.uniform(-14, 14)
                    r_c = max(0, min(255, int(base_col[0] + jitter)))
                    g_c = max(0, min(255, int(base_col[1] + jitter)))
                    b_c = max(0, min(255, int(base_col[2] + jitter)))

                    if nx > 0.85:
                        p_factor = (nx - 0.85) / 0.15
                        r_c = int(r_c * (1 - p_factor * 0.4) + COL_GLOW_PURPLE[0] * p_factor * 0.4)
                        g_c = int(g_c * (1 - p_factor * 0.4) + COL_GLOW_PURPLE[1] * p_factor * 0.4)
                        b_c = int(b_c * (1 - p_factor * 0.4) + COL_GLOW_PURPLE[2] * p_factor * 0.4)
                    color = (r_c, g_c, b_c)

                self.cells.append({
                    "x": x,
                    "y": y,
                    "char": char,
                    "color": color,
                    "is_seal": is_seal,
                })


# ==============================================================================
# 3D ASCII BLOOM RENDERER (Adapted from edwardjones7/ascii-art bloom3d.py, MIT)
# ==============================================================================
class Bloom3DRenderer:
    """3D volumetric ASCII flower that blooms, breathes, and blows away."""
    FONT_SIZE = 10
    DURATION = 10.0
    BLOW_START = 7.6
    MESSAGE = "for per "
    RAMP = ".:;=+*xo%#&@"
    GLITCH = "01<>{}[]#$%&*+=?!ABXZ"
    ELEV = math.radians(55)
    SCALE = 295.0

    LAYERS = [
        (6, 1.00, 0.34, 80, 2.0, 5.2, 0.70, 0.00, 1.00),
        (6, 0.80, 0.30, 58, 2.3, 5.5, 0.50, math.pi / 6, 0.95),
        (5, 0.62, 0.27, 40, 2.6, 5.8, 0.35, 0.30, 0.90),
        (4, 0.46, 0.24, 26, 2.9, 6.1, 0.20, 0.90, 0.85),
    ]

    def __init__(self, width, height):
        self.W = width
        self.H = height
        self.CY = self.H / 2.0

        self.font = pygame.font.SysFont(
            "consolas,menlo,dejavusansmono,liberationmono,couriernew",
            self.FONT_SIZE,
            bold=True,
        )
        self.cw, self.ch = self.font.size("M")
        self.COLS = self.W // self.cw
        self.ROWS = self.H // self.ch

        self.RAMP_ARR = np.array(list(self.RAMP))
        self.LETTERS = np.array([c for c in self.MESSAGE if c != " "])
        self.MSG_GRID = np.array(
            [[self.MESSAGE[(r * self.COLS + c) % len(self.MESSAGE)] for c in range(self.COLS)]
             for r in range(self.ROWS)]
        )

        self.rng = np.random.default_rng(11)
        self.gen = np.random.default_rng(5)
        self.SETTLE = 0.12 + self.rng.random((self.ROWS, self.COLS)) * 0.5

        self.U, self.V = 64, 45
        self.uu = np.linspace(0, 1, self.U)[None, :, None]
        self.vv = np.linspace(-1, 1, self.V)[None, None, :]

        # Build petal layers
        pet = {k: [] for k in ("theta", "L", "W", "open", "t0", "t1", "curl", "tint", "delay")}
        for li, (n, L, Wd, op, t0, t1, curl, az, tint) in enumerate(self.LAYERS):
            for k in range(n):
                pet["theta"].append(az + 2 * math.pi * k / n + self.rng.uniform(-0.08, 0.08))
                pet["L"].append(L * self.rng.uniform(0.95, 1.05))
                pet["W"].append(Wd)
                pet["open"].append(math.radians(op))
                pet["t0"].append(t0 + self.rng.uniform(-0.1, 0.1))
                pet["t1"].append(t1)
                pet["curl"].append(curl)
                pet["tint"].append(tint * self.rng.uniform(0.8, 1.1))
                pet["delay"].append(self.BLOW_START + 0.22 * li + self.rng.uniform(0, 0.35))
        self.pet = {k: np.array(v) for k, v in pet.items()}
        self.P = len(self.pet["theta"])
        self.NPET = self.P * self.U * self.V

        self.JIT = self.rng.normal(size=(self.NPET, 3)) * np.array([0.6, 0.6, 0.9])
        self.PID = self.rng.integers(0, 10_000, self.NPET)

        # Petal color stops (deep crimson -> vivid pink -> soft blush)
        stops = np.array([
            [0.70, 0.02, 0.20],
            [1.00, 0.12, 0.38],
            [1.00, 0.42, 0.62],
            [1.00, 0.80, 0.84],
        ])
        cu = np.linspace(0, 1, self.U) * (len(stops) - 1)
        i0 = np.minimum(cu.astype(int), len(stops) - 2)
        fr = (cu - i0)[:, None]
        ucol = stops[i0] * (1 - fr) + stops[i0 + 1] * fr
        self.PCOL = (
            ucol[None, :, None, :] * self.pet["tint"][:, None, None, None]
            * np.ones((1, 1, self.V, 1))
        ).reshape(-1, 3)

        self.AO = (
            (0.25 + 0.75 * np.linspace(0, 1, self.U) ** 0.8)[None, :, None]
            * (1 - 0.35 * np.abs(np.linspace(-1, 1, self.V)) ** 3)[None, None, :]
            * np.ones((self.P, 1, 1))
        ).reshape(-1)

        # Fibonacci spiral stamen center
        self.NC = 2600
        kk = np.arange(self.NC)
        self.C_R = np.sqrt((kk + 0.5) / self.NC)
        self.C_A = kk * 2.39996323
        self.C_JIT = self.rng.normal(size=(self.NC, 3)) * np.array([0.5, 0.5, 0.9])
        self.C_PID = self.rng.integers(0, 10_000, self.NC)
        self.C_COL = (
            np.array([1.0, 0.85, 0.35]) * (1 - self.C_R[:, None])
            + np.array([1.0, 0.45, 0.08]) * self.C_R[:, None]
        )
        self.C_DELAY = self.BLOW_START + 1.15

        light = np.array([-0.45, -0.75, 0.9])
        self.CAM_D = np.array([0.0, -math.cos(self.ELEV), math.sin(self.ELEV)])
        self.CAM_UP = np.array([0.0, math.sin(self.ELEV), math.cos(self.ELEV)])
        self.LIGHT_N = light / np.linalg.norm(light)
        self.HALF = (self.LIGHT_N + self.CAM_D) / np.linalg.norm(self.LIGHT_N + self.CAM_D)
        self.WIND = np.array([1.7, 0.0, 0.75])

        self.first_on = np.full((self.ROWS, self.COLS), np.inf)
        self.last_t = 0.0
        self.glyph_cache = {}

    @staticmethod
    def _ss(a, b, x):
        k = np.clip((x - a) / (b - a), 0.0, 1.0)
        return k * k * (3 - 2 * k)

    def _glyph(self, chr_, rgb):
        key = (chr_, rgb)
        s = self.glyph_cache.get(key)
        if s is None:
            s = self.font.render(chr_, True, rgb)
            self.glyph_cache[key] = s
        return s

    def reset(self):
        self.first_on[:] = np.inf
        self.last_t = 0.0

    def _petals(self, t):
        prog = self._ss(self.pet["t0"], self.pet["t1"], t)
        alpha = np.radians(6) + (self.pet["open"] - np.radians(6)) * prog
        phi = (
            alpha[:, None, None] * (0.25 + 0.75 * self.uu)
            + (self.pet["curl"] * prog)[:, None, None] * self.uu ** 2
        )
        du = 1 / (self.U - 1)
        Lr = self.pet["L"][:, None, None]
        rho = np.cumsum(np.sin(phi), axis=1) * du * Lr
        z = np.cumsum(np.cos(phi), axis=1) * du * Lr
        w = self.pet["W"][:, None, None] * np.sin(np.pi * self.uu ** 1.6) ** 0.7
        off_t = self.vv * w
        off_n = 0.55 * self.vv ** 2 * w
        R = 0.04 + rho - off_n * np.cos(phi)
        Z = z + off_n * np.sin(phi)
        th = self.pet["theta"][:, None, None]
        x = R * np.cos(th) - off_t * np.sin(th)
        y = R * np.sin(th) + off_t * np.cos(th)
        pts = np.stack(np.broadcast_arrays(x, y, Z), axis=-1)
        n = np.cross(np.gradient(pts, axis=1), np.gradient(pts, axis=2))
        n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
        delay = np.repeat(self.pet["delay"], self.U * self.V)
        return pts.reshape(-1, 3), n.reshape(-1, 3), delay

    def _centre(self, t):
        rc = 0.17 * self._ss(3.0, 5.5, t)
        r = self.C_R * rc
        pts = np.stack(
            [r * np.cos(self.C_A), r * np.sin(self.C_A),
             0.10 + 0.10 * (1 - self.C_R ** 2) * self._ss(3, 5.5, t)],
            -1,
        )
        n = np.stack(
            [np.cos(self.C_A) * self.C_R * 0.7, np.sin(self.C_A) * self.C_R * 0.7, np.ones(self.NC)],
            -1,
        )
        n /= np.linalg.norm(n, axis=-1, keepdims=True)
        return pts, n

    def _rasterize(self, t, t_rot=None):
        if t_rot is None:
            t_rot = t
        t_growth = min(6.0, t)
        pp, pn, pdelay = self._petals(t_growth)
        cp, cn = self._centre(t_growth)
        pos = np.concatenate([pp, cp])
        nrm = np.concatenate([pn, cn])
        col = np.concatenate([self.PCOL, self.C_COL])
        delay = np.concatenate([pdelay, np.full(self.NC, self.C_DELAY)])
        jit = np.concatenate([self.JIT, self.C_JIT])
        ao = np.concatenate([self.AO, np.ones(self.NC)])
        pid = np.concatenate([self.PID, self.C_PID])

        s = self._ss(0.9, 2.6, t_growth) * (1 + 0.02 * math.sin(t_rot * 2.2))
        if s <= 0:
            return None
        pos = pos * s

        yaw = 0.4 + 0.35 * t_rot
        cy_, sy_ = math.cos(yaw), math.sin(yaw)
        rot = np.array([[cy_, -sy_, 0], [sy_, cy_, 0], [0, 0, 1]])
        pos = pos @ rot.T
        nrm = nrm @ rot.T

        tau = np.maximum(0.0, t_growth - delay)
        brk = np.maximum(0.0, tau - 0.3)
        pos = pos + self.WIND * (tau ** 2)[:, None] * 1.5 + jit * (brk ** 1.5 * 0.9)[:, None]
        pos[:, 2] += 0.1 * np.sin(tau * 5 + pid % 7) * brk
        keep = (brk == 0) | (pid % 9 == 0)
        fade = np.clip(1 - tau / 1.5, 0, 1) * keep
        flying = brk > 0

        depth = pos @ self.CAM_D
        nd = nrm @ self.CAM_D
        nrm = np.where((nd < 0)[:, None], -nrm, nrm)
        nd = np.abs(nd)
        diff = np.maximum(nrm @ self.LIGHT_N, 0)
        spec = np.maximum(nrm @ self.HALF, 0) ** 24
        lum = (0.25 + 0.95 * diff + 0.3 * (1 - nd) ** 2) * (0.35 + 0.65 * ao)
        dof = 0.55 + 0.45 * np.clip((depth + 0.8) / 1.6, 0, 1)
        rgb = (col * lum[:, None] * 1.2 + 0.45 * spec[:, None]) * (dof * fade)[:, None]
        lumt = np.clip((lum + 0.45 * spec) * dof * fade, 0, 1)

        k = 5.0 / (5.0 - depth)
        sx = pos[:, 0] * k
        sy = (pos @ self.CAM_UP) * k
        c = ((self.W / 2 + sx * self.SCALE) / self.cw).astype(int)
        r = ((self.CY - sy * self.SCALE) / self.ch).astype(int)
        ok = (c >= 0) & (c < self.COLS) & (r >= 0) & (r < self.ROWS) & (fade > 0)
        idx = np.nonzero(ok)[0]
        ids = r[idx] * self.COLS + c[idx]
        order = np.argsort(-depth[idx], kind="stable")
        uid, first = np.unique(ids[order], return_index=True)
        win = idx[order[first]]

        Lg = np.zeros(self.ROWS * self.COLS)
        Cg = np.zeros((self.ROWS * self.COLS, 3))
        Dg = np.full(self.ROWS * self.COLS, -3.0)
        Fg = np.zeros(self.ROWS * self.COLS, bool)
        Pg = np.zeros(self.ROWS * self.COLS, int)
        Lg[uid] = lumt[win]
        Cg[uid] = rgb[win]
        Dg[uid] = depth[win]
        Fg[uid] = flying[win]
        Pg[uid] = pid[win]
        sh = (self.ROWS, self.COLS)
        return Lg.reshape(sh), Cg.reshape(sh + (3,)), Dg.reshape(sh), Fg.reshape(sh), Pg.reshape(sh)

    def _edge_chars(self, filled, D):
        F = np.where(filled, D, -3.0)
        Fp = np.pad(F, 1, constant_values=-3.0)
        nbs = [Fp[1:-1, 2:], Fp[1:-1, :-2], Fp[2:, 1:-1], Fp[:-2, 1:-1]]
        jump = np.max([np.abs(F - nb) for nb in nbs], axis=0)
        edge = filled & (jump > 0.35) & ((jump > 2.0) | (F >= np.max(nbs, axis=0)))
        gx = (Fp[1:-1, 2:] - Fp[1:-1, :-2]) / self.cw
        gy = (Fp[2:, 1:-1] - Fp[:-2, 1:-1]) / self.ch
        a = np.degrees(np.arctan2(-gx, -gy)) % 180
        ech = np.select([(a < 22.5) | (a >= 157.5), a < 67.5, a < 112.5], ["-", "/", "|"], "\\")
        return edge, ech

    def render(self, surface, t, t_rot=None):
        if t < self.last_t:
            self.first_on[:] = np.inf
        self.last_t = t

        blits = []
        res = self._rasterize(t, t_rot=t_rot)
        if res is not None:
            Lg, Cg, Dg, Fg, Pg = res
            filled = Lg > 0.03
            edge, ech = self._edge_chars(filled, Dg)
            edge &= ~Fg

            chars = self.RAMP_ARR[np.clip((Lg * (len(self.RAMP) - 1)).astype(int), 0, len(self.RAMP) - 1)]
            chars = np.where(Lg > 0.86, self.MSG_GRID, chars)
            chars = np.where(edge, ech, chars)
            chars = np.where(Fg, self.LETTERS[Pg % len(self.LETTERS)], chars)

            colr = np.where(edge[..., None], Cg * 1.25 + 0.06, Cg)

            if t < 5.5:
                self.first_on[filled & np.isinf(self.first_on)] = t
                self.first_on[~filled] = np.inf
                glitching = filled & ((t - self.first_on) < self.SETTLE)
                colr = np.where(glitching[..., None], colr * 0.5 + 0.45, colr)
            else:
                glitching = np.zeros_like(filled)

            colr = (np.clip(colr, 0, 1) * 255 // 10 * 10).astype(int)
            rows_i, cols_i = np.nonzero(filled)
            for rr, cc in zip(rows_i.tolist(), cols_i.tolist()):
                chr_ = self.GLITCH[self.gen.integers(len(self.GLITCH))] if glitching[rr, cc] else chars[rr, cc]
                if chr_ == " ":
                    continue
                rgb = (int(colr[rr, cc, 0]), int(colr[rr, cc, 1]), int(colr[rr, cc, 2]))
                if rgb == (0, 0, 0):
                    continue
                blits.append((self._glyph(chr_, rgb), (cc * self.cw, rr * self.ch)))

        if blits:
            surface.blits(blits, doreturn=False)

        # Two-pass additive bloom glow
        for div in (5, 18):
            small = pygame.transform.smoothscale(surface, (self.W // div, self.H // div))
            surface.blit(pygame.transform.smoothscale(small, (self.W, self.H)), (0, 0),
                         special_flags=pygame.BLEND_ADD)


# ==============================================================================
# 2D FLOATING PARTICLES (For Envelope & Transition)
# ==============================================================================
class Particle2D:
    def __init__(self, x, y, kind="sparkle", color=None, vx=None, vy=None):
        self.x = x
        self.y = y
        self.kind = kind
        self.char = random.choice(ASCII_CHARS_MED) if kind == "star" else random.choice(["*", "·", "•", "✧", "+"])
        self.color = color or random.choice([COL_POLLEN_GOLD, COL_STARDUST, COL_PINK_LIGHT])

        self.vx = vx if vx is not None else random.uniform(-1.4, 1.4)
        self.vy = vy if vy is not None else random.uniform(-2.2, -0.6)
        self.lifespan = random.randint(45, 95)
        self.age = 0
        self.alive = True
        self.wobble_freq = random.uniform(2.0, 5.0)

    def update(self):
        self.x += self.vx + math.sin(self.age * 0.08 * self.wobble_freq) * 0.8
        self.y += self.vy
        self.age += 1
        if self.age >= self.lifespan:
            self.alive = False

    def draw(self, surface, font):
        alpha = math.sin((self.age / self.lifespan) * math.pi)
        if alpha <= 0.05:
            return
        r = int(self.color[0] * alpha)
        g = int(self.color[1] * alpha)
        b = int(self.color[2] * alpha)
        t_surf = font.render(self.char, True, (r, g, b))
        surface.blit(t_surf, (int(self.x), int(self.y)))


# ==============================================================================
# MAIN APPLICATION ENGINE
# ==============================================================================
def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    font_mono = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 13, bold=True)
    font_btn = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 14, bold=True)

    center_x = WINDOW_WIDTH // 2
    center_y = WINDOW_HEIGHT // 2 - 10
    envelope = Envelope2D(center_x, center_y, width=760.0, height=450.0)
    bloom = Bloom3DRenderer(WINDOW_WIDTH, WINDOW_HEIGHT)
    replay_btn = AsciiReplayButton(x=45, y=WINDOW_HEIGHT - 95)

    # Precompute radial swirl targets toward center for envelope dissolve
    total_pts = len(envelope.cells)
    sorted_cells = sorted(
        envelope.cells,
        key=lambda c: math.hypot(c["x"] - center_x, c["y"] - center_y),
    )
    max_dist = max(math.hypot(c["x"] - center_x, c["y"] - center_y) for c in sorted_cells)
    delays = [
        (math.hypot(c["x"] - center_x, c["y"] - center_y) / (max_dist + 1e-4)) * 0.45
        for c in sorted_cells
    ]

    rng_ctrl = random.Random(777)
    morph_targets = []
    for c in sorted_cells:
        ang = rng_ctrl.uniform(0, 2 * math.pi)
        rad = rng_ctrl.uniform(10.0, 95.0)
        morph_targets.append((
            center_x + math.cos(ang) * rad,
            WINDOW_HEIGHT / 2.0 + math.sin(ang) * rad * 0.7,
        ))

    STATE_WAITING = 0
    STATE_OPENING = 1
    STATE_MORPHING = 2
    STATE_BLOOM = 3

    state = STATE_WAITING
    state_start_time = time.time()
    particles = []

    running = True
    while running:
        clock.tick(FPS)
        now = time.time()
        time_in_state = now - state_start_time
        mouse_pos = pygame.mouse.get_pos()

        if state == STATE_BLOOM:
            replay_btn.update(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if state == STATE_WAITING:
                        state = STATE_OPENING
                        state_start_time = now
                    elif state == STATE_BLOOM:
                        bloom.reset()
                        state_start_time = now
            elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
                click_pos = (
                    event.pos
                    if event.type == pygame.MOUSEBUTTONDOWN
                    else (int(event.x * WINDOW_WIDTH), int(event.y * WINDOW_HEIGHT))
                )
                if state == STATE_WAITING:
                    state = STATE_OPENING
                    state_start_time = now
                elif state == STATE_BLOOM and replay_btn.rect.collidepoint(click_pos):
                    state = STATE_WAITING
                    state_start_time = now
                    particles.clear()
                    bloom.reset()

        screen.fill(COLOR_BG)

        if state == STATE_WAITING:
            seal_pulse = 1.0 + 0.08 * math.sin(now * 5.0)
            for cell in envelope.cells:
                cx, cy = cell["x"], cell["y"]
                if cell["is_seal"]:
                    cx = center_x + (cx - center_x) * seal_pulse
                    cy = center_y + (cy - center_y) * seal_pulse
                t_surf = font_mono.render(cell["char"], True, cell["color"])
                screen.blit(t_surf, (int(cx), int(cy)))

            if random.random() < 0.22:
                particles.append(Particle2D(
                    center_x + random.uniform(-35, 35),
                    center_y + random.uniform(-25, 25),
                    kind="sparkle",
                    color=COL_POLLEN_GOLD,
                ))

        elif state == STATE_OPENING:
            if time_in_state < 0.06:
                for _ in range(85):
                    ang = random.uniform(0, 2 * math.pi)
                    spd = random.uniform(4.0, 10.0)
                    particles.append(Particle2D(
                        center_x, center_y,
                        kind=random.choice(["sparkle", "star"]),
                        color=random.choice([COL_SEAL_BRIGHT, COL_POLLEN_GOLD, COL_STARDUST, COL_PINK_LIGHT]),
                        vx=math.cos(ang) * spd,
                        vy=math.sin(ang) * spd - 2.0,
                    ))

            shake_x = random.uniform(-2.5, 2.5)
            shake_y = random.uniform(-2.5, 2.5)
            for cell in envelope.cells:
                t_surf = font_mono.render(cell["char"], True, cell["color"])
                screen.blit(t_surf, (int(cell["x"] + shake_x), int(cell["y"] + shake_y)))

            if time_in_state > 0.38:
                state = STATE_MORPHING
                state_start_time = now
                bloom.reset()

        elif state == STATE_MORPHING:
            morph_dur = 1.8
            raw_t = min(1.0, time_in_state / morph_dur)

            # Fade envelope characters inward into the bloom seed
            for i in range(total_pts):
                d = delays[i]
                if raw_t <= d:
                    loc_t = 0.0
                else:
                    loc_t = min(1.0, (raw_t - d) / (1.0 - d + 1e-5))
                ease = loc_t * loc_t * (3.0 - 2.0 * loc_t)
                if ease >= 0.96:
                    continue

                p0 = (sorted_cells[i]["x"], sorted_cells[i]["y"])
                p2 = morph_targets[i]
                curr_x = p0[0] + (p2[0] - p0[0]) * ease
                curr_y = p0[1] + (p2[1] - p0[1]) * ease

                fade = 1.0 - ease
                src_col = sorted_cells[i]["color"]
                col = (int(src_col[0] * fade), int(src_col[1] * fade), int(src_col[2] * fade))
                ch = sorted_cells[i]["char"] if ease < 0.5 else random.choice(Bloom3DRenderer.GLITCH)
                t_surf = font_mono.render(ch, True, col)
                screen.blit(t_surf, (int(curr_x), int(curr_y)))

            # Start growing Bloom3D smoothly during morph
            if raw_t > 0.45:
                bloom_t = 0.9 + (raw_t - 0.45) * 1.8
                bloom.render(screen, bloom_t, t_rot=bloom_t)

            if raw_t >= 1.0:
                state = STATE_BLOOM
                state_start_time = now

        elif state == STATE_BLOOM:
            t_growth = min(6.0, 1.89 + time_in_state * 1.5)
            t_rot = 1.89 + time_in_state * 0.95
            bloom.render(screen, t_growth, t_rot=t_rot)
            replay_btn.draw(screen, font_btn)

            if random.random() < 0.28:
                rx = center_x + random.uniform(-140, 140)
                ry = WINDOW_HEIGHT / 2.0 + random.uniform(-120, 360)
                particles.append(Particle2D(
                    rx, ry,
                    kind="sparkle",
                    color=random.choice([COL_POLLEN_GOLD, COL_STARDUST, COL_PINK_LIGHT])
                ))

        # Render 2D particles
        alive_p = []
        for p in particles:
            p.update()
            if p.alive:
                p.draw(screen, font_mono)
                alive_p.append(p)
        particles = alive_p

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
