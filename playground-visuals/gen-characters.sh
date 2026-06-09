#!/bin/bash
cd /Users/kaw/internalMac/.claude/worktrees/stupefied-knuth-8eaca0/playground-visuals
source /tmp/mlx-sdxl/bin/activate
mkdir -p characters

ARGS="--model-version argmaxinc/mlx-stable-diffusion-3-medium --steps 14 --cfg 4.5 --width 768 --height 768"
# Shared style suffix keeps the roster visually consistent
STYLE="full body game character sprite, retro 16-bit JRPG pixel art, thick clean outline, soft cel shading, warm sumi-e parchment palette with neon teal pink accents, centered single character, plain flat pale cream background, no text"
NEG="blurry, low quality, photorealistic, multiple characters, cropped, extra limbs, text, watermark, dark background, cluttered"

gen() {
  local name=$1; local seed=$2; local action=$3
  echo "[$(date +%H:%M:%S)] >>> $name"
  diffusionkit-cli $ARGS --seed $seed \
    --output-path characters/$name.png \
    --prompt "$action, $STYLE" \
    --negative_prompt "$NEG" 2>&1 | grep -E "Total time|Saved|ERROR" | tail -2
  echo "[$(date +%H:%M:%S)] <<< $name done"
}

gen mercury 42  "Roman god Mercury with winged silver helmet and winged sandals, standing and pointing forward giving orders, holding a golden caduceus staff and a scroll, golden tunic, confident leader pose"
gen uzume   128 "Japanese goddess Ame-no-Uzume dancing joyfully mid-spin holding a folding paper fan, flowing pink and white kimono, cheerful expression, dynamic dance pose, sakura petals"
gen cangjie 256 "ancient Chinese sage Cangjie the writing god with four eyes, sitting at a low wooden desk writing calligraphy with an ink brush, long white beard, brown scholar robe, focused"
gen ebisu   333 "Japanese fortune god Ebisu fishing, big joyful smile, holding a fishing rod in one hand and a large red sea bream fish in the other, tall fisherman hat, round belly, traditional robe"
gen cupid   404 "Roman god Cupid as a winged cherub child drawing a bow and aiming a love arrow, big white feathered wings, pink ribbon, mischievous focused expression, action shooting pose"
gen vulcan  512 "Roman blacksmith god Vulcan hammering glowing metal on an anvil, muscular arms, leather apron, sooty face, orange beard, sparks flying, mid-swing action pose, forge"
gen caishen 678 "Chinese god of wealth Caishen smiling holding a large gold ingot yuanbao, ornate red and gold imperial robe, tall ceremonial hat, long black beard, sitting on a tiger, coins around"
gen ceres   789 "Roman goddess Ceres of the harvest holding a cornucopia overflowing with fruits and a bowl of grain, golden wheat crown, flowing peach toga, gentle warm smile, presenting pose"
gen tenjin  890 "Japanese scholar god Tenjin reading an open book, Heian period white court robe and tall black cap, thin goatee, plum blossom branch, calm wise teaching pose"
gen niuwang 963 "Chinese ox king deity with white ox horns tending a small cow beside him, holding a pot of yogurt, blue and white cowherd robe, kind smile, farm pose"

echo "[$(date +%H:%M:%S)] ===== ALL CHARACTERS DONE ====="
ls -la characters/*.png
