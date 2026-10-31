import sys, time
from PIL import Image
import cap3 as V
times = [float(x) for x in sys.argv[2:]]
out = sys.argv[1]
ims = []
t0 = time.time()
for t in times:
    ims.append(V.render_frame(t).resize((360, 640)))
print('s/frame', (time.time() - t0) / len(times))
cols = 5
rows = (len(ims) + cols - 1) // cols
sh = Image.new('RGB', (360 * cols, 640 * rows), (255, 0, 255))
for i, im in enumerate(ims):
    sh.paste(im, ((i % cols) * 360, (i // cols) * 640))
sh.save(out)
