from __future__ import annotations

import base64
import os
from functools import wraps
from io import BytesIO

from PIL import Image


def img2str(
    img: Image.Image,
    inline: bool = True,
    name: str = "",
    width: str = "",
    height: str = "",
    preserve_aspect_ratio: bool = True,
    file_type: str = "",
) -> str:
    """Implement Inline Images Protocol of iTerm 2.
    The width and height are given as a number followed by a unit, or the word "auto".
        - N: N character cells.
        - Npx: N pixels.
        - N%: N percent of the session's width or height.
        - auto: The image's inherent size will be used to determine an appropriate dimension.

    Ref:
        - https://iterm2.com/documentation-images.html
        - https://iterm2.com/utilities/imgcat

    Args:
        img (Image.Image): Image to display/download
        inline (bool, optional): Display image inline if true, otherwise download. Defaults to True.
        name (str, optional): Download file name. Defaults to "".
        width (str, optional): Height to render. Defaults to "".
        height (str, optional): Height to render. Defaults to "".
        preserve_aspect_ratio (bool, optional): If true, fill the specified width and height as
            much as possible without stretching. Defaults to True.
        file_type (str, optional): File type hint. Defaults to "".

    Returns:
        str: Control sequence to display or download an image
    """
    img_file = BytesIO()

    if img.mode in ("RGBA", "P"): 
        img = img.convert("RGB")

    img.save(img_file, format="JPEG")
    img_b64 = img_file.getvalue()
    img_size = img_file.getbuffer().nbytes
    img_b64 = base64.b64encode(img_b64).decode()

    if os.environ.get("TERM", "").startswith(("tmux", "screen")):
        osc = "\033Ptmux;\033\033]"
        st = "\a\033\\"
    else:
        osc = "\033]"
        st = "\a"

    ctrl_seq = [f"{osc}1337;File=inline={int(inline)};size={img_size}"]

    if name:
        name = base64.b64encode(name.encode()).decode()
        ctrl_seq += [f";name={name}"]

    if width:
        ctrl_seq += [f";width={width}"]

    if height:
        ctrl_seq += [f";height={height}"]

    ctrl_seq += [f";preserveAspectRatio={int(preserve_aspect_ratio)}"]

    if file_type:
        ctrl_seq += [f";type={file_type}"]

    ctrl_seq += [f":{img_b64}{st}"]

    return "".join(ctrl_seq)


@wraps(img2str)
def print_img(
    *args,
    **kwargs,
) -> None:
    """Print an image in terminal cli"""
    print(img2str(*args, **kwargs))

