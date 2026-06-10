#!/bin/bash
cd /Users/kaw/internalMac/.claude/worktrees/stupefied-knuth-8eaca0/playground-visuals
source /tmp/mlx-sdxl/bin/activate

# Wide cinematic zone backgrounds in sumi-e ink-wash + warm-parchment palette.
# Steps 14, cfg 4.5 — fast preview quality (~2.5 min each at 1024x512 on M1).
ARGS_WIDE="--model-version argmaxinc/mlx-stable-diffusion-3-medium --steps 14 --cfg 4.5 --width 1024 --height 512"
ARGS_SQUARE="--model-version argmaxinc/mlx-stable-diffusion-3-medium --steps 14 --cfg 4.5 --width 768 --height 512"
NEG="modern photorealistic, blurry, low quality, text, watermark, distorted hands, signature, people, character, person, deity, sprite"

run() {
  local args="$1"; local seed=$2; local out=$3; local prompt=$4
  echo "[$(date +%H:%M:%S)] START $out (seed $seed)"
  diffusionkit-cli $args \
    --seed $seed \
    --output-path $out \
    --prompt "$prompt" \
    --negative_prompt "$NEG" 2>&1 | grep -E "(Total|Saved|Error|error)" | tail -3
  echo "[$(date +%H:%M:%S)] DONE  $out"
}

# Content zone (wide 2:1) — pink/sakura performance stage with bamboo and writing desk
run "$ARGS_WIDE" 8101 zone-content-bg.png \
  "japanese sumi-e ink wash painting, wide horizontal landscape, empty outdoor performance courtyard at golden hour, blooming pink cherry blossom tree on left with falling petals, raised wooden tatami stage in center, bamboo grove on right, soft warm parchment cream background with pink magenta sakura accents and dark calligraphy ink branches, watercolor texture, ghibli inspired, soft mist, NO characters, NO people, empty scene"

# Commerce zone (wide 2:1) — gold marketplace with koi pond, lanterns, abacus
run "$ARGS_WIDE" 8202 zone-commerce-bg.png \
  "japanese sumi-e ink wash painting, wide horizontal landscape, ancient asian marketplace bazaar, hanging red lantern on left, large oval koi pond with orange koi fish in center, stacks of gold coins and chinese yuanbao ingots on the right wooden shelf, traditional wooden shop counter, warm parchment gold palette, ink wash mountains in soft background, ghibli style, NO people, NO characters, empty marketplace at dusk"

# Plaza zone (3:2) — sacred plaza with torii arch, stone circle, lanterns
run "$ARGS_SQUARE" 8303 zone-plaza-bg.png \
  "japanese sumi-e ink wash painting, sacred shinto shrine plaza, large red vermillion torii gate in center background, stone tile ground with circular ceremonial pattern, six round meditation cushions arranged in circle, two stone lanterns flanking, mist swirling, warm parchment with crimson red and gold accents, ghibli inspired, soft glow, NO people, NO characters, empty sacred space"

# Ops zone (ultra-wide 6:1) — rural panorama: delivery cart, school, farm
run "--model-version argmaxinc/mlx-stable-diffusion-3-medium --steps 14 --cfg 4.5 --width 1536 --height 256" \
  8404 zone-ops-bg.png \
  "japanese sumi-e ink wash painting, ultra wide panoramic countryside landscape, golden rice paddy fields stretching across, on the left a wooden cart with bread loaves, in the center a small traditional asian schoolhouse with chalkboard sign, on the right a cow barn with wooden fence and clay yogurt jars, distant misty mountains, warm parchment earth tones with sage green and ochre, ghibli inspired, NO people, NO characters, dawn light"

echo "[$(date +%H:%M:%S)] ALL ZONES DONE"
ls -la zone-*.png
