#!/bin/bash
cd /Users/kaw/internalMac/.claude/worktrees/stupefied-knuth-8eaca0/playground-visuals
source /tmp/mlx-sdxl/bin/activate
mkdir -p cupid-candidates

ARGS="--model-version argmaxinc/mlx-stable-diffusion-3-medium --steps 18 --cfg 5.5 --width 768 --height 768"
STYLE="full body game character sprite, retro 16-bit JRPG pixel art, thick clean black outline, soft cel shading, vibrant colors, centered single character on plain flat pale cream background, no text, no signature"
NEG="blurry, low quality, photorealistic, multiple characters, cropped, extra limbs, missing wings, no wings, no bow, text, watermark, dark background, cluttered, adult man, scary, distorted face, deformed hands, painterly, watercolor, soft focus"

gen() {
  local name=$1; local seed=$2; local action=$3
  echo "[$(date +%H:%M:%S)] >>> $name"
  diffusionkit-cli $ARGS --seed $seed \
    --output-path cupid-candidates/$name.png \
    --prompt "$action, $STYLE" \
    --negative_prompt "$NEG" 2>&1 | grep -E "Total time|Saved|ERROR" | tail -2
  echo "[$(date +%H:%M:%S)] <<< $name done"
}

# Variant A — classic cherub aiming a bow, dynamic shooting pose
gen cupid-a 1001 \
  "Roman god Cupid as a chubby cherub baby angel, large white feathered angel wings spread wide behind him, curly golden blonde hair, big blue eyes, holding a small golden bow drawn with arrow nocked aiming forward, heart-shaped pink arrowtip glowing, pink and white toga sash, mischievous smiling expression, dynamic action pose mid-flight, soft pink heart particles around him"

# Variant B — toddler cupid standing on cloud, peaceful pose holding bow at side
gen cupid-b 2222 \
  "Roman god Cupid as a young cherub child angel about 8 years old, fluffy white feathered wings, tousled golden curly hair with a small laurel wreath, kind gentle smile, holding a golden ornate bow in one hand and a quiver of pink heart arrows over shoulder, white toga with pink sash, standing confidently on a small fluffy white cloud, soft glowing aura"

# Variant C — anime JRPG cute teen cupid archer
gen cupid-c 3737 \
  "Roman god Cupid reimagined as a cute anime archer boy hero, small angelic white feathered wings, short curly blonde hair, pink and white knight outfit with gold trim, holding an elegant golden bow drawn with a heart-tipped pink arrow aiming at viewer, confident smirk, action stance, sparkling heart particles, JRPG character art"

echo "[$(date +%H:%M:%S)] ===== ALL CUPID CANDIDATES DONE ====="
ls -la cupid-candidates/*.png
