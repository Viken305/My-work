"""Studio 'food commercial' renderer, built on gl3d's geometry and post: image-based studio reflections
(procedural softboxes), Fresnel, roughness, metals, light passing through thin food (translucency),
one shadowed key light plus up to 6 point lights (rims, kickers, flames).

Geo channel use in this renderer:
  C   base colour (linear)      E  emission strength      S  specular amount (0..1)
  Ht  roughness (0 glossy .. 1 matte, per vertex)
  M   metallic 0..1;  a NEGATIVE M means translucency (-M), for popcorn, butter, starch gel
  A   alpha (transparent pass only)
"""
import math
import os
import sys

import cv2
import moderngl
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "style-tests"))
from gl3d import (ATTRS, FMT, VS, VS_SHADOW, FS_SHADOW, Geo, Rx, Ry, Rz, S, T, bloom, box, cat, cylinder,  # noqa: E402,F401
                  depth_of_field, flat_normals, look_at, ortho, perspective, quad, quads_to_tris, sphere, srgb, tonemap,
                  torus, vignette)

FS = """
#version 330
uniform sampler2D shadow_map;
uniform vec3 key_dir; uniform vec3 key_col; uniform vec3 cam_pos;
uniform vec3 env_key_dir; uniform vec3 env_key_col; uniform vec3 env_rim_dir; uniform vec3 env_rim_col;
uniform vec3 env_amb; uniform vec3 env_floor;
uniform int n_lights; uniform vec4 l_pos[6]; uniform vec3 l_col[6];
in vec3 v_pos; in vec3 v_nrm; in vec3 v_col; in float v_emit; in float v_spec; in float v_heat; in float v_alpha; in vec4 v_lpos; in float v_mask;
out vec4 f_color;

float shadow(float bias) {
    vec3 p = v_lpos.xyz / v_lpos.w * 0.5 + 0.5;
    if (p.x < 0.0 || p.x > 1.0 || p.y < 0.0 || p.y > 1.0 || p.z > 1.0) return 1.0;
    vec2 ts = 1.0 / vec2(textureSize(shadow_map, 0));
    float s = 0.0;
    for (int i = -2; i <= 2; i++) for (int j = -2; j <= 2; j++) {
        float d = texture(shadow_map, p.xy + vec2(i, j) * ts * 1.5).r;
        s += (p.z - bias > d) ? 0.0 : 1.0;
    }
    return s / 25.0;
}

// the studio, as seen in reflections: a big warm softbox, a hard cool strip, a dim ceiling and a dark floor
vec3 env(vec3 d, float rough) {
    float w = 0.02 + rough * 0.35;
    vec3 c = env_amb * (0.35 + 0.65 * max(d.y, 0.0)) + env_floor * max(-d.y, 0.0);
    float k = dot(d, normalize(env_key_dir));
    c += env_key_col * smoothstep(0.80 - w, 0.86 + w * 0.3, k) / (1.0 + rough * 3.0);
    float r = dot(d, normalize(env_rim_dir));
    c += env_rim_col * smoothstep(0.93 - w, 0.97, r) / (1.0 + rough * 4.0);
    return c;
}

void main() {
    vec3 n = normalize(v_nrm);
    vec3 V = normalize(cam_pos - v_pos);
    if (!gl_FrontFacing && dot(n, V) < 0.0) n = -n;
    float rough = clamp(v_heat, 0.02, 1.0);
    float metal = clamp(v_mask, 0.0, 1.0);
    float trans = clamp(-v_mask, 0.0, 1.0);
    vec3 L = -normalize(key_dir);
    float ndl_raw = dot(n, L);
    float ndl = max(ndl_raw, 0.0);
    float sh = shadow(0.0015 + 0.005 * (1.0 - ndl));
    float ndv = max(dot(n, V), 0.0);
    vec3 F0 = mix(vec3(0.04), v_col, metal);
    vec3 F = F0 + (1.0 - F0) * pow(1.0 - ndv, 5.0) * (1.0 - rough * 0.7);
    vec3 diff_col = v_col * (1.0 - metal);
    // key light: wrapped diffuse (soft food look) + glossy highlight
    float wrap = max((ndl_raw + 0.25) / 1.25, 0.0);
    vec3 col = diff_col * key_col * wrap * sh;
    vec3 H = normalize(L + V);
    float shin = mix(400.0, 12.0, rough);
    col += key_col * F * pow(max(dot(n, H), 0.0), shin) * (shin + 8.0) / 60.0 * v_spec * sh;
    // light coming through thin food (backlit popcorn glows)
    float back = pow(max(dot(V, -L), 0.0), 2.0) * (0.4 + 0.6 * (1.0 - ndv));
    col += v_col * key_col * trans * (back * 0.45 + max(-ndl_raw, 0.0) * 0.15);
    // studio reflections + ambient
    vec3 R = reflect(-V, n);
    col += diff_col * (env(n, 1.0) * 0.6 + env_amb * 0.4);
    col += env(R, rough) * F * v_spec * 1.6;
    for (int i = 0; i < n_lights; i++) {
        vec3 d = l_pos[i].xyz - v_pos;
        float dist = length(d);
        vec3 Lp = d / dist;
        float att = 1.0 / (1.0 + dist * dist / (l_pos[i].w * l_pos[i].w));
        float nl = dot(n, Lp);
        col += diff_col * l_col[i] * max((nl + 0.2) / 1.2, 0.0) * att;
        col += l_col[i] * F * pow(max(dot(n, normalize(Lp + V)), 0.0), shin * 0.6) * v_spec * att * 2.0;
        col += v_col * l_col[i] * trans * pow(max(dot(V, -Lp), 0.0), 2.0) * att * 0.4;
    }
    col += v_col * v_emit;
    f_color = vec4(col, v_alpha);
}
"""


class Lux:
    def __init__(self, w, h, ss=2.0, shadow_size=2048):
        self.w, self.h, self.ss = w, h, ss
        self.rw, self.rh = int(w * ss), int(h * ss)
        self.ctx = moderngl.create_standalone_context(backend="egl")
        ctx = self.ctx
        self.prog = ctx.program(vertex_shader=VS, fragment_shader=FS)
        self.sprog = ctx.program(vertex_shader=VS_SHADOW, fragment_shader=FS_SHADOW)
        self.color = ctx.texture((self.rw, self.rh), 4, dtype="f4")
        self.depth = ctx.depth_texture((self.rw, self.rh))
        self.fbo = ctx.framebuffer([self.color], self.depth)
        self.smap = ctx.depth_texture((shadow_size, shadow_size))
        self.smap.compare_func = ""
        self.smap.repeat_x = self.smap.repeat_y = False
        self.sfbo = ctx.framebuffer(depth_attachment=self.smap)
        self.clear_col = (0.0, 0.0, 0.0)

    def _vao(self, data, shadow=False):
        buf = self.ctx.buffer(data.astype(np.float32).tobytes())
        if shadow:
            return self.ctx.vertex_array(self.sprog, [(buf, "3f 44x", "in_pos")]), buf
        return self.ctx.vertex_array(self.prog, [(buf, FMT, *ATTRS)]), buf

    def render(self, cam, light, opaque, trans=None, lights=()):
        """cam: dict(eye, target, fov, roll, near, far). light: dict(dir, col, center, extent, env...)."""
        ctx = self.ctx
        made = []

        def mk(g, shadow=False):
            if g is None or not len(g):
                return None
            v = self._vao(g.vbo(), shadow)
            made.append(v)
            return v[0]
        o_main, o_sh = mk(opaque), mk(opaque, True)
        t_main = mk(trans)
        sd = np.asarray(light["dir"], np.float64)
        sd /= np.linalg.norm(sd)
        c = np.asarray(light["center"], np.float64)
        ext = light["extent"]
        dist = light.get("dist", 40.0)
        lv = look_at(c - sd * dist, c, up=(0, 0, 1) if abs(sd[1]) > 0.95 else (0, 1, 0))
        lvp = ortho(-ext, ext, -ext, ext, 0.1, dist * 2.2) @ lv
        self.sfbo.use()
        self.sfbo.clear(depth=1.0)
        ctx.enable(moderngl.DEPTH_TEST)
        ctx.disable(moderngl.BLEND)
        ctx.disable(moderngl.CULL_FACE)
        self.sprog["light_vp"].write(lvp.T.copy().tobytes())
        if o_sh:
            o_sh.render()
        aspect = self.rw / self.rh
        view = look_at(cam["eye"], cam["target"], roll=cam.get("roll", 0.0))
        near, far = cam.get("near", 0.05), cam.get("far", 200.0)
        proj = perspective(math.radians(cam["fov"]), aspect, near, far)
        p = self.prog
        p["vp"].write((proj @ view).T.copy().tobytes())
        p["light_vp"].write(lvp.T.copy().tobytes())
        p["key_dir"].value = tuple(sd)
        p["key_col"].value = tuple(light["col"])
        p["cam_pos"].value = tuple(float(v) for v in cam["eye"])
        for k in ("env_key_dir", "env_key_col", "env_rim_dir", "env_rim_col", "env_amb", "env_floor"):
            p[k].value = tuple(float(v) for v in light[k])
        n = min(6, len(lights))
        p["n_lights"].value = n
        lp = np.zeros((6, 4), np.float32)
        lc = np.zeros((6, 3), np.float32)
        for i, (pos, rad, colr) in enumerate(list(lights)[:6]):
            lp[i] = (*pos, rad)
            lc[i] = colr
        p["l_pos"].write(lp.tobytes())
        p["l_col"].write(lc.tobytes())
        self.smap.use(0)
        p["shadow_map"].value = 0
        self.fbo.use()
        self.fbo.clear(*self.clear_col, 1.0, depth=1.0)
        if o_main:
            o_main.render()
        if t_main:
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
            self.fbo.depth_mask = False
            t_main.render()
            self.fbo.depth_mask = True
            ctx.disable(moderngl.BLEND)
        img = np.frombuffer(self.color.read(), np.float32).reshape(self.rh, self.rw, 4)[::-1, :, :3].copy()
        d = np.frombuffer(self.depth.read(), np.float32).reshape(self.rh, self.rw)[::-1]
        lin = (2 * near * far) / (far + near - (d * 2 - 1) * (far - near))
        for vao, buf in made:
            vao.release()
            buf.release()
        return img, lin, (proj @ view)


def project(VP, pts, w, h):
    """World points -> pixel coords (x right, y down) for overlays."""
    P = np.asarray(pts, np.float64).reshape(-1, 3)
    q = np.c_[P, np.ones(len(P))] @ VP.T
    q = q[:, :3] / q[:, 3:4]
    return np.stack([(q[:, 0] * 0.5 + 0.5) * w, (1 - (q[:, 1] * 0.5 + 0.5)) * h], 1), q[:, 2]


# ---------------------------------------------------------------- grading
_GRAIN = {}


def grade(img, t, grain=0.012):
    """Food-commercial grade on a display-referred image: warm highlights, deep but not crushed shadows, fine grain."""
    lum = img @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    sh = np.clip(1 - lum / 0.35, 0, 1)[..., None]
    hi = np.clip((lum - 0.55) / 0.45, 0, 1)[..., None]
    out = img + sh * np.array([-0.004, 0.0, 0.012], np.float32) * 1.0 + hi * np.array([0.03, 0.012, -0.03], np.float32)
    out = np.clip(out, 0, 1)
    out = out * out * (3 - 2 * out) * 0.25 + out * 0.75  # gentle S-curve
    if grain > 0:
        h, w = img.shape[:2]
        key = (h, w)
        if key not in _GRAIN:
            r = np.random.default_rng(3)
            _GRAIN[key] = [cv2.GaussianBlur(r.standard_normal((h, w)).astype(np.float32), (0, 0), 0.7) for _ in range(6)]
        g = _GRAIN[key][int(t * 24) % 6]
        out = out + g[..., None] * grain * (0.6 + 0.4 * (1 - lum[..., None]))
    return np.clip(out, 0, 1)


# ---------------------------------------------------------------- geometry helpers
def lathe(profile, n=64, rgb=(200, 200, 200), smooth=True, **kw):
    """Revolve a profile [(r, y), ...] (listed bottom to top, outside first) around the y axis."""
    pr = np.asarray(profile, np.float64)
    a = np.linspace(0, 2 * np.pi, n + 1)
    # per-vertex profile normals from neighbours
    d = np.gradient(pr, axis=0)
    pn = np.stack([d[:, 1], -d[:, 0]], 1)
    pn /= np.maximum(np.linalg.norm(pn, axis=1, keepdims=True), 1e-9)
    tris, nrm = [], []
    for i in range(n):
        c0, s0, c1, s1 = math.cos(a[i]), math.sin(a[i]), math.cos(a[i + 1]), math.sin(a[i + 1])
        for j in range(len(pr) - 1):
            (r0, y0), (r1, y1) = pr[j], pr[j + 1]
            A = (r0 * c0, y0, r0 * s0)
            B = (r0 * c1, y0, r0 * s1)
            C = (r1 * c1, y1, r1 * s1)
            D = (r1 * c0, y1, r1 * s0)
            nA = (pn[j][0] * c0, pn[j][1], pn[j][0] * s0)
            nB = (pn[j][0] * c1, pn[j][1], pn[j][0] * s1)
            nC = (pn[j + 1][0] * c1, pn[j + 1][1], pn[j + 1][0] * s1)
            nD = (pn[j + 1][0] * c0, pn[j + 1][1], pn[j + 1][0] * s0)
            tris += [[A, C, B], [A, D, C]]
            nrm += [[nA, nC, nB], [nA, nD, nC]]
    P = np.array(tris, np.float32)
    N = np.array(nrm, np.float32) if smooth else flat_normals(P)
    return Geo(P, N, srgb(rgb), **kw)


def star_mesh(rfun, n=40, m=24, cfun=None, **kw):
    """A closed star-shaped surface r(direction); normals from finite differences. cfun(dirs) -> colours per face."""
    th = np.linspace(0, np.pi, m + 1)
    ph = np.linspace(0, 2 * np.pi, n + 1)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    D = np.stack([np.sin(TH) * np.cos(PH), np.cos(TH), np.sin(TH) * np.sin(PH)], -1)
    Rr = rfun(D.reshape(-1, 3)).reshape(D.shape[:2])
    X = D * Rr[..., None]
    # normals: cross of parametric derivatives (fall back to radial at poles)
    dth = np.gradient(X, axis=0)
    dph = np.gradient(X, axis=1)
    N = np.cross(dph, dth)
    bad = np.linalg.norm(N, axis=-1) < 1e-9
    N[bad] = D[bad]
    N /= np.maximum(np.linalg.norm(N, axis=-1, keepdims=True), 1e-9)
    flip = (N * D).sum(-1) < 0
    N[flip] *= -1
    tris, nr, dirs = [], [], []
    for i in range(m):
        for j in range(n):
            a, b, c, d = (i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j)
            if i > 0:
                tris.append([X[a], X[c], X[b]]); nr.append([N[a], N[c], N[b]]); dirs.append(D[a])
            if i < m - 1:
                tris.append([X[a], X[d], X[c]]); nr.append([N[a], N[d], N[c]]); dirs.append(D[a])
    P = np.array(tris, np.float32)
    C = cfun(np.array(dirs)) if cfun else kw.pop("rgb", (0.8, 0.8, 0.8))
    return Geo(P, np.array(nr, np.float32), C, **kw)


def rough(g, r):
    """Set roughness on a Geo (stored in the per-vertex Ht channel)."""
    g.Ht = np.full_like(g.Ht, r)
    return g
