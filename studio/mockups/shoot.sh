#!/bin/sh
# Screenshot each mockup page to out/NN_name.png (1600x1000 at 1.5x).
cd "$(dirname "$0")"; mkdir -p out
CHROME=${CHROME:-/opt/pw-browsers/chromium-1194/chrome-linux/chrome}
for f in ${@:-[0-9]*.html}; do
  "$CHROME" --headless=new --no-sandbox --disable-gpu --hide-scrollbars --allow-file-access-from-files \
    --force-device-scale-factor=1.5 --window-size=1600,1100 --virtual-time-budget=2000 \
    --screenshot="out/${f%.html}.png" "file://$PWD/$f" 2>/dev/null
done
python3 -c "import glob;from PIL import Image
for f in glob.glob('out/*.png'):
  i=Image.open(f)
  if i.height>1500: i.crop((0,0,2400,1500)).save(f)"
ls out
