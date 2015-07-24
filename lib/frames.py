import subprocess, re, os, shutil
from color import print_g
from util import find_executable

def main(args):
    v_info = get_video_info(args.video)

    print_g("DAR:   {}".format(v_info["dar"]))
    print_g("Size:  {}x{}".format(v_info["width"], v_info["height"]))
    print_g("FRate: {}".format(v_info["frame_rate"]))

    if os.path.exists(args.dist):
        shutil.rmtree(args.dist)
    os.makedirs(args.dist)

    dump_frames(args, v_info)
    open_dir(args.dist)

def get_video_info(video):
    cmd = [
        find_executable("avprobe", "ffprobe"),
        "-loglevel", "error",
        "-show_streams",
        "-show_format_entry", "width",
        "-show_format_entry", "height",
        "-show_format_entry", "display_aspect_ratio",
        "-show_format_entry", "avg_frame_rate",
        video
    ]
    print("exec: {}".format(" ".join(cmd)))
    out = subprocess.check_output(cmd, stderr=subprocess.PIPE)

    info = {}
    for line in out.split(os.linesep):
        kv = line.split("=")
        if len(kv) == 1:
            k = kv[0]
            v = None
        elif len(kv) == 2:
            k, v = kv
        else:
            raise "Invalid line format: {}".format(kv)
        if k not in info:
            info[k] = v

    info["dar"] = info.get("display_aspect_ratio")
    info["frame_rate"] = parse_frame_rate(info.get("avg_frame_rate"))

    return info

def parse_frame_rate(fr_str):
    arr = fr_str.split("/")
    if len(arr) == 1:
        return float(arr[0])
    if len(arr) == 2:
        return float(arr[0]) / float(arr[1])
    raise "Invalit frame rate format: {}".format(fr_str)

def dump_frames(args, v_info):
    if args.frame_rate is None:
        frame_rate = v_info["frame_rate"]
    else:
        frame_rate = args.frame_rate

    cmd = [
        find_executable("avconv", "ffmpeg"),
        "-loglevel", "info",
        "-r", str(frame_rate),
        "-i", args.video,
        "-filter:v", "yadif",
        "-ss", str(args.offset),
        "-t", str(args.duration)
    ]

    if args.width != 0:
        if v_info["dar"] is not None:
            src_width, src_height = v_info["dar"].split(":")
        else:
            src_width, src_height = map(v_info.get, ["width", "height"])

        src_width, src_height = map(int, [src_width, src_height])

        width = args.width
        height = (args.width * src_height) / src_width

        cmd += ["-s", "{}x{}".format(width, height)]

    cmd += ["{}/%05d.png".format(args.dist)]

    print("exec: {}".format(" ".join(cmd)))
    subprocess.check_call(cmd)

def open_dir(directory):
    cmd = [
        find_executable("xdg-open", "open"),
        directory
    ]
    print("exec: {}".format(" ".join(cmd)))
    subprocess.check_call(cmd, stderr=subprocess.PIPE)
