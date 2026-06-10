#!/bin/bash
cd /Users/kaw/internalMac/.claude/worktrees/stupefied-knuth-8eaca0/playground-visuals
source /tmp/mlx-sdxl/bin/activate

# SD3 medium on M1 — optimized for speed
# 16 steps × 768×768 ≈ 6-8 min per image
ARGS="--model-version argmaxinc/mlx-stable-diffusion-3-medium --steps 16 --cfg 4.5 --width 768 --height 768"
NEG="blurry, low quality, modern photorealistic, text, watermark, distorted"

run() {
  local seed=$1
  local out=$2
  local prompt=$3
  echo "[$(date +%H:%M:%S)] Starting $out (seed $seed)"
  diffusionkit-cli $ARGS \
    --seed $seed \
    --output-path $out \
    --prompt "$prompt" \
    --negative_prompt "$NEG" 2>&1 | grep -E "(Total|Saved|Error|error)" | tail -3
  echo "[$(date +%H:%M:%S)] Done $out"
}

run 42 eden-v1-master.png \
  "isometric pixel art game scene of a sacred Eden garden, japanese sumi-e ink wash painting style background, ancient red torii gate on raised stone platform at center, mossy stones, blooming sakura and plum trees, bamboo grove, small koi pond with stone bridge, deity character pixel sprites scattered, warm parchment brown and gray earth palette with neon teal and pink magic accents, ghibli inspired, retro 16-bit RPG town aesthetic, top-down 3/4 view"

run 128 eden-v2-pantheon.png \
  "wide pixel art landscape of an eden garden with Roman Japanese and Chinese pantheon deities gathered together, japanese ink wash mountain background, traditional pixel art deity characters in flowing robes, sitting and standing around a central torii gate and koi pond, lush garden with sakura petals falling, warm parchment colors with teal and pink magic glow, cinematic wide view"

run 256 eden-v3-deity-portrait.png \
  "detailed pixel art portrait of a Japanese shinto kami deity standing in a sumi-e ink wash garden, 128x128 pixel sprite with rich shading, ornate kimono with golden ornaments, floating sakura petals, soft warm brown and gray palette with pink neon halo glow, retro JRPG character"

run 512 eden-v4-ui.png \
  "retro 16-bit JRPG game UI dashboard mockup, sumi-e ink wash painting background, japanese style HUD panels with calligraphy borders, deity character pixel portraits in side panels, warm brown gray parchment palette with neon teal progress bars and pink accents, business management game interface"

run 1024 eden-v5-title.png \
  "title screen for a video game called Business Playground Pantheon, sumi-e ink wash painting background with mountain silhouette and cherry blossoms, ornate japanese pixel art logo center, warm parchment palette with pink gold accents, cinematic centered composition, retro RPG title"

echo "[$(date +%H:%M:%S)] ALL DONE"
ls -la eden-*.png
