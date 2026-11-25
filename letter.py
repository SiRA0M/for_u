import math
import random
import sys
import time
import pygame

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
TITLE = "Special Letter 💌 For You"
WINDOW_WIDTH = 1050
WINDOW_HEIGHT = 800
FPS = 60

# Palette matching the uploaded image & romantic flower aesthetic
COLOR_BG = (10, 8, 16)

# Envelope colors (Warm peach / sepia / gold with purple ambient glow)
COL_BORDER = (245, 215, 195)
COL_PAPER_MAIN = (230, 165, 125)
COL_PAPER_SHADOW = (175, 105, 75)
COL_PAPER_HIGHLIGHT = (255, 215, 180)
COL_GLOW_PURPLE = (145, 95, 225)

# Wax seal colors
COL_SEAL_BRIGHT = (255, 70, 155)
COL_SEAL_CORE = (255, 20, 110)
COL_SEAL_OUTER = (210, 30, 95)
COL_SEAL_SPECULAR = (255, 180, 220)

# Flower Bouquet colors
COL_STEM_DEEP = (45, 120, 65)
COL_STEM_LIGHT = (75, 175, 95)
COL_LEAF_DARK = (55, 140, 75)
COL_LEAF_BRIGHT = (95, 205, 115)
COL_LEAF_MINT = (140, 225, 170)

# Petal colors
COL_ROSE_RED = (235, 35, 75)
COL_ROSE_PINK = (255, 95, 160)
COL_ROSE_LIGHT = (255, 175, 210)
COL_ROSE_CORE = (180, 15, 50)

COL_PEONY_LILAC = (215, 145, 255)
COL_PEONY_PURPLE = (170, 80, 230)
COL_PEONY_SOFT = (240, 195, 255)

COL_TULIP_CORAL = (255, 125, 110)
COL_TULIP_PEACH = (255, 175, 130)

COL_DAISY_WHITE = (255, 250, 245)
COL_DAISY_YELLOW = (255, 215, 60)

COL_WRAPPER = (240, 215, 210)
COL_WRAPPER_SHADOW = (195, 160, 165)
COL_RIBBON = (255, 85, 140)
COL_RIBBON_GOLD = (255, 210, 100)

COL_GOLD_SPARK = (255, 235, 150)
COL_WHITE_SPARK = (255, 255, 255)

# Characters
ASCII_CHARS_DENSE = ["8", "%", "&", "#", "S", "B", "w", "m", "Z", "X", "Q", "0"]
ASCII_CHARS_MED = ["o", "*", "a", "s", "z", "x", "e", "u", "r", "n", "v"]
ASCII_CHARS_LIGHT = [".", ":", "-", "~", "+", "=", "·", "'"]
FLOWER_CHARS = ["@", "%", "&", "8", "♥", "❀", "✿", "*", "(", ")", "c", "o", "S"]
SPARKLE_CHARS = ["*", "+", "·", "✧", "✦", "°", "•", "♡"]


# ==============================================================================
# ENVELOPE GENERATION (Exact replica of high-detail image)
# ==============================================================================
class EnvelopeModel:
    """Generates the high-density ASCII envelope matching user's photo."""
    def __init__(self, cx, cy, width=760, height=450):
        self.cx = cx
        self.cy = cy
        self.w = width
        self.h = height
        self.left = cx - width // 2
        self.right = cx + width // 2
        self.top = cy - height // 2
        self.bottom = cy + height // 2
        
        # Grid definition
        self.char_w = 9.5
        self.char_h = 15.5
        self.cols = int(self.w / self.char_w)
        self.rows = int(self.h / self.char_h)
        
        self.cells = []
        self._build_grid()

    def _build_grid(self):
        rng = random.Random(42)  # Deterministic beautiful texture
        
        for r in range(self.rows):
            y = self.top + r * self.char_h
            # Normalized row pos 0 to 1
            ny = r / (self.rows - 1)
            
            for c in range(self.cols):
                x = self.left + c * self.char_w
                nx = c / (self.cols - 1)
                
                # Check borders
                is_top_border = (r == 0)
                is_bottom_border = (r == self.rows - 1)
                is_left_border = (c == 0)
                is_right_border = (c == self.cols - 1)
                
                # Diagonal crease calculations (from corners to center)
                # Center is at nx=0.5, ny=0.5
                dx = abs(nx - 0.5) * 2.0  # 0 at center, 1 at edges
                dy = abs(ny - 0.5) * 2.0
                
                # Top flap fold diagonal: line from (0,0) to (0.5, 0.5) and (1,0) to (0.5, 0.5)
                # When ny < 0.5, fold line is where ny ~= 1.0 - dx
                top_flap_crease = abs(ny - (1.0 - dx) * 0.5) < 0.035 and ny <= 0.52
                bot_flap_crease = abs((1.0 - ny) - (1.0 - dx) * 0.5) < 0.035 and ny >= 0.48
                
                # Distance to center for heart seal
                seal_dx = (x - self.cx) / 38.0
                seal_dy = (y - self.cy) / 34.0
                # Heart equation: (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0
                # Inverted y for screen coords
                sy = -seal_dy - 0.15
                sx = seal_dx
                heart_eq = (sx*sx + sy*sy - 1.0)**3 - sx*sx * (sy**3)
                is_seal = heart_eq <= 0.05
                is_seal_edge = abs(heart_eq) <= 0.12
                
                # Determine character & color
                if is_top_border or is_bottom_border:
                    # Slanted hatch border like photo
                    char = "/" if (c % 2 == 0) else "\\"
                    color = COL_BORDER
                elif is_left_border:
                    char = "\\"
                    color = COL_BORDER
                elif is_right_border:
                    char = "/"
                    # Right border has subtle purple glow like in photo
                    color = (200, 170, 240)
                elif is_seal:
                    # Heart wax seal (Vivid pink & magenta)
                    if is_seal_edge:
                        char = rng.choice(["♥", "#", "@", "%"])
                        color = COL_SEAL_OUTER
                    elif sy > 0.3 and sx < 0.1:  # Specular highlight on heart
                        char = rng.choice(["*", "+", "♥"])
                        color = COL_SEAL_SPECULAR
                    else:
                        char = rng.choice(["♥", "@", "#", "8", "%", "&"])
                        color = rng.choice([COL_SEAL_BRIGHT, COL_SEAL_CORE])
                elif top_flap_crease or bot_flap_crease:
                    # Crease highlight line
                    char = "/" if (nx > 0.5) else "\\"
                    color = COL_PAPER_HIGHLIGHT
                else:
                    # Dense textured envelope paper
                    # Upper flap area vs lower area shading
                    if ny < (1.0 - dx) * 0.5:
                        # Inside top flap (slightly brighter)
                        char = rng.choice(ASCII_CHARS_DENSE)
                        base_col = COL_PAPER_MAIN
                    else:
                        # Lower envelope body
                        if ny > 0.75:
                            # Shadow near bottom
                            char = rng.choice(ASCII_CHARS_DENSE if rng.random() < 0.8 else ASCII_CHARS_MED)
                            base_col = COL_PAPER_SHADOW
                        else:
                            char = rng.choice(ASCII_CHARS_DENSE)
                            base_col = COL_PAPER_MAIN
                    
                    # Add subtle random brightness jitter
                    jitter = rng.uniform(-15, 15)
                    r_c = max(0, min(255, int(base_col[0] + jitter)))
                    g_c = max(0, min(255, int(base_col[1] + jitter)))
                    b_c = max(0, min(255, int(base_col[2] + jitter)))
                    
                    # Right edge ambient purple tint spill
                    if nx > 0.85:
                        purple_blend = (nx - 0.85) / 0.15
                        r_c = int(r_c * (1 - purple_blend * 0.4) + COL_GLOW_PURPLE[0] * purple_blend * 0.4)
                        g_c = int(g_c * (1 - purple_blend * 0.4) + COL_GLOW_PURPLE[1] * purple_blend * 0.4)
                        b_c = int(b_c * (1 - purple_blend * 0.4) + COL_GLOW_PURPLE[2] * purple_blend * 0.4)
                    
                    color = (r_c, g_c, b_c)

                # Store cell point
                self.cells.append({
                    "x": x,
                    "y": y,
                    "char": char,
                    "color": color,
                    "is_seal": is_seal,
                    "orig_x": x,
                    "orig_y": y,
                })


# ==============================================================================
# FLOWER BOUQUET GENERATOR (Detailed botanical art points)
# ==============================================================================
class BouquetModel:
    """Generates detailed 2D target points for a lush flower bouquet."""
    def __init__(self, cx, cy, total_points=1400):
        self.cx = cx
        self.cy = cy
        self.total_points = total_points
        self.points = []
        self._build_bouquet()

    def _build_bouquet(self):
        rng = random.Random(1337)
        points = []

        # ----------------------------------------------------------------------
        # 1. KRAFT WRAPPER & RIBBON BOW (Base of bouquet)
        # ----------------------------------------------------------------------
        wrap_top_y = self.cy + 60
        wrap_bot_y = self.cy + 220
        wrap_top_w = 220
        wrap_bot_w = 70
        
        num_wrap = int(self.total_points * 0.16)
        for _ in range(num_wrap):
            u = rng.uniform(0, 1)  # 0 at top, 1 at bottom
            y = wrap_top_y + u * (wrap_bot_y - wrap_top_y)
            w_at_y = wrap_top_w * (1 - u) + wrap_bot_w * u
            x = self.cx + rng.uniform(-w_at_y / 2, w_at_y / 2)
            
            # Shading on cone wrapper
            side_factor = abs(x - self.cx) / (w_at_y / 2 + 1e-4)
            if side_factor > 0.8:
                col = COL_WRAPPER_SHADOW
                char = rng.choice(["|", "/", "\\", "%"])
            else:
                col = COL_WRAPPER
                char = rng.choice(["#", "%", "8", "=", ":"])
            points.append((x, y, char, col, 0.0))  # 0.0 = layer depth

        # Ribbon bow at waist
        ribbon_y = wrap_top_y + 35
        num_ribbon = int(self.total_points * 0.05)
        for _ in range(num_ribbon):
            # Two loops + center knot + two tails
            choice = rng.random()
            if choice < 0.4:
                # Left loop
                ang = rng.uniform(0, 2 * math.pi)
                rad = rng.uniform(8, 28)
                x = self.cx - 28 + math.cos(ang) * rad * 1.3
                y = ribbon_y + math.sin(ang) * rad * 0.7
            elif choice < 0.8:
                # Right loop
                ang = rng.uniform(0, 2 * math.pi)
                rad = rng.uniform(8, 28)
                x = self.cx + 28 + math.cos(ang) * rad * 1.3
                y = ribbon_y + math.sin(ang) * rad * 0.7
            else:
                # Center knot
                x = self.cx + rng.uniform(-14, 14)
                y = ribbon_y + rng.uniform(-12, 12)
            points.append((x, y, rng.choice(["♥", "@", "*", "%"]), COL_RIBBON, 0.5))

        # ----------------------------------------------------------------------
        # 2. STEMS & FOLIAGE / LEAVES (Radiating outwards)
        # ----------------------------------------------------------------------
        num_leaves = int(self.total_points * 0.22)
        leaf_clusters = [
            # (center_x, center_y, angle, length, width, color)
            (self.cx - 160, self.cy - 10, -0.65, 120, 45, COL_LEAF_BRIGHT),
            (self.cx + 160, self.cy - 10, 0.65, 120, 45, COL_LEAF_BRIGHT),
            (self.cx - 130, self.cy - 90, -0.95, 100, 38, COL_LEAF_DARK),
            (self.cx + 130, self.cy - 90, 0.95, 100, 38, COL_LEAF_DARK),
            (self.cx - 70, self.cy - 160, -1.3, 90, 32, COL_LEAF_MINT),
            (self.cx + 70, self.cy - 160, 1.3, 90, 32, COL_LEAF_MINT),
            (self.cx, self.cy - 180, 0.0, 80, 30, COL_LEAF_BRIGHT),
        ]
        
        for _ in range(num_leaves):
            lc = rng.choice(leaf_clusters)
            lx, ly, lang, llen, lwid, lcol = lc
            # Generate leaf shape along angle
            u = rng.uniform(0.1, 1.0)
            v = rng.uniform(-1.0, 1.0)
            # Oval profile
            max_v = math.sin(u * math.pi)
            if abs(v) <= max_v:
                dist_along = u * llen
                dist_across = v * lwid * 0.5
                ca, sa = math.cos(lang), math.sin(lang)
                px = lx + ca * dist_along - sa * dist_across
                py = ly + sa * dist_along + ca * dist_across
                
                ch = rng.choice(["$", "%", "8", "*", "#", ";"])
                col = lcol if abs(v) > 0.3 else COL_STEM_DEEP
                points.append((px, py, ch, col, 0.2))

        # ----------------------------------------------------------------------
        # 3. BLOOMING FLOWERS
        # ----------------------------------------------------------------------
        flower_heads = [
            # Main central Grand Rose
            {"cx": self.cx, "cy": self.cy - 50, "rad": 78, "type": "rose", "col_core": COL_ROSE_CORE, "col_mid": COL_ROSE_RED, "col_edge": COL_ROSE_PINK},
            # Left Soft Peony
            {"cx": self.cx - 85, "cy": self.cy - 40, "rad": 62, "type": "peony", "col_core": COL_PEONY_PURPLE, "col_mid": COL_PEONY_LILAC, "col_edge": COL_PEONY_SOFT},
            # Right Soft Rose
            {"cx": self.cx + 85, "cy": self.cy - 40, "rad": 62, "type": "rose", "col_core": COL_ROSE_CORE, "col_mid": COL_ROSE_PINK, "col_edge": COL_ROSE_LIGHT},
            # Top-Left Coral Tulip
            {"cx": self.cx - 55, "cy": self.cy - 120, "rad": 46, "type": "tulip", "col_core": COL_TULIP_CORAL, "col_mid": COL_TULIP_CORAL, "col_edge": COL_TULIP_PEACH},
            # Top-Right Pink Rosebud
            {"cx": self.cx + 55, "cy": self.cy - 120, "rad": 46, "type": "rose", "col_core": COL_ROSE_RED, "col_mid": COL_ROSE_PINK, "col_edge": COL_ROSE_LIGHT},
            # Daisies / Chamomiles scattered around edges
            {"cx": self.cx - 130, "cy": self.cy + 20, "rad": 34, "type": "daisy", "col_core": COL_DAISY_YELLOW, "col_mid": COL_DAISY_WHITE, "col_edge": COL_DAISY_WHITE},
            {"cx": self.cx + 130, "cy": self.cy + 20, "rad": 34, "type": "daisy", "col_core": COL_DAISY_YELLOW, "col_mid": COL_DAISY_WHITE, "col_edge": COL_DAISY_WHITE},
            {"cx": self.cx, "cy": self.cy - 145, "rad": 36, "type": "daisy", "col_core": COL_DAISY_YELLOW, "col_mid": COL_DAISY_WHITE, "col_edge": COL_DAISY_WHITE},
        ]

        remaining_pts = self.total_points - len(points)
        pts_per_flower = remaining_pts // len(flower_heads)

        for fh in flower_heads:
            fcx = fh["cx"]
            fcy = fh["cy"]
            frad = fh["rad"]
            ftype = fh["type"]
            
            for _ in range(pts_per_flower):
                if ftype in ["rose", "peony"]:
                    # Multi-petal spiraling golden ratio distribution
                    r = math.sqrt(rng.uniform(0.04, 1.0)) * frad
                    theta = rng.uniform(0, 2 * math.pi)
                    # Add petal scalloping modulation
                    n_petals = 5 if ftype == "rose" else 7
                    r_mod = r * (1.0 + 0.12 * math.sin(n_petals * theta))
                    
                    px = fcx + math.cos(theta) * r_mod
                    py = fcy + math.sin(theta) * r_mod * 0.88  # Slight 3D perspective foreshortening
                    
                    frac = r / frad
                    if frac < 0.25:
                        col = fh["col_core"]
                        ch = rng.choice(["@", "#", "♥"])
                    elif frac < 0.7:
                        col = fh["col_mid"]
                        ch = rng.choice(["%", "&", "8", "♥", "✿"])
                    else:
                        col = fh["col_edge"]
                        ch = rng.choice(["*", "(", ")", "c", "o", "❀"])
                
                elif ftype == "tulip":
                    # Upright cup shape
                    u = rng.uniform(0, 1)
                    v = rng.uniform(-1, 1)
                    ang = v * (math.pi / 2.3)
                    rad_y = frad * 1.15
                    rad_x = frad * 0.75 * math.sin(u * math.pi * 0.8 + 0.2)
                    
                    px = fcx + v * rad_x
                    py = fcy - u * rad_y + frad * 0.5
                    
                    col = fh["col_mid"] if u > 0.4 else fh["col_core"]
                    ch = rng.choice(["#", "%", "8", "U", "V", "|"])
                
                else:  # daisy
                    r = rng.uniform(0, frad)
                    theta = rng.uniform(0, 2 * math.pi)
                    px = fcx + math.cos(theta) * r
                    py = fcy + math.sin(theta) * r
                    if r < frad * 0.35:
                        col = fh["col_core"]
                        ch = rng.choice(["*", "@", "•", "o"])
                    else:
                        col = fh["col_mid"]
                        ch = rng.choice(["+", "|", "/", "\\", "1", "i"])

                points.append((px, py, ch, col, 0.8))

        self.points = points


# ==============================================================================
# PARTICLE SPARKLE / PETAL DRIFT
# ==============================================================================
class FloatingParticle:
    def __init__(self, x, y, kind="sparkle", color=None, vx=None, vy=None):
        self.x = x
        self.y = y
        self.kind = kind
        self.char = random.choice(SPARKLE_CHARS) if kind == "sparkle" else random.choice(["♥", "❀", "·", "•"])
        self.color = color or random.choice([COL_GOLD_SPARK, COL_WHITE_SPARK, COL_ROSE_LIGHT, COL_SEAL_BRIGHT])
        
        self.vx = vx if vx is not None else random.uniform(-1.5, 1.5)
        self.vy = vy if vy is not None else random.uniform(-2.5, -0.6)
        self.lifespan = random.randint(45, 110)
        self.age = 0
        self.alive = True
        self.wobble_freq = random.uniform(2.0, 5.0)
        self.wobble_amp = random.uniform(0.5, 2.0)

    def update(self):
        self.x += self.vx + math.sin(self.age * 0.08 * self.wobble_freq) * self.wobble_amp
        self.y += self.vy
        self.age += 1
        if self.age >= self.lifespan:
            self.alive = False

    def draw(self, surface, font):
        progress = self.age / self.lifespan
        alpha = math.sin(progress * math.pi)
        if alpha <= 0:
            return
        
        r = int(self.color[0] * alpha)
        g = int(self.color[1] * alpha)
        b = int(self.color[2] * alpha)
        
        surf = font.render(self.char, True, (r, g, b))
        surface.blit(surf, (int(self.x), int(self.y)))


# ==============================================================================
# MORPHING CHARACTER SYSTEM (Smooth Non-linear Spline Transitions)
# ==============================================================================
class MorphingNode:
    """Represents a character that transitions smoothly from envelope to bouquet."""
    def __init__(self, src_x, src_y, src_char, src_color, dst_x, dst_y, dst_char, dst_color, delay=0.0):
        self.src_x = src_x
        self.src_y = src_y
        self.src_char = src_char
        self.src_color = src_color
        
        self.dst_x = dst_x
        self.dst_y = dst_y
        self.dst_char = dst_char
        self.dst_color = dst_color
        
        self.curr_x = src_x
        self.curr_y = src_y
        self.curr_char = src_char
        self.curr_color = src_color
        
        self.delay = delay  # Staggered wave timing
        
        # Swirl control point for organic curve trajectory
        mid_x = (src_x + dst_x) / 2.0
        mid_y = (src_y + dst_y) / 2.0
        dist = math.hypot(dst_x - src_x, dst_y - src_y)
        angle = math.atan2(dst_y - src_y, dst_x - src_x) + math.pi / 2.0
        offset = random.uniform(-0.35, 0.35) * dist
        self.ctrl_x = mid_x + math.cos(angle) * offset
        self.ctrl_y = mid_y + math.sin(angle) * offset

    def update(self, global_progress):
        """Global progress 0.0 -> 1.0 with individual delay factor."""
        # Local progress normalized after delay
        if global_progress <= self.delay:
            loc_t = 0.0
        else:
            loc_t = (global_progress - self.delay) / (1.0 - self.delay + 1e-5)
            loc_t = min(1.0, max(0.0, loc_t))

        # Quintic / elastic smoothstep
        ease = loc_t * loc_t * (3.0 - 2.0 * loc_t)

        # Quadratic Bezier Curve: B(t) = (1-t)^2 P0 + 2(1-t)t P1 + t^2 P2
        inv = 1.0 - ease
        self.curr_x = inv * inv * self.src_x + 2.0 * inv * ease * self.ctrl_x + ease * ease * self.dst_x
        self.curr_y = inv * inv * self.src_y + 2.0 * inv * ease * self.ctrl_y + ease * ease * self.dst_y

        # Character and color morph
        if ease < 0.45:
            self.curr_char = self.src_char
            self.curr_color = self.src_color
        elif ease < 0.65:
            # Transition glyphs
            self.curr_char = "*" if random.random() < 0.5 else self.dst_char
            # Blend color
            factor = (ease - 0.45) / 0.20
            r = int(self.src_color[0] * (1 - factor) + self.dst_color[0] * factor)
            g = int(self.src_color[1] * (1 - factor) + self.dst_color[1] * factor)
            b = int(self.src_color[2] * (1 - factor) + self.dst_color[2] * factor)
            self.curr_color = (r, g, b)
        else:
            self.curr_char = self.dst_char
            self.curr_color = self.dst_color

    def draw(self, surface, font, breeze_offset_x=0.0):
        x = self.curr_x + breeze_offset_x
        y = self.curr_y
        text_surf = font.render(self.curr_char, True, self.curr_color)
        surface.blit(text_surf, (int(x), int(y)))


# ==============================================================================
# MAIN APPLICATION ENGINE
# ==============================================================================
def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Fonts
    font_mono = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 13, bold=True)
    font_title = pygame.font.SysFont(["georgia", "timesnewroman", "serif"], 28, bold=True)
    font_sub = pygame.font.SysFont(["consolas", "sans-serif"], 15)
    font_prompt = pygame.font.SysFont(["consolas", "sans-serif"], 16, bold=True)

    # 1. Generate Envelope and Bouquet Models
    center_x = WINDOW_WIDTH // 2
    center_y = WINDOW_HEIGHT // 2 - 20
    envelope = EnvelopeModel(center_x, center_y, width=780, height=460)
    bouquet = BouquetModel(center_x, center_y - 20, total_points=len(envelope.cells))

    # 2. Pair Envelope Cells to Bouquet Points for Morphing
    morph_nodes = []
    # Sort points radially for wave dissipation
    sorted_cells = sorted(
        envelope.cells,
        key=lambda c: math.hypot(c["x"] - center_x, c["y"] - center_y)
    )

    rng = random.Random(999)
    # Shuffle destination points slightly for natural organic flight
    dst_indices = list(range(len(bouquet.points)))
    rng.shuffle(dst_indices)

    max_dist = max(math.hypot(c["x"] - center_x, c["y"] - center_y) for c in sorted_cells)

    for i, cell in enumerate(sorted_cells):
        dst_idx = dst_indices[i % len(bouquet.points)]
        bx, by, bchar, bcol, bdepth = bouquet.points[dst_idx]
        
        # Stagger delay: center opens first, radiating outwards
        dist_from_center = math.hypot(cell["x"] - center_x, cell["y"] - center_y)
        delay = (dist_from_center / (max_dist + 1e-4)) * 0.40  # up to 40% staggered
        
        node = MorphingNode(
            src_x=cell["x"],
            src_y=cell["y"],
            src_char=cell["char"],
            src_color=cell["color"],
            dst_x=bx,
            dst_y=by,
            dst_char=bchar,
            dst_color=bcol,
            delay=delay
        )
        morph_nodes.append(node)

    # State Machine Variables
    # 0 = WAITING_INTERACTION (Envelope glowing, waiting for click / touch)
    # 1 = OPENING_BURST (Seal pops, particles blast outwards)
    # 2 = MORPHING (Characters flowing along curves into bouquet)
    # 3 = BOUQUET_ACTIVE (Bouquet breathing, petals drifting, text typed)
    STATE_WAITING = 0
    STATE_BURST = 1
    STATE_MORPHING = 2
    STATE_ACTIVE = 3

    current_state = STATE_WAITING
    state_start_time = time.time()
    morph_progress = 0.0
    particles = []

    # Text Messages
    FINAL_TITLE = "For Someone Special 💐"
    FINAL_BODY = "Wishing you endless joy, blooming love, and beautiful days."

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now = time.time()
        mouse_pos = pygame.mouse.get_pos()
        hovering_envelope = (
            envelope.left <= mouse_pos[0] <= envelope.right and
            envelope.top <= mouse_pos[1] <= envelope.bottom
        )

        # ----------------------------------------------------------------------
        # EVENT HANDLING (Mouse Click, Touchscreen, Keyboard)
        # ----------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    # Trigger interaction via keyboard
                    if current_state == STATE_WAITING:
                        current_state = STATE_BURST
                        state_start_time = now
                    elif current_state == STATE_ACTIVE:
                        # Reset
                        current_state = STATE_WAITING
                        morph_progress = 0.0
                        particles.clear()
            
            # MOUSE & TOUCHSCREEN INTERACTION
            elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
                if current_state == STATE_WAITING:
                    current_state = STATE_BURST
                    state_start_time = now
                    # Spawn explosive burst of sparkles from center seal
                    for _ in range(75):
                        ang = random.uniform(0, 2 * math.pi)
                        spd = random.uniform(3.0, 9.5)
                        particles.append(FloatingParticle(
                            center_x, center_y,
                            kind=random.choice(["sparkle", "petal"]),
                            color=random.choice([COL_SEAL_BRIGHT, COL_GOLD_SPARK, COL_WHITE_SPARK, COL_ROSE_PINK]),
                            vx=math.cos(ang) * spd,
                            vy=math.sin(ang) * spd - 2.0
                        ))
                elif current_state == STATE_ACTIVE:
                    # Click to replay
                    current_state = STATE_WAITING
                    morph_progress = 0.0
                    particles.clear()

        # ----------------------------------------------------------------------
        # STATE UPDATES
        # ----------------------------------------------------------------------
        screen.fill(COLOR_BG)
        time_in_state = now - state_start_time

        if current_state == STATE_WAITING:
            # Ambient pulse effect
            pulse = (math.sin(now * 3.8) + 1.0) / 2.0
            seal_pulse = 1.0 + 0.08 * math.sin(now * 5.0)

            # Draw envelope cells
            for cell in envelope.cells:
                cx = cell["x"]
                cy = cell["y"]
                ch = cell["char"]
                col = cell["color"]

                # If it's the heart wax seal, apply glowing heartbeat
                if cell["is_seal"]:
                    # Slightly scale out from center seal
                    dx = cx - center_x
                    dy = cy - center_y
                    cx = center_x + dx * seal_pulse
                    cy = center_y + dy * seal_pulse
                    # Brighten color when hovered
                    if hovering_envelope:
                        col = (
                            min(255, int(col[0] * 1.25)),
                            min(255, int(col[1] * 1.25)),
                            min(255, int(col[2] * 1.25)),
                        )
                elif hovering_envelope:
                    # Subtle ambient glow when user hovers mouse / pointer
                    col = (
                        min(255, int(col[0] * 1.06)),
                        min(255, int(col[1] * 1.06)),
                        min(255, int(col[2] * 1.06)),
                    )

                text_surf = font_mono.render(ch, True, col)
                screen.blit(text_surf, (int(cx), int(cy)))

            # Ambient sparkles drifting off wax seal
            if random.random() < 0.22:
                sx = center_x + random.randint(-40, 40)
                sy = center_y + random.randint(-30, 30)
                particles.append(FloatingParticle(sx, sy, kind="sparkle", color=COL_GOLD_SPARK))

            # Interactive Prompt below envelope
            prompt_alpha = (math.sin(now * 4.0) + 1.0) / 2.0
            p_col = (
                int(255 * (0.6 + 0.4 * prompt_alpha)),
                int(220 * (0.6 + 0.4 * prompt_alpha)),
                int(160 * (0.6 + 0.4 * prompt_alpha))
            )
            prompt_str = "💌  [ TAP / CLICK THE ENVELOPE TO OPEN ]  💌"
            prompt_surf = font_prompt.render(prompt_str, True, p_col)
            prompt_rect = prompt_surf.get_rect(center=(center_x, WINDOW_HEIGHT - 65))
            screen.blit(prompt_surf, prompt_rect)

        elif current_state == STATE_BURST:
            # 0.4 seconds initial burst vibration
            if time_in_state > 0.4:
                current_state = STATE_MORPHING
                state_start_time = now

            # Shake envelope slightly before flight
            shake_x = random.uniform(-2.5, 2.5)
            shake_y = random.uniform(-2.5, 2.5)
            for cell in envelope.cells:
                text_surf = font_mono.render(cell["char"], True, cell["color"])
                screen.blit(text_surf, (int(cell["x"] + shake_x), int(cell["y"] + shake_y)))

        elif current_state == STATE_MORPHING:
            # Duration: 3.2 seconds smooth flight
            duration = 3.2
            morph_progress = min(1.0, time_in_state / duration)

            # Update and draw each morphing node
            for node in morph_nodes:
                node.update(morph_progress)
                node.draw(screen, font_mono)

            # Mid-flight sparkles
            if random.random() < 0.5:
                rand_node = random.choice(morph_nodes)
                particles.append(FloatingParticle(
                    rand_node.curr_x, rand_node.curr_y,
                    kind="sparkle",
                    color=random.choice([COL_GOLD_SPARK, COL_ROSE_PINK, COL_WHITE_SPARK])
                ))

            if morph_progress >= 1.0:
                current_state = STATE_ACTIVE
                state_start_time = now

        elif current_state == STATE_ACTIVE:
            # Flower bouquet is fully formed and gently breathing in the wind
            breeze = math.sin(now * 1.8) * 4.0
            
            # Draw all bouquet nodes
            for node in morph_nodes:
                node.draw(screen, font_mono, breeze_offset_x=breeze * 0.4)

            # Continuous petal and pollen sparkles floating up
            if random.random() < 0.28:
                px = center_x + random.uniform(-180, 180)
                py = center_y + random.uniform(-140, 80)
                particles.append(FloatingParticle(
                    px, py,
                    kind=random.choice(["petal", "sparkle"]),
                    color=random.choice([COL_ROSE_LIGHT, COL_GOLD_SPARK, COL_PEONY_SOFT, COL_WHITE_SPARK]),
                    vy=random.uniform(-2.2, -0.7)
                ))

            # Fading in typography & typewriter message
            active_time = now - state_start_time
            fade_in = min(1.0, active_time / 1.5)

            # Title
            title_col = (
                int(COL_GOLD_SPARK[0] * fade_in),
                int(COL_GOLD_SPARK[1] * fade_in),
                int(COL_GOLD_SPARK[2] * fade_in),
            )
            title_surf = font_title.render(FINAL_TITLE, True, title_col)
            title_rect = title_surf.get_rect(center=(center_x, WINDOW_HEIGHT - 120))
            screen.blit(title_surf, title_rect)

            # Typewriter body
            if active_time > 0.8:
                type_progress = min(1.0, (active_time - 0.8) / 2.0)
                chars_to_show = int(len(FINAL_BODY) * type_progress)
                current_msg = FINAL_BODY[:chars_to_show]
                
                body_col = (
                    int(255 * fade_in),
                    int(240 * fade_in),
                    int(245 * fade_in),
                )
                body_surf = font_sub.render(current_msg, True, body_col)
                body_rect = body_surf.get_rect(center=(center_x, WINDOW_HEIGHT - 80))
                screen.blit(body_surf, body_rect)

            # Replay hint
            if active_time > 3.0:
                hint_alpha = (math.sin(now * 3.0) + 1.0) / 2.0
                h_col = (
                    int(160 * hint_alpha),
                    int(140 * hint_alpha),
                    int(180 * hint_alpha)
                )
                hint_surf = font_sub.render("[ Click / Tap anywhere to replay ]", True, h_col)
                hint_rect = hint_surf.get_rect(center=(center_x, WINDOW_HEIGHT - 35))
                screen.blit(hint_surf, hint_rect)

        # ----------------------------------------------------------------------
        # UPDATE & DRAW PARTICLES
        # ----------------------------------------------------------------------
        alive_particles = []
        for p in particles:
            p.update()
            if p.alive:
                p.draw(screen, font_mono)
                alive_particles.append(p)
        particles = alive_particles

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
