"""Convert an XWD window dump (from `xwd -id <window>`) to PNG.

Used by the figure pipeline to capture usdview GUI screenshots without
ImageMagick. Handles the common 24/32-bit TrueColor ZPixmap dumps.

Usage:  .venv/bin/python tools/xwd2png.py in.xwd out.png
"""
import struct
import sys

from PIL import Image

HEADER_FIELDS = 25  # 4-byte big-endian words before the window-name string


def xwd_to_image(path):
    data = open(path, 'rb').read()
    words = struct.unpack('>25I', data[:HEADER_FIELDS * 4])
    (header_size, _version, _format, _depth, width, height, _xoff, byte_order,
     _unit, _bit_order, _pad, bits_per_pixel, bytes_per_line, _visual,
     red_mask, _green_mask, _blue_mask, _bits_rgb, _cmap, ncolors,
     *_rest) = words

    pixels_start = header_size + ncolors * 12
    raw = data[pixels_start:pixels_start + bytes_per_line * height]

    if bits_per_pixel not in (24, 32):
        raise SystemExit(f'unsupported bits_per_pixel={bits_per_pixel}')

    red_high = red_mask > 0xFF  # red occupies the high byte of the pixel value
    if bits_per_pixel == 32:
        # MSB-first dump of XRGB, or LSB-first dump of the same value (BGRX).
        rawmode = ('XRGB' if red_high else 'XBGR') if byte_order == 1 else \
                  ('BGRX' if red_high else 'RGBX')
    else:
        rawmode = ('RGB' if red_high else 'BGR') if byte_order == 1 else \
                  ('BGR' if red_high else 'RGB')

    return Image.frombytes('RGB', (width, height), raw, 'raw', rawmode,
                           bytes_per_line, 1)


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    xwd_to_image(src).save(dst)
    print('wrote', dst)
