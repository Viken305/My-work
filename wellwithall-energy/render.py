"""Renders the WellWithAll Energy reel.
  python3 render.py --still 2.3,7.7     # check frames -> build/stills
  python3 render.py --audio             # soundtrack only -> build/mix.wav
  python3 render.py                     # -> out/wellwithall_energy_reel.mp4 (1080x1920, 30 fps, -14 LUFS)
"""
import os, subprocess, sys
from multiprocessing import Pool

import film
from kit import FPS, H, HERE, W

BUILD, OUT = os.path.join(HERE, "build"), os.path.join(HERE, "out")


def _job(i):
    return film.draw_frame(i / FPS).tobytes()


def render_video(path):
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                           "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    n = int(round(film.DURATION * FPS))
    with Pool(os.cpu_count()) as pool:
        for k, buf in enumerate(pool.imap(_job, range(n), chunksize=4)):
            ff.stdin.write(buf)
            if k % 60 == 0:
                print(f"frame {k}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    return path


def main():
    os.makedirs(BUILD, exist_ok=True)
    if "--still" in sys.argv:
        from PIL import Image
        d = os.path.join(BUILD, "stills")
        os.makedirs(d, exist_ok=True)
        for t in sys.argv[sys.argv.index("--still") + 1].split(","):
            Image.fromarray(film.draw_frame(float(t))).save(os.path.join(d, f"t{float(t):05.2f}.png"))
        return
    import music
    wav = music.render(os.path.join(BUILD, "mix.wav"))
    if "--audio" in sys.argv:
        return
    video = render_video(os.path.join(BUILD, "video.mp4"))
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "wellwithall_energy_reel.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "256k", "-shortest", "-movflags", "+faststart", out], check=True)
    print(out)


if __name__ == "__main__":
    main()
