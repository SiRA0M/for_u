# For You — Special Letter Animation 💌

Animated ASCII & Procedural Typography project in Python, inspired by [@buildmeri](https://www.tiktok.com/@buildmeri).

## Features
- **Phase 1: Sealed ASCII Envelope**: Renders a purple/pink glowing envelope with heart seal.
- **Phase 2: Envelope Opening**: The flap unfolds upwards with glowing golden particles escaping.
- **Phase 3: Character Morphing**: Envelope ASCII characters interpolate smoothly along trajectories toward a parametric heart shape.
- **Phase 4: Beating Heart & Ambient Sparkles**: Heart pulses with a realistic lub-dub rhythm, surrounded by twinkling particles and typing out a customizable message.

## Quick Start

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python letter.py
   ```

## Controls
- **SPACE**: Fast-forward through animation stages, or replay from the beginning.
- **ESC**: Exit window.

## Customization
Open `letter.py` and modify the top configuration section:
```python
MESSAGE_TITLE = "Special Letter"
MESSAGE_BODY = "Every moment with you is special."
```
