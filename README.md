# Special Letter 3D — Interactive ASCII to Flower Bouquet 💌💐

Animated 3D Volumetric ASCII & Procedural Typography project in Python (`pygame-ce` + `numpy`), featuring 3D perspective projection, interactive 3D orbit camera controls, touchscreen/mouse interaction, and a seamless 3D spline morphing transition into a lush 3D flower bouquet.

## 3D Features
- **True 3D Spatial Envelope**:
  - Positioned in 3D space with natural perspective depth and tilted aesthetic view.
  - High-density ASCII paper texture (over 2,180 points) with slanted hatch borders.
  - Flap physically hinges and folds open 180° in 3D space along its top axis.
  - Pulsing magenta heart wax seal elevated in 3D ($Z$).
- **Interactive 3D Camera (Orbit & Zoom)**:
  - **Click / Touch & Drag**: Rotate camera around Pitch and Yaw to view the envelope and bouquet from any 3D angle.
  - **Scroll Wheel**: Zoom camera in and out in 3D space.
  - **Click / Tap**: Open the envelope (or replay after bouquet forms).
- **3D Spline Transition (Quadratic Bezier in $\mathbb{R}^3$)**:
  - On opening, seal shatters with a 3D spherical particle burst ($vx, vy, vz$).
  - Points lift off the 2D surface and travel through 3D space along curved Bezier trajectories with radial wave delays.
- **Volumetric 3D Flower Bouquet**:
  - **3D Kraft Paper Wrapper**: Conical volume in 3D space.
  - **3D Satin Ribbon**: Torus loops and tails wrapping around bouquet waist.
  - **3D Leaves & Stems**: Eucalyptus and fern leaves curving outward in 3D hemispheres.
  - **3D Blooms**: Central layered 3D rose, side peonies, tulips, and daisies arranged with 3D dome curvature.
  - **3D Depth Fog & Perspective Sizing**: Far glyphs attenuate in brightness and scale dynamically based on $Z$-depth.
  - **Ambient Life**: 3D turntable rotation, gentle wind sway, and 3D floating rose petals/pollen sparkles.

## Requirements
```bash
pip install -r requirements.txt
```

## Run
```bash
python letter.py
```

## Controls
- **Left Click / Touch Tap**: Open letter / Replay.
- **Mouse / Touch Drag**: Orbit camera in 3D space (360° rotation).
- **Mouse Scroll**: Zoom in / out.
- **SPACE / ENTER**: Keyboard trigger to open or restart.
- **ESC**: Exit window.
