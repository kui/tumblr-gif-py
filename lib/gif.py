import os, re, subprocess
from math import sqrt
from color import print_g, print_r

import loop_effect as le

UNITS = {
    "B":  pow(1024.0, 0),
    "KB": pow(1024.0, 1),
    "MB": pow(1024.0, 2),
    "GB": pow(1024.0, 3)
}

# FIXME refactor because of too big block
def main(args):
    normalize_args(args)

    basedir = os.path.dirname(args.imgs[0])

    le.delete_blends(basedir)

    imgs = [f for f in args.imgs if not le.is_blend(f)]
    # thin out with interval
    imgs = [imgs[i] for i in range(0, len(imgs)) if i % args.interval == 0]

    if args.loop_effect is not None:
        args.loop_effect.generate(imgs, basedir)

    n_imgs = len(imgs)
    if args.loop_effect is not None and args.loop_effect.imgs != []:
        n_imgs += len(args.loop_effect.imgs)
    print_g("frames: {}".format(n_imgs))

    width = args.init_width
    if args.max_side < args.init_width:
        print_r("WARN: Ignore init-width, Using max-side")
        width = args.max_side

    if args.crop is not None:
        crop_width = parse_crop_width(args.crop)
        if width >= crop_width:
            print_g("Using crop width for init-width: {}x".format(crop_width))
            width = crop_width

    print_g("init width: {}".format(width))

    width_history = []
    while True:
        generate_gif(imgs, width, basedir, args)

        if is_valid_gif(args):
            print_g("Success")
            break

        width = get_next_width(args)
        print_g("next width: {}".format(width))

        if width in width_history:
            print_g("gif width convergence: {}x".format(width))
            print_g("Success")
            break

        width_history.append(width)

    open_gif(args.gif)

def normalize_args(args):
    if args.max_side is None:
        args.max_side = args.init_width
    if args.loop_effect is not None:
        delay = get_delay(args)
        args.loop_effect = le.parse_loop_effect(args.loop_effect, delay)
    if args.init_width is None:
        args.init_width = args.max_side
    args.max_size = parse_size_fmt(args.max_size)

def parse_size_fmt(size):
    f = float(re.search(r"\s*[\d\.]+", size).group(0))
    unit = re.search(r"([gmk]?b)\s*$", size, re.IGNORECASE).group(1)
    return f * UNITS[unit]

def parse_crop_width(c):
    arr = c.split("x")

    if len(arr) == 2:
        if arr[0] == "":
            return None
        else:
            return int(arr[0])

    raise """Invalid "crop" format"""

def get_delay(args):
    return args.interval * args.delay_factor

# FIXME refactor because of too big block
def generate_gif(imgs, width, basedir, args):
    cmd = [
        "convert",
        "-loop", "0"
    ]

    delay = get_delay(args)

    if args.first_delay is not None:
        cmd += [
            "-delay", str(args.first_delay),
            imgs[0],
            "-delay", str(delay)
        ] + imgs[1:-1]
    else:
        cmd += [
            "-delay", str(delay)
        ] + imgs[:-1]

    if args.last_delay is not None:
        cmd += ["-delay", str(args.last_delay)]

    cmd += [imgs[-1]]

    if args.loop_effect is not None:
        cmd += args.loop_effect.get_convert_args_fragments()

    if not args.dither:
        cmd += ["+dither"]

    if args.crop:
        cmd += [
            "-crop", args.crop,
            "+repage"
        ]

    cmd += [
        "-resize", str(width),
        "-fuzz", "{}%".format(args.fuzz),
        "-layers", "OptimizeTransparency",
        args.gif
    ]

    print("exec: {}".format(" ".join(cmd)))
    subprocess.check_call(cmd)

def open_gif(gif):
    cmd = ["xdg-open", gif]
    print("exec: {}".format(" ".join(cmd)))
    subprocess.check_call(cmd, stderr=subprocess.PIPE)

def get_next_width(args):
    width, height = get_sides(args.gif)
    size = os.path.getsize(args.gif)

    if size >= args.max_size:
        w = sqrt(args.max_size / size) * width
        return int(w / 4) * 4 # round 4 multiple num

    if height > width:
        return int((float(args.max_side) / height) * width)

    return args.max_side

def is_valid_gif(args):
    width, height = get_sides(args.gif)

    if width > args.max_side or height > args.max_side:
        return False

    size = os.path.getsize(args.gif)

    print_g("gif size: {}".format(get_pretty_size(size)))

    if size > args.max_size:
        return False

    if width == args.max_side or height == args.max_side:
        return True

    return (args.max_size * 0.95) < size

def get_pretty_size(size):
    for u in UNITS:
        s = float(size) / UNITS[u]
        if 1 < s < 1024:
            return "%.3f%s" % (s, u)
    raise "Unreachable block"

def get_sides(gif):
    cmd = ["identify", "-format", "%[fx:w]x%[fx:h],", gif]
    out = subprocess.check_output(cmd)
    return map(int, re.split(r"[x,]", out)[:2])
