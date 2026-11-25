import math
import random
import sys
import time
import pygame

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
TITLE = "Special Letter 💌 Stargazer Lilies"
WINDOW_WIDTH = 1050
WINDOW_HEIGHT = 880
FPS = 60

# ------------------------------------------------------------------------------
# COLOR PALETTE (RGB) - Matching exact photo colors
# ------------------------------------------------------------------------------
COLOR_BG = (8, 6, 14)

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

# Lily Flower Specific Palettes (From user reference image)
# 1. Red Stargazer (Top-Center)
COL_RED_PETAL = (235, 42, 52)
COL_RED_DARK = (160, 15, 28)
COL_RED_HIGHLIGHT = (255, 95, 105)

# 2. Pink Lily (Mid-Left)
COL_PINK_PETAL = (245, 100, 185)
COL_PINK_DARK = (185, 35, 125)
COL_PINK_LIGHT = (255, 170, 220)

# 3. White Lily (Mid-Right)
COL_WHITE_PETAL = (255, 252, 248)
COL_WHITE_SHADOW = (220, 225, 228)
COL_WHITE_CORE = (185, 225, 140)  # Chartreuse lime throat

# 4. Peach/Apricot Lily (Bottom-Center)
COL_PEACH_PETAL = (255, 185, 135)
COL_PEACH_DARK = (225, 130, 80)
COL_PEACH_LIGHT = (255, 218, 175)

# 5. Yellow Lilies (Left Flank)
COL_YELLOW_PETAL = (255, 215, 45)
COL_YELLOW_DARK = (215, 160, 20)
COL_YELLOW_LIGHT = (255, 240, 120)

# 6. Burgundy / Maroon Lilies (Right Flank)
COL_WINE_PETAL = (180, 42, 78)
COL_WINE_DARK = (120, 15, 45)
COL_WINE_LIGHT = (215, 90, 125)

# 7. Background Lilies (Top)
COL_IVORY_PETAL = (240, 235, 220)
COL_PALE_GOLD = (230, 200, 130)

# Stems & Strappy Lily Leaves (Base)
COL_LEAF_BRIGHT = (85, 210, 105)
COL_LEAF_MID = (55, 175, 75)
COL_LEAF_DARK = (30, 115, 48)

# Center Stamens & Pollen Anthers
COL_POLLEN_GOLD = (255, 235, 140)
COL_POLLEN_BROWN = (140, 60, 30)
COL_STARDUST = (255, 255, 255)

# Character sets
ASCII_CHARS_DENSE = ["8", "%", "&", "#", "S", "B", "w", "m", "Z", "X", "Q", "0"]
ASCII_CHARS_MED = ["o", "*", "a", "s", "z", "x", "e", "u", "r", "n", "v"]
ASCII_LILY_PETAL = ["=", "-", "~", "#", "%", "8", "*", "+", "H", "M"]


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

                is_flap = (ny < (1.0 - dx) * 0.5) and not is_top
                
                self.cells.append({
                    "x": x,
                    "y": y,
                    "char": char,
                    "color": color,
                    "is_seal": is_seal,
                    "is_flap": is_flap,
                })


# ==============================================================================
# EXACT LILY BOUQUET GENERATOR (Matching User Reference Image)
# ==============================================================================
class LilyBouquet2D:
    """Generates 2D points for the multi-colored 6-petal lily bouquet from reference photo."""
    def __init__(self, cx, cy, total_points=2490):
        self.cx = cx
        self.cy = cy
        self.total_points = total_points
        self.points = []
        self._generate_lilies()

    def _generate_lilies(self):
        rng = random.Random(321)
        pts_list = []

        # ----------------------------------------------------------------------
        # 1. BASE STRAPPY LILY LEAVES (Dense Green Foliage at Bottom)
        # ----------------------------------------------------------------------
        num_leaves = int(self.total_points * 0.16)
        leaf_base_y = self.cy + 340.0
        
        for _ in range(num_leaves):
            u = rng.uniform(0.0, 1.0)  # 0 at bottom, 1 at top of foliage
            # Leaves fan out slightly from center
            fan_spread = rng.uniform(-140.0, 140.0)
            leaf_x = self.cx + fan_spread * (0.4 + 0.6 * (1.0 - u))
            leaf_y = leaf_base_y - u * 155.0 + rng.uniform(-6, 6)
            
            # Shading
            if u > 0.6:
                col = rng.choice([COL_LEAF_BRIGHT, COL_LEAF_MID])
                ch = rng.choice(["|", "!", "/", "\\", "%"])
            else:
                col = rng.choice([COL_LEAF_MID, COL_LEAF_DARK])
                ch = rng.choice(["#", "%", "8", "|", ";"])
                
            pts_list.append({
                "base_x": leaf_x,
                "base_y": leaf_y,
                "part": "leaf",
                "u": u,
                "char": ch,
                "color": col
            })

        # ----------------------------------------------------------------------
        # 2. DEFINITION OF THE 10 LILIES (Positions, Radii, Palette from Photo)
        # ----------------------------------------------------------------------
        # Each lily has 6 pointed petals radiating from its center:
        lily_specs = [
            # Top-Center Fire Red Lily (The prominent red lily in photo)
            {
                "cx": self.cx, "cy": self.cy - 160.0, "rad": 115.0, "rot": 0.0,
                "col_main": COL_RED_PETAL, "col_dark": COL_RED_DARK, "col_hi": COL_RED_HIGHLIGHT,
                "priority": 4
            },
            # Mid-Left Vivid Pink Lily
            {
                "cx": self.cx - 85.0, "cy": self.cy - 20.0, "rad": 120.0, "rot": 0.35,
                "col_main": COL_PINK_PETAL, "col_dark": COL_PINK_DARK, "col_hi": COL_PINK_LIGHT,
                "priority": 5
            },
            # Mid-Right Pure White Lily (with soft green throat)
            {
                "cx": self.cx + 95.0, "cy": self.cy - 10.0, "rad": 125.0, "rot": -0.25,
                "col_main": COL_WHITE_PETAL, "col_dark": COL_WHITE_SHADOW, "col_hi": COL_WHITE_PETAL,
                "col_core": COL_WHITE_CORE,
                "priority": 6
            },
            # Bottom-Center Peach/Apricot Lily
            {
                "cx": self.cx - 5.0, "cy": self.cy + 105.0, "rad": 115.0, "rot": 0.15,
                "col_main": COL_PEACH_PETAL, "col_dark": COL_PEACH_DARK, "col_hi": COL_PEACH_LIGHT,
                "priority": 7
            },
            # Mid-Left Golden Yellow Lily
            {
                "cx": self.cx - 145.0, "cy": self.cy - 85.0, "rad": 90.0, "rot": 0.52,
                "col_main": COL_YELLOW_PETAL, "col_dark": COL_YELLOW_DARK, "col_hi": COL_YELLOW_LIGHT,
                "priority": 2
            },
            # Lower-Left Golden Yellow Lily
            {
                "cx": self.cx - 155.0, "cy": self.cy + 95.0, "rad": 85.0, "rot": -0.40,
                "col_main": COL_YELLOW_PETAL, "col_dark": COL_YELLOW_DARK, "col_hi": COL_YELLOW_LIGHT,
                "priority": 3
            },
            # Mid-Right Burgundy / Plum Lily
            {
                "cx": self.cx + 140.0, "cy": self.cy - 100.0, "rad": 90.0, "rot": -0.50,
                "col_main": COL_WINE_PETAL, "col_dark": COL_WINE_DARK, "col_hi": COL_WINE_LIGHT,
                "priority": 2
            },
            # Lower-Right Deep Crimson / Maroon Lily
            {
                "cx": self.cx + 140.0, "cy": self.cy + 125.0, "rad": 80.0, "rot": 0.45,
                "col_main": COL_RED_DARK, "col_dark": (120, 10, 25), "col_hi": COL_RED_PETAL,
                "priority": 3
            },
            # Top-Left Background Ivory Lily
            {
                "cx": self.cx - 65.0, "cy": self.cy - 245.0, "rad": 75.0, "rot": 0.20,
                "col_main": COL_IVORY_PETAL, "col_dark": (195, 190, 180), "col_hi": COL_WHITE_PETAL,
                "priority": 1
            },
            # Top-Right Background Pale Gold Lily
            {
                "cx": self.cx + 60.0, "cy": self.cy - 245.0, "rad": 75.0, "rot": -0.20,
                "col_main": COL_PALE_GOLD, "col_dark": (190, 155, 95), "col_hi": (255, 235, 175),
                "priority": 1
            },
        ]

        rem_pts = self.total_points - len(pts_list)
        pts_per_lily = rem_pts // len(lily_specs)

        for l_spec in lily_specs:
            lcx = l_spec["cx"]
            lcy = l_spec["cy"]
            lrad = l_spec["rad"]
            lrot = l_spec["rot"]
            c_main = l_spec["col_main"]
            c_dark = l_spec["col_dark"]
            c_hi = l_spec["col_hi"]
            c_core = l_spec.get("col_core", None)

            # Generate 6 pointed lanceolate petals for this lily
            for _ in range(pts_per_lily):
                # Pick one of the 6 petals
                petal_idx = rng.randint(0, 5)
                base_angle = lrot + petal_idx * (2.0 * math.pi / 6.0)
                
                # Position along petal length: u from 0.0 (center) to 1.0 (tip)
                u = math.sqrt(rng.uniform(0.01, 1.0))
                # Lanceolate petal width profile: widest at u ~ 0.55
                max_w = math.sin(u * math.pi) * (0.34 * lrad)
                v = rng.uniform(-1.0, 1.0)
                
                # Transverse coordinate inside petal
                dist_along = u * lrad
                dist_across = v * max_w
                
                ca, sa = math.cos(base_angle), math.sin(base_angle)
                px = lcx + ca * dist_along - sa * dist_across
                py = lcy + sa * dist_along + ca * dist_across
                
                # Central vein & stippled scanline texture like in reference photo
                abs_v = abs(v)
                if u < 0.18:
                    # Center core / throat
                    col = c_core if c_core else c_dark
                    ch = rng.choice(["*", "o", "+", "·"])
                elif abs_v < 0.12:
                    # Center crease/vein of the petal
                    col = c_dark
                    ch = rng.choice(["-", "=", "|", ";"])
                elif abs_v > 0.82:
                    # Petal edge highlight
                    col = c_hi
                    ch = rng.choice(["-", "~", "=", "'"])
                else:
                    # Petal body with horizontal/linear striations (like photo)
                    col = c_main if rng.random() < 0.75 else c_hi
                    ch = rng.choice(["=", "-", "#", "%", "H", "8"])

                pts_list.append({
                    "base_x": px,
                    "base_y": py,
                    "part": "lily",
                    "lcx": lcx,
                    "lcy": lcy,
                    "u": u,
                    "char": ch,
                    "color": col
                })

        # ----------------------------------------------------------------------
        # 3. FILL REMAINING POINTS WITH LILY STAMENS / PARTICLES
        # ----------------------------------------------------------------------
        while len(pts_list) < self.total_points:
            # Pick random prominent lily to add anthers / stamens
            l_pick = rng.choice(lily_specs[:4])
            stamen_ang = rng.uniform(0, 2 * math.pi)
            stamen_r = rng.uniform(8.0, 32.0)
            sx = l_pick["cx"] + math.cos(stamen_ang) * stamen_r
            sy = l_pick["cy"] + math.sin(stamen_ang) * stamen_r
            pts_list.append({
                "base_x": sx,
                "base_y": sy,
                "part": "stamen",
                "lcx": l_pick["cx"],
                "lcy": l_pick["cy"],
                "u": 0.1,
                "char": rng.choice(["*", "·", "•", "+"]),
                "color": rng.choice([COL_POLLEN_GOLD, COL_POLLEN_BROWN])
            })

        self.points = pts_list


# ==============================================================================
# 2D FLOATING PARTICLES (Sparkles & Stardust)
# ==============================================================================
class Particle2D:
    def __init__(self, x, y, kind="sparkle", color=None, vx=None, vy=None):
        self.x = x
        self.y = y
        self.kind = kind
        self.char = random.choice(ASCII_CHARS_MED) if kind == "star" else random.choice(["*", "·", "•", "✧", "+"])
        self.color = color or random.choice([COL_POLLEN_GOLD, COL_STARDUST, COL_PEACH_LIGHT, COL_PINK_LIGHT])
        
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

    # 1. Models
    center_x = WINDOW_WIDTH // 2
    center_y = WINDOW_HEIGHT // 2 - 10
    envelope = Envelope2D(center_x, center_y, width=760.0, height=450.0)
    total_pts = len(envelope.cells)
    lilies = LilyBouquet2D(center_x, center_y, total_points=total_pts)
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
        p2 = (lilies.points[i]["base_x"], lilies.points[i]["base_y"])
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
    STATE_LILIES = 3

    state = STATE_WAITING
    state_start_time = time.time()
    particles = []

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now = time.time()
        time_in_state = now - state_start_time
        mouse_pos = pygame.mouse.get_pos()

        if state == STATE_LILIES:
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
                click_pos = event.pos if event.type == pygame.MOUSEBUTTONDOWN else (int(event.x * WINDOW_WIDTH), int(event.y * WINDOW_HEIGHT))
                
                if state == STATE_WAITING:
                    state = STATE_OPENING
                    state_start_time = now
                elif state == STATE_LILIES and replay_btn.rect.collidepoint(click_pos):
                    # Pure ASCII replay icon resets
                    state = STATE_WAITING
                    state_start_time = now
                    particles.clear()

        # ----------------------------------------------------------------------
        # DRAWING & LOGIC
        # ----------------------------------------------------------------------
        screen.fill(COLOR_BG)

        if state == STATE_WAITING:
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

            if random.random() < 0.22:
                particles.append(Particle2D(
                    center_x + random.uniform(-35, 35),
                    center_y + random.uniform(-25, 25),
                    kind="sparkle", color=COL_POLLEN_GOLD
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
                        vy=math.sin(ang) * spd - 2.0
                    ))

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
                p2 = (lilies.points[i]["base_x"], lilies.points[i]["base_y"])

                curr_x = inv * inv * p0[0] + 2.0 * inv * ease * p1[0] + ease * ease * p2[0]
                curr_y = inv * inv * p0[1] + 2.0 * inv * ease * p1[1] + ease * ease * p2[1]

                src_ch = sorted_cells[i]["char"]
                src_col = sorted_cells[i]["color"]
                dst_ch = lilies.points[i]["char"]
                dst_col = lilies.points[i]["color"]

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
                    lilies.points[idx]["base_x"], lilies.points[idx]["base_y"],
                    kind="sparkle", color=random.choice([COL_POLLEN_GOLD, COL_PINK_PETAL, COL_STARDUST])
                ))

            if raw_t >= 1.0:
                state = STATE_LILIES
                state_start_time = now

        elif state == STATE_LILIES:
            # ------------------------------------------------------------------
            # LIVING BOTANICAL MOTION (Breeze Sway + Petal Breathing)
            # ------------------------------------------------------------------
            # Gentle overall breeze sway
            breeze_x = math.sin(now * 1.8) * 6.0
            
            # Breathing pulse for lilies
            petal_pulse = 1.0 + 0.025 * math.sin(now * 2.4)

            for pt in lilies.points:
                bx = pt["base_x"]
                by = pt["base_y"]
                part = pt["part"]
                ch = pt["char"]
                col = pt["color"]

                # Foliage base vs flower head motion
                if part in ["lily", "stamen"]:
                    lcx = pt["lcx"]
                    lcy = pt["lcy"]
                    # Expand petals slightly from each lily center
                    dx = bx - lcx
                    dy = by - lcy
                    rx = lcx + dx * petal_pulse + breeze_x * 0.8
                    ry = lcy + dy * petal_pulse + math.sin(now * 2.0 + lcx * 0.01) * 2.0
                else:
                    # Leaf base fixed, upper leaf sways with breeze
                    u = pt.get("u", 0.5)
                    rx = bx + breeze_x * (1.0 - u * 0.5)
                    ry = by

                t_surf = font_mono.render(ch, True, col)
                screen.blit(t_surf, (int(rx), int(ry)))

            # Ambient stardust sparkles drifting around the bouquet (as seen in photo)
            if random.random() < 0.35:
                sx = center_x + random.uniform(-220, 220)
                sy = center_y + random.uniform(-250, 200)
                particles.append(Particle2D(
                    sx, sy,
                    kind="sparkle",
                    color=random.choice([COL_STARDUST, COL_POLLEN_GOLD, COL_PEACH_LIGHT, COL_WHITE_PETAL]),
                    vy=random.uniform(-1.8, -0.5)
                ))

            # ASCII Replay Icon Button at bottom-left
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
