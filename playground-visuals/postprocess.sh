#!/bin/bash
cd /Users/kaw/internalMac/.claude/worktrees/stupefied-knuth-8eaca0/playground-visuals
source /tmp/mlx-sdxl/bin/activate
WEB=/Users/kaw/internalMac/.claude/worktrees/stupefied-knuth-8eaca0/playground-web/assets/characters
mkdir -p characters/cutout "$WEB"

NAMES="mercury uzume cangjie ebisu cupid vulcan caishen ceres tenjin niuwang"

# Wait until all 10 source PNGs exist AND the generator process is gone
echo "[$(date +%H:%M:%S)] waiting for all character gens..."
while pgrep -f "gen-characters.sh" > /dev/null || pgrep -f "output-path characters/" > /dev/null; do
  sleep 20
done
for n in $NAMES; do
  while [ ! -f "characters/$n.png" ]; do sleep 10; done
done
echo "[$(date +%H:%M:%S)] all gens present — removing backgrounds"

for n in $NAMES; do
  python3 -c "
from rembg import remove
from PIL import Image
img = Image.open('characters/$n.png')
out = remove(img)
# autocrop to content bbox for tight sprites
bbox = out.getbbox()
if bbox: out = out.crop(bbox)
out.save('characters/cutout/$n.png')
print('cut $n', out.size)
" 2>&1 | grep -E "^cut "
  cp "characters/cutout/$n.png" "$WEB/$n.png"
done
echo "[$(date +%H:%M:%S)] ===== POSTPROCESS DONE ====="
ls -la "$WEB"
