import math
import random
import sys
import time
import numpy as np
import pygame

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
TITLE = "Special Letter 3D"
WINDOW_WIDTH = 1150
WINDOW_HEIGHT = 860
FPS = 60

# 3D Camera Projection
FOV = 900.0
CAMERA_DIST = 920.0
ZOOM_MIN = 450.0
ZOOM_MAX = 1600.0

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

# Bouquet Floral Colors
COL_WRAP_OUTER = (242, 222, 215)
COL_WRAP_INNER = (252, 238, 230)
COL_WRAP_SHADOW = (180, 145, 155)
COL_RIBBON = (255, 75, 135)
COL_RIBBON_GOLD = (255, 215, 110)

COL_STEM_DEEP = (35, 105, 50)
COL_STEM_LIGHT = (65, 160, 82)
COL_LEAF_DARK = (45, 125, 62)
COL_LEAF_BRIGHT = (82, 190, 100)
COL_LEAF_MINT = (130, 215, 155)
COL_EUCALYPTUS = (110, 185, 155)

# Flower Bloom Gradients
COL_ROSE_DEEP = (130, 8, 35)        # Deep velvet wine
COL_ROSE_RED = (235, 25, 65)        # Rich crimson
COL_ROSE_CORAL = (255, 90, 145)     # Glowing coral rose
COL_ROSE_CHAMPAGNE = (255, 205, 225) # Soft petal edge highlight

COL_PEONY_PURPLE = (165, 70, 225)
COL_PEONY_LILAC = (215, 140, 255)
COL_PEONY_SOFT = (250, 210, 255)

COL_TULIP_CORAL = (255, 115, 90)
COL_TULIP_APRICOT = (255, 175, 125)

COL_DAISY_WHITE = (255, 252, 248)
COL_DAISY_YELLOW = (255, 215, 55)

COL_BABY_BREATH = (255, 250, 240)
COL_GOLD_SPARK = (255, 235, 145)
COL_WHITE_SPARK = (255, 255, 255)

# Characters
ASCII_CHARS_DENSE = ["8", "%", "&", "#", "S", "B", "w", "m", "Z", "X", "Q", "0"]
ASCII_CHARS_MED = ["o", "*", "a", "s", "z", "x", "e", "u", "r", "n", "v"]
SPARKLE_CHARS = ["*", "+", "·", "✧", "✦", "°", "•", "♡", "❀"]


# ==============================================================================
# 3D MATH & PROJECTION ENGINE
# ==============================================================================
def create_rotation_matrix(pitch, yaw, roll=0.0):
    """Calculates combined 3x3 rotation matrix for 3D camera orientation."""
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    cr, sr = math.cos(roll), math.sin(roll)

    R = np.array([
        [cy * cr + sy * sp * sr, -cy * sr + sy * sp * cr, sy * cp],
        [cp * sr,                cp * cr,                -sp],
        [-sy * cr + cy * sp * sr, sy * sr + cy * sp * cr, cy * cp]
    ], dtype=np.float32)
    return R


def project_points_3d(pts_3d, R_cam, cam_dist, fov, center_screen):
    """Projects Nx3 world coordinates to screen space with depth sorting."""
    rotated = pts_3d @ R_cam.T
    z_eye = rotated[:, 2] + cam_dist
    z_safe = np.maximum(z_eye, 40.0)
    scale = fov / z_safe
    screen_x = center_screen[0] + rotated[:, 0] * scale
    screen_y = center_screen[1] + rotated[:, 1] * scale
    depth_order = np.argsort(z_eye)[::-1]
    return screen_x, screen_y, z_safe, scale, depth_order


# ==============================================================================
# PURE ASCII / TYPOGRAPHY REPLAY ICON BUTTON
# ==============================================================================
class AsciiReplayButton:
    """A purely ASCII / Typography Art Replay Icon button at bottom-left."""
    # Custom ASCII badge icon design (circular return arrow in ASCII)
    ICON_LINES = [
        " .----. ",
        "/  <-- \\",
        "\\      /",
        " '----' "
    ]

    def __init__(self, x=40, y=WINDOW_HEIGHT - 95):
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
        # Color transition when hovered
        if self.is_hovered:
            col_fg = (255, 235, 180)     # Bright glowing gold
            col_accent = (255, 80, 160)  # Vivid pink
            col_bg = (35, 20, 45)
            col_border = (200, 120, 220)
        else:
            col_fg = (210, 180, 235)     # Soft lavender
            col_accent = (180, 100, 210)
            col_bg = (20, 14, 28)
            col_border = (80, 55, 105)

        # Subtle backdrop badge
        pygame.draw.rect(surface, col_bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, col_border, self.rect, 1, border_radius=8)

        # Render ASCII icon characters
        for r_idx, line in enumerate(self.ICON_LINES):
            py = self.y + r_idx * self.char_h
            for c_idx, ch in enumerate(line):
                if ch != " ":
                    px = self.x + c_idx * self.char_w
                    color = col_accent if ch in ["<", "-", "-"] else col_fg
                    t_surf = font.render(ch, True, color)
                    surface.blit(t_surf, (int(px), int(py)))


# ==============================================================================
# HIGH-DETAIL 3D ENVELOPE GENERATOR
# ==============================================================================
class Envelope3D:
    def __init__(self, width=750.0, height=445.0):
        self.w = width
        self.h = height
        
        self.char_w = 9.0
        self.char_h = 14.8
        self.cols = int(self.w / self.char_w)
        self.rows = int(self.h / self.char_h)
        
        self.all_envelope_points = []
        self._build_envelope()

    def _build_envelope(self):
        rng = random.Random(42)
        
        for r in range(self.rows):
            y = -self.h / 2.0 + r * self.char_h
            ny = r / (self.rows - 1)
            
            for c in range(self.cols):
                x = -self.w / 2.0 + c * self.char_w
                nx = c / (self.cols - 1)
                
                is_top = (r == 0)
                is_bot = (r == self.rows - 1)
                is_left = (c == 0)
                is_right = (c == self.cols - 1)
                
                dx = abs(nx - 0.5) * 2.0
                top_flap_crease = abs(ny - (1.0 - dx) * 0.5) < 0.032 and ny <= 0.52
                bot_flap_crease = abs((1.0 - ny) - (1.0 - dx) * 0.5) < 0.032 and ny >= 0.48
                
                # Heart seal math
                seal_dx = x / 36.0
                seal_dy = y / 32.0
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
                z = -4.5 if is_seal else 0.0
                
                self.all_envelope_points.append({
                    "orig_3d": np.array([x, y, z], dtype=np.float32),
                    "char": char,
                    "color": color,
                    "is_seal": is_seal,
                    "is_flap": is_flap,
                    "hinge_y": -self.h / 2.0,
                })

    def get_3d_coordinates(self, flap_angle=0.0):
        coords = np.zeros((len(self.all_envelope_points), 3), dtype=np.float32)
        c_flap = math.cos(flap_angle)
        s_flap = math.sin(flap_angle)
        hinge_y = -self.h / 2.0
        
        for i, pt in enumerate(self.all_envelope_points):
            orig = pt["orig_3d"]
            if pt["is_flap"] and flap_angle > 0.0:
                dy = orig[1] - hinge_y
                dz = orig[2]
                ny = hinge_y + dy * c_flap - dz * s_flap
                nz = dy * s_flap + dz * c_flap
                coords[i] = [orig[0], ny, nz]
            else:
                coords[i] = orig
        return coords


# ==============================================================================
# REDESIGNED GORGEOUS 3D BOTANICAL BOUQUET
# ==============================================================================
class Bouquet3D:
    """Volumetric 3D flower bouquet with Korean layered kraft wrap, rich multi-tier blooms."""
    def __init__(self, total_points=2400):
        self.total_points = total_points
        self.points_3d = np.zeros((total_points, 3), dtype=np.float32)
        self.glyphs = []
        self.colors = []
        self._generate_3d_bouquet()

    def _generate_3d_bouquet(self):
        rng = random.Random(999)
        pts_list = []
        glyphs_list = []
        colors_list = []

        # ----------------------------------------------------------------------
        # 1. KOREAN FLORAL KRAFT WRAPPING (Collar Backdrop + Bottom Conical Wrap)
        # ----------------------------------------------------------------------
        # A. Flared Paper Collar (Rises up behind the flowers in 3D: z > 0)
        num_collar = int(self.total_points * 0.12)
        for _ in range(num_collar):
            u = rng.uniform(0.0, 1.0)
            ang = rng.uniform(-math.pi * 0.85, math.pi * 0.85)
            r = 160.0 + u * 75.0
            x = math.sin(ang) * r
            y = -110.0 - math.cos(ang) * (r * 0.55) + u * 30.0
            z = 25.0 + u * 70.0  # Placed behind blooms
            
            # Pleated paper texture
            pleat = math.sin(ang * 8.0)
            ch = rng.choice(["/", "\\", "|", "%"]) if pleat > 0 else rng.choice(["#", "%", "="])
            col = COL_WRAP_OUTER if u > 0.4 else COL_WRAP_INNER
            pts_list.append([x, y, z])
            glyphs_list.append(ch)
            colors_list.append(col)

        # B. Bottom Conical Wrap (Under the bouquet)
        wrap_top_y = 65.0
        wrap_bot_y = 280.0
        wrap_top_r = 145.0
        wrap_bot_r = 38.0
        
        num_cone = int(self.total_points * 0.14)
        for _ in range(num_cone):
            u = rng.uniform(0.0, 1.0)
            y = wrap_top_y + u * (wrap_bot_y - wrap_top_y)
            r = wrap_top_r * (1.0 - u) + wrap_bot_r * u
            theta = rng.uniform(-math.pi * 0.9, math.pi * 0.9)
            x = math.sin(theta) * r
            z = math.cos(theta) * r * 0.72
            
            if abs(theta) > math.pi * 0.65:
                col = COL_WRAP_SHADOW
                ch = rng.choice(["|", "/", "\\", "%"])
            else:
                col = COL_WRAP_OUTER if rng.random() < 0.6 else COL_WRAP_INNER
                ch = rng.choice(["#", "%", "8", "=", ":"])
            pts_list.append([x, y, z])
            glyphs_list.append(ch)
            colors_list.append(col)

        # C. 3D Satin Ribbon with Bow Loops
        ribbon_y = wrap_top_y + 36.0
        num_ribbon = int(self.total_points * 0.06)
        for _ in range(num_ribbon):
            choice = rng.random()
            if choice < 0.38:
                ang = rng.uniform(0, 2 * math.pi)
                rad = rng.uniform(8.0, 36.0)
                x = -36.0 + math.cos(ang) * rad * 1.35
                y = ribbon_y + math.sin(ang) * rad * 0.75
                z = -math.sin(ang) * 16.0 - 20.0
                col = COL_RIBBON
            elif choice < 0.76:
                ang = rng.uniform(0, 2 * math.pi)
                rad = rng.uniform(8.0, 36.0)
                x = 36.0 + math.cos(ang) * rad * 1.35
                y = ribbon_y + math.sin(ang) * rad * 0.75
                z = -math.sin(ang) * 16.0 - 20.0
                col = COL_RIBBON
            else:
                x = rng.uniform(-18, 18)
                y = ribbon_y + rng.uniform(-15, 15)
                z = -30.0 + rng.uniform(-5, 5)
                col = COL_RIBBON_GOLD
            
            pts_list.append([x, y, z])
            glyphs_list.append(rng.choice(["♥", "@", "*", "%"]))
            colors_list.append(col)

        # ----------------------------------------------------------------------
        # 2. 3D BOTANICAL FOLIAGE (Eucalyptus, Ferns, Stems)
        # ----------------------------------------------------------------------
        num_foliage = int(self.total_points * 0.20)
        leaf_anchors = [
            # (ax, ay, az, a_xy, a_z, len, wid, col)
            (-155.0, -15.0, -20.0, -0.65, 0.35, 140.0, 52.0, COL_LEAF_BRIGHT),
            (155.0, -15.0, -20.0,   0.65, 0.35, 140.0, 52.0, COL_LEAF_BRIGHT),
            (-130.0, -90.0, -50.0, -0.95, -0.20, 120.0, 44.0, COL_EUCALYPTUS),
            (130.0, -90.0, -50.0,   0.95, -0.20, 120.0, 44.0, COL_EUCALYPTUS),
            (-70.0, -180.0, 20.0,  -1.30, 0.40, 105.0, 38.0, COL_LEAF_MINT),
            (70.0, -180.0, 20.0,    1.30, 0.40, 105.0, 38.0, COL_LEAF_MINT),
            (0.0, -215.0, -25.0,    0.0,  0.50, 95.0, 35.0, COL_LEAF_BRIGHT),
            (-115.0, -40.0, 60.0,  -0.5, -0.60, 110.0, 44.0, COL_LEAF_DARK),
            (115.0, -40.0, 60.0,    0.5, -0.60, 110.0, 44.0, COL_LEAF_DARK),
        ]

        for _ in range(num_foliage):
            la = rng.choice(leaf_anchors)
            ax, ay, az, a_xy, a_z, llen, lwid, lcol = la
            u = rng.uniform(0.1, 1.0)
            v = rng.uniform(-1.0, 1.0)
            
            if abs(v) <= math.sin(u * math.pi):
                dist_along = u * llen
                dist_across = v * lwid * 0.5
                c_xy, s_xy = math.cos(a_xy), math.sin(a_xy)
                px = ax + c_xy * dist_along - s_xy * dist_across
                py = ay + s_xy * dist_along + c_xy * dist_across
                pz = az + math.sin(a_z) * dist_along + math.sin(u * math.pi) * 15.0
                
                ch = rng.choice(["$", "%", "8", "*", "#", ";"])
                col = lcol if abs(v) > 0.3 else COL_STEM_DEEP
                pts_list.append([px, py, pz])
                glyphs_list.append(ch)
                colors_list.append(col)

        # ----------------------------------------------------------------------
        # 3. 3D MASTER ROSE (Centerpiece - Fibonacci Spiral)
        # ----------------------------------------------------------------------
        GOLDEN_ANGLE = 137.507764 * (math.pi / 180.0)
        num_rose = int(self.total_points * 0.22)
        rcx, rcy, rcz = 0.0, -62.0, -85.0
        rose_max_r = 92.0
        
        for i in range(num_rose):
            frac = i / (num_rose - 1)
            r = math.sqrt(frac) * rose_max_r
            theta = i * GOLDEN_ANGLE
            r_scallop = r * (1.0 + 0.15 * math.sin(5.0 * theta))
            
            px = rcx + math.cos(theta) * r_scallop
            py = rcy + math.sin(theta) * r_scallop * 0.94
            # Deep conical cup to flared outward petals in 3D
            pz = rcz - math.cos(frac * math.pi * 0.5) * 42.0 + (frac * 14.0)
            
            if frac < 0.18:
                col = COL_ROSE_DEEP
                ch = rng.choice(["@", "#", "♥"])
            elif frac < 0.52:
                col = COL_ROSE_RED
                ch = rng.choice(["%", "&", "♥", "8"])
            elif frac < 0.84:
                col = COL_ROSE_CORAL
                ch = rng.choice(["*", "✿", "(", ")"])
            else:
                col = COL_ROSE_CHAMPAGNE
                ch = rng.choice(["❀", "c", "o", "·"])
                
            pts_list.append([px, py, pz])
            glyphs_list.append(ch)
            colors_list.append(col)

        # ----------------------------------------------------------------------
        # 4. SURROUNDING LUXURY BLOOMS (Peonies, Apricot Tulips, Daisies, Baby's Breath)
        # ----------------------------------------------------------------------
        surrounding_heads = [
            # Left Fluffy Lilac Peony
            {"cx": -96.0, "cy": -50.0, "cz": -35.0, "rad": 72.0, "type": "peony", "col_core": COL_PEONY_PURPLE, "col_mid": COL_PEONY_LILAC, "col_edge": COL_PEONY_SOFT},
            # Right Velvet Rose
            {"cx": 96.0, "cy": -50.0, "cz": -35.0, "rad": 72.0, "type": "rose", "col_core": COL_ROSE_DEEP, "col_mid": COL_ROSE_CORAL, "col_edge": COL_ROSE_CHAMPAGNE},
            # Top-Left Coral/Apricot Tulip
            {"cx": -65.0, "cy": -145.0, "cz": -15.0, "rad": 54.0, "type": "tulip", "col_core": COL_TULIP_CORAL, "col_mid": COL_TULIP_CORAL, "col_edge": COL_TULIP_APRICOT},
            # Top-Right Pink Blossom
            {"cx": 65.0, "cy": -145.0, "cz": -15.0, "rad": 54.0, "type": "rose", "col_core": COL_ROSE_RED, "col_mid": COL_ROSE_CORAL, "col_edge": COL_ROSE_CHAMPAGNE},
            # Perimeter Starry Daisies
            {"cx": -142.0, "cy": 16.0, "cz": 25.0, "rad": 40.0, "type": "daisy", "col_core": COL_DAISY_YELLOW, "col_mid": COL_DAISY_WHITE, "col_edge": COL_DAISY_WHITE},
            {"cx": 142.0, "cy": 16.0, "cz": 25.0, "rad": 40.0, "type": "daisy", "col_core": COL_DAISY_YELLOW, "col_mid": COL_DAISY_WHITE, "col_edge": COL_DAISY_WHITE},
            {"cx": 0.0, "cy": -175.0, "cz": 20.0, "rad": 42.0, "type": "daisy", "col_core": COL_DAISY_YELLOW, "col_mid": COL_DAISY_WHITE, "col_edge": COL_DAISY_WHITE},
        ]

        rem_pts = self.total_points - len(pts_list)
        pts_per_head = rem_pts // len(surrounding_heads)

        for bl in surrounding_heads:
            fcx = bl["cx"]
            fcy = bl["cy"]
            fcz = bl["cz"]
            frad = bl["rad"]
            ftype = bl["type"]
            
            for i in range(pts_per_head):
                if ftype in ["rose", "peony"]:
                    frac = i / (pts_per_head - 1)
                    r = math.sqrt(frac) * frad
                    theta = i * GOLDEN_ANGLE
                    r_scallop = r * (1.0 + 0.12 * math.sin(7.0 * theta))
                    
                    px = fcx + math.cos(theta) * r_scallop
                    py = fcy + math.sin(theta) * r_scallop
                    pz = fcz - math.cos(frac * math.pi * 0.5) * (frad * 0.44)
                    
                    if frac < 0.28:
                        col = bl["col_core"]
                        ch = rng.choice(["@", "#", "♥"])
                    elif frac < 0.74:
                        col = bl["col_mid"]
                        ch = rng.choice(["%", "&", "8", "♥", "✿"])
                    else:
                        col = bl["col_edge"]
                        ch = rng.choice(["*", "(", ")", "c", "❀"])
                
                elif ftype == "tulip":
                    u = rng.uniform(0.0, 1.0)
                    ang_around = rng.uniform(0, 2 * math.pi)
                    rad_tube = frad * 0.65 * math.sin(u * math.pi * 0.8 + 0.2)
                    
                    px = fcx + math.cos(ang_around) * rad_tube
                    py = fcy - u * frad * 1.1 + frad * 0.4
                    pz = fcz + math.sin(ang_around) * rad_tube
                    
                    col = bl["col_mid"] if u > 0.4 else bl["col_core"]
                    ch = rng.choice(["#", "%", "8", "U", "V", "|"])
                
                else:  # daisy / baby's breath
                    r = rng.uniform(0.0, frad)
                    theta = rng.uniform(0, 2 * math.pi)
                    px = fcx + math.cos(theta) * r
                    py = fcy + math.sin(theta) * r
                    pz = fcz + (r / frad) * 10.0
                    
                    if r < frad * 0.35:
                        col = bl["col_core"]
                        ch = rng.choice(["*", "@", "•", "o"])
                    else:
                        col = bl["col_mid"]
                        ch = rng.choice(["+", "|", "/", "\\", "1", "i"])

                pts_list.append([px, py, pz])
                glyphs_list.append(ch)
                colors_list.append(col)

        # 5. Baby's Breath Star Constellations (Fills remaining gaps with delicate stars)
        while len(pts_list) < self.total_points:
            ang = rng.uniform(0, 2 * math.pi)
            rad = rng.uniform(40.0, 170.0)
            px = math.cos(ang) * rad
            py = -70.0 + math.sin(ang) * rad * 0.8
            pz = rng.uniform(-60.0, 40.0)
            pts_list.append([px, py, pz])
            glyphs_list.append(rng.choice(["*", "·", "+", "°", "✧"]))
            colors_list.append(rng.choice([COL_BABY_BREATH, COL_WHITE_SPARK, COL_GOLD_SPARK]))

        self.points_3d = np.array(pts_list[:self.total_points], dtype=np.float32)
        self.glyphs = glyphs_list[:self.total_points]
        self.colors = colors_list[:self.total_points]


# ==============================================================================
# 3D FLOATING PARTICLES
# ==============================================================================
class Particle3D:
    def __init__(self, x, y, z, kind="sparkle", color=None, vx=None, vy=None, vz=None):
        self.pos = np.array([x, y, z], dtype=np.float32)
        self.kind = kind
        self.char = random.choice(SPARKLE_CHARS) if kind == "sparkle" else random.choice(["♥", "❀", "·", "•"])
        self.color = color or random.choice([COL_GOLD_SPARK, COL_WHITE_SPARK, COL_ROSE_CHAMPAGNE, COL_SEAL_BRIGHT])
        
        self.vel = np.array([
            vx if vx is not None else random.uniform(-1.8, 1.8),
            vy if vy is not None else random.uniform(-2.8, -0.7),
            vz if vz is not None else random.uniform(-1.8, 1.8)
        ], dtype=np.float32)
        
        self.lifespan = random.randint(45, 110)
        self.age = 0
        self.alive = True
        self.wobble_freq = random.uniform(2.0, 5.0)

    def update(self):
        self.pos += self.vel
        self.pos[0] += math.sin(self.age * 0.08 * self.wobble_freq) * 0.9
        self.pos[2] += math.cos(self.age * 0.08 * self.wobble_freq) * 0.9
        self.age += 1
        if self.age >= self.lifespan:
            self.alive = False


# ==============================================================================
# MAIN 3D APPLICATION
# ==============================================================================
def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Fonts
    font_mono_lg = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 14, bold=True)
    font_mono_md = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 12, bold=True)
    font_mono_sm = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 10, bold=True)
    font_btn = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 14, bold=True)

    # 1. Models & Replay Button
    envelope = Envelope3D(width=750.0, height=445.0)
    total_pts = len(envelope.all_envelope_points)
    bouquet = Bouquet3D(total_points=total_pts)
    replay_btn = AsciiReplayButton(x=45, y=WINDOW_HEIGHT - 85)

    env_coords_initial = envelope.get_3d_coordinates(flap_angle=0.0)
    bouquet_target_3d = bouquet.points_3d.copy()

    # 2. Setup Morphing Pairs with 3D Bezier Splines
    center_env = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    distances = np.linalg.norm(env_coords_initial - center_env, axis=1)
    max_dist = np.max(distances)
    delays = (distances / (max_dist + 1e-4)) * 0.42

    rng_ctrl = random.Random(555)
    ctrl_points_3d = np.zeros_like(env_coords_initial)
    for i in range(total_pts):
        p0 = env_coords_initial[i]
        p2 = bouquet_target_3d[i]
        mid = (p0 + p2) * 0.5
        d = np.linalg.norm(p2 - p0)
        rand_vec = np.array([
            rng_ctrl.uniform(-1, 1),
            rng_ctrl.uniform(-1, 1),
            rng_ctrl.uniform(-1, 1)
        ], dtype=np.float32)
        rand_vec /= (np.linalg.norm(rand_vec) + 1e-5)
        ctrl_points_3d[i] = mid + rand_vec * (d * rng_ctrl.uniform(0.25, 0.55))

    # 3. Interactive Camera Parameters
    cam_pitch = math.radians(12.0)
    cam_yaw = math.radians(-16.0)
    cam_dist = CAMERA_DIST

    is_dragging = False
    last_mouse_pos = (0, 0)
    has_dragged = False

    # States
    STATE_WAITING = 0
    STATE_OPENING = 1
    STATE_MORPHING = 2
    STATE_BOUQUET = 3

    state = STATE_WAITING
    state_start_time = time.time()
    flap_angle = 0.0
    particles_3d = []

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now = time.time()
        time_in_state = now - state_start_time
        center_screen = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        mouse_pos = pygame.mouse.get_pos()

        if state == STATE_BOUQUET:
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

            # MOUSE BUTTON DOWN
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    is_dragging = True
                    has_dragged = False
                    last_mouse_pos = event.pos
                    
                    # Check Replay Button on Bouquet Screen
                    if state == STATE_BOUQUET and replay_btn.rect.collidepoint(event.pos):
                        state = STATE_WAITING
                        state_start_time = now
                        flap_angle = 0.0
                        particles_3d.clear()
                        cam_pitch = math.radians(12.0)
                        cam_yaw = math.radians(-16.0)
                
                # MOUSE WHEEL ZOOM
                elif event.button == 4:
                    cam_dist = max(ZOOM_MIN, cam_dist - 35.0)
                elif event.button == 5:
                    cam_dist = min(ZOOM_MAX, cam_dist + 35.0)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging = False
                    # Tap without dragging in WAITING state opens envelope
                    if state == STATE_WAITING and not has_dragged:
                        state = STATE_OPENING
                        state_start_time = now

            # MOUSE MOTION (3D Orbit Drag)
            elif event.type == pygame.MOUSEMOTION:
                if is_dragging:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    if abs(dx) > 2 or abs(dy) > 2:
                        has_dragged = True
                    cam_yaw += dx * 0.006
                    cam_pitch += dy * 0.006
                    cam_pitch = max(-math.pi * 0.45, min(math.pi * 0.45, cam_pitch))
                    last_mouse_pos = event.pos

            # TOUCH EVENTS
            elif event.type == pygame.FINGERDOWN:
                if state == STATE_WAITING:
                    state = STATE_OPENING
                    state_start_time = now

        # ----------------------------------------------------------------------
        # STATE LOGIC & 3D COORDINATE COMPUTATION
        # ----------------------------------------------------------------------
        screen.fill(COLOR_BG)

        current_3d = np.zeros((total_pts, 3), dtype=np.float32)
        current_glyphs = []
        current_colors = []

        if state == STATE_WAITING:
            idle_yaw = cam_yaw + math.sin(now * 1.5) * 0.03
            idle_pitch = cam_pitch + math.cos(now * 1.2) * 0.02
            R_cam = create_rotation_matrix(idle_pitch, idle_yaw)
            
            current_3d = envelope.get_3d_coordinates(flap_angle=0.0)
            seal_pulse = 1.0 + 0.08 * math.sin(now * 5.0)
            
            for i, pt in enumerate(envelope.all_envelope_points):
                ch = pt["char"]
                col = pt["color"]
                if pt["is_seal"]:
                    current_3d[i, 0] *= seal_pulse
                    current_3d[i, 1] *= seal_pulse
                    current_3d[i, 2] = -6.0 * seal_pulse
                current_glyphs.append(ch)
                current_colors.append(col)

            if random.random() < 0.25:
                particles_3d.append(Particle3D(
                    random.uniform(-40, 40), random.uniform(-30, 30), -15.0,
                    kind="sparkle", color=COL_GOLD_SPARK
                ))

        elif state == STATE_OPENING:
            open_dur = 1.2
            open_t = min(1.0, time_in_state / open_dur)
            open_ease = 1.0 - math.pow(1.0 - open_t, 3)
            flap_angle = open_ease * math.pi * 0.98
            
            R_cam = create_rotation_matrix(cam_pitch, cam_yaw)
            current_3d = envelope.get_3d_coordinates(flap_angle=flap_angle)
            
            if time_in_state < 0.06:
                for _ in range(85):
                    ang_xy = random.uniform(0, 2 * math.pi)
                    ang_z = random.uniform(-math.pi * 0.4, math.pi * 0.4)
                    spd = random.uniform(4.0, 11.0)
                    particles_3d.append(Particle3D(
                        0.0, 0.0, -10.0,
                        kind=random.choice(["sparkle", "petal"]),
                        color=random.choice([COL_SEAL_BRIGHT, COL_GOLD_SPARK, COL_WHITE_SPARK, COL_ROSE_CORAL]),
                        vx=math.cos(ang_xy) * math.cos(ang_z) * spd,
                        vy=math.sin(ang_xy) * math.cos(ang_z) * spd - 2.0,
                        vz=math.sin(ang_z) * spd - 3.0
                    ))

            for pt in envelope.all_envelope_points:
                current_glyphs.append(pt["char"])
                current_colors.append(pt["color"])

            if open_t >= 1.0:
                state = STATE_MORPHING
                state_start_time = now

        elif state == STATE_MORPHING:
            morph_dur = 3.4
            raw_t = min(1.0, time_in_state / morph_dur)
            R_cam = create_rotation_matrix(cam_pitch, cam_yaw + raw_t * 0.15)
            
            for i in range(total_pts):
                d = delays[i]
                if raw_t <= d:
                    loc_t = 0.0
                else:
                    loc_t = (raw_t - d) / (1.0 - d + 1e-5)
                    loc_t = min(1.0, max(0.0, loc_t))
                
                ease = loc_t * loc_t * (3.0 - 2.0 * loc_t)
                inv = 1.0 - ease
                
                p0 = env_coords_initial[i]
                p1 = ctrl_points_3d[i]
                p2 = bouquet_target_3d[i]
                current_3d[i] = inv * inv * p0 + 2.0 * inv * ease * p1 + ease * ease * p2
                
                src_ch = envelope.all_envelope_points[i]["char"]
                src_col = envelope.all_envelope_points[i]["color"]
                dst_ch = bouquet.glyphs[i]
                dst_col = bouquet.colors[i]
                
                if ease < 0.4:
                    current_glyphs.append(src_ch)
                    current_colors.append(src_col)
                elif ease < 0.7:
                    current_glyphs.append("*" if random.random() < 0.5 else dst_ch)
                    frac = (ease - 0.4) / 0.3
                    r = int(src_col[0] * (1 - frac) + dst_col[0] * frac)
                    g = int(src_col[1] * (1 - frac) + dst_col[1] * frac)
                    b = int(src_col[2] * (1 - frac) + dst_col[2] * frac)
                    current_colors.append((r, g, b))
                else:
                    current_glyphs.append(dst_ch)
                    current_colors.append(dst_col)

            if random.random() < 0.6:
                idx = random.randint(0, total_pts - 1)
                particles_3d.append(Particle3D(
                    current_3d[idx, 0], current_3d[idx, 1], current_3d[idx, 2],
                    kind="sparkle", color=random.choice([COL_GOLD_SPARK, COL_ROSE_CORAL])
                ))

            if raw_t >= 1.0:
                state = STATE_BOUQUET
                state_start_time = now

        elif state == STATE_BOUQUET:
            turntable_yaw = cam_yaw + math.sin(time_in_state * 0.45) * 0.22
            turntable_pitch = cam_pitch + math.cos(time_in_state * 0.35) * 0.08
            R_cam = create_rotation_matrix(turntable_pitch, turntable_yaw)
            
            breeze = math.sin(now * 2.2) * 4.5
            current_3d = bouquet_target_3d.copy()
            current_3d[:, 0] += breeze * 0.25 * (current_3d[:, 1] < 0)
            
            current_glyphs = bouquet.glyphs
            current_colors = bouquet.colors

            if random.random() < 0.35:
                px = random.uniform(-140, 140)
                py = random.uniform(-120, 80)
                pz = random.uniform(-90, 60)
                particles_3d.append(Particle3D(
                    px, py, pz,
                    kind=random.choice(["petal", "sparkle"]),
                    color=random.choice([COL_ROSE_CHAMPAGNE, COL_GOLD_SPARK, COL_PEONY_SOFT, COL_WHITE_SPARK]),
                    vy=random.uniform(-2.5, -0.9)
                ))

        # ----------------------------------------------------------------------
        # 3D PROJECTION & RENDERING (Depth-Sorted, No Axes)
        # ----------------------------------------------------------------------
        sx, sy, z_safe, scale, depth_order = project_points_3d(
            current_3d, R_cam, cam_dist, FOV, center_screen
        )

        for idx in depth_order:
            x_screen = sx[idx]
            y_screen = sy[idx]
            sc = scale[idx]
            
            if -30 <= x_screen <= WINDOW_WIDTH + 30 and -30 <= y_screen <= WINDOW_HEIGHT + 30:
                ch = current_glyphs[idx]
                col = current_colors[idx]
                
                if sc > 1.25:
                    font = font_mono_lg
                elif sc > 0.85:
                    font = font_mono_md
                else:
                    font = font_mono_sm

                depth_factor = np.clip(1.35 - (z_safe[idx] / (cam_dist * 1.5)), 0.45, 1.15)
                r = int(np.clip(col[0] * depth_factor, 0, 255))
                g = int(np.clip(col[1] * depth_factor, 0, 255))
                b = int(np.clip(col[2] * depth_factor, 0, 255))
                
                t_surf = font.render(ch, True, (r, g, b))
                screen.blit(t_surf, (int(x_screen), int(y_screen)))

        # ----------------------------------------------------------------------
        # 3D PARTICLES UPDATE & DRAW
        # ----------------------------------------------------------------------
        alive_p = []
        if particles_3d:
            p_coords = np.array([p.pos for p in particles_3d], dtype=np.float32)
            psx, psy, pz, pscale, p_order = project_points_3d(
                p_coords, R_cam, cam_dist, FOV, center_screen
            )
            for p_idx in p_order:
                p = particles_3d[p_idx]
                p.update()
                if p.alive:
                    alive_p.append(p)
                    alpha = math.sin((p.age / p.lifespan) * math.pi)
                    if alpha > 0.05 and 0 <= psx[p_idx] <= WINDOW_WIDTH and 0 <= psy[p_idx] <= WINDOW_HEIGHT:
                        r = int(p.color[0] * alpha)
                        g = int(p.color[1] * alpha)
                        b = int(p.color[2] * alpha)
                        f = font_mono_lg if pscale[p_idx] > 1.0 else font_mono_md
                        surf = f.render(p.char, True, (r, g, b))
                        screen.blit(surf, (int(psx[p_idx]), int(psy[p_idx])))
        particles_3d = alive_p

        # ----------------------------------------------------------------------
        # HUD / REPLAY ICON (No Text Lines, No XYZ Radar)
        # ----------------------------------------------------------------------
        if state == STATE_BOUQUET:
            # Pure ASCII / Typography Replay Icon button
            replay_btn.draw(screen, font_btn)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
