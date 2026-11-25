# For You — Interactive Special Letter to Flower Bouquet 💌💐

Animated high-density ASCII & Procedural Typography project in Python (`pygame-ce`), featuring user touch/click interaction and a seamless morphing transition into a lush flower bouquet.

## Features
- **High-Detail ASCII Envelope**:
  - Slanted hatch borders (`/ / / /`) on top and bottom.
  - Over 2,300 dense textured ASCII glyphs mimicking real woven letter paper.
  - Accurate diagonal crease folds leading to a center heart-shaped wax seal.
  - Warm sepia/peach shading with subtle purple rim lighting.
  - Pulsing magenta heart wax seal (`♥`, `@`, `#`) that reacts to mouse hover and touch.
- **Interactive User Control**:
  - Touchscreen tap (`pygame.FINGERDOWN`) or Mouse click (`pygame.MOUSEBUTTONDOWN`) to open the letter.
  - Fallback keyboard controls (`SPACE` or `ENTER`).
- **Smooth Spline Transition**:
  - Quadratic Bezier curves with non-linear easing and radial delay waves.
  - Burst of golden and rose particles as the seal breaks open.
  - Characters fluidly transform from envelope cells into blooming flower petals.
- **Detailed Botanical Flower Bouquet**:
  - Central multi-layered grand rose with spiraling petal geometry.
  - Soft lilac peonies, coral tulip buds, and white daisies with golden stamens.
  - Rich foliage with emerald leaves, eucalyptus sprigs, and stems.
  - Kraft paper conical wrapper tied with a satin ribbon bow.
- **Ambient Life & Typography**:
  - Gentle breeze oscillation swaying the bouquet.
  - Floating petals and twinkling sparkles rising upwards.
  - Fading in elegant typewriter message: *"For Someone Special 💐"*.
  - Tap / Click anywhere to replay anytime.

## Requirements
```bash
pip install -r requirements.txt
```

## Run
```bash
python letter.py
```

## Controls
- **Click / Tap screen**: Open envelope (or replay after bouquet forms).
- **SPACE / ENTER**: Keyboard trigger to open or restart.
- **ESC**: Close application window.
