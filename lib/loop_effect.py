import os, re, subprocess

GEN_BLENDS_PATTERN = "__blended-%03d.png"
RM_BLENDS_PATTERN = r"__blended-\d+.png$"

class CrossFadeLoop:
    def __init__(self, n_frames, delay):
        self.n_frames = n_frames
        self.delay = delay

    def generate(self, imgs, basedir):
        step = 100 / (self.n_frames + 1)
        self.imgs = []
        for i in range(0, self.n_frames):
            last_i = - self.n_frames + i

            first = imgs[i]
            last  = imgs[last_i]
            b = blend(first, last, basedir, (i + 1) * step)
            self.imgs.append(b)

            imgs[i] = None
            imgs[last_i] = None

        while imgs.count(None) != 0:
            imgs.remove(None)

    def get_convert_args_fragments(self):
        return ["-delay", str(self.delay)] + self.imgs

class StaticFadeLoop:
    def __init__(self, n_frames, delay):
        self.n_frames = n_frames
        self.delay = delay

    def generate(self, imgs, basedir):
        step = 100 / (self.n_frames + 1)
        first = imgs[0]
        last  = imgs[-1]
        self.imgs = []
        for i in range(0, self.n_frames):
            b = blend(first, last, basedir, (i + 1) * step)
            self.imgs.append(b)

    def get_convert_args_fragments(self):
        return ["-delay", str(self.delay)] + self.imgs

class ReverseLoop:
    def __init__(self, delay):
        self.delay = delay

    def generate(self, imgs, basedir):
        self.imgs = [imgs[i - 1] for i in range(len(imgs), 0, -1)]

    def get_convert_args_fragments(self):
        return ["-delay", str(self.delay)] + self.imgs

def parse_loop_effect(loop_effect, default_delay):
    arr = loop_effect.split(",")
    ltype, lframes, ldelay = (arr + [None] * 2)[:3]

    if ltype is None or ltype == "":
        raise "Invalid first arg of -L/--loop-effect: {}".format(loop_effect)
    if lframes is not None and not re.match(r"^\d+$", lframes):
        raise "Invalid second arg of -L/--loop-effect: {}".format(loop_effect)
    if ldelay is not None and not re.match(r"^\d+$", lframes):
        raise "Invalid third arg of -L/--loop-effect: {}".format(loop_effect)

    if lframes is not None:
        lframes = int(lframes)

    if ldelay is None:
        ldelay = default_delay
    else:
        ldelay = int(ldelay)

    if ltype == "static":
        return StaticFadeLoop(lframes, ldelay)
    if ltype == "cross":
        return CrossFadeLoop(lframes, ldelay)
    if ltype == "reverse":
        return ReverseLoop(ldelay)

    raise "Unknown loop effect TYPE"

def delete_blends(basedir):
    for f in get_all_blends(basedir):
        print("delete {}".format(f))
        os.remove(f)

def get_all_blends(basedir):
    files = os.listdir(basedir)
    blends = [os.path.join(basedir, f) for f in files if is_blend(f)]
    return sorted(blends)

def is_blend(img):
    return re.search(RM_BLENDS_PATTERN, img)

def blend(img1, img2, basedir, ratio):
    out = os.path.join(basedir, GEN_BLENDS_PATTERN % int(ratio))
    cmd = [
        "composite",
        "-blend", str(ratio),
        img1, img2, out
    ]
    print("exec: {}".format(" ".join(cmd)))
    subprocess.check_call(cmd)
    return out
