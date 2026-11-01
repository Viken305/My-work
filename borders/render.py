"""Render the 3D globe version of "Why Borders Are Shaped the Way They Are".

  python3 render.py --still 3,10.5,40     -> build/stills/tXXX.XX.png
  python3 render.py sheet 1,5,9,...       -> build/sheet3d.png
  python3 render.py full                  -> out/full.mp4 + out/full_share.mp4
"""
import os, subprocess, sys
from multiprocessing import Pool

from PIL import Image

import film3d as F
import sound

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD, OUT = os.path.join(HERE, "build"), os.path.join(HERE, "out")


def _job(i):
    return F.frame(i / F.FPS).tobytes()


def render_video(path):
    F.setup()
    n = int(round(F.TOTAL * F.FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{F.W}x{F.H}", "-r", str(F.FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for i, b in enumerate(pool.imap(_job, range(n), chunksize=3)):
            p.stdin.write(b)
            if i % 300 == 0:
                print(f"  frame {i}/{n}", flush=True)
    p.stdin.close()
    p.wait()


def _still(t):
    return F.frame(t)


def main(argv):
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    F.setup()
    if argv and argv[0] == "--still":
        d = os.path.join(BUILD, "stills")
        os.makedirs(d, exist_ok=True)
        ts = [float(x) for x in argv[1].split(",")]
        with Pool(os.cpu_count()) as pool:
            ims = pool.map(_still, ts)
        for t, im in zip(ts, ims):
            Image.fromarray(im).save(os.path.join(d, f"t{t:06.2f}.png"))
        print(d)
    elif argv and argv[0] == "sheet":
        ts = [float(x) for x in argv[1].split(",")]
        with Pool(os.cpu_count()) as pool:
            ims = pool.map(_still, ts)
        cols = 6
        rows = (len(ts) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 300, rows * 533), (0, 0, 0))
        for i, im in enumerate(ims):
            sheet.paste(Image.fromarray(im).resize((300, 533), Image.LANCZOS), ((i % cols) * 300, (i // cols) * 533))
        out = os.path.join(BUILD, argv[2] if len(argv) > 2 else "sheet3d.png")
        sheet.save(out)
        print(out)
    elif argv and argv[0] == "full":
        import audio
        video = os.path.join(BUILD, "full_video.mp4")
        if "--audio-only" not in argv:
            render_video(video)
        wav = os.path.join(BUILD, "full_mix.wav")
        audio.render_mix(wav, F.TOTAL, sound.vo_clips(), sound.sfx_events(), sound.music())
        master = os.path.join(OUT, "full.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                        "-shortest", master], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", master, "-c:v", "libx264", "-preset", "slow", "-crf", "23",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", os.path.join(OUT, "full_share.mp4")], check=True)
        print(master, f"{F.TOTAL:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1:])
