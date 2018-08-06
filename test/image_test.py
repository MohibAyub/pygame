if __name__ == '__main__':
    import sys
    import os
    pkg_dir = os.path.split(os.path.abspath(__file__))[0]
    parent_dir, pkg_name = os.path.split(pkg_dir)
    is_pygame_pkg = (pkg_name == 'tests' and
                     os.path.split(parent_dir)[1] == 'pygame')
    if not is_pygame_pkg:
        sys.path.insert(0, parent_dir)
else:
    is_pygame_pkg = __name__.startswith('pygame.tests.')

import unittest
if is_pygame_pkg:
    from pygame.tests.test_utils import example_path, png
else:
    from test.test_utils import example_path, png
import pygame, pygame.image, pygame.pkgdata
from pygame.compat import xrange_, ord_

import os
import array
import tempfile

def test_magic(f, magic_hex):
    """ tests a given file to see if the magic hex matches.
    """
    data = f.read(len(magic_hex))

    if len(data) != len(magic_hex):
        return 0

    for i in range(len(magic_hex)):
        if magic_hex[i] != ord_(data[i]):
            return 0

    return 1


class ImageModuleTest( unittest.TestCase ):
    def testLoadIcon(self):
        """ see if we can load the pygame icon.
        """
        f = pygame.pkgdata.getResource("pygame_icon.bmp")
        self.assertEqual(f.mode, "rb")

        surf = pygame.image.load_basic(f)

        self.assertEqual(surf.get_at((0,0)),(5, 4, 5, 255))
        self.assertEqual(surf.get_height(),32)
        self.assertEqual(surf.get_width(),32)

    def testLoadPNG(self):
        """ see if we can load a png with color values in the proper channels.
        """
        # Create a PNG file with known colors
        reddish_pixel = (210, 0, 0, 255)
        greenish_pixel = (0, 220, 0, 255)
        bluish_pixel = (0, 0, 230, 255)
        greyish_pixel = (110, 120, 130, 140)
        pixel_array = [reddish_pixel + greenish_pixel,
                       bluish_pixel + greyish_pixel]

        f_descriptor, f_path = tempfile.mkstemp(suffix='.png')
        f = os.fdopen(f_descriptor, 'wb')
        w = png.Writer(2, 2, alpha=True)
        w.write(f, pixel_array)
        f.close()

        # Read the PNG file and verify that pygame interprets it correctly
        surf = pygame.image.load(f_path)

        pixel_x0_y0 = surf.get_at((0, 0))
        pixel_x1_y0 = surf.get_at((1, 0))
        pixel_x0_y1 = surf.get_at((0, 1))
        pixel_x1_y1 = surf.get_at((1, 1))

        self.assertEquals(pixel_x0_y0, reddish_pixel)
        self.assertEquals(pixel_x1_y0, greenish_pixel)
        self.assertEquals(pixel_x0_y1, bluish_pixel)
        self.assertEquals(pixel_x1_y1, greyish_pixel)

        # Read the PNG file obj. and verify that pygame interprets it correctly
        f = open(f_path, 'rb')
        surf = pygame.image.load(f)
        f.close()

        pixel_x0_y0 = surf.get_at((0, 0))
        pixel_x1_y0 = surf.get_at((1, 0))
        pixel_x0_y1 = surf.get_at((0, 1))
        pixel_x1_y1 = surf.get_at((1, 1))

        self.assertEquals(pixel_x0_y0, reddish_pixel)
        self.assertEquals(pixel_x1_y0, greenish_pixel)
        self.assertEquals(pixel_x0_y1, bluish_pixel)
        self.assertEquals(pixel_x1_y1, greyish_pixel)

        os.remove(f_path)

    def testLoadJPG(self):
        """ see if we can load a jpg.
        """

        f = example_path('data/alien1.jpg')      # normalized
        # f = os.path.join("examples", "data", "alien1.jpg")
        surf = pygame.image.load(f)

        f = open(f, "rb")

        # f = open(os.path.join("examples", "data", "alien1.jpg"), "rb")

        surf = pygame.image.load(f)

        # surf = pygame.image.load(open(os.path.join("examples", "data", "alien1.jpg"), "rb"))

    def testSaveJPG(self):
        """ JPG equivalent to issue #211 - color channel swapping

        Make sure the SDL surface color masks represent the rgb memory format
        required by the JPG library. The masks are machine endian dependent
        """

        from pygame import Color, Rect

        # The source image is a 2 by 2 square of four colors. Since JPEG is
        # lossy, there can be color bleed. Make each color square 16 by 16,
        # to avoid the significantly color value distorts found at color
        # boundaries due to the compression value set by Pygame.
        square_len = 16
        sz = 2 * square_len, 2 * square_len

        #  +---------------------------------+
        #  | red            | green          |
        #  |----------------+----------------|
        #  | blue           | (255, 128, 64) |
        #  +---------------------------------+
        #
        #  as (rect, color) pairs.
        def as_rect(square_x, square_y):
            return Rect(square_x * square_len, square_y * square_len,
                        square_len, square_len)
        squares = [(as_rect(0, 0), Color("red")),
                   (as_rect(1, 0), Color("green")),
                   (as_rect(0, 1), Color("blue")),
                   (as_rect(1, 1), Color(255, 128, 64))]

        # A surface format which is not directly usable with libjpeg.
        surf = pygame.Surface(sz, 0, 32)
        for rect, color in squares:
            surf.fill(color, rect)

        # Assume pygame.image.Load works correctly as it is handled by the
        # third party SDL_image library.
        f_path = tempfile.mktemp(suffix='.jpg')
        pygame.image.save(surf, f_path)
        jpg_surf = pygame.image.load(f_path)

        # Allow for small differences in the restored colors.
        def approx(c):
            mask = 0xFC
            return pygame.Color(c.r & mask, c.g & mask, c.b & mask)
        offset = square_len // 2
        for rect, color in squares:
            posn = rect.move((offset, offset)).topleft
            self.assertEqual(approx(jpg_surf.get_at(posn)), approx(color))

    def testSavePNG32(self):
        """ see if we can save a png with color values in the proper channels.
        """
        # Create a PNG file with known colors
        reddish_pixel = (215, 0, 0, 255)
        greenish_pixel = (0, 225, 0, 255)
        bluish_pixel = (0, 0, 235, 255)
        greyish_pixel = (115, 125, 135, 145)

        surf = pygame.Surface((1, 4), pygame.SRCALPHA, 32)
        surf.set_at((0, 0), reddish_pixel)
        surf.set_at((0, 1), greenish_pixel)
        surf.set_at((0, 2), bluish_pixel)
        surf.set_at((0, 3), greyish_pixel)

        f_path = tempfile.mktemp(suffix='.png')
        pygame.image.save(surf, f_path)

        # Read the PNG file and verify that pygame saved it correctly
        width, height, pixels, metadata = png.Reader(filename=f_path).asRGBA8()
        pixels_as_tuples = []
        for pixel in pixels:
            pixels_as_tuples.append(tuple(pixel))

        self.assertEquals(pixels_as_tuples[0], reddish_pixel)
        self.assertEquals(pixels_as_tuples[1], greenish_pixel)
        self.assertEquals(pixels_as_tuples[2], bluish_pixel)
        self.assertEquals(pixels_as_tuples[3], greyish_pixel)

        os.remove(f_path)

    def testSavePNG24(self):
        """ see if we can save a png with color values in the proper channels.
        """
        # Create a PNG file with known colors
        reddish_pixel = (215, 0, 0)
        greenish_pixel = (0, 225, 0)
        bluish_pixel = (0, 0, 235)
        greyish_pixel = (115, 125, 135)

        surf = pygame.Surface((1, 4), 0, 24)
        surf.set_at((0, 0), reddish_pixel)
        surf.set_at((0, 1), greenish_pixel)
        surf.set_at((0, 2), bluish_pixel)
        surf.set_at((0, 3), greyish_pixel)

        f_path = tempfile.mktemp(suffix='.png')
        pygame.image.save(surf, f_path)

        # Read the PNG file and verify that pygame saved it correctly
        width, height, pixels, metadata = png.Reader(filename=f_path).asRGB8()
        pixels_as_tuples = []
        for pixel in pixels:
            pixels_as_tuples.append(tuple(pixel))

        self.assertEquals(pixels_as_tuples[0], reddish_pixel)
        self.assertEquals(pixels_as_tuples[1], greenish_pixel)
        self.assertEquals(pixels_as_tuples[2], bluish_pixel)
        self.assertEquals(pixels_as_tuples[3], greyish_pixel)

        os.remove(f_path)

    def test_save(self):

        s = pygame.Surface((10,10))
        s.fill((23,23,23))
        magic_hex = {}
        magic_hex['jpg'] = [0xff, 0xd8, 0xff, 0xe0]
        magic_hex['png'] = [0x89 ,0x50 ,0x4e ,0x47]
        # magic_hex['tga'] = [0x0, 0x0, 0xa]
        magic_hex['bmp'] = [0x42, 0x4d]


        formats = ["jpg", "png", "bmp"]
        # uppercase too... JPG
        formats = formats + [x.upper() for x in formats]

        for fmt in formats:
            try:
                temp_filename = "%s.%s" % ("tmpimg", fmt)
                pygame.image.save(s, temp_filename)
                # test the magic numbers at the start of the file to ensure they are saved
                #   as the correct file type.
                self.assertEqual((1, fmt), (test_magic(open(temp_filename, "rb"), magic_hex[fmt.lower()]), fmt))
                # load the file to make sure it was saved correctly.
                #    Note load can load a jpg saved with a .png file name.
                s2 = pygame.image.load(temp_filename)
                #compare contents, might only work reliably for png...
                #   but because it's all one color it seems to work with jpg.
                self.assertEquals(s2.get_at((0,0)), s.get_at((0,0)))
            finally:
                #clean up the temp file, comment out to leave tmp file after run.
                os.remove(temp_filename)
                pass


    def test_save_colorkey(self):
        """ make sure the color key is not changed when saving.
        """
        s = pygame.Surface((10,10), pygame.SRCALPHA, 32)
        s.fill((23,23,23))
        s.set_colorkey((0,0,0))
        colorkey1 = s.get_colorkey()
        p1 = s.get_at((0,0))

        temp_filename = "tmpimg.png"
        try:
            pygame.image.save(s, temp_filename)
            s2 = pygame.image.load(temp_filename)
        finally:
            os.remove(temp_filename)


        colorkey2 = s.get_colorkey()
        # check that the pixel and the colorkey is correct.
        self.assertEqual(colorkey1, colorkey2)
        self.assertEqual(p1, s2.get_at((0,0)))




    def assertPremultipliedAreEqual(self, string1, string2, source_string):
        self.assertEqual(len(string1), len(string2))
        block_size = 20
        if string1 != string2:
            for block_start in xrange_(0, len(string1), block_size):
                block_end = min(block_start + block_size, len(string1))
                block1 = string1[block_start:block_end]
                block2 = string2[block_start:block_end]
                if block1 != block2:
                    source_block = source_string[block_start:block_end]
                    msg = "string difference in %d to %d of %d:\n%s\n%s\nsource:\n%s" % (block_start, block_end, len(string1), block1.encode("hex"), block2.encode("hex"), source_block.encode("hex"))
                    self.fail(msg)

    def test_to_string__premultiplied(self):
        """ test to make sure we can export a surface to a premultiplied alpha string
        """

        def convertRGBAtoPremultiplied(surface_to_modify):
            for x in xrange_(surface_to_modify.get_width()):
                for y in xrange_(surface_to_modify.get_height()):
                    color = surface_to_modify.get_at((x, y))
                    premult_color = (color[0]*color[3]/255,
                                     color[1]*color[3]/255,
                                     color[2]*color[3]/255,
                                     color[3])
                    surface_to_modify.set_at((x, y), premult_color)

        test_surface = pygame.Surface((256, 256), pygame.SRCALPHA, 32)
        for x in xrange_(test_surface.get_width()):
            for y in xrange_(test_surface.get_height()):
                i = x + y*test_surface.get_width()
                test_surface.set_at((x,y), ((i*7) % 256, (i*13) % 256, (i*27) % 256, y))
        premultiplied_copy = test_surface.copy()
        convertRGBAtoPremultiplied(premultiplied_copy)
        self.assertPremultipliedAreEqual(pygame.image.tostring(test_surface, "RGBA_PREMULT"),
                                         pygame.image.tostring(premultiplied_copy, "RGBA"),
                                         pygame.image.tostring(test_surface, "RGBA"))
        self.assertPremultipliedAreEqual(pygame.image.tostring(test_surface, "ARGB_PREMULT"),
                                         pygame.image.tostring(premultiplied_copy, "ARGB"),
                                         pygame.image.tostring(test_surface, "ARGB"))

        no_alpha_surface = pygame.Surface((256, 256), 0, 24)
        self.assertRaises(ValueError, pygame.image.tostring, no_alpha_surface, "RGBA_PREMULT")


    def test_fromstring__and_tostring(self):
        """ see if fromstring, and tostring methods are symmetric.
        """

        def AreSurfacesIdentical(surf_a, surf_b):
            if surf_a.get_width() != surf_b.get_width() or surf_a.get_height() != surf_b.get_height():
                return False
            for y in xrange_(surf_a.get_height()):
                for x in xrange_(surf_b.get_width()):
                    if surf_a.get_at((x,y)) != surf_b.get_at((x,y)):
                        return False
            return True

        ####################################################################
        def RotateRGBAtoARGB(str_buf):
            byte_buf = array.array("B", str_buf)
            num_quads = len(byte_buf)//4
            for i in xrange_(num_quads):
                alpha = byte_buf[i*4 + 3]
                byte_buf[i*4 + 3] = byte_buf[i*4 + 2]
                byte_buf[i*4 + 2] = byte_buf[i*4 + 1]
                byte_buf[i*4 + 1] = byte_buf[i*4 + 0]
                byte_buf[i*4 + 0] = alpha
            return byte_buf.tostring()

        ####################################################################
        def RotateARGBtoRGBA(str_buf):
            byte_buf = array.array("B", str_buf)
            num_quads = len(byte_buf)//4
            for i in xrange_(num_quads):
                alpha = byte_buf[i*4 + 0]
                byte_buf[i*4 + 0] = byte_buf[i*4 + 1]
                byte_buf[i*4 + 1] = byte_buf[i*4 + 2]
                byte_buf[i*4 + 2] = byte_buf[i*4 + 3]
                byte_buf[i*4 + 3] = alpha
            return byte_buf.tostring()

        ####################################################################
        test_surface = pygame.Surface((64, 256), flags=pygame.SRCALPHA, depth=32)
        for i in xrange_(256):
            for j in xrange_(16):
                intensity = j*16 + 15
                test_surface.set_at((j + 0, i), (intensity, i, i, i))
                test_surface.set_at((j + 16, i), (i, intensity, i, i))
                test_surface.set_at((j + 32, i), (i, i, intensity, i))
                test_surface.set_at((j + 32, i), (i, i, i, intensity))

        self.assert_(AreSurfacesIdentical(test_surface, test_surface))

        rgba_buf = pygame.image.tostring(test_surface, "RGBA")
        rgba_buf = RotateARGBtoRGBA(RotateRGBAtoARGB(rgba_buf))
        test_rotate_functions = pygame.image.fromstring(rgba_buf, test_surface.get_size(), "RGBA")

        self.assert_(AreSurfacesIdentical(test_surface, test_rotate_functions))

        rgba_buf = pygame.image.tostring(test_surface, "RGBA")
        argb_buf = RotateRGBAtoARGB(rgba_buf)
        test_from_argb_string = pygame.image.fromstring(argb_buf, test_surface.get_size(), "ARGB")

        self.assert_(AreSurfacesIdentical(test_surface, test_from_argb_string))
        #"ERROR: image.fromstring with ARGB failed"


        argb_buf = pygame.image.tostring(test_surface, "ARGB")
        rgba_buf = RotateARGBtoRGBA(argb_buf)
        test_to_argb_string = pygame.image.fromstring(rgba_buf, test_surface.get_size(), "RGBA")

        self.assert_(AreSurfacesIdentical(test_surface, test_to_argb_string))
        #"ERROR: image.tostring with ARGB failed"


        argb_buf = pygame.image.tostring(test_surface, "ARGB")
        test_to_from_argb_string = pygame.image.fromstring(argb_buf, test_surface.get_size(), "ARGB")

        self.assert_(AreSurfacesIdentical(test_surface, test_to_from_argb_string))
        #"ERROR: image.fromstring and image.tostring with ARGB are not symmetric"

    def todo_test_frombuffer(self):

        # __doc__ (as of 2008-08-02) for pygame.image.frombuffer:

          # pygame.image.frombuffer(string, size, format): return Surface
          # create a new Surface that shares data inside a string buffer
          #
          # Create a new Surface that shares pixel data directly from the string
          # buffer. This method takes the same arguments as
          # pygame.image.fromstring(), but is unable to vertically flip the
          # source data.
          #
          # This will run much faster than pygame.image.fromstring, since no
          # pixel data must be allocated and copied.

        self.fail()

    def todo_test_get_extended(self):

        # __doc__ (as of 2008-08-02) for pygame.image.get_extended:

          # pygame.image.get_extended(): return bool
          # test if extended image formats can be loaded
          #
          # If pygame is built with extended image formats this function will
          # return True. It is still not possible to determine which formats
          # will be available, but generally you will be able to load them all.

        self.fail()

    def todo_test_load_basic(self):

        # __doc__ (as of 2008-08-02) for pygame.image.load_basic:

          # pygame.image.load(filename): return Surface
          # pygame.image.load(fileobj, namehint=): return Surface
          # load new image from a file

        self.fail()

    def todo_test_load_extended(self):

        # __doc__ (as of 2008-08-02) for pygame.image.load_extended:

          # pygame module for image transfer

        self.fail()

    def todo_test_save_extended(self):

        # __doc__ (as of 2008-08-02) for pygame.image.save_extended:

          # pygame module for image transfer

        self.fail()

if __name__ == '__main__':
    unittest.main()
