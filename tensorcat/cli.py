import argparse
from pathlib import Path

from PIL import Image, ImageOps

from .iterm2 import print_img


def main():
    parser = argparse.ArgumentParser(description="Display or download an image in terminal")
    parser.add_argument("image", type=Path, help="Path to the image file")
    parser.add_argument(
        "--download", "-d", action="store_true", help="Download the image"
    )

    parser.add_argument(
        "--orig_res",
        "-or",
        action="store_true",
        help="No downsample, use original resolution, ignoring max_width and max_height",
    )
    parser.add_argument(
        "--max_width", "-mw", type=int, default=1024, help="Downsample to the max width"
    )
    parser.add_argument(
        "--max_height",
        "-mh",
        type=int,
        default=1024,
        help="Downsample to the max height",
    )
    parser.add_argument("--name", "-n", type=str, help="Name of the image (download file name)")

    parser.add_argument(
        "--render_width", "-rw", type=str, help="Render width of the image"
    )
    parser.add_argument(
        "--render_height", "-rh", type=str, help="Render height of the image"
    )

    parser.add_argument(
        "--stretch",
        "-s",
        action="store_true",
        help="Do not preserve aspect ratio if true when rendering",
    )
    parser.add_argument("--file_type", "-t", type=str, help="File type")
    args = parser.parse_args()

    img = Image.open(args.image)
    if args.name is None:
        args.name = args.image.name

    if not args.orig_res and (
        img.size[0] > args.max_width or img.size[1] > args.max_height
    ):
        img = ImageOps.contain(img, (args.max_width, args.max_height))

    print_img(
        img=img,
        inline=not args.download,
        name=args.name,
        width=args.render_width,
        height=args.render_height,
        preserve_aspect_ratio=not args.stretch,
        file_type=args.file_type,
    )


if __name__ == "__main__":
    main()
