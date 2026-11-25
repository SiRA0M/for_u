import math
import random
import sys
import time
import numpy as np
import pygame

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
TITLE = "Special Letter 3D 💌 Bouquet For You"
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 850
FPS = 60

# Camera & 3D Projection
FOV = 850.0          # Field of view / focal length
CAMERA_DIST = 900.0   # Default camera distance along Z
ZOOM_MIN = 450.0
ZOOM_MAX = 1500.0

# ------------------------------------------------------------------------------
# COLOR PALETTE (RGB)
# ------------------------------------------------------------------------------
COLOR_BG = (10, 8, 16)

# Envelope Colors (Warm Peach / Sepia / Gold with Purple Rim)
COL_BORDER = (245, 215, 195)
COL_PAPER_MAIN = (235, 170, 130)
COL_PAPER_SHADOW = (175, 105, 75)
COL_PAPER_HIGHLIGHT = (255, 225, 190)
COL_GLOW_PURPLE = (150, 95, 230)

# Wax Seal Colors
COL_SEAL_BRIGHT = (255, 60, 150)
COL_SEAL_CORE = (255, 15, 105)
COL_SEAL_OUTER = (210, 25, 90)
COL_SEAL_SPECULAR = (255, 200, 230)

# 3D Bouquet Colors
COL_WRAPPER = (240, 215, 210)
COL_WRAPPER_SHADOW = (190, 150, 160)
COL_RIBBON = (255, 75, 135)
COL_RIBBON_GOLD = (255, 215, 105)

COL_STEM_DEEP = (40, 115, 60)
COL_STEM_LIGHT = (70, 170, 90)
COL_LEAF_DARK = (50, 135, 70)
COL_LEAF_BRIGHT = (90, 200, 110)
COL_LEAF_MINT = (140, 225, 165)

# Flowers
COL_ROSE_RED = (235, 30, 70)
COL_ROSE_PINK = (255, 90, 155)
COL_ROSE_LIGHT = (255, 175, 210)
COL_ROSE_CORE = (175, 10, 45)

COL_PEONY_LILAC = (215, 140, 255)
COL_PEONY_PURPLE = (170, 75, 230)
COL_PEONY_SOFT = (240, 195, 255)

COL_TULIP_CORAL = (255, 120, 105)
COL_TULIP_PEACH = (255, 175, 130)

COL_DAISY_WHITE = (255, 250, 245)
COL_DAISY_YELLOW = (255, 215, 60)

COL_GOLD_SPARK = (255, 235, 145)
COL_WHITE_SPARK = (255, 255, 255)

# Character sets
ASCII_CHARS_DENSE = ["8", "%", "&", "#", "S", "B", "w", "m", "Z", "X", "Q", "0"]
ASCII_CHARS_MED = ["o", "*", "a", "s", "z", "x", "e", "u", "r", "n", "v"]
FLOWER_CHARS = ["@", "%", "&", "8", "♥", "❀", "✿", "*", "(", ")", "c", "o", "S"]
SPARKLE_CHARS = ["*", "+", "·", "✧", "✦", "°", "•", "♡"]


# ==============================================================================
# 3D MATH ENGINE
# ==============================================================================
def create_rotation_matrix(pitch, yaw, roll=0.0):
    """Calculates combined 3x3 rotation matrix for 3D camera orientation."""
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    cr, sr = math.cos(roll), math.sin(roll)

    # R = Rz * Rx * Ry
    R = np.array([
        [cy * cr + sy * sp * sr, -cy * sr + sy * sp * cr, sy * cp],
        [cp * sr,                cp * cr,                -sp],
        [-sy * cr + cy * sp * sr, sy * sr + cy * sp * cr, cy * cp]
    ], dtype=np.float32)
    return R


def project_points_3d(pts_3d, R_cam, cam_dist, fov, center_screen):
    """Projects Nx3 world coordinates to screen space with depth sorting."""
    # Rotate points
    rotated = pts_3d @ R_cam.T
    
    # Camera translation (Camera looks down Z axis)
    z_eye = rotated[:, 2] + cam_dist
    
    # Avoid division by zero
    z_safe = np.maximum(z_eye, 50.0)
    
    # Perspective division
    scale = fov / z_safe
    screen_x = center_screen[0] + rotated[:, 0] * scale
    screen_y = center_screen[1] + rotated[:, 1] * scale
    
    # Sort order: back to front (largest z_eye first)
    depth_order = np.argsort(z_eye)[::-1]
    
    return screen_x, screen_y, z_safe, scale, depth_order


# ==============================================================================
# 3D ENVELOPE GENERATOR (Matching user photo with 3D folding flap)
# ==============================================================================
class Envelope3D:
    def __init__(self, width=720.0, height=430.0):
        self.w = width
        self.h = height
        
        self.char_w = 9.2
        self.char_h = 15.0
        self.cols = int(self.w / self.char_w)
        self.rows = int(self.h / self.char_h)
        
        self.points_static = []  # Points on bottom body (don't fold)
        self.points_flap = []    # Points on top flap (rotate around hinge)
        self.all_envelope_points = []
        self._build_envelope()

    def _build_envelope(self):
        rng = random.Random(42)
        
        for r in range(self.rows):
            # y ranges from -h/2 to +h/2
            y = -self.h / 2.0 + r * self.char_h
            ny = r / (self.rows - 1)  # 0 at top, 1 at bottom
            
            for c in range(self.cols):
                # x ranges from -w/2 to +w/2
                x = -self.w / 2.0 + c * self.char_w
                nx = c / (self.cols - 1)
                
                is_top = (r == 0)
                is_bot = (r == self.rows - 1)
                is_left = (c == 0)
                is_right = (c == self.cols - 1)
                
                dx = abs(nx - 0.5) * 2.0  # 0 at center, 1 at side edges
                top_flap_crease = abs(ny - (1.0 - dx) * 0.5) < 0.035 and ny <= 0.52
                bot_flap_crease = abs((1.0 - ny) - (1.0 - dx) * 0.5) < 0.035 and ny >= 0.48
                
                # Check heart seal
                seal_dx = x / 36.0
                seal_dy = y / 32.0
                sy = -seal_dy - 0.15
                sx = seal_dx
                heart_eq = (sx*sx + sy*sy - 1.0)**3 - sx*sx * (sy**3)
                is_seal = heart_eq <= 0.05
                is_seal_edge = abs(heart_eq) <= 0.12
                
                # Assign characters and colors
                if is_top or is_bot:
                    char = "/" if (c % 2 == 0) else "\\"
                    color = COL_BORDER
                elif is_left:
                    char = "\\"
                    color = COL_BORDER
                elif is_right:
                    char = "/"
                    color = (200, 170, 240)
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
                        char = rng.choice(ASCII_CHARS_DENSE if ny < 0.75 else ASCII_CHARS_MED)
                        base_col = COL_PAPER_MAIN if ny < 0.75 else COL_PAPER_SHADOW
                    
                    jitter = rng.uniform(-14, 14)
                    r_c = max(0, min(255, int(base_col[0] + jitter)))
                    g_c = max(0, min(255, int(base_col[1] + jitter)))
                    b_c = max(0, min(255, int(base_col[2] + jitter)))
                    
                    # Ambient purple rim glow on right
                    if nx > 0.85:
                        p_factor = (nx - 0.85) / 0.15
                        r_c = int(r_c * (1 - p_factor * 0.4) + COL_GLOW_PURPLE[0] * p_factor * 0.4)
                        g_c = int(g_c * (1 - p_factor * 0.4) + COL_GLOW_PURPLE[1] * p_factor * 0.4)
                        b_c = int(b_c * (1 - p_factor * 0.4) + COL_GLOW_PURPLE[2] * p_factor * 0.4)
                    color = (r_c, g_c, b_c)

                # Determine whether point belongs to top flap
                # Flap is triangle where ny < (1.0 - dx) * 0.5
                is_flap = (ny < (1.0 - dx) * 0.5) and not is_top
                
                # Z coordinate: seal has subtle 3D thickness (z = -3.0)
                z = -4.0 if is_seal else 0.0
                
                pt_dict = {
                    "orig_3d": np.array([x, y, z], dtype=np.float32),
                    "char": char,
                    "color": color,
                    "is_seal": is_seal,
                    "is_flap": is_flap,
                    "hinge_y": -self.h / 2.0,  # Top edge is hinge
                }
                self.all_envelope_points.append(pt_dict)

    def get_3d_coordinates(self, flap_angle=0.0):
        """Returns Nx3 numpy array with top flap rotated in 3D around hinge."""
        coords = np.zeros((len(self.all_envelope_points), 3), dtype=np.float32)
        
        c_flap = math.cos(flap_angle)
        s_flap = math.sin(flap_angle)
        hinge_y = -self.h / 2.0
        
        for i, pt in enumerate(self.all_envelope_points):
            orig = pt["orig_3d"]
            if pt["is_flap"] and flap_angle > 0.0:
                # Rotate around hinge line at hinge_y
                # Local coords relative to hinge
                dy = orig[1] - hinge_y
                dz = orig[2]
                # Rotate around X-axis: y' = dy * cos(a) - dz * sin(a), z' = dy * sin(a) + dz * cos(a)
                ny = hinge_y + dy * c_flap - dz * s_flap
                nz = dy * s_flap + dz * c_flap
                coords[i] = [orig[0], ny, nz]
            else:
                coords[i] = orig
        return coords


# ==============================================================================
# VOLUMETRIC 3D FLOWER BOUQUET GENERATOR
# ==============================================================================
class Bouquet3D:
    """Generates true 3D volumetric coordinates for a lush flower bouquet."""
    def __init__(self, total_points=2300):
        self.total_points = total_points
        self.points_3d = np.zeros((total_points, 3), dtype=np.float32)
        self.glyphs = []
        self.colors = []
        self._generate_3d_bouquet()

    def _generate_3d_bouquet(self):
        rng = random.Random(777)
        pts_list = []
        glyphs_list = []
        colors_list = []

        # ----------------------------------------------------------------------
        # 1. 3D CONICAL KRAFT WRAPPER & SATIN RIBBON
        # ----------------------------------------------------------------------
        wrap_top_y = 60.0
        wrap_bot_y = 260.0
        wrap_top_r = 135.0
        wrap_bot_r = 45.0
        
        num_wrap = int(self.total_points * 0.18)
        for _ in range(num_wrap):
            u = rng.uniform(0.0, 1.0)  # 0 = top, 1 = bottom
            y = wrap_top_y + u * (wrap_bot_y - wrap_top_y)
            r = wrap_top_r * (1.0 - u) + wrap_bot_r * u
            # Wrapped around front half (semi-cone in 3D: angle from -pi*0.85 to +pi*0.85)
            theta = rng.uniform(-math.pi * 0.9, math.pi * 0.9)
            x = math.sin(theta) * r
            z = math.cos(theta) * r * 0.7  # Depth
            
            # Shading by 3D curvature
            if abs(theta) > math.pi * 0.65:
                col = COL_WRAPPER_SHADOW
                ch = rng.choice(["|", "/", "\\", "%"])
            else:
                col = COL_WRAPPER
                ch = rng.choice(["#", "%", "8", "=", ":"])
            pts_list.append([x, y, z])
            glyphs_list.append(ch)
            colors_list.append(col)

        # 3D Ribbon Bow at Wrapper Waist
        ribbon_y = wrap_top_y + 35.0
        num_ribbon = int(self.total_points * 0.06)
        for _ in range(num_ribbon):
            choice = rng.random()
            if choice < 0.42:
                # Left 3D loop
                ang = rng.uniform(0, 2 * math.pi)
                rad = rng.uniform(8.0, 32.0)
                x = -32.0 + math.cos(ang) * rad * 1.3
                y = ribbon_y + math.sin(ang) * rad * 0.7
                z = -math.sin(ang) * 15.0 - 15.0
            elif choice < 0.84:
                # Right 3D loop
                ang = rng.uniform(0, 2 * math.pi)
                rad = rng.uniform(8.0, 32.0)
                x = 32.0 + math.cos(ang) * rad * 1.3
                y = ribbon_y + math.sin(ang) * rad * 0.7
                z = -math.sin(ang) * 15.0 - 15.0
            else:
                # Center knot in front (z = -25.0)
                x = rng.uniform(-16, 16)
                y = ribbon_y + rng.uniform(-14, 14)
                z = -25.0 + rng.uniform(-5, 5)
            
            pts_list.append([x, y, z])
            glyphs_list.append(rng.choice(["♥", "@", "*", "%"]))
            colors_list.append(COL_RIBBON)

        # ----------------------------------------------------------------------
        # 2. 3D STEMS & FOLIAGE (Leaves spreading in 3D dome)
        # ----------------------------------------------------------------------
        num_leaves = int(self.total_points * 0.22)
        leaf_anchors = [
            # (anchor_x, anchor_y, anchor_z, dir_angle_xy, elev_angle_z, len, wid, col)
            (-140.0, -10.0, -20.0, -0.65, 0.35, 130.0, 48.0, COL_LEAF_BRIGHT),
            (140.0, -10.0, -20.0,  0.65, 0.35, 130.0, 48.0, COL_LEAF_BRIGHT),
            (-120.0, -80.0, -50.0, -0.95, -0.20, 110.0, 40.0, COL_LEAF_DARK),
            (120.0, -80.0, -50.0,  0.95, -0.20, 110.0, 40.0, COL_LEAF_DARK),
            (-60.0, -170.0, 10.0,  -1.30, 0.40, 95.0, 35.0, COL_LEAF_MINT),
            (60.0, -170.0, 10.0,   1.30, 0.40, 95.0, 35.0, COL_LEAF_MINT),
            (0.0, -195.0, -30.0,   0.0,  0.50, 85.0, 32.0, COL_LEAF_BRIGHT),
            (-100.0, -30.0, 60.0,  -0.5, -0.60, 100.0, 40.0, COL_LEAF_DARK),
            (100.0, -30.0, 60.0,   0.5, -0.60, 100.0, 40.0, COL_LEAF_DARK),
        ]

        for _ in range(num_leaves):
            la = rng.choice(leaf_anchors)
            ax, ay, az, a_xy, a_z, llen, lwid, lcol = la
            u = rng.uniform(0.1, 1.0)
            v = rng.uniform(-1.0, 1.0)
            
            # Oval profile along leaf length
            if abs(v) <= math.sin(u * math.pi):
                dist_along = u * llen
                dist_across = v * lwid * 0.5
                
                # 3D leaf positioning
                c_xy, s_xy = math.cos(a_xy), math.sin(a_xy)
                px = ax + c_xy * dist_along - s_xy * dist_across
                py = ay + s_xy * dist_along + c_xy * dist_across
                pz = az + math.sin(a_z) * dist_along + math.sin(u * math.pi) * 12.0  # 3D curl
                
                ch = rng.choice(["$", "%", "8", "*", "#", ";"])
                col = lcol if abs(v) > 0.3 else COL_STEM_DEEP
                pts_list.append([px, py, pz])
                glyphs_list.append(ch)
                colors_list.append(col)

        # ----------------------------------------------------------------------
        # 3. 3D VOLUMETRIC FLOWER HEADS
        # ----------------------------------------------------------------------
        flower_heads = [
            # Main central 3D Rose (proudly facing front-center)
            {"cx": 0.0, "cy": -55.0, "cz": -75.0, "rad": 82.0, "type": "rose", "col_core": COL_ROSE_CORE, "col_mid": COL_ROSE_RED, "col_edge": COL_ROSE_PINK},
            # Left 3D Peony
            {"cx": -90.0, "cy": -45.0, "cz": -30.0, "rad": 66.0, "type": "peony", "col_core": COL_PEONY_PURPLE, "col_mid": COL_PEONY_LILAC, "col_edge": COL_PEONY_SOFT},
            # Right 3D Pink Rose
            {"cx": 90.0, "cy": -45.0, "cz": -30.0, "rad": 66.0, "type": "rose", "col_core": COL_ROSE_CORE, "col_mid": COL_ROSE_PINK, "col_edge": COL_ROSE_LIGHT},
            # Top-Left 3D Coral Tulip
            {"cx": -60.0, "cy": -130.0, "cz": -10.0, "rad": 48.0, "type": "tulip", "col_core": COL_TULIP_CORAL, "col_mid": COL_TULIP_CORAL, "col_edge": COL_TULIP_PEACH},
            # Top-Right 3D Rosebud
            {"cx": 60.0, "cy": -130.0, "cz": -10.0, "rad": 48.0, "type": "rose", "col_core": COL_ROSE_RED, "col_mid": COL_ROSE_PINK, "col_edge": COL_ROSE_LIGHT},
            # Daisies / Chamomiles on 3D perimeter
            {"cx": -135.0, "cy": 15.0, "cz": 20.0, "rad": 36.0, "type": "daisy", "col_core": COL_DAISY_YELLOW, "col_mid": COL_DAISY_WHITE, "col_edge": COL_DAISY_WHITE},
            {"cx": 135.0, "cy": 15.0, "cz": 20.0, "rad": 36.0, "type": "daisy", "col_core": COL_DAISY_YELLOW, "col_mid": COL_DAISY_WHITE, "col_edge": COL_DAISY_WHITE},
            {"cx": 0.0, "cy": -160.0, "cz": 15.0, "rad": 38.0, "type": "daisy", "col_core": COL_DAISY_YELLOW, "col_mid": COL_DAISY_WHITE, "col_edge": COL_DAISY_WHITE},
        ]

        remaining_pts = self.total_points - len(pts_list)
        pts_per_head = remaining_pts // len(flower_heads)

        for fh in flower_heads:
            fcx = fh["cx"]
            fcy = fh["cy"]
            fcz = fh["cz"]
            frad = fh["rad"]
            ftype = fh["type"]
            
            for _ in range(pts_per_head):
                if ftype in ["rose", "peony"]:
                    # Multi-petal 3D spiraling dome
                    r_norm = math.sqrt(rng.uniform(0.04, 1.0))
                    r = r_norm * frad
                    theta = rng.uniform(0, 2 * math.pi)
                    n_petals = 5 if ftype == "rose" else 7
                    r_mod = r * (1.0 + 0.12 * math.sin(n_petals * theta))
                    
                    px = fcx + math.cos(theta) * r_mod
                    py = fcy + math.sin(theta) * r_mod
                    # 3D dome curvature: core is recessed, petals cup forward
                    dome_z = -math.cos(r_norm * math.pi * 0.5) * (frad * 0.45)
                    pz = fcz + dome_z
                    
                    if r_norm < 0.28:
                        col = fh["col_core"]
                        ch = rng.choice(["@", "#", "♥"])
                    elif r_norm < 0.72:
                        col = fh["col_mid"]
                        ch = rng.choice(["%", "&", "8", "♥", "✿"])
                    else:
                        col = fh["col_edge"]
                        ch = rng.choice(["*", "(", ")", "c", "o", "❀"])
                
                elif ftype == "tulip":
                    u = rng.uniform(0.0, 1.0)
                    v = rng.uniform(-1.0, 1.0)
                    ang_around = rng.uniform(0, 2 * math.pi)
                    rad_tube = frad * 0.65 * math.sin(u * math.pi * 0.8 + 0.2)
                    
                    px = fcx + math.cos(ang_around) * rad_tube
                    py = fcy - u * frad * 1.1 + frad * 0.4
                    pz = fcz + math.sin(ang_around) * rad_tube
                    
                    col = fh["col_mid"] if u > 0.4 else fh["col_core"]
                    ch = rng.choice(["#", "%", "8", "U", "V", "|"])
                
                else:  # daisy
                    r = rng.uniform(0.0, frad)
                    theta = rng.uniform(0, 2 * math.pi)
                    px = fcx + math.cos(theta) * r
                    py = fcy + math.sin(theta) * r
                    pz = fcz + (r / frad) * 10.0  # slight cone
                    
                    if r < frad * 0.35:
                        col = fh["col_core"]
                        ch = rng.choice(["*", "@", "•", "o"])
                    else:
                        col = fh["col_mid"]
                        ch = rng.choice(["+", "|", "/", "\\", "1", "i"])

                pts_list.append([px, py, pz])
                glyphs_list.append(ch)
                colors_list.append(col)

        # Truncate or pad to exact total_points
        while len(pts_list) < self.total_points:
            pts_list.append([0.0, 0.0, 0.0])
            glyphs_list.append("*")
            colors_list.append(COL_WHITE_SPARK)
            
        self.points_3d = np.array(pts_list[:self.total_points], dtype=np.float32)
        self.glyphs = glyphs_list[:self.total_points]
        self.colors = colors_list[:self.total_points]


# ==============================================================================
# 3D FLOATING PARTICLES (Sparkles & Drifting Rose Petals in 3D Space)
# ==============================================================================
class Particle3D:
    def __init__(self, x, y, z, kind="sparkle", color=None, vx=None, vy=None, vz=None):
        self.pos = np.array([x, y, z], dtype=np.float32)
        self.kind = kind
        self.char = random.choice(SPARKLE_CHARS) if kind == "sparkle" else random.choice(["♥", "❀", "·", "•"])
        self.color = color or random.choice([COL_GOLD_SPARK, COL_WHITE_SPARK, COL_ROSE_LIGHT, COL_SEAL_BRIGHT])
        
        self.vel = np.array([
            vx if vx is not None else random.uniform(-1.8, 1.8),
            vy if vy is not None else random.uniform(-3.0, -0.8),
            vz if vz is not None else random.uniform(-1.8, 1.8)
        ], dtype=np.float32)
        
        self.lifespan = random.randint(45, 110)
        self.age = 0
        self.alive = True
        self.wobble_freq = random.uniform(2.0, 5.0)

    def update(self):
        # 3D cylindrical vortex float
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

    # Fonts with anti-aliasing
    font_mono_lg = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 14, bold=True)
    font_mono_md = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 12, bold=True)
    font_mono_sm = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 10, bold=True)
    
    font_title = pygame.font.SysFont(["georgia", "timesnewroman", "serif"], 28, bold=True)
    font_sub = pygame.font.SysFont(["consolas", "sans-serif"], 15)
    font_hint = pygame.font.SysFont(["consolas", "sans-serif"], 14, bold=True)

    # 1. Build Models
    envelope = Envelope3D(width=740.0, height=440.0)
    total_pts = len(envelope.all_envelope_points)
    bouquet = Bouquet3D(total_points=total_pts)

    # Pre-extract envelope initial static 3D array
    env_coords_initial = envelope.get_3d_coordinates(flap_angle=0.0)
    bouquet_target_3d = bouquet.points_3d.copy()

    # 2. Setup Morphing Pairs with 3D Bezier Curvature Control Points
    center_env = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    distances = np.linalg.norm(env_coords_initial - center_env, axis=1)
    max_dist = np.max(distances)
    delays = (distances / (max_dist + 1e-4)) * 0.42  # Radial outward wave

    # Random swirl control points in 3D
    rng_ctrl = random.Random(555)
    ctrl_points_3d = np.zeros_like(env_coords_initial)
    for i in range(total_pts):
        p0 = env_coords_initial[i]
        p2 = bouquet_target_3d[i]
        mid = (p0 + p2) * 0.5
        d = np.linalg.norm(p2 - p0)
        # Random perpendicular vector in 3D
        rand_vec = np.array([
            rng_ctrl.uniform(-1, 1),
            rng_ctrl.uniform(-1, 1),
            rng_ctrl.uniform(-1, 1)
        ], dtype=np.float32)
        rand_vec /= (np.linalg.norm(rand_vec) + 1e-5)
        ctrl_points_3d[i] = mid + rand_vec * (d * rng_ctrl.uniform(0.25, 0.55))

    # 3. Interactive 3D Camera Parameters
    # Initial tilted aesthetic angle (matching photo perspective)
    cam_pitch = math.radians(12.0)
    cam_yaw = math.radians(-16.0)
    cam_dist = CAMERA_DIST

    is_dragging = False
    last_mouse_pos = (0, 0)

    # Animation States
    STATE_WAITING = 0     # Sealed envelope glowing in 3D, waiting for tap/click
    STATE_OPENING = 1     # Flap rotating 180 deg in 3D + seal particle explosion
    STATE_MORPHING = 2    # Points flowing along 3D curves into bouquet
    STATE_BOUQUET = 3     # 3D bouquet turntable rotation, floating petals, typography

    state = STATE_WAITING
    state_start_time = time.time()
    flap_angle = 0.0
    morph_t = 0.0
    particles_3d = []

    # Final Text
    FINAL_TITLE = "For Someone Special 💐"
    FINAL_BODY = "Blooming with endless love, happiness, and beauty."

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now = time.time()
        time_in_state = now - state_start_time
        center_screen = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        # ----------------------------------------------------------------------
        # EVENT HANDLING (Mouse Drag 3D Orbit, Touch, Keyboard)
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
                    elif state == STATE_BOUQUET:
                        state = STATE_WAITING
                        morph_t = 0.0
                        flap_angle = 0.0
                        particles_3d.clear()
                        cam_pitch = math.radians(12.0)
                        cam_yaw = math.radians(-16.0)

            # MOUSE BUTTON DOWN / TOUCH PRESS
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    is_dragging = True
                    last_mouse_pos = event.pos
                    if state == STATE_WAITING:
                        state = STATE_OPENING
                        state_start_time = now
                    elif state == STATE_BOUQUET and time_in_state > 3.0:
                        # Tap to replay
                        state = STATE_WAITING
                        morph_t = 0.0
                        flap_angle = 0.0
                        particles_3d.clear()
                        cam_pitch = math.radians(12.0)
                        cam_yaw = math.radians(-16.0)
                
                # MOUSE WHEEL ZOOM IN / OUT
                elif event.button == 4:  # Wheel up
                    cam_dist = max(ZOOM_MIN, cam_dist - 35.0)
                elif event.button == 5:  # Wheel down
                    cam_dist = min(ZOOM_MAX, cam_dist + 35.0)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging = False

            # MOUSE MOTION (3D Trackball Orbit Drag)
            elif event.type == pygame.MOUSEMOTION:
                if is_dragging:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    cam_yaw += dx * 0.006
                    cam_pitch += dy * 0.006
                    cam_pitch = max(-math.pi * 0.45, min(math.pi * 0.45, cam_pitch))
                    last_mouse_pos = event.pos

            # TOUCHSCREEN EVENTS (pygame touch mapping)
            elif event.type == pygame.FINGERDOWN:
                if state == STATE_WAITING:
                    state = STATE_OPENING
                    state_start_time = now
                elif state == STATE_BOUQUET and time_in_state > 3.0:
                    state = STATE_WAITING
                    morph_t = 0.0
                    flap_angle = 0.0
                    particles_3d.clear()

        # ----------------------------------------------------------------------
        # STATE LOGIC & 3D COORDINATE COMPUTATION
        # ----------------------------------------------------------------------
        screen.fill(COLOR_BG)

        # Current working 3D point array & glyphs/colors
        current_3d = np.zeros((total_pts, 3), dtype=np.float32)
        current_glyphs = []
        current_colors = []

        if state == STATE_WAITING:
            # Subtle floating 3D breathing idle oscillation
            idle_yaw = cam_yaw + math.sin(now * 1.5) * 0.03
            idle_pitch = cam_pitch + math.cos(now * 1.2) * 0.02
            R_cam = create_rotation_matrix(idle_pitch, idle_yaw)
            
            # Envelope is sealed
            current_3d = envelope.get_3d_coordinates(flap_angle=0.0)
            
            # Pulsing heart wax seal
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

            # Ambient sparkles drifting off wax seal
            if random.random() < 0.25:
                particles_3d.append(Particle3D(
                    random.uniform(-40, 40), random.uniform(-30, 30), -15.0,
                    kind="sparkle", color=COL_GOLD_SPARK
                ))

        elif state == STATE_OPENING:
            # Flap physically rotates in 3D around hinge axis by 175 degrees
            open_dur = 1.2
            open_t = min(1.0, time_in_state / open_dur)
            # Smooth cubic ease-out
            open_ease = 1.0 - math.pow(1.0 - open_t, 3)
            flap_angle = open_ease * math.pi * 0.98
            
            R_cam = create_rotation_matrix(cam_pitch, cam_yaw)
            current_3d = envelope.get_3d_coordinates(flap_angle=flap_angle)
            
            # Seal pop burst at initial moment
            if time_in_state < 0.06:
                for _ in range(85):
                    ang_xy = random.uniform(0, 2 * math.pi)
                    ang_z = random.uniform(-math.pi * 0.4, math.pi * 0.4)
                    spd = random.uniform(4.0, 11.0)
                    particles_3d.append(Particle3D(
                        0.0, 0.0, -10.0,
                        kind=random.choice(["sparkle", "petal"]),
                        color=random.choice([COL_SEAL_BRIGHT, COL_GOLD_SPARK, COL_WHITE_SPARK, COL_ROSE_PINK]),
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
            # 3D Bezier Spline Flight: Envelope -> Bouquet
            morph_dur = 3.4
            raw_t = min(1.0, time_in_state / morph_dur)
            
            # Continuous subtle 3D camera pan
            R_cam = create_rotation_matrix(cam_pitch, cam_yaw + raw_t * 0.15)
            
            # Calculate Bezier interpolation for each point with wave delay
            for i in range(total_pts):
                d = delays[i]
                if raw_t <= d:
                    loc_t = 0.0
                else:
                    loc_t = (raw_t - d) / (1.0 - d + 1e-5)
                    loc_t = min(1.0, max(0.0, loc_t))
                
                # Ease in out
                ease = loc_t * loc_t * (3.0 - 2.0 * loc_t)
                inv = 1.0 - ease
                
                # Quadratic 3D Bezier: B(t) = (1-t)^2 P0 + 2(1-t)t P1 + t^2 P2
                p0 = env_coords_initial[i]
                p1 = ctrl_points_3d[i]
                p2 = bouquet_target_3d[i]
                current_3d[i] = inv * inv * p0 + 2.0 * inv * ease * p1 + ease * ease * p2
                
                # Morph glyph & color
                src_ch = envelope.all_envelope_points[i]["char"]
                src_col = envelope.all_envelope_points[i]["color"]
                dst_ch = bouquet.glyphs[i]
                dst_col = bouquet.colors[i]
                
                if ease < 0.4:
                    current_glyphs.append(src_ch)
                    current_colors.append(src_col)
                elif ease < 0.7:
                    current_glyphs.append("*" if random.random() < 0.5 else dst_ch)
                    # Blend RGB
                    frac = (ease - 0.4) / 0.3
                    r = int(src_col[0] * (1 - frac) + dst_col[0] * frac)
                    g = int(src_col[1] * (1 - frac) + dst_col[1] * frac)
                    b = int(src_col[2] * (1 - frac) + dst_col[2] * frac)
                    current_colors.append((r, g, b))
                else:
                    current_glyphs.append(dst_ch)
                    current_colors.append(dst_col)

            # Flight particles
            if random.random() < 0.6:
                idx = random.randint(0, total_pts - 1)
                particles_3d.append(Particle3D(
                    current_3d[idx, 0], current_3d[idx, 1], current_3d[idx, 2],
                    kind="sparkle", color=random.choice([COL_GOLD_SPARK, COL_ROSE_PINK])
                ))

            if raw_t >= 1.0:
                state = STATE_BOUQUET
                state_start_time = now

        elif state == STATE_BOUQUET:
            # 3D Turntable Auto-rotation + User Orbit Drag
            turntable_yaw = cam_yaw + math.sin(time_in_state * 0.45) * 0.22
            turntable_pitch = cam_pitch + math.cos(time_in_state * 0.35) * 0.08
            R_cam = create_rotation_matrix(turntable_pitch, turntable_yaw)
            
            # Gentle 3D wind breeze on foliage
            breeze = math.sin(now * 2.2) * 4.5
            current_3d = bouquet_target_3d.copy()
            current_3d[:, 0] += breeze * 0.25 * (current_3d[:, 1] < 0)  # Top leaves sway
            
            current_glyphs = bouquet.glyphs
            current_colors = bouquet.colors

            # Continuous 3D drifting petals and pollen sparkles
            if random.random() < 0.35:
                px = random.uniform(-140, 140)
                py = random.uniform(-120, 80)
                pz = random.uniform(-90, 60)
                particles_3d.append(Particle3D(
                    px, py, pz,
                    kind=random.choice(["petal", "sparkle"]),
                    color=random.choice([COL_ROSE_LIGHT, COL_GOLD_SPARK, COL_PEONY_SOFT, COL_WHITE_SPARK]),
                    vy=random.uniform(-2.5, -0.9)
                ))

        # ----------------------------------------------------------------------
        # 3D PROJECTION & RENDERING (Depth-Sorted)
        # ----------------------------------------------------------------------
        # Project main object points
        sx, sy, z_safe, scale, depth_order = project_points_3d(
            current_3d, R_cam, cam_dist, FOV, center_screen
        )

        # Render points in depth order (Back to Front)
        for idx in depth_order:
            x_screen = sx[idx]
            y_screen = sy[idx]
            sc = scale[idx]
            
            # Frustum culling check
            if -30 <= x_screen <= WINDOW_WIDTH + 30 and -30 <= y_screen <= WINDOW_HEIGHT + 30:
                ch = current_glyphs[idx]
                col = current_colors[idx]
                
                # Dynamic perspective font sizing
                if sc > 1.25:
                    font = font_mono_lg
                elif sc > 0.85:
                    font = font_mono_md
                else:
                    font = font_mono_sm

                # 3D Depth Cueing / Atmospheric Lighting
                # Closer points are brighter, far points gently attenuate
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
                    # Alpha fade
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
        # 2D HUD / TYPOGRAPHY OVERLAY
        # ----------------------------------------------------------------------
        if state == STATE_WAITING:
            # 3D Orbit hint & Click prompt
            prompt_alpha = (math.sin(now * 4.0) + 1.0) / 2.0
            p_col = (
                int(255 * (0.6 + 0.4 * prompt_alpha)),
                int(220 * (0.6 + 0.4 * prompt_alpha)),
                int(160 * (0.6 + 0.4 * prompt_alpha))
            )
            p_surf = font_hint.render("💌  [ TAP / CLICK TO OPEN ]  •  [ DRAG TO ROTATE 3D ]", True, p_col)
            p_rect = p_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))
            screen.blit(p_surf, p_rect)

        elif state == STATE_BOUQUET:
            fade_in = min(1.0, time_in_state / 1.5)
            
            # Title
            t_col = (
                int(COL_GOLD_SPARK[0] * fade_in),
                int(COL_GOLD_SPARK[1] * fade_in),
                int(COL_GOLD_SPARK[2] * fade_in),
            )
            t_surf = font_title.render(FINAL_TITLE, True, t_col)
            t_rect = t_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 120))
            screen.blit(t_surf, t_rect)

            # Typewriter body
            if time_in_state > 0.8:
                type_progress = min(1.0, (time_in_state - 0.8) / 2.0)
                chars_shown = int(len(FINAL_BODY) * type_progress)
                body_txt = FINAL_BODY[:chars_shown]
                
                b_col = (int(255 * fade_in), int(240 * fade_in), int(245 * fade_in))
                b_surf = font_sub.render(body_txt, True, b_col)
                b_rect = b_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80))
                screen.blit(b_surf, b_rect)

            # Replay & 3D Orbit hint
            if time_in_state > 3.0:
                h_alpha = (math.sin(now * 3.0) + 1.0) / 2.0
                h_col = (int(180 * h_alpha), int(160 * h_alpha), int(200 * h_alpha))
                h_surf = font_hint.render("🔄  Click to replay  •  🖱️ Drag to rotate 3D bouquet  •  Scroll to zoom", True, h_col)
                h_rect = h_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 35))
                screen.blit(h_surf, h_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
