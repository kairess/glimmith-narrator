import sys, glob, os
from PIL import Image, ImageDraw, ImageFont
files = sorted(glob.glob(sys.argv[1]))
per = int(sys.argv[3]) if len(sys.argv) > 3 else 16
cols = 4; tw, th = 480, 270
f = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf', 18)
for si in range(0, len(files), per):
    chunk = files[si:si+per]
    rows = (len(chunk)+cols-1)//cols
    sheet = Image.new('RGB', (cols*tw, rows*th), (40,40,40))
    for i, fn in enumerate(chunk):
        im = Image.open(fn).convert('RGB').resize((tw, th), Image.LANCZOS)
        d = ImageDraw.Draw(im); d.text((6,4), os.path.basename(fn), fill=(255,255,0), font=f)
        sheet.paste(im, ((i%cols)*tw, (i//cols)*th))
    sheet.save(f'{sys.argv[2]}_{si//per}.png')
