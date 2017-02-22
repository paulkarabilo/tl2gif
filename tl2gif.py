import json, sys, base64
import PIL
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import argparse
from os import path

class Frame:
    def __init__(self, base64, ts, i):
        self.base64 = base64
        self.ts = ts
        self.index = i

class FrameBuffer:
    def __init__(self, frames):
        self.frames = map(lambda (i, frame): Frame(frame[0], frame[1], i), enumerate(frames))
        self.start_ts = self.frames[0].ts
        self.end_ts = self.frames[-1].ts

    def at(self, time, start=0):
        ts = self.start_ts + time
        for f in range(start, len(self.frames) - 1):
            if self.frames[f].ts <= ts and self.frames[f + 1].ts > ts:
                return self.frames[f]
        return None

    def sequence(self, interval):
        time = 0
        frame = self.at(time)
        seq = []
        while frame != None:
            im = Image.open(BytesIO(base64.b64decode(frame.base64)))
            dr = ImageDraw.Draw(im)
            font = ImageFont.truetype("font.ttf", 24)
            dr.rectangle([0, 0, 60, 30], (255, 255, 255))
            dr.text((0,0), "{} s".format(float(time) / 1000000.0), (0,0,0), font=font)
            del dr
            seq.append(im)
            time += interval
            frame = self.at(time, frame.index)
        return seq

    def image(self, interval, output):
        images = self.sequence(interval * 1000)
        images[0].save(output, save_all=True, append_images=images[1:], duration=interval*2)


def main(args):
    with open(path.abspath(args.input)) as file:
        data = json.load(file)
    frames = FrameBuffer([(d["args"]["snapshot"], d["ts"]) for d in data if d["name"] == "Screenshot"])
    frames.image(args.step, args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert Chrome Dev Tools timeline frames to gif animation')
    parser.add_argument('-i', dest='input', type=str, required=True,
        help='Timeline JSON input file')
    parser.add_argument('-o', dest='output', type=str, required=False,
        default='out.gif', help='Path to output gif image')
    parser.add_argument('-s', dest='step', type=int, required=False,
        default=100, help='time interval between frames, in ms')
    parser.add_argument('-f', dest='font', type=int, required=False,
        default=100, help='time interval between frames, in ms')
    parser.add_argument('-fs', dest='fontsize', type=int, required=False,
        default=100, help='time interval between frames, in ms')
    main(parser.parse_args())