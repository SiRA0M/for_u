import math
import random
import sys
import time
import pygame

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
TITLE = "Special Letter 💌 Single Rose"
WINDOW_WIDTH = 1050
WINDOW_HEIGHT = 850
FPS = 60

# ------------------------------------------------------------------------------
# COLOR PALETTE (RGB)
# ------------------------------------------------------------------------------
COLOR_BG = (10, 8, 16)

# Envelope Colors (Warm Peach / Sepia / Gold with Purple Rim)
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

# Single Rose Colors (Deep Velvet Crimson -> Radiant Pink -> Champagne)
COL_ROSE_DEEP = (130, 8, 35)         # Center core
COL_ROSE_VELVET = (195, 15, 50)      # Inner whorl
COL_ROSE_RED = (235, 28, 68)         # Mid petals
COL_ROSE_CORAL = (255, 88, 140)      # Flared petals
COL_ROSE_CHAMPAGNE = (255, 200, 220)  # Petal edge tips

# Stem & Leaf Colors
COL_STEM_DEEP = (32, 95, 45)
COL_STEM_LIGHT = (62, 155, 78)
COL_THORN = (130, 60, 50)
COL_SEPAL = (45, 125, 60)

COL_LEAF_DARK = (42, 115, 55)
COL_LEAF_MID = (68, 165, 85)
COL_LEAF_BRIGHT = (105, 205, 125)
COL_LEAF_VEIN = (145, 230, 160)

# Sparkles & Dewdrops
COL_GOLD_SPARK = (255, 235, 145)
COL_WHITE_SPARK = (255, 255, 255)
COL_DEW_GLOW = (220, 240, 255)

# Character sets
ASCII_CHARS_DENSE = ["8", "%", "&", "#", "S", "B", "w", "m", "Z", "X", "Q", "0"]
ASCII_CHARS_MED = ["o", "*", "a", "s", "z", "x", "e", "u", "r", "n", "v"]
SPARKLE_CHARS = ["*", "+", "·", "✧", "✦", "°", "•", "♡", "❀"]


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
            col_fg = (255, 235, 180)     # Glowing gold
            col_accent = (255, 80, 160)  # Vivid pink arrow
            col_bg = (35, 20, 45)
            col_border = (200, 120, 220)
        else:
            col_fg = (210, 180, 235)     # Soft lavender
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
                    color = col_accent if ch in ["<", "-", "-"] else col_fg
                    t_surf = font.render(ch, True, color)
                    surface.blit(t_surf, (int(px), int(py)))


# ==============================================================================
# 2D ENVELOPE GENERATOR (High-Detail Matching User Photo)
# ==============================================================================
class Envelope2D:
    def __init__(self, cx, cy, width=750.0, height=445.0):
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
                
                # Wax Seal Math
                seal_dx = (x - self.cx) / 36.0
                seal_dy = (y - self.cy) / 32.0
                sy = -seal_dy - 0.15
                sx = seal_dx
                heart_eq = (sx*sx + sy*sy - 1.0)**3 - sx*sx * (sy**3)
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

                # Is point on top folding flap
                is_flap = (ny < (1.0 - dx) * 0.5) and not is_top
                
                self.cells.append({
                    "x": x,
                    "y": y,
                    "orig_x": x,
                    "orig_y": y,
                    "char": char,
                    "color": color,
                    "is_seal": is_seal,
                    "is_flap": is_flap,
                })


# ==============================================================================
# GRAND SINGLE ROSE GENERATOR (2D With Botanical Details)
# ==============================================================================
class SingleRose2D:
    """Generates 2D coordinates for a grand single rose with head, stem, thorns & leaves."""
    def __init__(self, cx, cy, total_points=2200):
        self.cx = cx
        self.cy = cy
        self.total_points = total_points
        self.points = []
        self._generate_rose()

    def _generate_rose(self):
        rng = random.Random(404)
        pts_list = []

        # ----------------------------------------------------------------------
        # 1. STEM & THORNS (S-Curved Botanical Stem)
        # ----------------------------------------------------------------------
        stem_top_y = self.cy - 15.0
        stem_bot_y = self.cy + 270.0
        num_stem = int(self.total_points * 0.14)
        
        for _ in range(num_stem):
            u = rng.uniform(0.0, 1.0)
            y = stem_top_y + u * (stem_bot_y - stem_top_y)
            # Gentle elegant S-curve formula
            curve_x = math.sin(u * math.pi * 1.4) * 22.0 - (u * 12.0)
            stem_cx = self.cx + curve_x
            
            # Stem thickness (wider at base)
            thickness = 6.0 + (1.0 - u) * 4.0
            x_off = rng.uniform(-thickness / 2.0, thickness / 2.0)
            
            col = COL_STEM_LIGHT if x_off > 0.5 else COL_STEM_DEEP
            ch = rng.choice(["|", "!", ":", "#", "%"])
            
            pts_list.append({
                "base_x": stem_cx + x_off,
                "base_y": y,
                "part": "stem",
                "u": u,
                "char": ch,
                "color": col
            })

        # Thorns along stem
        thorn_configs = [
            (0.35, -1, 14.0),  # (u_along_stem, direction_left_right, length)
            (0.60, 1, 15.0),
            (0.82, -1, 12.0),
        ]
        num_thorns = int(self.total_points * 0.03)
        for _ in range(num_thorns):
            tc = rng.choice(thorn_configs)
            tu, tdir, tlen = tc
            ty = stem_top_y + tu * (stem_bot_y - stem_top_y)
            curve_x = math.sin(tu * math.pi * 1.4) * 22.0 - (tu * 12.0)
            stem_cx = self.cx + curve_x
            
            v = rng.uniform(0.1, 1.0)
            tx = stem_cx + tdir * (5.0 + v * tlen)
            py = ty + (v * v) * 7.0  # Curved downward hook of a thorn
            
            pts_list.append({
                "base_x": tx,
                "base_y": py,
                "part": "thorn",
                "u": tu,
                "char": ">" if tdir > 0 else "<",
                "color": COL_THORN
            })

        # ----------------------------------------------------------------------
        # 2. GREEN SEPALS (Calyx Embracing Blossom Base)
        # ----------------------------------------------------------------------
        num_sepals = int(self.total_points * 0.06)
        sepal_angles = [-1.3, -0.7, 0.0, 0.7, 1.3]
        for _ in range(num_sepals):
            sang = rng.choice(sepal_angles)
            u = rng.uniform(0.1, 1.0)
            slen = rng.uniform(22.0, 36.0)
            swid = 8.0 * (1.0 - u)
            
            # Pointing downward and curling out
            sx = self.cx + math.sin(sang) * (u * slen) + rng.uniform(-swid, swid)
            sy = stem_top_y + math.cos(sang) * (u * slen * 0.7) + (u * 10.0)
            
            pts_list.append({
                "base_x": sx,
                "base_y": sy,
                "part": "sepal",
                "u": 0.05,
                "char": rng.choice(["v", "V", "|", ";"]),
                "color": COL_SEPAL
            })

        # ----------------------------------------------------------------------
        # 3. SERRATED ROSE LEAVES (Left & Right Branches)
        # ----------------------------------------------------------------------
        num_leaves = int(self.total_points * 0.22)
        leaf_clusters = [
            # (stem_u, angle_rad, length, width, side)
            (0.38, -0.65, 95.0, 48.0, -1),  # Upper-left leaf branch
            (0.58, 0.60, 100.0, 52.0, 1),   # Mid-right leaf branch
            (0.78, -0.55, 80.0, 42.0, -1),  # Lower-left small leaf
        ]

        for _ in range(num_leaves):
            lc = rng.choice(leaf_clusters)
            lu, lang, llen, lwid, lside = lc
            
            # Anchor on stem
            ly = stem_top_y + lu * (stem_bot_y - stem_top_y)
            curve_x = math.sin(lu * math.pi * 1.4) * 22.0 - (lu * 12.0)
            lx = self.cx + curve_x
            
            # Leaf profile (pointed oval)
            u = rng.uniform(0.08, 1.0)
            v = rng.uniform(-1.0, 1.0)
            max_v = math.sin(u * math.pi) * (1.0 - 0.2 * u)
            
            if abs(v) <= max_v:
                dist_along = u * llen
                dist_across = v * lwid * 0.5
                ca, sa = math.cos(lang), math.sin(lang)
                
                px = lx + ca * dist_along - sa * dist_across
                py = ly + sa * dist_along + ca * dist_across
                
                # Vein vs blade color
                if abs(v) < 0.12:
                    col = COL_LEAF_VEIN
                    ch = rng.choice(["|", "/", "-", "+"])
                elif abs(v) > max_v * 0.8:
                    col = COL_LEAF_DARK
                    ch = rng.choice([">", "<", "*", ";"])
                else:
                    col = COL_LEAF_MID if rng.random() < 0.65 else COL_LEAF_BRIGHT
                    ch = rng.choice(["%", "#", "8", "&", "s"])
                
                pts_list.append({
                    "base_x": px,
                    "base_y": py,
                    "part": "leaf",
                    "u": lu,
                    "char": ch,
                    "color": col
                })

        # ----------------------------------------------------------------------
        # 4. GRAND BLOOMING ROSE HEAD (Velveteen Spiral Phyllotaxis)
        # ----------------------------------------------------------------------
        head_cy = self.cy - 90.0
        head_max_r = 115.0
        GOLDEN_ANGLE = 137.507764 * (math.pi / 180.0)
        
        num_rose = self.total_points - len(pts_list)
        for i in range(num_rose):
            frac = i / (num_rose - 1)
            r = math.sqrt(frac) * head_max_r
            theta = i * GOLDEN_ANGLE
            
            # 5-lobed natural rose scalloping
            scallop = 1.0 + 0.14 * math.sin(5.0 * theta)
            r_mod = r * scallop
            
            px = self.cx + math.cos(theta) * r_mod
            # Vertical foreshortening for natural 2D angle (slight upward tilt)
            py = head_cy + math.sin(theta) * r_mod * 0.90
            
            # 5-Tier Velveteen Gradient
            if frac < 0.15:
                col = COL_ROSE_DEEP
                ch = rng.choice(["@", "#", "♥"])
            elif frac < 0.38:
                col = COL_ROSE_VELVET
                ch = rng.choice(["%", "&", "♥", "8"])
            elif frac < 0.68:
                col = COL_ROSE_RED
                ch = rng.choice(["*", "✿", "%", "8"])
            elif frac < 0.88:
                col = COL_ROSE_CORAL
                ch = rng.choice(["❀", "c", "o", "S"])
            else:
                col = COL_ROSE_CHAMPAGNE
                ch = rng.choice(["*", "·", ")", "(", "'"])
                
            pts_list.append({
                "base_x": px,
                "base_y": py,
                "part": "head",
                "u": 0.0,
                "frac": frac,
                "theta": theta,
                "dist_r": r_mod,
                "char": ch,
                "color": col
            })

        self.points = pts_list


# ==============================================================================
# 2D FLOATING PARTICLES (Sparkles & Dewdrops)
# ==============================================================================
class Particle2D:
    def __init__(self, x, y, kind="sparkle", color=None, vx=None, vy=None):
        self.x = x
        self.y = y
        self.kind = kind
        self.char = random.choice(SPARKLE_CHARS) if kind == "sparkle" else random.choice(["♥", "❀", "·", "•"])
        self.color = color or random.choice([COL_GOLD_SPARK, COL_WHITE_SPARK, COL_ROSE_CHAMPAGNE, COL_DEW_GLOW])
        
        self.vx = vx if vx is not None else random.uniform(-1.5, 1.5)
        self.vy = vy if vy is not None else random.uniform(-2.5, -0.6)
        self.lifespan = random.randint(45, 100)
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

    # Monospace fonts
    font_mono = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 13, bold=True)
    font_btn = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 14, bold=True)

    # 1. Models
    center_x = WINDOW_WIDTH // 2
    center_y = WINDOW_HEIGHT // 2
    envelope = Envelope2D(center_x, center_y, width=760.0, height=450.0)
    total_pts = len(envelope.cells)
    rose = SingleRose2D(center_x, center_y, total_points=total_pts)
    replay_btn = AsciiReplayButton(x=45, y=WINDOW_HEIGHT - 95)

    # 2. Setup Morphing Pairs with Bezier Splines
    sorted_cells = sorted(
        envelope.cells,
        key=lambda c: math.hypot(c["x"] - center_x, c["y"] - center_y)
    )
    max_dist = max(math.hypot(c["x"] - center_x, c["y"] - center_y) for c in sorted_cells)
    delays = [(math.hypot(c["x"] - center_x, c["y"] - center_y) / (max_dist + 1e-4)) * 0.40 for c in sorted_cells]

    rng_ctrl = random.Random(777)
    ctrl_points = []
    for i in range(total_pts):
        p0 = (sorted_cells[i]["x"], sorted_cells[i]["y"])
        p2 = (rose.points[i]["base_x"], rose.points[i]["base_y"])
        mid_x = (p0[0] + p2[0]) * 0.5
        mid_y = (p0[1] + p2[1]) * 0.5
        dist = math.hypot(p2[0] - p0[0], p2[1] - p0[1])
        angle = math.atan2(p2[1] - p0[1], p2[0] - p0[0]) + math.pi / 2.0
        offset = rng_ctrl.uniform(-0.35, 0.35) * dist
        ctrl_points.append((
            mid_x + math.cos(angle) * offset,
            mid_y + math.sin(angle) * offset
        ))

    # States
    STATE_WAITING = 0
    STATE_OPENING = 1
    STATE_MORPHING = 2
    STATE_ROSE = 3

    state = STATE_WAITING
    state_start_time = time.time()
    particles = []

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now = time.time()
        time_in_state = now - state_start_time
        mouse_pos = pygame.mouse.get_pos()

        if state == STATE_ROSE:
            replay_btn.update(mouse_pos)

        # ----------------------------------------------------------------------
        # EVENT HANDLING
        # ----------------------------------------------------------------------
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

            # MOUSE BUTTON DOWN / TOUCHSCREEN
            elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
                is_click = True
                click_pos = event.pos if event.type == pygame.MOUSEBUTTONDOWN else (int(event.x * WINDOW_WIDTH), int(event.y * WINDOW_HEIGHT))
                
                if state == STATE_WAITING:
                    state = STATE_OPENING
                    state_start_time = now
                elif state == STATE_ROSE and replay_btn.rect.collidepoint(click_pos):
                    # Only the ASCII replay icon resets
                    state = STATE_WAITING
                    state_start_time = now
                    particles.clear()

        # ----------------------------------------------------------------------
        # DRAWING & LOGIC
        # ----------------------------------------------------------------------
        screen.fill(COLOR_BG)

        if state == STATE_WAITING:
            # Subtle breathing pulse on heart seal
            seal_pulse = 1.0 + 0.08 * math.sin(now * 5.0)

            for cell in envelope.cells:
                cx = cell["x"]
                cy = cell["y"]
                ch = cell["char"]
                col = cell["color"]

                if cell["is_seal"]:
                    dx = cx - center_x
                    dy = cy - center_y
                    cx = center_x + dx * seal_pulse
                    cy = center_y + dy * seal_pulse

                t_surf = font_mono.render(ch, True, col)
                screen.blit(t_surf, (int(cx), int(cy)))

            # Ambient seal sparkles
            if random.random() < 0.22:
                particles.append(Particle2D(
                    center_x + random.uniform(-35, 35),
                    center_y + random.uniform(-25, 25),
                    kind="sparkle", color=COL_GOLD_SPARK
                ))

        elif state == STATE_OPENING:
            # Flap opening burst
            if time_in_state < 0.06:
                for _ in range(85):
                    ang = random.uniform(0, 2 * math.pi)
                    spd = random.uniform(4.0, 10.0)
                    particles.append(Particle2D(
                        center_x, center_y,
                        kind=random.choice(["sparkle", "petal"]),
                        color=random.choice([COL_SEAL_BRIGHT, COL_GOLD_SPARK, COL_WHITE_SPARK, COL_ROSE_CORAL]),
                        vx=math.cos(ang) * spd,
                        vy=math.sin(ang) * spd - 2.0
                    ))

            # Vibrate slightly before morphing
            shake_x = random.uniform(-2.5, 2.5)
            shake_y = random.uniform(-2.5, 2.5)
            for cell in envelope.cells:
                t_surf = font_mono.render(cell["char"], True, cell["color"])
                screen.blit(t_surf, (int(cell["x"] + shake_x), int(cell["y"] + shake_y)))

            if time_in_state > 0.4:
                state = STATE_MORPHING
                state_start_time = now

        elif state == STATE_MORPHING:
            morph_dur = 3.2
            raw_t = min(1.0, time_in_state / morph_dur)

            for i in range(total_pts):
                d = delays[i]
                if raw_t <= d:
                    loc_t = 0.0
                else:
                    loc_t = (raw_t - d) / (1.0 - d + 1e-5)
                    loc_t = min(1.0, max(0.0, loc_t))

                ease = loc_t * loc_t * (3.0 - 2.0 * loc_t)
                inv = 1.0 - ease

                p0 = (sorted_cells[i]["x"], sorted_cells[i]["y"])
                p1 = ctrl_points[i]
                p2 = (rose.points[i]["base_x"], rose.points[i]["base_y"])

                curr_x = inv * inv * p0[0] + 2.0 * inv * ease * p1[0] + ease * ease * p2[0]
                curr_y = inv * inv * p0[1] + 2.0 * inv * ease * p1[1] + ease * ease * p2[1]

                src_ch = sorted_cells[i]["char"]
                src_col = sorted_cells[i]["color"]
                dst_ch = rose.points[i]["char"]
                dst_col = rose.points[i]["color"]

                if ease < 0.4:
                    ch, col = src_ch, src_col
                elif ease < 0.7:
                    ch = "*" if random.random() < 0.5 else dst_ch
                    frac = (ease - 0.4) / 0.3
                    r = int(src_col[0] * (1 - frac) + dst_col[0] * frac)
                    g = int(src_col[1] * (1 - frac) + dst_col[1] * frac)
                    b = int(src_col[2] * (1 - frac) + dst_col[2] * frac)
                    col = (r, g, b)
                else:
                    ch, col = dst_ch, dst_col

                t_surf = font_mono.render(ch, True, col)
                screen.blit(t_surf, (int(curr_x), int(curr_y)))

            if random.random() < 0.5:
                idx = random.randint(0, total_pts - 1)
                particles.append(Particle2D(
                    rose.points[idx]["base_x"], rose.points[idx]["base_y"],
                    kind="sparkle", color=random.choice([COL_GOLD_SPARK, COL_ROSE_CORAL])
                ))

            if raw_t >= 1.0:
                state = STATE_ROSE
                state_start_time = now

        elif state == STATE_ROSE:
            # ------------------------------------------------------------------
            # ORGANIC FLOWER MOTION (Living 2D Rose Dynamics)
            # ------------------------------------------------------------------
            # 1. Gentle wind sway along stem height
            stem_base_y = center_y + 270.0
            stem_top_y = center_y - 15.0
            total_stem_h = stem_base_y - stem_top_y
            
            # 2. Breathing Bloom (Petals breathe subtly in and out)
            bloom_pulse = 1.0 + 0.035 * math.sin(now * 2.2)
            head_cy = center_y - 90.0

            for pt in rose.points:
                bx = pt["base_x"]
                by = pt["base_y"]
                part = pt["part"]
                ch = pt["char"]
                col = pt["color"]

                # Sway calculation: fixed at stem bottom, swaying more towards top
                h_factor = max(0.0, min(1.0, (stem_base_y - by) / (total_stem_h + 100.0)))
                sway_offset_x = math.sin(now * 1.8 + by * 0.006) * (18.0 * (h_factor ** 1.8))

                if part == "head":
                    # Head sways with top of stem and breathes organically
                    dx = bx - center_x
                    dy = by - head_cy
                    render_x = center_x + dx * bloom_pulse + sway_offset_x
                    render_y = head_cy + dy * bloom_pulse
                elif part in ["leaf", "stem", "thorn", "sepal"]:
                    render_x = bx + sway_offset_x
                    render_y = by

                t_surf = font_mono.render(ch, True, col)
                screen.blit(t_surf, (int(render_x), int(render_y)))

            # Ambient rising dew sparkles and soft floral glow
            if random.random() < 0.32:
                # Spawn near rose head or leaves
                rx = center_x + random.uniform(-110, 110)
                ry = head_cy + random.uniform(-90, 120)
                particles.append(Particle2D(
                    rx, ry,
                    kind=random.choice(["sparkle", "petal"]),
                    color=random.choice([COL_ROSE_CHAMPAGNE, COL_GOLD_SPARK, COL_WHITE_SPARK, COL_DEW_GLOW]),
                    vy=random.uniform(-2.2, -0.6)
                ))

            # Draw ASCII Replay Icon (Pure Typography, No Text Lines)
            replay_btn.draw(screen, font_btn)

        # ----------------------------------------------------------------------
        # PARTICLES UPDATE & DRAW
        # ----------------------------------------------------------------------
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
