import sys
import math
import random
import time
import pygame

# ==============================================================================
# CONFIGURATION
# ==============================================================================
TITLE = "For You"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
FPS = 60

# Custom text inside / below the heart
MESSAGE_TITLE = "Special Letter"
MESSAGE_BODY = "Every moment with you is special."
PROMPT_TEXT = "Press SPACE to open or wait..."

# Color Palette (RGB)
BG_COLOR = (12, 10, 18)
PINK_PRIMARY = (255, 95, 162)
ROSE_GLOW = (255, 50, 110)
CRIMSON_DEEP = (180, 20, 60)
PURPLE_LIGHT = (210, 140, 255)
PURPLE_DARK = (130, 60, 200)
GOLD_SPARK = (255, 230, 150)
WHITE_SPARK = (255, 250, 250)
TEXT_MUTED = (160, 140, 180)

# ==============================================================================
# ASCII ART DEFINITIONS
# ==============================================================================
ENVELOPE_CLOSED = [
    r" +---------------------------------------+ ",
    r" | \                                   / | ",
    r" |  \                                 /  | ",
    r" |   \                               /   | ",
    r" |    \                             /    | ",
    r" |     \                           /     | ",
    r" |      \                         /      | ",
    r" |       \           *           /       | ",
    r" |        \        /   \        /        | ",
    r" |         \      / <3  \      /         | ",
    r" |          \    +-------+    /          | ",
    r" |           \  /         \  /           | ",
    r" |            \/           \/            | ",
    r" |            /\           /\            | ",
    r" |           /  \         /  \           | ",
    r" |          /    \       /    \          | ",
    r" |         /      \     /      \         | ",
    r" |        /        \   /        \        | ",
    r" |       /          \ /          \       | ",
    r" |      /            v            \      | ",
    r" +---------------------------------------+ ",
]

ENVELOPE_OPEN = [
    r"                   / \                   ",
    r"                  /   \                  ",
    r"                 /  *  \                 ",
    r"                /  <3   \                ",
    r"               /         \               ",
    r"              /           \              ",
    r"             /             \             ",
    r"            /               \            ",
    r" +---------+-----------------+---------+ ",
    r" | \       |   FOR YOU       |       / | ",
    r" |  \      |   ~~~~~~~       |      /  | ",
    r" |   \     |                 |     /   | ",
    r" |    \    +-----------------+    /    | ",
    r" |     \                         /     | ",
    r" |      \                       /      | ",
    r" |       \                     /       | ",
    r" |        \                   /        | ",
    r" |         \                 /         | ",
    r" |          \               /          | ",
    r" |           \             /           | ",
    r" +-------------------------------------+ ",
]

HEART_CHARS = ["@", "#", "%", "*", "+", "o", "♥", "=", ":", "."]
SPARKLE_CHARS = ["*", "+", "·", "✧", "✦", "°", "•"]

# ==============================================================================
# MATHEMATICAL HELPERS
# ==============================================================================
def heart_coords(theta):
    """Parametric heart shape formula."""
    x = 16 * (math.sin(theta) ** 3)
    y = -(13 * math.cos(theta) - 5 * math.cos(2 * theta) - 2 * math.cos(3 * theta) - math.cos(4 * theta))
    return x, y

def generate_heart_points(density=360):
    """Generates boundary and interior points for heart ASCII mesh."""
    points = []
    # Perimeter
    for i in range(density):
        theta = (2 * math.pi * i) / density
        hx, hy = heart_coords(theta)
        points.append((hx, hy, True))
    
    # Fill interior
    for i in range(density // 2):
        theta = (2 * math.pi * i) / (density // 2)
        hx, hy = heart_coords(theta)
        scale = random.uniform(0.15, 0.90)
        points.append((hx * scale, hy * scale, False))
    return points

# ==============================================================================
# PARTICLE CLASS
# ==============================================================================
class Sparkle:
    def __init__(self, x, y, char=None, color=None, vx=None, vy=None, lifespan=None):
        self.x = x
        self.y = y
        self.char = char or random.choice(SPARKLE_CHARS)
        self.color = color or random.choice([GOLD_SPARK, WHITE_SPARK, PINK_PRIMARY, PURPLE_LIGHT])
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 3.0)
        self.vx = vx if vx is not None else math.cos(angle) * speed
        self.vy = vy if vy is not None else math.sin(angle) * speed
        self.lifespan = lifespan or random.randint(35, 90)
        self.age = 0
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.015  # slight float/gravity
        self.age += 1
        if self.age >= self.lifespan:
            self.alive = False

    def draw(self, surface, font):
        progress = self.age / self.lifespan
        alpha = math.sin(progress * math.pi)
        if alpha <= 0:
            return
        
        # Color fading
        r = int(self.color[0] * alpha)
        g = int(self.color[1] * alpha)
        b = int(self.color[2] * alpha)
        
        text_surf = font.render(self.char, True, (r, g, b))
        surface.blit(text_surf, (int(self.x), int(self.y)))


# ==============================================================================
# MORPHING CHARACTER CLASS
# ==============================================================================
class MorphChar:
    """Character that starts at an envelope ASCII cell and transitions to heart."""
    def __init__(self, src_x, src_y, dst_x, dst_y, char, color):
        self.src_x = src_x
        self.src_y = src_y
        self.dst_x = dst_x
        self.dst_y = dst_y
        self.curr_x = src_x
        self.curr_y = src_y
        self.char = char
        self.color = color
        self.target_color = color

    def update(self, morph_progress):
        # Cubic ease-in-out
        t = max(0.0, min(1.0, morph_progress))
        ease = t * t * (3.0 - 2.0 * t)
        
        self.curr_x = self.src_x + (self.dst_x - self.src_x) * ease
        self.curr_y = self.src_y + (self.dst_y - self.src_y) * ease

    def draw(self, surface, font, pulse_scale=1.0, center_x=0, center_y=0):
        # Scale with heartbeat pulse if close to destination
        px = self.curr_x
        py = self.curr_y
        if pulse_scale != 1.0:
            px = center_x + (px - center_x) * pulse_scale
            py = center_y + (py - center_y) * pulse_scale

        text_surf = font.render(self.char, True, self.color)
        surface.blit(text_surf, (int(px), int(py)))


# ==============================================================================
# MAIN APPLICATION
# ==============================================================================
def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Fonts
    font_mono = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 13, bold=True)
    font_large = pygame.font.SysFont(["consolas", "georgia", "serif"], 22, bold=True)
    font_sub = pygame.font.SysFont(["consolas", "sans-serif"], 14)

    # Grid sizes for envelope
    char_w = 9
    char_h = 16
    env_rows = len(ENVELOPE_CLOSED)
    env_cols = max(len(row) for row in ENVELOPE_CLOSED)
    env_pixel_w = env_cols * char_w
    env_pixel_h = env_rows * char_h
    env_start_x = (WINDOW_WIDTH - env_pixel_w) // 2
    env_start_y = (WINDOW_HEIGHT - env_pixel_h) // 2 - 20

    # Generate Heart Points
    heart_center_x = WINDOW_WIDTH // 2
    heart_center_y = WINDOW_HEIGHT // 2 - 30
    heart_scale = 13.5
    raw_heart_points = generate_heart_points(density=320)
    
    # Envelope characters mapping
    envelope_points = []
    for r_idx, line in enumerate(ENVELOPE_CLOSED):
        for c_idx, ch in enumerate(line):
            if ch != " ":
                px = env_start_x + c_idx * char_w
                py = env_start_y + r_idx * char_h
                envelope_points.append((px, py, ch))

    # Match envelope characters to heart points for morphing
    morph_chars = []
    num_particles = max(len(envelope_points), len(raw_heart_points))
    for i in range(num_particles):
        if i < len(envelope_points):
            src_x, src_y, ch = envelope_points[i]
        else:
            # Extra points spawn near envelope center
            src_x = env_start_x + env_pixel_w // 2 + random.randint(-40, 40)
            src_y = env_start_y + env_pixel_h // 2 + random.randint(-20, 20)
            ch = random.choice(HEART_CHARS)

        # Destination heart coordinate
        h_idx = i % len(raw_heart_points)
        hx, hy, is_edge = raw_heart_points[h_idx]
        dst_x = heart_center_x + hx * heart_scale
        dst_y = heart_center_y + hy * heart_scale

        # Coloring
        dist = math.hypot(hx, hy)
        if is_edge:
            char_choice = random.choice(["♥", "#", "@", "%"])
            color = random.choice([PINK_PRIMARY, ROSE_GLOW, (255, 120, 180)])
        else:
            char_choice = random.choice(["*", "+", "o", ".", ":"])
            color = random.choice([CRIMSON_DEEP, ROSE_GLOW, PURPLE_LIGHT])

        morph_chars.append(MorphChar(src_x, src_y, dst_x, dst_y, char_choice, color))

    # Particles & animation states
    sparkles = []
    start_time = time.time()
    forced_stage = 0

    # Timing Constants (Seconds)
    T_ENVELOPE_OPEN = 3.0
    T_MORPH_START = 4.5
    T_MORPH_END = 7.0
    T_HEART_PULSE = 7.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        elapsed = time.time() - start_time

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if elapsed < T_ENVELOPE_OPEN:
                        # Fast-forward to open envelope
                        start_time = time.time() - T_ENVELOPE_OPEN
                    elif elapsed < T_MORPH_START:
                        # Fast-forward to morph
                        start_time = time.time() - T_MORPH_START
                    else:
                        # Reset
                        start_time = time.time()
                        sparkles.clear()

        # Update Animation Stage
        screen.fill(BG_COLOR)

        # ----------------------------------------------------------------------
        # STAGE 1: CLOSED ENVELOPE (0.0s - 3.0s)
        # ----------------------------------------------------------------------
        if elapsed < T_ENVELOPE_OPEN:
            # Ambient pulse color
            pulse = (math.sin(elapsed * 3.5) + 1.0) / 2.0
            r_val = int(PURPLE_LIGHT[0] * (0.7 + 0.3 * pulse))
            g_val = int(PURPLE_LIGHT[1] * (0.7 + 0.3 * pulse))
            b_val = int(PURPLE_LIGHT[2] * (0.7 + 0.3 * pulse))
            env_color = (r_val, g_val, b_val)

            for r_idx, line in enumerate(ENVELOPE_CLOSED):
                for c_idx, ch in enumerate(line):
                    if ch != " ":
                        px = env_start_x + c_idx * char_w
                        py = env_start_y + r_idx * char_h
                        # Heart emblem inside envelope glows red
                        if ch in ["<", "3"]:
                            c = PINK_PRIMARY
                        elif ch == "*":
                            c = GOLD_SPARK
                        else:
                            c = env_color
                        text_s = font_mono.render(ch, True, c)
                        screen.blit(text_s, (px, py))

            # Prompt text
            prompt_s = font_sub.render(PROMPT_TEXT, True, TEXT_MUTED)
            prompt_rect = prompt_s.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))
            screen.blit(prompt_s, prompt_rect)

            # Occasional sparkle
            if random.random() < 0.2:
                sx = env_start_x + random.randint(0, env_pixel_w)
                sy = env_start_y + random.randint(0, env_pixel_h)
                sparkles.append(Sparkle(sx, sy, lifespan=40))

        # ----------------------------------------------------------------------
        # STAGE 2: ENVELOPE OPENING (3.0s - 4.5s)
        # ----------------------------------------------------------------------
        elif elapsed < T_MORPH_START:
            open_progress = (elapsed - T_ENVELOPE_OPEN) / (T_MORPH_START - T_ENVELOPE_OPEN)
            
            for r_idx, line in enumerate(ENVELOPE_OPEN):
                for c_idx, ch in enumerate(line):
                    if ch != " ":
                        px = env_start_x + c_idx * char_w
                        py = env_start_y + r_idx * char_h - int(open_progress * 15)
                        if "FOR YOU" in line:
                            c = GOLD_SPARK
                        elif ch in ["<", "3", "*"]:
                            c = PINK_PRIMARY
                        else:
                            c = PURPLE_LIGHT
                        text_s = font_mono.render(ch, True, c)
                        screen.blit(text_s, (px, py))

            # Sparkles eruption from envelope opening
            for _ in range(3):
                sx = env_start_x + env_pixel_w // 2 + random.randint(-60, 60)
                sy = env_start_y + 40 + random.randint(-10, 10)
                vy = random.uniform(-3.5, -0.8)
                vx = random.uniform(-2.0, 2.0)
                sparkles.append(Sparkle(sx, sy, vx=vx, vy=vy, lifespan=60))

        # ----------------------------------------------------------------------
        # STAGE 3 & 4: MORPHING & GLOWING HEART (4.5s+)
        # ----------------------------------------------------------------------
        else:
            morph_t = (elapsed - T_MORPH_START) / (T_MORPH_END - T_MORPH_START)
            morph_t = min(1.0, morph_t)

            # Heartbeat pulse calculation
            pulse_scale = 1.0
            if elapsed >= T_HEART_PULSE:
                t_pulse = elapsed - T_HEART_PULSE
                # Heart rhythm: lub-dub
                beat = (math.sin(t_pulse * 4.0) ** 63) * 0.08 + (math.sin(t_pulse * 4.0 + 0.35) ** 63) * 0.04
                pulse_scale = 1.0 + beat

            # Render characters
            for m in morph_chars:
                m.update(morph_t)
                m.draw(screen, font_mono, pulse_scale=pulse_scale, center_x=heart_center_x, center_y=heart_center_y)

            # Continuous sparkle emitter around heart perimeter
            if elapsed >= T_MORPH_END:
                for _ in range(2):
                    theta = random.uniform(0, 2 * math.pi)
                    hx, hy = heart_coords(theta)
                    dist_offset = random.uniform(0.9, 1.25)
                    sx = heart_center_x + hx * heart_scale * dist_offset * pulse_scale
                    sy = heart_center_y + hy * heart_scale * dist_offset * pulse_scale
                    sparkles.append(Sparkle(sx, sy, lifespan=50))

            # Display Letter Message
            if elapsed >= T_MORPH_END - 0.5:
                fade_in = min(1.0, (elapsed - (T_MORPH_END - 0.5)) / 1.5)
                # Typewriter effect for body text
                body_len = int(len(MESSAGE_BODY) * min(1.0, (elapsed - (T_MORPH_END + 0.5)) / 2.0))
                current_body = MESSAGE_BODY[:body_len]

                # Title
                title_color = (
                    int(GOLD_SPARK[0] * fade_in),
                    int(GOLD_SPARK[1] * fade_in),
                    int(GOLD_SPARK[2] * fade_in),
                )
                title_surf = font_large.render(MESSAGE_TITLE, True, title_color)
                title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 120))
                screen.blit(title_surf, title_rect)

                # Subtext / Message
                if current_body:
                    msg_color = (
                        int(WHITE_SPARK[0] * fade_in),
                        int(WHITE_SPARK[1] * fade_in),
                        int(WHITE_SPARK[2] * fade_in),
                    )
                    msg_surf = font_sub.render(current_body, True, msg_color)
                    msg_rect = msg_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 85))
                    screen.blit(msg_surf, msg_rect)

        # ----------------------------------------------------------------------
        # UPDATE & DRAW SPARKLES
        # ----------------------------------------------------------------------
        alive_sparkles = []
        for s in sparkles:
            s.update()
            if s.alive:
                s.draw(screen, font_mono)
                alive_sparkles.append(s)
        sparkles = alive_sparkles

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
