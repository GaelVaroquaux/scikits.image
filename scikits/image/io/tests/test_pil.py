import os.path
import numpy as np
from numpy.testing import *
from numpy.testing.decorators import skipif

from tempfile import NamedTemporaryFile

from scikits.image import data_dir
from scikits.image.io import imread, imsave, use_plugin

try:
    from PIL import Image
    from scikits.image.io._plugins.pil_plugin import _palette_is_grayscale
    use_plugin('pil')
except ImportError:
    PIL_available = False
else:
    PIL_available = True


@skipif(not PIL_available)
def test_imread_flatten():
    # a color image is flattened
    img = imread(os.path.join(data_dir, 'color.png'), flatten=True)
    assert img.ndim == 2
    assert img.dtype == np.float64
    img = imread(os.path.join(data_dir, 'camera.png'), flatten=True)
    # check that flattening does not occur for an image that is grey already.
    assert np.sctype2char(img.dtype) in np.typecodes['AllInteger']

@skipif(not PIL_available)
def test_imread_palette():
    img = imread(os.path.join(data_dir, 'palette_gray.png'))
    assert img.ndim == 2
    img = imread(os.path.join(data_dir, 'palette_color.png'))
    assert img.ndim == 3

@skipif(not PIL_available)
def test_palette_is_gray():
    from PIL import Image
    gray = Image.open(os.path.join(data_dir, 'palette_gray.png'))
    assert _palette_is_grayscale(gray)
    color = Image.open(os.path.join(data_dir, 'palette_color.png'))
    assert not _palette_is_grayscale(color)

class TestSave:
    def roundtrip(self, dtype, x, scaling=1):
        f = NamedTemporaryFile(suffix='.png')
        fname = f.name
        f.close()
        imsave(fname, x)
        y = imread(fname)

        assert_array_almost_equal((x * scaling).astype(np.int32), y)

    @skipif(not PIL_available)
    def test_imsave_roundtrip(self):
        for shape in [(10, 10), (10, 10, 3), (10, 10, 4)]:
            for dtype in (np.uint8, np.uint16, np.float32, np.float64):
                x = np.ones(shape, dtype=dtype) * np.random.random(shape)

                if np.issubdtype(dtype, float):
                    yield self.roundtrip, dtype, x, 255
                else:
                    x = (x * 255).astype(dtype)
                    yield self.roundtrip, dtype, x
