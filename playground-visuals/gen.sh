#!/bin/bash
set -e
cd /Users/kaw/internalMac/.claude/worktrees/stupefied-knuth-8eaca0/playground-visuals
export PATH="$HOME/.local/bin:$PATH"

# Use Z-Image Turbo — open weights, no HF auth needed, fast on Apple Silicon
COMMON_ARGS="--base-model z-image-turbo --quantize 8 --steps 8 --guidance 3.5 --width 1024 --height 1024"

echo "[$(date +%H:%M:%S)] Starting variant 1: Isometric Village Map"
mflux-generate-z-image $COMMON_ARGS \
  --seed 42 \
  --output v1-isometric-village.png \
  --prompt "isometric pixel art village game scene, japanese sumi-e ink wash painting background, traditional Thai-Japanese fusion temple buildings made of brown and warm gray ink strokes, soft misty mountains, tiny pixel character sprites walking around, minimalist composition with negative space, low-saturation earth tones with subtle teal neon accent, retro 16-bit aesthetic, top-down 3/4 view, clean game UI" || echo "FAILED v1"

echo "[$(date +%H:%M:%S)] Starting variant 2: Top-down Map"
mflux-generate-z-image $COMMON_ARGS \
  --seed 123 \
  --output v2-topdown-map.png \
  --prompt "top-down 2d pixel art map of a small fantasy business hub, sumi-e ink wash painting background with brush stroke borders, 9 small temple buildings each with a tiny pixel deity character standing in front, monochrome warm brown and gray palette, soft pink neon glow accent on building labels, stardew valley style, retro RPG aesthetic, japanese ink art" || echo "FAILED v2"

echo "[$(date +%H:%M:%S)] Starting variant 3: Character Roster"
mflux-generate-z-image $COMMON_ARGS \
  --seed 777 \
  --output v3-character-roster.png \
  --prompt "pixel art character sprite sheet of 9 hindu and japanese deities lined up, sumi-e ink illustration background, each character 64x64 pixel art with subtle ink brush halo, parchment scroll backdrop, warm gray and burnt sienna palette with cyan magic glow, minimalist asian aesthetic, game character select screen" || echo "FAILED v3"

echo "[$(date +%H:%M:%S)] Starting variant 4: Dashboard UI"
mflux-generate-z-image $COMMON_ARGS \
  --seed 256 \
  --output v4-dashboard-ui.png \
  --prompt "retro video game UI dashboard mockup, sumi-e ink wash painting background, pixel art HUD elements, japanese calligraphy frame borders, warm brown and gray palette with soft neon teal HUD progress bars, deity character pixel portraits in corner panels, minimalist clean composition, business management game interface, japanese RPG menu style" || echo "FAILED v4"

echo "[$(date +%H:%M:%S)] Starting variant 5: Title Screen"
mflux-generate-z-image $COMMON_ARGS \
  --seed 1024 \
  --output v5-title-screen.png \
  --prompt "title screen mockup for a video game called Business Playground, sumi-e ink painting background with mountain silhouette and bamboo grove, pixel art logo and menu in foreground, japanese calligraphy aesthetic, warm brown and gray palette, pink neon glow on title text, retro 16-bit RPG vibe, cinematic centered composition" || echo "FAILED v5"

echo "[$(date +%H:%M:%S)] All variants complete."
ls -la *.png 2>/dev/null
