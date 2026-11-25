# Special Letter 3D — Volumetric ASCII & Flower Bouquet 💌💐

Animated 3D Volumetric ASCII & Botanical Typography project in Python (`pygame-ce` + `numpy`), featuring 3D XYZ coordinate axes, interactive 3D orbit camera controls, touchscreen/mouse interaction, dedicated replay button, and a seamless 3D spline morphing transition into a lush flower bouquet.

## Features
- **3D XYZ Coordinate Axes**:
  - **World Origin Tripod**: Red (X), Green (Y), Blue (Z) axes drawn with 3D projection.
  - **Top-Right 3D Orientation Gizmo**: Interactive rotation indicator tracking camera orientation in real time.
- **Dedicated Replay UI Button (`↺ Replay`)**:
  - Placed at the bottom-left corner of the bouquet screen.
  - Clicking/dragging the 3D model will never accidentally reset the scene; only clicking the designated button triggers replay.
- **Ultra-Aesthetic 3D Flower Bouquet**:
  - Built using Fibonacci phyllotaxis ($\theta = 137.5^\circ$) for organic petal geometry.
  - Multi-tier color ramp: Deep velvet wine $\to$ Crimson $\to$ Coral $\to$ Champagne rose highlights.
  - Side peonies, peach tulips, chamomile daisies, and eucalyptus foliage.
  - Pure visual presentation (text removed per user preference).
- **High-Detail 3D Envelope**:
  - Slanted hatch borders, fine paper texture, and diagonal crease highlights.
  - Flap physically hinges and folds open 175° in 3D space.
  - Pulsing magenta heart wax seal elevated in 3D.
- **3D Controls**:
  - **Left Click / Touch Tap**: Open letter.
  - **Mouse / Touch Drag**: Orbit camera around 3D space (360° Pitch & Yaw).
  - **Mouse Scroll**: Zoom in / out.
  - **`↺ Replay` Button**: Reset animation.

## Requirements
```bash
pip install -r requirements.txt
```

## Run
```bash
python letter.py
```
