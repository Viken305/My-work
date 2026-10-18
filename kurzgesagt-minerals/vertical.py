"""9:16 vertical version (Shorts / Reels / TikTok) of the finished film.

  python3 vertical.py            -> out/vertical.mp4 (1080x1920)   needs out/full.mp4 (python3 render.py full)

Layout: the full 16:9 film sits in the middle (nothing is cropped, so labels and chapter badges stay visible);
a blurred, zoomed copy of the same frame fills the background; a title sits on top; big word-by-word captions,
generated from the narration timing, sit underneath.
"""
import importlib, json, os, subprocess

from render import PARTS
from script import PARTS as LINES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
VW, VH = 1080, 1920
PANEL_Y = 600                    # top of the 16:9 panel (1080x608)
TITLE = ("HOW THE EARTH", "MAKES CRYSTALS")
GOLD, WHITE = "&H0078D6FF", "&H00FFFFFF"   # ASS colours are &HAABBGGRR


def ts(t):
    h, r = divmod(max(0.0, t), 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def words_with_times():
    """[(start, end, word)] for the whole film: part offsets + line starts + words spread by character position."""
    out, offset = [], 0.0
    for name in PARTS:
        mod = importlib.import_module(name)
        dur = json.load(open(os.path.join(HERE, "build", name, "vo", "durations.json")))
        for key, line in LINES[name]:
            t0, d = offset + mod.VO[key], dur[key]
            ws = line.split()
            total = sum(len(w) + 1 for w in ws)
            pos = 0
            for w in ws:
                a = t0 + 0.08 + pos / total * (d - 0.15)
                pos += len(w) + 1
                b = t0 + 0.08 + pos / total * (d - 0.15)
                out.append((a, b, w))
        offset += mod.DURATION
    return out


def chunks(words, max_words=4, max_chars=22):
    """Group words into short caption chunks, breaking at punctuation and long gaps."""
    cur, res = [], []
    for i, (a, b, w) in enumerate(words):
        if cur and (len(cur) >= max_words or sum(len(x[2]) + 1 for x in cur) + len(w) > max_chars or a - cur[-1][1] > 0.6):
            res.append(cur)
            cur = []
        cur.append((a, b, w))
        if w[-1] in ".,?!:;":
            res.append(cur)
            cur = []
    if cur:
        res.append(cur)
    return res


def write_ass(path):
    words = words_with_times()
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {VW}
PlayResY: {VH}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat ExtraBold,78,{WHITE},{WHITE},&H00301018,&H90000000,1,0,0,0,100,100,1,0,1,7,3,5,60,60,0,1
Style: Title,Montserrat ExtraBold,62,{WHITE},{WHITE},&H00301018,&H90000000,1,0,0,0,100,100,6,0,1,5,2,5,40,40,0,1
Style: TitleGold,Montserrat ExtraBold,86,{GOLD},{GOLD},&H00301018,&H90000000,1,0,0,0,100,100,6,0,1,6,2,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    end = words[-1][1] + 3
    ev.append(f"Dialogue: 0,{ts(0)},{ts(end)},Title,,0,0,0,,{{\\pos({VW // 2},300)\\fad(600,0)}}{TITLE[0]}")
    ev.append(f"Dialogue: 0,{ts(0)},{ts(end)},TitleGold,,0,0,0,,{{\\pos({VW // 2},395)\\fad(600,0)}}{TITLE[1]}")
    cy = PANEL_Y + 608 + 300
    chs = chunks(words)
    for ci, ch in enumerate(chs):
        c_end = ch[-1][1] + 0.25
        if ci + 1 < len(chs):
            c_end = min(c_end, chs[ci + 1][0][0])
        for i, (a, b, w) in enumerate(ch):
            nxt = ch[i + 1][0] if i + 1 < len(ch) else c_end
            parts = []
            for j, (_, _, ww) in enumerate(ch):
                ww = ww.upper()
                parts.append(f"{{\\c{GOLD}\\fscx108\\fscy108}}{ww}{{\\c{WHITE}\\fscx100\\fscy100}}" if j == i else ww)
            pop = "\\fscx92\\fscy92\\t(0,90,\\fscx100\\fscy100)" if i == 0 else ""
            ev.append(f"Dialogue: 1,{ts(a)},{ts(nxt)},Cap,,0,0,0,,{{\\pos({VW // 2},{cy}){pop}}}" + " ".join(parts))
    open(path, "w").write(head + "\n".join(ev) + "\n")


def main():
    src = os.path.join(OUT, "full.mp4")
    ass = os.path.join(HERE, "build", "vertical.ass")
    os.makedirs(os.path.dirname(ass), exist_ok=True)
    write_ass(ass)
    fonts = os.path.join(HERE, "fonts")
    fg = ("[0:v]split=2[a][b];"
          f"[a]scale=-2:{VH},crop={VW}:{VH},gblur=sigma=38,eq=brightness=-0.22:saturation=1.15[bg];"
          f"[b]scale={VW}:-2[fg];"
          f"[bg][fg]overlay=0:{PANEL_Y},"
          f"drawbox=x=0:y={PANEL_Y - 3}:w={VW}:h=3:color=white@0.35:t=fill,"
          f"drawbox=x=0:y={PANEL_Y + 608}:w={VW}:h=3:color=white@0.35:t=fill,"
          f"subtitles={ass}:fontsdir={fonts}[v]")
    dst = os.path.join(OUT, "vertical.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", fg, "-map", "[v]", "-map", "0:a",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", dst], check=True)
    print(dst)


if __name__ == "__main__":
    main()
