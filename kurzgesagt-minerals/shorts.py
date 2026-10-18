"""YouTube Shorts cut (under 3 minutes) of the vertical film.

  python3 shorts.py   -> out/short.mp4   needs out/vertical.mp4 (python3 vertical.py)

Keeps the whole story but drops three side-trips (lava -> glass, diamonds' journey up, the oldest zircon) and one pause.
Cuts sit in narration gaps, each joined with a quick dip (0.3 s fade out/in).
"""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KEEP = [(0.0, 38.4), (40.0, 66.2), (76.5, 135.8), (146.5, 178.5), (199.0, 218.0)]
XF = 0.3

if __name__ == "__main__":
    src = os.path.join(HERE, "out", "vertical.mp4")
    dst = os.path.join(HERE, "out", "short.mp4")
    tmp = os.path.join(HERE, "build", "short")
    os.makedirs(tmp, exist_ok=True)
    lst, total = os.path.join(tmp, "list.txt"), 0.0
    with open(lst, "w") as f:
        for i, (a, b) in enumerate(KEEP):
            seg = os.path.join(tmp, f"seg{i}.mp4")
            d = b - a
            vf = f"fade=t=in:st=0:d={XF}:color=black" if i else "null"
            vf += f",fade=t=out:st={d - XF}:d={XF}:color=black" if i < len(KEEP) - 1 else ""
            af = f"afade=t=in:st=0:d={XF},afade=t=out:st={d - XF}:d={XF}"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-t", str(d), "-i", src, "-vf", vf, "-af", af,
                            "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
                            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", seg], check=True)
            f.write(f"file '{seg}'\n")
            total += d
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", dst], check=True)
    print(dst, f"{total:.1f}s")
