# tensorcat

This utility provides an easy way to display an image/tensor/array in the terminal, notebook, and Python interpreter/debugger. It supports both batched and non-batched input and will automatically deduce its format (BCHW, HWC) and range (0-1, 0-255).

## How
It utilizes the iTerm2's [Inline Images Protocol](https://iterm2.com/documentation-images.html) to display an image inline. This protocol is also implemented by VSCode (xterm.js). It first encodes the image binary into base64 text and sends the text to the terminal. The terminal then decodes and renders the image. Therefore, as long as the terminal can capture the control sequence, the terminal can display/transfer images regardless of the network connection. By default, the `tensorcat` will downsample the image to at most 1024x1024 when displayed inline, as displaying large images inline is not stable.

## Installation
```
pip install tensorcat
```

## Setting
- Terminal
  - You need to use iTerm2 or the VSCode integrated terminal with the `terminal.integrated.enableImages` setting enabled. 
- Tmux
  - You need to use iTerm2's [tmux integration mode](https://iterm2.com/documentation-tmux-integration.html) (launch tmux with `tmux -CC` in iTerm2).

## Usage

### CLI
If called from CLI directly, `tensorcat` can display or download a single image give the path to the image. 

```shell
python -m tensorcat.cli /path/to/img.png
tensorcat /path/to/img.png
```

```
usage: tensorcat [-h] [--download] [--orig_res] [--max_width MAX_WIDTH] [--max_height MAX_HEIGHT] [--name NAME] [--render_width RENDER_WIDTH] [--render_height RENDER_HEIGHT] [--stretch]
                 [--file_type FILE_TYPE]
                 image

Display or download an image in terminal

positional arguments:
  image                 Path to the image file

optional arguments:
  -h, --help            show this help message and exit
  --download, -d        Download the image
  --orig_res, -or       No downsample, use original resolution, ignoring max_width and max_height
  --max_width MAX_WIDTH, -mw MAX_WIDTH
                        Downsample to the max width
  --max_height MAX_HEIGHT, -mh MAX_HEIGHT
                        Downsample to the max height
  --name NAME, -n NAME  Name of the image (download file name)
  --render_width RENDER_WIDTH, -rw RENDER_WIDTH
                        Render width of the image
  --render_height RENDER_HEIGHT, -rh RENDER_HEIGHT
                        Render height of the image
  --stretch, -s         Do not preserve aspect ratio if true when rendering
  --file_type FILE_TYPE, -t FILE_TYPE
                        File type
```

### Python API
It can be called in Python interpreter/debugger or IPython Notebook. `tensorcat` can display `th.Tensor`, `np.ndarray`, `PIL.Image.Image`, or path to the image. For array data, the format is flexible. `tensorcat` will automatically deduce the likely format (HW, CHW, HWC, BHW, BCHW, BHWC) and range (0-1, 0-255, Out of Range). For out-of-range input, it will automatically rescale linearly. For batched input, it will tile the images into a grid.

```python
import torch as th
import pdb
from tensorcat import tensorcat
 
batch = th.randn(4, 3, 32, 32)
tensorcat(batch)

gray = th.randn(32, 32, 1)
tensorcat(gray)

pdb.set_trace()
tensorcat(gray)
```

```python
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
```

## Examples
### PDB
![](/assets/pdb.png)


### Notebook
![](/assets/notebook.png)


### CLI
![](/assets/cli.png)
