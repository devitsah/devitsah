"""
Generates dithered portrait dot-data (foreground mask + 1-bit dither grid)
from the user's uploaded photo: tight head-and-shoulders crop, lighter/
truer-to-photo tone, Floyd-Steinberg serpentine dither, background segmentation
for the dark-mode "lit subject" variant.
"""
import numpy as np
from PIL import Image, ImageOps, ImageFilter
from scipy import ndimage

SRC = "/mnt/user-data/uploads/Media__22_.jpg"
GRID_W, GRID_H = 150, 170

im = Image.open(SRC).convert("RGB")
a = np.array(im).astype(int)

# --- background color + subject mask (flat wall background) ---
corners = np.concatenate([a[0:15,0:15].reshape(-1,3), a[0:15,-15:].reshape(-1,3), a[-15:,0:15].reshape(-1,3)])
bgcolor = corners.mean(axis=0)
dist = np.sqrt(((a - bgcolor) ** 2).sum(axis=2))
mask = dist > 30
lbl, n = ndimage.label(mask)
sizes = ndimage.sum(mask, lbl, range(1, n + 1))
big = np.argmax(sizes) + 1
subject_mask = lbl == big
subject_mask = ndimage.binary_closing(subject_mask, structure=np.ones((9,9)))
subject_mask = ndimage.binary_fill_holes(subject_mask)
lbl2, n2 = ndimage.label(subject_mask)
sizes2 = ndimage.sum(subject_mask, lbl2, range(1, n2 + 1))
subject_mask = lbl2 == (np.argmax(sizes2) + 1)

ys, xs = np.where(subject_mask)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
h_person = y1 - y0

# --- tight head-and-shoulders crop (classic profile-photo framing) ---
top_pad = int(h_person * 0.055)
bottom_cut = y0 + int(h_person * 0.62)   # head + shoulders + upper chest only
cy0 = max(0, y0 - top_pad)
cy1 = min(a.shape[0], bottom_cut)
h_crop = cy1 - cy0

target_ratio = GRID_W / GRID_H   # width:height
target_w = h_crop * target_ratio
cx_center = (x0 + x1) / 2
cx0 = int(cx_center - target_w / 2)
cx1 = int(cx_center + target_w / 2)

# clamp / pad with bg color if crop would run off the image edges
pad_left = max(0, -cx0)
pad_right = max(0, cx1 - a.shape[1])
cx0c, cx1c = max(0, cx0), min(a.shape[1], cx1)

im_c = im.crop((cx0c, cy0, cx1c, cy1))
mask_c = subject_mask[cy0:cy1, cx0c:cx1c]

if pad_left or pad_right:
    neww = im_c.width + pad_left + pad_right
    canvas = Image.new("RGB", (neww, im_c.height), tuple(int(c) for c in bgcolor))
    canvas.paste(im_c, (pad_left, 0))
    im_c = canvas
    mcanvas = np.zeros((mask_c.shape[0], neww), dtype=bool)
    mcanvas[:, pad_left:pad_left + mask_c.shape[1]] = mask_c
    mask_c = mcanvas

im_small = im_c.resize((GRID_W, GRID_H), Image.LANCZOS)
mask_small = Image.fromarray((mask_c * 255).astype(np.uint8)).resize((GRID_W, GRID_H), Image.NEAREST)
mask_small = np.array(mask_small) > 127

gray = ImageOps.grayscale(im_small)
gray = ImageOps.autocontrast(gray, cutoff=1)
gray = gray.filter(ImageFilter.UnsharpMask(radius=2, percent=110))
g = np.array(gray).astype(float)
# lighter, truer-to-photo tone: gentler contrast + a brightness lift so the
# result reads as a soft photographic dither rather than a heavy silhouette
g = (g - 127.5) * 1.12 + 127.5
g = g + 22
g = np.clip(g, 0, 255)

# --- Floyd-Steinberg dithering, serpentine order ---
h, w = g.shape
out = np.zeros((h, w), dtype=np.uint8)
buf = g.copy()
for y in range(h):
    xr = range(0, w) if y % 2 == 0 else range(w - 1, -1, -1)
    for x in xr:
        old = buf[y, x]
        new = 0 if old < 128 else 255
        out[y, x] = 1 if new == 0 else 0
        err = old - new
        if y % 2 == 0:
            if x + 1 < w: buf[y, x+1]     += err * 7/16
            if y + 1 < h and x-1 >= 0: buf[y+1, x-1] += err * 3/16
            if y + 1 < h: buf[y+1, x]     += err * 5/16
            if y + 1 < h and x+1 < w: buf[y+1, x+1] += err * 1/16
        else:
            if x - 1 >= 0: buf[y, x-1]     += err * 7/16
            if y + 1 < h and x+1 < w: buf[y+1, x+1] += err * 3/16
            if y + 1 < h: buf[y+1, x]     += err * 5/16
            if y + 1 < h and x-1 >= 0: buf[y+1, x-1] += err * 1/16

np.save("/home/claude/work/gen/dots_full.npy", out)
np.save("/home/claude/work/gen/mask_subject.npy", mask_small)
print("grid", out.shape, "ink dots total:", out.sum(), "subject px:", mask_small.sum())
