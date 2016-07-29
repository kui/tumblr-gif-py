import subprocess, re, os, shutil, json
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
        "-of", "json",
        "-loglevel", "error",
        "-show_streams",
        video
    ]
    print("exec: {}".format(" ".join(cmd)))
    out = subprocess.check_output(cmd, stderr=subprocess.PIPE)
    out = json.loads(out)

    for stream in out["streams"]:
        if stream["codec_type"] != "video":
            continue
        info = stream
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
        "-ss", str(args.offset),
        "-i", args.video,
        "-filter:v", "yadif",
        "-r", str(frame_rate),
        "-t", str(args.duration)
    ]

    if args.width != 0:
        if v_info["dar"] is None:
            src_width, src_height = 0, 0
        else:
            src_width, src_height = map(int, v_info["dar"].split(":"))

        if src_width == 0 or src_height == 0:
            src_width, src_height = map(int,
                                        map(v_info.get,
                                            ["width", "height"]))

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
