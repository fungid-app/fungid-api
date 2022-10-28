from PIL import Image, ImageOps
from typing import List, Tuple
import math
import numpy as np
import colorsys
import io

# https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Lon..2Flat._to_tile_numbers_2


def num2deg(xtile, ytile, zoom) -> Tuple[float, float]:
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


def deg2num(lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def get_bounds(xtile: int, ytile: int, zoom) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    return (num2deg(xtile, ytile, zoom), num2deg(xtile + 1, ytile + 1, zoom))


def generate_heatmap(points: List[Tuple[float, float]], max_x: float, max_y: float, size: int, zoom: int) -> Image.Image:
    # (60, 90, 90)

    bins = 16
    rect_size = int(size / bins)

    if len(points) == 0:
        blank_img = Image.new(
            'RGBA',
            (size, size),
            (0, 0, 0, 0)
        )
        return blank_img

    x, y = zip(*points)

    n3 = np.zeros((size, size, 4), dtype='uint8')
    heatmap, xedges, yedges = np.histogram2d(
        x, y, bins=bins, range=[[0, max_x], [0, max_y]])

    for i in range(bins):
        for j in range(bins):
            if(heatmap[i, j] > 0):
                val = heatmap[i, j]
                intensity = 1 if val > 19 else (val / 19)
                h = .17 - (intensity * .17)
                vr, vg, vb, va = hlsa_to_rgb(h, .6, 1, 1)
                irect = i * rect_size
                jrect = j * rect_size
                n3[irect:irect+rect_size, jrect:jrect+rect_size, 0] = vr
                n3[irect:irect+rect_size, jrect:jrect+rect_size, 1] = vg
                n3[irect:irect+rect_size, jrect:jrect+rect_size, 2] = vb
                n3[irect:irect+rect_size, jrect:jrect+rect_size, 3] = va

    img = Image.fromarray(n3, mode="RGBA")  # .resize((size, size))
    img = ImageOps.flip(img)
    return img


def generate_heatmap_bytes(points: List[Tuple[float, float]], max_x: float, max_y: float, size: int, zoom: int) -> bytes:
    img = generate_heatmap(points, max_x, max_y, size, zoom)
    return get_img_byte_array(img)


def hlsa_to_rgb(h: float, l: float, s: float, a: float) -> Tuple[int, int, int, int]:
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255), int(a * 255))


def get_img_byte_array(img: Image.Image) -> bytes:
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    # img.save('test.png')
    return img_byte_arr.getvalue()
