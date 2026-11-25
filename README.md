# Special Letter — Single Rose Animation 💌🌹

Animated 2D Botanical ASCII & Typography project in Python (`pygame-ce`), featuring a high-density ASCII envelope that morphs into a living, swaying, breathing grand single rose.

## Features
- **High-Detail 2D ASCII Envelope**:
  - Slanted hatch borders (`/ / / /`) top & bottom matching original reference.
  - Textured warm peach/sepia paper with diagonal crease fold highlights.
  - Pulsing magenta heart wax seal (`♥`, `@`, `#`) that bursts with particles when opened.
- **Pure 2D Rendering with Organic Motion**:
  - **Living Wind Sway**: The rose stem sways naturally in the breeze using height-attenuated sine oscillations.
  - **Breathing Blossom Bloom**: Rose petals gently breathe and pulse with realistic organic rhythm.
  - **Ambient Life**: Rising dewdrops, floating petals, and soft floral shimmer.
- **Grand Single Rose Anatomy**:
  - **Blossom Head**: Concentric Fibonacci spiraling petals (Velvet wine $\to$ Crimson $\to$ Coral $\to$ Champagne tips).
  - **Sepals**: Green calyx cradling the flower head.
  - **Botanical Stem**: Elegant S-curved emerald stem with thorns (`<`, `>`).
  - **Serrated Leaves**: Left and right leaf branches with vein highlights.
- **Pure ASCII Typography Replay Icon**:
  - Minimalist ASCII icon badge at bottom-left:
    ```
     .----. 
    /  <-- \
    \      /
     '----' 
    ```
  - Standard monospace characters (no missing unicode box `[?]`).
  - Only clicking this icon triggers reset; no text or prompt lines cluttering the screen.

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
