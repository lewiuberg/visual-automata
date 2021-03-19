from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor
from typing import Generator
import numpy as np


def create_palette(
    start_rgb: sRGBColor, end_rgb: sRGBColor, n: int, colorspace: sRGBColor
) -> list:
    """
    Generates color palette based on start and end color.

    Args:
        start_rgb (sRGBColor): Palette start color.
        end_rgb (sRGBColor): Palette end color.
        n (int): Number of colors in the palette.
        colorspace (sRGBColor): The colorspace to use.

    Returns:
        list: Generated color palette.
    """
    # convert start and end to a point in the given colorspace
    start = convert_color(start_rgb, colorspace).get_value_tuple()
    end = convert_color(end_rgb, colorspace).get_value_tuple()

    # create a set of n points along start to end
    points = list(zip(*[np.linspace(start[i], end[i], n) for i in range(3)]))

    # create a color for each point and convert back to rgb
    rgb_colors = [
        convert_color(colorspace(*point), sRGBColor) for point in points
    ]

    # finally convert rgb colors back to hex
    return [color.get_rgb_hex() for color in rgb_colors]


def hex_to_rgb_color(hex: str) -> sRGBColor:
    """
    Converts hex color to RBG color.

    Args:
        hex (str): Hex color code.

    Returns:
        sRGBColor: RBG color values.
    """
    return sRGBColor(*[int(hex[i + 1: i + 3], 16) for i in (0, 2, 4)],
                     is_upscaled=True)


def list_cycler(lst: list) -> Generator[list, None, None]:
    """
    Generator that yields elements of a list. If all list values are yielded,
    it resets and start from the beginning.

    Args:
        lst (list): List to yield elements from.

    Yields:
        Generator[list, None, None]: Generator yielding list elements.
    """
    while True:
        yield from lst
