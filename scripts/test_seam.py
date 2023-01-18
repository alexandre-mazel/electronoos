import numpy as np
from PIL import Image
import seam_carving # pip install seam-carving

# https://pypi.org/project/seam-carving/

src = np.array(Image.open('../alex_pytools/autotest_data/BroadwayTowerSeamCarvingA.png'))
src_h, src_w, _ = src.shape
dst = seam_carving.resize(
    src, (src_w - 100, src_h), # dest size can dramatically shrink original
    energy_mode='backward',   # Choose from {backward, forward}
    order='width-first',  # Choose from {width-first, height-first}
    keep_mask=None
)
Image.fromarray(dst).show()


"""
remove object:
src = np.array(Image.open('fig/beach.jpg'))
mask = np.array(Image.open('fig/beach_girl.png').convert('L'))
dst = seam_carving.remove_object(src, drop_mask=mask, keep_mask=None)
Image.fromarray(dst).show()
"""