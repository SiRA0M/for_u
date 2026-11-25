# Special Letter — Stargazer Lily Bouquet 💌🌸

Animated 2D Botanical ASCII & Typography project in Python (`pygame-ce`), featuring a high-density ASCII envelope morphing into the multi-colored 6-petal Stargazer Lily bouquet from the original video.

## Features
- **High-Detail 2D ASCII Envelope**:
  - Slanted hatch borders (`/ / / /`) top & bottom.
  - Textured warm peach/sepia paper with diagonal crease fold highlights.
  - Pulsing magenta heart wax seal (`♥`, `@`, `#`) that bursts with particles when opened.
- **Accurate Lily Bouquet (10 Lilies & Base Foliage)**:
  - **Top-Center Fire Red Lily**: 6 pointed petals in rich scarlet & crimson (`(235, 42, 52)`).
  - **Mid-Left Vivid Pink Lily**: Rose-magenta petals with delicate freckles (`(245, 100, 185)`).
  - **Mid-Right Pure White Lily**: Luminous petals with chartreuse-lime throat (`(255, 252, 248)`).
  - **Bottom-Center Peach Lily**: Warm apricot petals (`(255, 185, 135)`).
  - **Left Flanking Yellow Lilies**: Bright golden-amber blooms (`(255, 215, 45)`).
  - **Right Flanking Burgundy Lilies**: Velvet plum and deep maroon blooms (`(180, 42, 78)`).
  - **Top Background Lilies**: Soft ivory and pale gold buds.
  - **Base Strappy Green Leaves**: Lush emerald lily foliage fanning out at the base.
  - **Petal Striations**: Monospace ASCII scanline texture (`=`, `-`, `~`, `#`, `8`, `%`) matching the reference image.
- **Organic Motion**:
  - **Living Wind Sway**: Whole bouquet sways gently in the breeze.
  - **Breathing Petals**: Petals expand and breathe with subtle organic pulse.
  - **Stardust Sparkles**: Floating pollen and ambient starry sparkles drifting around the flowers.
- **ASCII Typography Replay Icon**:
  - Monospace ASCII badge at bottom-left:
    ```
     .----. 
    /  <-- \
    \      /
     '----' 
    ```
  - Standard ASCII characters (no missing unicode `[?]` boxes).
  - Only clicking this icon triggers reset; clean UI without text lines.

## Requirements
```bash
pip install -r requirements.txt
```

## Run
```bash
python letter.py
```

## Controls
- **Click / Tap screen**: Open envelope.
- **Click ASCII Icon (Bottom-Left)**: Replay animation.
- **ESC**: Exit window.
