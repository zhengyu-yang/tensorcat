from __future__ import annotations

from functools import partial
from typing import cast, TYPE_CHECKING

import numpy as np
from IPython.display import display
from PIL import Image, ImageOps

from .iterm2 import print_img

if TYPE_CHECKING:
    from torch import Tensor


# https://stackoverflow.com/a/39662359
def is_notebook() -> bool:
    try:
        shell = get_ipython().__class__.__name__ # type: ignore
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def format_img(x: Tensor | np.ndarray, verbose: bool = False) -> np.ndarray:
    """Format the input image to a <[B, H, W, C], (0-255), (unit8)> format numpy array"""

    if not isinstance(x, np.ndarray):
        assert hasattr(x, "cpu") and hasattr(
            x, "numpy"
        ), f"Input must be a tensor or numpy array, got {type(x)}"
        x = x.cpu().numpy()

    x = cast(np.ndarray, x)

    shape = x.shape
    ndim = len(shape)

    format_guess = ""  # HW, CHW, HWC, BHW, BCHW, BHWC
    range_guess = ""  # 0-1, 0-255, Out of Range

    # shape
    if ndim == 2:
        format_guess = "HW"
        x = x[None, ..., None]
    elif ndim == 3:
        if shape[0] in [1, 3]:
            format_guess = "CHW"
            x = x.transpose(1, 2, 0)[None]
        elif shape[-1] in [1, 3]:
            format_guess = "HWC"
            x = x[None]
        else:
            format_guess = "BHW"
            x = x[..., None]
    elif ndim == 4:
        if shape[1] in [1, 3]:
            format_guess = "BCHW"
            x = x.transpose(0, 2, 3, 1)
        elif shape[-1] in [1, 3]:
            format_guess = "BHWC"
        else:
            raise ValueError(f"Cannot deduce shape mode from shape: {shape}")

    # range
    if x.min() >= 0 and x.max() <= 1:
        range_guess = "0-1"
        x = (x * 255).astype(np.uint8)
    elif x.min() >= 0 and x.max() <= 255:
        range_guess = "0-255"
        x = x.astype(np.uint8)
    else:
        range_guess = "Out of Range"
        x = (x - x.min()) / (x.max() - x.min()) * 255
        x = cast(np.ndarray, x)
        x = x.astype(np.uint8)
    
    # force RGB
    if x.shape[-1] == 1:
        x = np.broadcast_to(x, x.shape[:-1] + (3,))
    elif x.shape[-1] == 4:
        x = x[..., :3]

    if verbose:
        print(f"format: {format_guess}")
        print(f"range: {range_guess}")

    return x


def get_grid_size(b: int, h: int, w: int, nrow=0, ncol=0) -> tuple[int, int]:
    if nrow != 0:
        ncol = int(np.ceil(b / nrow))
    elif ncol != 0:
        nrow = int(np.ceil(b / ncol))
    else:
        ncol = int(np.ceil(np.sqrt(b / w * h)))
        nrow = int(np.ceil(b / ncol))

    return nrow, ncol


def tile_img(
    x: np.ndarray, nrow: int = 0, ncol: int = 0, padding: int = 2, pad_value: int = 0
) -> Image.Image:
    b, h, w, c = x.shape

    nrow, ncol = get_grid_size(b, h, w, nrow, ncol)

    h, w = h + padding, w + padding
    grid = np.full(
        (h * nrow + padding, w * ncol + padding, c), pad_value, dtype=np.uint8
    )

    k = 0
    for row in range(nrow):
        for col in range(ncol):
            if k >= b:
                break

            y0 = row * h + padding
            y1 = y0 + h - padding

            x0 = col * w + padding
            x1 = x0 + w - padding

            grid[y0:y1, x0:x1] = x[k]

            k += 1

    return Image.fromarray(grid)


def tensorcat(
    x: Tensor | np.ndarray | Image.Image | str,
    nrow: int = 0,
    ncol: int = 0,
    padding: int = 2,
    pad_value: int = 0,
    verbose: bool = False,
    max_h: int = 1024,
    max_w: int = 1024,
    orig_res: bool = False,
    render_h: str = "",
    render_w: str = "",
) -> None:
    """Display an image in terminal or notebook

    Args:
        x (Tensor | np.ndarray | Image.Image | str): Input image. If str, it is the path to the image file.
        nrow (int, optional): If x is a batched input, number of rows for the resulting grid. O for auto. Defaults to 0.
        ncol (int, optional): If x is a batched input, number of columns for the resulting grid. O for auto. Defaults to 0.
        padding (int, optional): Width of padding in the grid. Defaults to 2.
        pad_value (int, optional): Padding value in the grid. Defaults to 0.
        verbose (bool, optional): If print out debug info. Defaults to False.
        max_h (int, optional): Downsample image to the height limit. Defaults to 1024.
        max_w (int, optional): Downsample image to the width limit. Defaults to 1024.
        orig_res (bool, optional): Force original resolution, ignoring max_h and max_w. Defaults to False.
        render_h (str, optional): Height of the image render (can be measured in pixel ["Npx"], character ["N"], percentage of the display area ["N%"], or "auto"). If empty, then auto. Defaults to "".
        render_w (str, optional): Width of the image render (can be measured in pixel, character width, percentage of the display area ["N%"], or "auto"). If empty, then auto. Defaults to "".
    """
    if isinstance(x, str):
        x = Image.open(x)
        if x.mode == "RGBA":
            x = x.convert("RGB")

    if not isinstance(x, Image.Image):
        x = format_img(x, verbose)
        if x.shape[0] > 1:
            x = tile_img(x, nrow, ncol, padding, pad_value)
        else:
            x = Image.fromarray(x[0])

    x = cast(Image.Image, x)

    if verbose:
        print(f"size: {x.size}")

    show_fn = (
        display
        if is_notebook()
        else partial(print_img, width=render_w, height=render_h)
    )

    if orig_res or x.size[0] <= max_w and x.size[1] <= max_h:
        show_fn(x)
    else:
        x = ImageOps.contain(x, (max_w, max_h))
        show_fn(x)
