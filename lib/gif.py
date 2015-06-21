import os, re, subprocess
from math import sqrt
from color import print_g, print_r

GEN_BLENDS_PATTERN = "__blended-%03d.png"
RM_BLENDS_PATTERN = r"__blended-\d+.png$"

UNITS = {
    "B":  pow(1024.0, 0),
    "KB": pow(1024.0, 1),
    "MB": pow(1024.0, 2),
    "GB": pow(1024.0, 3)
}

def main(args):
    normalize_args(args)

    basedir = os.path.dirname(args.imgs[0])

    rm_blends(basedir)

    imgs = [f for f in args.imgs if not is_blend(f)]
    imgs = [imgs[i] for i in range(0, len(imgs)) if i % args.interval == 0]

    generate_loop_frames(imgs, basedir, args)

    print_g("frames: {}".format(len(imgs + get_all_blends(basedir))))

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
        args.loop_effect = parse_loop_effect(args.loop_effect)
    if args.init_width is None:
        args.init_width = args.max_side
    args.max_size = parse_size_fmt(args.max_size)

def parse_loop_effect(loop_effect):
    arr = loop_effect.split(",")
    ltype, lframes, ldelay = (arr + [None]*2)[:3]

    if ltype is None or ltype == "":
        raise "Invalid first arg of -L/--loop-effect: {}".format(loop_effect)
    if lframes is not None and not re.match(r"^\d+$", lframes):
        raise "Invalid second arg of -L/--loop-effect: {}".format(loop_effect)
    if ldelay is not None and not re.match(r"^\d+$", lframes):
        raise "Invalid third arg of -L/--loop-effect: {}".format(loop_effect)

    lframes = int(lframes)
    if ldelay is not None:
        ldelay = int(ldelay)

    return ltype, lframes, ldelay

def parse_size_fmt(size):
    f = float(re.search(r"\s*[\d\.]+", size).group(0))
    unit = re.search(r"([gmk]?b)\s*$", size, re.IGNORECASE).group(1)
    return f * UNITS[unit]

def rm_blends(basedir):
    for f in get_all_blends(basedir):
        print("rm {}".format(f))
        os.remove(f)

def generate_loop_frames(imgs, basedir, args):
    if args.loop_effect is None:
        return

    ltype, lframes, _ = args.loop_effect

    if ltype == "static":
        generate_blends(imgs, basedir, lframes)
    elif ltype == "cross":
        generate_cross_blends(imgs, basedir, lframes)
    else:
        raise "Unknown loop type"

def parse_crop_width(c):
    arr = c.split("x")

    if len(arr) == 2:
        if arr[0] == "":
            return None
        else:
            return int(arr[0])

    raise """Invalid "crop" format"""


def generate_gif(imgs, width, basedir, args):
    delay = args.interval * args.delay_factor

    cmd = [
        "convert",
        "-loop", "0"
    ]

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

    blends = get_all_blends(basedir)
    if blends != []:
        _, _, ldelay = args.loop_effect
        if ldelay is not None:
            cmd += ["-delay", str(ldelay)]
        elif args.last_delay is not None:
            cmd += ["-delay", str(delay)]
        cmd += blends

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
    raise "unreachable block"

def get_sides(gif):
    cmd = ["identify", "-format", "%[fx:w]x%[fx:h],", gif]
    out = subprocess.check_output(cmd)
    return map(int, re.split(r"[x,]", out)[:2])

def get_all_blends(basedir):
    files = os.listdir(basedir)
    blends = [os.path.join(basedir, f) for f in files if is_blend(f)]
    return sorted(blends)

def is_blend(img):
    return re.search(RM_BLENDS_PATTERN, img)

def generate_blends(imgs, basedir, n):
    if n is None:
        raise "require loop effect frames"
    step = 100 / (n + 1)
    first = imgs[0]
    last  = imgs[-1]
    for i in range(0, n):
        blend(first, last, basedir, (i + 1) * step)

def generate_cross_blends(imgs, basedir, n):
    if n is None:
        raise "require loop effect frames"
    step = 100 / (n + 1)
    for i in range(0, n):
        last_i = - n + i
        first = imgs[i]
        last  = imgs[last_i]
        blend(first, last, basedir, (i + 1) * step)

        imgs[i] = None
        imgs[last_i] = None

    while imgs.count(None) != 0:
        imgs.remove(None)

def blend(img1, img2, basedir, ratio):
    out = os.path.join(basedir, GEN_BLENDS_PATTERN % int(ratio))
    cmd = [
        "composite",
        "-blend", str(ratio),
        img1, img2, out
    ]
    print("exec: {}".format(" ".join(cmd)))
    subprocess.check_call(cmd)
