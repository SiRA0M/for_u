import math
import random
import sys
import time
import numpy as np
import pygame

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
TITLE = "Special Letter 3D 💌 Volumetric Bouquet"
WINDOW_WIDTH = 1150
WINDOW_HEIGHT = 860
FPS = 60

# Camera & 3D Projection
FOV = 880.0
CAMERA_DIST = 920.0
ZOOM_MIN = 450.0
ZOOM_MAX = 1600.0

# ------------------------------------------------------------------------------
# COLOR PALETTE (RGB)
# ------------------------------------------------------------------------------
COLOR_BG = (10, 8, 16)

# XYZ Axes Colors
COL_AXIS_X = (255, 65, 75)    # Red = X
COL_AXIS_Y = (65, 225, 95)    # Green = Y
COL_AXIS_Z = (65, 165, 255)   # Blue = Z

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
COL_WRAPPER = (242, 218, 212)
COL_WRAPPER_SHADOW = (185, 145, 155)
COL_RIBBON = (255, 80, 140)
COL_RIBBON_GOLD = (255, 215, 110)

COL_STEM_DEEP = (38, 110, 55)
COL_STEM_LIGHT = (68, 165, 88)
COL_LEAF_DARK = (48, 130, 68)
COL_LEAF_BRIGHT = (88, 195, 105)
COL_LEAF_MINT = (135, 220, 160)
COL_EUCALYPTUS = (110, 185, 155)

# Flower Colors
COL_ROSE_DEEP = (145, 12, 42)     # Velvet core
COL_ROSE_RED = (235, 28, 68)      # Mid petal
COL_ROSE_CORAL = (255, 95, 145)   # Outer petal
COL_ROSE_CHAMPAGNE = (255, 195, 215) # Tip highlight

COL_PEONY_PURPLE = (165, 70, 225)
COL_PEONY_LILAC = (215, 140, 255)
COL_PEONY_SOFT = (245, 205, 255)

COL_TULIP_CORAL = (255, 115, 95)
COL_TULIP_PEACH = (255, 175, 130)

COL_DAISY_WHITE = (255, 252, 248)
COL_DAISY_YELLOW = (255, 215, 55)

COL_GOLD_SPARK = (255, 235, 145)
COL_WHITE_SPARK = (255, 255, 255)

# Characters
ASCII_CHARS_DENSE = ["8", "%", "&", "#", "S", "B", "w", "m", "Z", "X", "Q", "0"]
ASCII_CHARS_MED = ["o", "*", "a", "s", "z", "x", "e", "u", "r", "n", "v"]
SPARKLE_CHARS = ["*", "+", "·", "✧", "✦", "°", "•", "♡", "❀"]


# ==============================================================================
# 3D ROTATION & PROJECTION ENGINE
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
# 3D XYZ AXES GIZMO (Origin Tripod + Top-Right HUD Widget)
# ==============================================================================
class AxisGizmo:
    """Renders 3D coordinate axes both at origin and as a corner orientation widget."""
    def __init__(self, axis_length=120.0):
        self.axis_length = axis_length
        # Unit vectors along X, Y, Z
        self.origin = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.axis_ends = np.array([
            [axis_length, 0.0, 0.0],   # X
            [0.0, -axis_length, 0.0],  # Y (Up in world)
            [0.0, 0.0, axis_length],   # Z (Front)
        ], dtype=np.float32)

    def draw_origin_axes(self, surface, font, R_cam, cam_dist, fov, center_screen):
        """Draws XYZ tripod directly at world origin."""
        all_pts = np.vstack([self.origin, self.axis_ends])
        sx, sy, z_safe, scale, _ = project_points_3d(all_pts, R_cam, cam_dist, fov, center_screen)
        
        ox, oy = int(sx[0]), int(sy[0])
        axes_info = [
            (sx[1], sy[1], COL_AXIS_X, "X"),
            (sx[2], sy[2], COL_AXIS_Y, "Y"),
            (sx[3], sy[3], COL_AXIS_Z, "Z"),
        ]
        
        for ax, ay, col, label in axes_info:
            ex, ey = int(ax), int(ay)
            # Line
            pygame.draw.line(surface, col, (ox, oy), (ex, ey), 2)
            # Label
            lbl_surf = font.render(label, True, col)
            surface.blit(lbl_surf, (ex + 4, ey - 7))

    def draw_corner_hud(self, surface, font, R_cam, corner_pos=(WINDOW_WIDTH - 70, 70), radius=38.0):
        """Draws interactive 3D orientation cube/tripod in top-right HUD."""
        cx, cy = corner_pos
        # Background ring
        pygame.draw.circle(surface, (25, 20, 35), (cx, cy), int(radius + 8))
        pygame.draw.circle(surface, (55, 45, 75), (cx, cy), int(radius + 8), 1)

        # Rotate standard unit axes by camera orientation
        rotated_axes = self.axis_ends @ R_cam.T
        # Depth sort the 3 axes
        order = np.argsort(rotated_axes[:, 2])

        axes_info = [
            (0, COL_AXIS_X, "X"),
            (1, COL_AXIS_Y, "Y"),
            (2, COL_AXIS_Z, "Z"),
        ]

        for idx in order:
            rot = rotated_axes[idx]
            col = axes_info[idx][1]
            label = axes_info[idx][2]
            
            # 2D projection on HUD widget
            scale_fac = radius / self.axis_length
            ex = int(cx + rot[0] * scale_fac)
            ey = int(cy + rot[1] * scale_fac)
            
            # Axis line with thickness based on Z
            thick = 3 if rot[2] < 0 else 1
            pygame.draw.line(surface, col, (cx, cy), (ex, ey), thick)
            
            # Axis endpoint dot & label
            pygame.draw.circle(surface, col, (ex, ey), 3)
            lbl = font.render(label, True, col)
            surface.blit(lbl, (ex + 3, ey - 6))


# ==============================================================================
# BACK / REPLAY BUTTON WIDGET (Final Screen)
# ==============================================================================
class ReplayButton:
    """Dedicated interactive button so users don't accidentally restart on screen click."""
    def __init__(self, x=45, y=WINDOW_HEIGHT - 75, w=160, h=44):
        self.rect = pygame.Rect(x, y, w, h)
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface, font):
        # Colors
        bg_col = (50, 30, 65) if not self.is_hovered else (85, 45, 110)
        border_col = (180, 120, 220) if not self.is_hovered else (255, 180, 240)
        txt_col = (240, 220, 255) if not self.is_hovered else (255, 255, 255)

        # Rounded rectangle
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=10)
        pygame.draw.rect(surface, border_col, self.rect, 2, border_radius=10)

        # Text with icon
        txt = "↺  Replay"
        t_surf = font.render(txt, True, txt_col)
        t_rect = t_surf.get_rect(center=self.rect.center)
        surface.blit(t_surf, t_rect)


# ==============================================================================
# HIGH-DETAIL 3D ENVELOPE GENERATOR
# ==============================================================================
class Envelope3D:
    def __init__(self, width=740.0, height=440.0):
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
# HIGH-AESTHETIC 3D FLOWER BOUQUET GENERATOR (Fibonacci Phyllotaxis)
# ==============================================================================
class Bouquet3D:
    """Generates true 3D volumetric coordinates for an ultra-aesthetic botanical bouquet."""
    def __init__(self, total_points=2400):
        self.total_points = total_points
        self.points_3d = np.zeros((total_points, 3), dtype=np.float32)
        self.glyphs = []
        self.colors = []
        self._generate_3d_bouquet()

    def _generate_3d_bouquet(self):
        rng = random.Random(888)
        pts_list = []
        glyphs_list = []
        colors_list = []

        # ----------------------------------------------------------------------
        # 1. 3D CONICAL KRAFT WRAPPER & GOLDEN SATIN RIBBON
        # ----------------------------------------------------------------------
        wrap_top_y = 65.0
        wrap_bot_y = 270.0
        wrap_top_r = 140.0
        wrap_bot_r = 42.0
        
        num_wrap = int(self.total_points * 0.17)
        for _ in range(num_wrap):
            u = rng.uniform(0.0, 1.0)
            y = wrap_top_y + u * (wrap_bot_y - wrap_top_y)
            r = wrap_top_r * (1.0 - u) + wrap_bot_r * u
            theta = rng.uniform(-math.pi * 0.88, math.pi * 0.88)
            x = math.sin(theta) * r
            z = math.cos(theta) * r * 0.68
            
            if abs(theta) > math.pi * 0.65:
                col = COL_WRAPPER_SHADOW
                ch = rng.choice(["|", "/", "\\", "%"])
            else:
                col = COL_WRAPPER
                ch = rng.choice(["#", "%", "8", "=", ":"])
            pts_list.append([x, y, z])
            glyphs_list.append(ch)
            colors_list.append(col)

        # 3D Satin Ribbon with Trailing Tails
        ribbon_y = wrap_top_y + 36.0
        num_ribbon = int(self.total_points * 0.07)
        for _ in range(num_ribbon):
            choice = rng.random()
            if choice < 0.38:
                # Left bow loop
                ang = rng.uniform(0, 2 * math.pi)
                rad = rng.uniform(8.0, 34.0)
                x = -34.0 + math.cos(ang) * rad * 1.35
                y = ribbon_y + math.sin(ang) * rad * 0.7
                z = -math.sin(ang) * 16.0 - 18.0
                col = COL_RIBBON
            elif choice < 0.76:
                # Right bow loop
                ang = rng.uniform(0, 2 * math.pi)
                rad = rng.uniform(8.0, 34.0)
                x = 34.0 + math.cos(ang) * rad * 1.35
                y = ribbon_y + math.sin(ang) * rad * 0.7
                z = -math.sin(ang) * 16.0 - 18.0
                col = COL_RIBBON
            else:
                # Center knot & golden pin
                x = rng.uniform(-16, 16)
                y = ribbon_y + rng.uniform(-14, 14)
                z = -28.0 + rng.uniform(-5, 5)
                col = COL_RIBBON_GOLD
            
            pts_list.append([x, y, z])
            glyphs_list.append(rng.choice(["♥", "@", "*", "%"]))
            colors_list.append(col)

        # ----------------------------------------------------------------------
        # 2. 3D FOLIAGE, EUCALYPTUS & STEMS
        # ----------------------------------------------------------------------
        num_leaves = int(self.total_points * 0.22)
        leaf_anchors = [
            (-150.0, -10.0, -25.0, -0.65, 0.35, 135.0, 50.0, COL_LEAF_BRIGHT),
            (150.0, -10.0, -25.0,  0.65, 0.35, 135.0, 50.0, COL_LEAF_BRIGHT),
            (-125.0, -85.0, -55.0, -0.95, -0.20, 115.0, 42.0, COL_EUCALYPTUS),
            (125.0, -85.0, -55.0,  0.95, -0.20, 115.0, 42.0, COL_EUCALYPTUS),
            (-65.0, -175.0, 15.0,  -1.30, 0.40, 100.0, 36.0, COL_LEAF_MINT),
            (65.0, -175.0, 15.0,   1.30, 0.40, 100.0, 36.0, COL_LEAF_MINT),
            (0.0, -205.0, -35.0,   0.0,  0.50, 90.0, 34.0, COL_LEAF_BRIGHT),
            (-110.0, -35.0, 65.0,  -0.5, -0.60, 105.0, 42.0, COL_LEAF_DARK),
            (110.0, -35.0, 65.0,   0.5, -0.60, 105.0, 42.0, COL_LEAF_DARK),
        ]

        for _ in range(num_leaves):
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
                pz = az + math.sin(a_z) * dist_along + math.sin(u * math.pi) * 14.0
                
                ch = rng.choice(["$", "%", "8", "*", "#", ";"])
                col = lcol if abs(v) > 0.3 else COL_STEM_DEEP
                pts_list.append([px, py, pz])
                glyphs_list.append(ch)
                colors_list.append(col)

        # ----------------------------------------------------------------------
        # 3. HIGH-DENSITY 3D FLORAL BLOOMS (Fibonacci Phyllotaxis)
        # ----------------------------------------------------------------------
        GOLDEN_ANGLE = 137.507764 * (math.pi / 180.0)
        
        # GRAND CENTER ROSE (Rich 4-tier color gradient)
        num_rose_pts = int(self.total_points * 0.20)
        rcx, rcy, rcz = 0.0, -58.0, -80.0
        rose_max_r = 86.0
        for i in range(num_rose_pts):
            frac = i / (num_rose_pts - 1)
            r = math.sqrt(frac) * rose_max_r
            theta = i * GOLDEN_ANGLE
            
            # Scalloped petal edge
            r_scallop = r * (1.0 + 0.14 * math.sin(5.0 * theta))
            px = rcx + math.cos(theta) * r_scallop
            py = rcy + math.sin(theta) * r_scallop * 0.95
            # Deep recessed core to flared petals in 3D
            pz = rcz - math.cos(frac * math.pi * 0.5) * 36.0 + (frac * 12.0)
            
            # 4-tier color ramp
            if frac < 0.20:
                col = COL_ROSE_DEEP
                ch = rng.choice(["@", "#", "♥"])
            elif frac < 0.55:
                col = COL_ROSE_RED
                ch = rng.choice(["%", "&", "♥", "8"])
            elif frac < 0.85:
                col = COL_ROSE_CORAL
                ch = rng.choice(["*", "✿", "(", ")"])
            else:
                col = COL_ROSE_CHAMPAGNE
                ch = rng.choice(["❀", "c", "o", "·"])
                
            pts_list.append([px, py, pz])
            glyphs_list.append(ch)
            colors_list.append(col)

        # SIDE BLOOMS (Peonies, Tulips, Daisies, Baby's Breath)
        side_blooms = [
            # Left Peony
            {"cx": -92.0, "cy": -46.0, "cz": -32.0, "rad": 68.0, "type": "peony", "col_core": COL_PEONY_PURPLE, "col_mid": COL_PEONY_LILAC, "col_edge": COL_PEONY_SOFT},
            # Right Rose
            {"cx": 92.0, "cy": -46.0, "cz": -32.0, "rad": 68.0, "type": "rose", "col_core": COL_ROSE_DEEP, "col_mid": COL_ROSE_CORAL, "col_edge": COL_ROSE_CHAMPAGNE},
            # Top-Left Coral Tulip
            {"cx": -62.0, "cy": -135.0, "cz": -12.0, "rad": 50.0, "type": "tulip", "col_core": COL_TULIP_CORAL, "col_mid": COL_TULIP_CORAL, "col_edge": COL_TULIP_PEACH},
            # Top-Right Pink Rosebud
            {"cx": 62.0, "cy": -135.0, "cz": -12.0, "rad": 50.0, "type": "rose", "col_core": COL_ROSE_RED, "col_mid": COL_ROSE_CORAL, "col_edge": COL_ROSE_CHAMPAGNE},
            # Perimeter Daisies & Baby's Breath
            {"cx": -138.0, "cy": 18.0, "cz": 22.0, "rad": 38.0, "type": "daisy", "col_core": COL_DAISY_YELLOW, "col_mid": COL_DAISY_WHITE, "col_edge": COL_DAISY_WHITE},
            {"cx": 138.0, "cy": 18.0, "cz": 22.0, "rad": 38.0, "type": "daisy", "col_core": COL_DAISY_YELLOW, "col_mid": COL_DAISY_WHITE, "col_edge": COL_DAISY_WHITE},
            {"cx": 0.0, "cy": -165.0, "cz": 18.0, "rad": 40.0, "type": "daisy", "col_core": COL_DAISY_YELLOW, "col_mid": COL_DAISY_WHITE, "col_edge": COL_DAISY_WHITE},
        ]

        remaining_pts = self.total_points - len(pts_list)
        pts_per_bloom = remaining_pts // len(side_blooms)

        for bl in side_blooms:
            fcx = bl["cx"]
            fcy = bl["cy"]
            fcz = bl["cz"]
            frad = bl["rad"]
            ftype = bl["type"]
            
            for i in range(pts_per_bloom):
                if ftype in ["rose", "peony"]:
                    frac = i / (pts_per_bloom - 1)
                    r = math.sqrt(frac) * frad
                    theta = i * GOLDEN_ANGLE
                    r_scallop = r * (1.0 + 0.12 * math.sin(7.0 * theta))
                    
                    px = fcx + math.cos(theta) * r_scallop
                    py = fcy + math.sin(theta) * r_scallop
                    pz = fcz - math.cos(frac * math.pi * 0.5) * (frad * 0.42)
                    
                    if frac < 0.30:
                        col = bl["col_core"]
                        ch = rng.choice(["@", "#", "♥"])
                    elif frac < 0.75:
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

        while len(pts_list) < self.total_points:
            pts_list.append([0.0, 0.0, 0.0])
            glyphs_list.append("*")
            colors_list.append(COL_WHITE_SPARK)
            
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
    
    font_hud = pygame.font.SysFont(["consolas", "sans-serif"], 13, bold=True)
    font_btn = pygame.font.SysFont(["consolas", "sans-serif"], 16, bold=True)

    # 1. Models & Widgets
    envelope = Envelope3D(width=750.0, height=445.0)
    total_pts = len(envelope.all_envelope_points)
    bouquet = Bouquet3D(total_points=total_pts)
    gizmo = AxisGizmo(axis_length=120.0)
    replay_btn = ReplayButton(x=45, y=WINDOW_HEIGHT - 70, w=160, h=44)

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
    has_dragged = False  # Track if click was drag or tap

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

        # Update replay button hover state
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
                        # ONLY the replay button resets!
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
            # 3D Turntable Auto-rotation
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
        # 3D PROJECTION & RENDERING (Depth-Sorted)
        # ----------------------------------------------------------------------
        sx, sy, z_safe, scale, depth_order = project_points_3d(
            current_3d, R_cam, cam_dist, FOV, center_screen
        )

        # 1. Draw 3D Origin Axes (Red=X, Green=Y, Blue=Z)
        gizmo.draw_origin_axes(screen, font_hud, R_cam, cam_dist, FOV, center_screen)

        # 2. Draw Points in Back-to-Front Depth Order
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
        # 3D HUD & WIDGETS
        # ----------------------------------------------------------------------
        # Corner 3D Orientation Gizmo (Top-Right)
        gizmo.draw_corner_hud(screen, font_hud, R_cam, corner_pos=(WINDOW_WIDTH - 65, 65))

        if state == STATE_WAITING:
            # Click prompt
            prompt_alpha = (math.sin(now * 4.0) + 1.0) / 2.0
            p_col = (
                int(255 * (0.6 + 0.4 * prompt_alpha)),
                int(220 * (0.6 + 0.4 * prompt_alpha)),
                int(160 * (0.6 + 0.4 * prompt_alpha))
            )
            p_surf = font_hud.render("💌  [ TAP / CLICK TO OPEN ]  •  [ DRAG TO ROTATE 3D ]", True, p_col)
            p_rect = p_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 45))
            screen.blit(p_surf, p_rect)

        elif state == STATE_BOUQUET:
            # NO TEXT IN CENTER/BOTTOM (Removed per user request)
            # Dedicated Replay Button at Bottom-Left
            replay_btn.draw(screen, font_btn)

            # Orbit guide hint next to button
            guide_col = (140, 125, 160)
            g_surf = font_hud.render("🖱️ Drag screen to orbit 3D bouquet  •  Scroll to zoom", True, guide_col)
            screen.blit(g_surf, (replay_btn.rect.right + 20, replay_btn.rect.centery - 7))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
