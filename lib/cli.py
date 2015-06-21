import sys, argparse, re
import gif, frames

def main():
    parser = build_parser()
    args = parser.parse_args()
    dump_args(args)
    args.func(args)

def build_parser():
    parser = argparse.ArgumentParser(
        description="GIF generator for tubmlr GIF specs")

    subparser = parser.add_subparsers(title="commands")
    parser_frames = subparser.add_parser("frames",
                                         help="Generate frames")
    parser_frames.set_defaults(func=frames.main)
    parser_frames.add_argument("video", metavar="FILE", type=str,
                               help="a video file")
    parser_frames.add_argument("offset", metavar="H:M:S[.s]", type=str,
                               help="a time offset")
    parser_frames.add_argument("duration", metavar="SEC", type=int,
                               help="a duration")
    parser_frames.add_argument("dist", metavar="DIST", type=str,
                               help="an frames output directory")
    parser_frames.add_argument("-w", "--width", metavar="N", type=int,
                               default=800,
                               help="a frames width or 0 for original width (default: 700)")
    parser_frames.add_argument("-r", "--frame-rate", metavar="N", type=float,
                               help="a frames rate (default: original frame rate)")

    parser_gif = subparser.add_parser("gif",
                                      help="Generate gif from frames")
    parser_gif.set_defaults(func=gif.main)
    parser_gif.add_argument("imgs", metavar="IMG", type=str, nargs="+",
                            help="image files")
    parser_gif.add_argument("gif", metavar="GIF", type=str,
                            help="a output gif")
    parser_gif.add_argument("-i", "--interval", metavar="N", type=int,
                            default=2, help="an interval of image files")
    parser_gif.add_argument("-w", "--init-width", metavar="N", type=int,
                            help="an initial gif width (default: max-side)")
    parser_gif.add_argument("-s", "--max-size", metavar="N", type=str,
                            default="2MB", help="an max gif size")
    parser_gif.add_argument("-S", "--max-side", metavar="N", type=int,
                            default=540, help="an max gif width and height")
    parser_gif.add_argument("-F", "--fuzz", metavar="N", type=float,
                            default=1.6,
                            help="see imagemagick \"-fuzz\" option")
    parser_gif.add_argument("-f", "--first-delay", metavar="N", type=int,
                            help="a delay of the farst frame")
    parser_gif.add_argument("-l", "--last-delay", metavar="N", type=int,
                            help="a delay of the last frame")
    parser_gif.add_argument("-d", "--dither", action="store_true",
                            help="remove \"+dither\" option from imagemagick \"convert\"")
    parser_gif.add_argument("-c", "--crop", metavar="WxH+X+Y",
                            help="a crop value for ImageMagick \"-crop\" option")
    parser_gif.add_argument("-L", "--loop-effect",
                            metavar="TYPE[,FRAMES[,DELAY]]", type=str,
                            help="a string to specify effect type, # of "+
                            "frames and delay. TYPE: static, cross, reverse")
    parser_gif.add_argument("-D", "--delay-factor", metavar="N", type=int, default=3,
                            help="a factor for delay. The delay of "+
                            "generated GIF is interval * delay_factor msec")
    return parser

def dump_args(args):
    for k in sorted(args.__dict__.keys(), key=lambda k: len(k)):
        if k == "func":
            continue
        elif k == "imgs":
            print("#imgs:\t{}".format(str(len(args.imgs))))
        else:
            print("{}:\t{}".format(k, str(args.__dict__[k])))
    print("----")

if __name__ == "__main__":
    main()

