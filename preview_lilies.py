"""Render the final LilyBouquet2D state to a PNG for visual comparison."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame, math
from letter import LilyBouquet2D, WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BG, COL_STARDUST

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
font = pygame.font.SysFont(["consolas", "couriernew", "monospace"], 13, bold=True)

cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 10
lilies = LilyBouquet2D(cx, cy, total_points=2490)

screen.fill(COLOR_BG)
for pt in lilies.points:
    screen.blit(font.render(pt["char"], True, pt["color"]),
                (int(pt["base_x"]), int(pt["base_y"])))

pygame.image.save(screen, "preview_lilies.png")
print("saved preview_lilies.png", len(lilies.points))
