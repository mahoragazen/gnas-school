#!/bin/bash
cd /Users/kaw/internalMac/.claude/worktrees/stupefied-knuth-8eaca0/playground-visuals
source /tmp/mlx-sdxl/bin/activate
mkdir -p characters

ARGS="--model-version argmaxinc/mlx-stable-diffusion-3-medium --steps 18 --cfg 5.5 --width 768 --height 768"
STYLE="full body game character sprite, retro 16-bit JRPG pixel art, thick clean black outline, soft cel shading, vibrant colors, centered single character on plain flat pale cream background, no text, no signature"
NEG="blurry, low quality, photorealistic, multiple characters, cropped, extra limbs, text, watermark, dark background, cluttered, distorted face, deformed hands, painterly, watercolor, soft focus, modern clothes"

gen() {
  local name=$1; local seed=$2; local action=$3
  echo "[$(date +%H:%M:%S)] >>> $name"
  diffusionkit-cli $ARGS --seed $seed \
    --output-path characters/$name.png \
    --prompt "$action, $STYLE" \
    --negative_prompt "$NEG" 2>&1 | grep -E "Total time|Saved|ERROR" | tail -2
  echo "[$(date +%H:%M:%S)] <<< $name done"
}

# Konohanasakuya — Japanese goddess HR
gen konohana 5511 \
  "Japanese Shinto goddess Konohanasakuya-hime princess of cherry blossoms, beautiful young woman with long flowing black hair decorated with pink sakura petals, wearing elegant traditional pink and white silk kimono with sakura flower pattern, gentle warm motherly smile, holding a delicate cherry blossom branch in one hand and a small scroll list in the other, soft pink and white aura, peaceful protective stance"

# Bao Zheng — Chinese god of justice QA
gen baozheng 6622 \
  "ancient Chinese god of justice Bao Zheng Bao Gong, tall stern judge with black face and white crescent moon mark on forehead, long thin black beard, wearing ornate black official court robe with gold trim and red sash, tall scholar judge hat with wings, holding a wooden gavel in one hand and a brass scale of justice in the other, serious dignified expression, regal upright stance, golden light behind him"

echo "[$(date +%H:%M:%S)] ===== HR + QA DONE ====="
ls -la characters/konohana.png characters/baozheng.png
