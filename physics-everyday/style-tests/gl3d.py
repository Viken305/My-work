"""Small OpenGL 3D renderer for code-made films (headless, moderngl on EGL; runs on CPU via llvmpipe).

Geometry is built in Python as triangle soups (Geo). Each frame: sun shadow map -> opaque pass -> transparent pass,
rendered supersampled into a float buffer. Post (numpy/OpenCV): depth of field from the depth buffer, bloom,
filmic tone map, vignette. Motion blur = averaging sub-frames in linear light.
"""
import math

import cv2
import moderngl
import numpy as np

STRIDE = 14  # pos3 nrm3 col3 emit spec heat alpha thermal-mask


def srgb(c):
    c = np.asarray(c, dtype=np.float32) / (255.0 if max(c) > 1.0 else 1.0)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- geometry
class Geo:
    """Triangle soup. P, N: (n, 3, 3). C: (n, 3) linear rgb. E, S, A: (n,). Ht: (n, 3) per-vertex heat 0..1."""

    def __init__(self, P, N, C, E=0.0, S=0.0, A=1.0, Ht=0.0, M=0.0):
        n = len(P)
        self.P = np.asarray(P, np.float32).reshape(n, 3, 3)
        self.N = np.asarray(N, np.float32).reshape(n, 3, 3)
        self.C = np.broadcast_to(np.asarray(C, np.float32), (n, 3)).copy()
        self.E = np.broadcast_to(np.asarray(E, np.float32), (n,)).copy()
        self.S = np.broadcast_to(np.asarray(S, np.float32), (n,)).copy()
        self.A = np.broadcast_to(np.asarray(A, np.float32), (n,)).copy()
        Ht = np.asarray(Ht, np.float32)
        self.Ht = np.broadcast_to(Ht[:, None] if Ht.ndim == 1 else Ht, (n, 3)).copy()
        self.M = np.broadcast_to(np.asarray(M, np.float32), (n,)).copy()

    def __len__(self):
        return len(self.P)

    def xf(self, M):
        M = np.asarray(M, np.float32)
        R, t = M[:3, :3], M[:3, 3]
        self.P = self.P @ R.T + t
        Nm = np.linalg.inv(R).T
        N = self.N @ Nm.T
        self.N = N / np.maximum(np.linalg.norm(N, axis=-1, keepdims=True), 1e-8)
        return self

    def set(self, **kw):
        for k, v in kw.items():
            cur = getattr(self, k)
            setattr(self, k, np.broadcast_to(np.asarray(v, np.float32), cur.shape).copy())
        return self

    def heat_from(self, fn):
        """Per-vertex heat from a function of world position (arrays x, y, z)."""
        P = self.P.reshape(-1, 3)
        self.Ht = np.asarray(fn(P[:, 0], P[:, 1], P[:, 2]), np.float32).reshape(-1, 3)
        return self

    def vbo(self):
        n = len(self)
        out = np.empty((n, 3, STRIDE), np.float32)
        out[:, :, 0:3] = self.P
        out[:, :, 3:6] = self.N
        out[:, :, 6:9] = self.C[:, None, :]
        out[:, :, 9] = self.E[:, None]
        out[:, :, 10] = self.S[:, None]
        out[:, :, 11] = self.Ht
        out[:, :, 12] = self.A[:, None]
        out[:, :, 13] = self.M[:, None]
        return out.reshape(-1)


def cat(geos):
    geos = [g for g in geos if g is not None and len(g)]
    if not geos:
        return None
    g = Geo.__new__(Geo)
    for k in ("P", "N", "C", "E", "S", "A", "Ht", "M"):
        setattr(g, k, np.concatenate([getattr(x, k) for x in geos]))
    return g


def flat_normals(P):
    n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)
    return np.repeat(n[:, None, :], 3, axis=1)


def jitter_cols(n, rgb, amt, seed):
    r = np.random.default_rng(seed)
    base = srgb(rgb)
    return np.clip(base[None, :] * (1 + r.uniform(-amt, amt, (n, 1))), 0, 4)


def quads_to_tris(Q):
    Q = np.asarray(Q, np.float32)
    return np.concatenate([Q[:, [0, 1, 2]], Q[:, [0, 2, 3]]])


def box(x0, x1, y0, y1, z0, z1, rgb, jit=0.03, seed=0, **kw):
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], np.float32)
    faces = [(4, 5, 6, 7), (1, 0, 3, 2), (5, 1, 2, 6), (0, 4, 7, 3), (3, 7, 6, 2), (0, 1, 5, 4)]  # ccw outward
    Q = np.array([[v[i] for i in f] for f in faces])
    P = quads_to_tris(Q)
    C = np.repeat(jitter_cols(6, rgb, jit, seed), 1, axis=0)
    C = np.concatenate([C, C])
    return Geo(P, flat_normals(P), C, **kw)


def cylinder(r, y0, y1, n=24, rgb=(200, 200, 200), r_top=None, smooth=True, caps=(True, True), jit=0.0, seed=0, **kw):
    r_top = r if r_top is None else r_top
    a = np.linspace(0, 2 * np.pi, n + 1)
    tris, nrm = [], []
    slope = (r - r_top) / max(y1 - y0, 1e-6)
    for i in range(n):
        a0, a1 = a[i], a[i + 1]
        b0 = np.array([r * math.cos(a0), y0, r * math.sin(a0)])
        b1 = np.array([r * math.cos(a1), y0, r * math.sin(a1)])
        t0 = np.array([r_top * math.cos(a0), y1, r_top * math.sin(a0)])
        t1 = np.array([r_top * math.cos(a1), y1, r_top * math.sin(a1)])
        n0 = np.array([math.cos(a0), slope, math.sin(a0)])
        n1 = np.array([math.cos(a1), slope, math.sin(a1)])
        if not smooth:
            am = (a0 + a1) / 2
            n0 = n1 = np.array([math.cos(am), slope, math.sin(am)])
        tris += [[b0, t1, b1], [b0, t0, t1]]
        nrm += [[n0, n1, n1], [n0, n0, n1]]
        if caps[1] and r_top > 0:
            tris.append([[0, y1, 0], t1, t0])
            nrm.append([[0, 1, 0]] * 3)
        if caps[0]:
            tris.append([[0, y0, 0], b0, b1])
            nrm.append([[0, -1, 0]] * 3)
    P = np.array(tris, np.float32)
    N = np.array(nrm, np.float32)
    N /= np.linalg.norm(N, axis=-1, keepdims=True)
    return Geo(P, N, jitter_cols(len(P), rgb, jit, seed), **kw)


def sphere(r, n=18, m=12, rgb=(200, 200, 200), smooth=True, jit=0.0, seed=0, **kw):
    tris = []
    for j in range(m):
        v0, v1 = math.pi * j / m, math.pi * (j + 1) / m
        for i in range(n):
            u0, u1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            p = lambda u, v: [math.sin(v) * math.cos(u), math.cos(v), math.sin(v) * math.sin(u)]  # noqa: E731
            a, b, c, d = p(u0, v0), p(u1, v0), p(u1, v1), p(u0, v1)
            if j > 0:
                tris.append([a, b, c])
            if j < m - 1:
                tris.append([a, c, d])
    U = np.array(tris, np.float32)
    P = U * r
    N = U if smooth else flat_normals(P)
    return Geo(P, N, jitter_cols(len(P), rgb, jit, seed), **kw)


def torus(R, r, n=20, m=10, arc=2 * math.pi, rgb=(200, 200, 200), **kw):
    """Ring in the XY plane around the origin."""
    tris, nrm = [], []
    for i in range(n):
        u0, u1 = arc * i / n, arc * (i + 1) / n
        for j in range(m):
            v0, v1 = 2 * math.pi * j / m, 2 * math.pi * (j + 1) / m
            def pt(u, v):
                c = np.array([math.cos(u), math.sin(u), 0])
                nn = c * math.cos(v) + np.array([0, 0, 1]) * math.sin(v)
                return c * R + nn * r, nn
            (a, na), (b, nb), (c, nc), (d, nd) = pt(u0, v0), pt(u1, v0), pt(u1, v1), pt(u0, v1)
            tris += [[a, b, c], [a, c, d]]
            nrm += [[na, nb, nc], [na, nc, nd]]
    return Geo(np.array(tris), np.array(nrm), srgb(rgb), **kw)


def contact_shadow(cx, cz, rx, rz, y=0.0, strength=0.5, rings=5, n=28):
    """Soft dark blob under an object: stacked transparent discs (cheap ambient occlusion)."""
    out = []
    for i in range(rings):
        k = 1 - i / rings
        a = np.linspace(0, 2 * np.pi, n + 1)
        P = np.array([[[0, 0, 0], [math.cos(a[j]) * k, 0, math.sin(a[j]) * k], [math.cos(a[j + 1]) * k, 0, math.sin(a[j + 1]) * k]]
                      for j in range(n)], np.float32)
        P[..., 0] = P[..., 0] * rx + cx
        P[..., 2] = P[..., 2] * rz + cz
        P[..., 1] = y + 0.004 + 0.001 * i
        N = np.zeros_like(P)
        N[..., 1] = 1
        out.append(Geo(P, N, (0.0, 0.0, 0.0), A=strength / rings * 1.6))
    return cat(out)


def quad(p0, p1, p2, p3, rgb, **kw):
    P = quads_to_tris([[p0, p1, p2, p3]])
    return Geo(P, flat_normals(P), srgb(rgb), **kw)


# ---------------------------------------------------------------- matrices
def T(x, y, z):
    M = np.eye(4, dtype=np.float32)
    M[:3, 3] = (x, y, z)
    return M


def S(x, y=None, z=None):
    y = x if y is None else y
    z = x if z is None else z
    return np.diag([x, y, z, 1]).astype(np.float32)


def Ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], np.float32)


def Rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], np.float32)


def Rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)


def look_at(eye, target, up=(0, 1, 0), roll=0.0):
    eye, target = np.asarray(eye, np.float64), np.asarray(target, np.float64)
    f = target - eye
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    if roll:
        c, s = math.cos(roll), math.sin(roll)
        r, u = r * c + u * s, -r * s + u * c
    M = np.eye(4)
    M[0, :3], M[1, :3], M[2, :3] = r, u, -f
    M[:3, 3] = -M[:3, :3] @ eye
    return M.astype(np.float32)


def perspective(fovy, aspect, near, far):
    f = 1 / math.tan(fovy / 2)
    M = np.zeros((4, 4), np.float32)
    M[0, 0], M[1, 1] = f / aspect, f
    M[2, 2], M[2, 3] = (far + near) / (near - far), 2 * far * near / (near - far)
    M[3, 2] = -1
    return M


def ortho(l, r, b, t, n, f):
    M = np.eye(4, dtype=np.float32)
    M[0, 0], M[1, 1], M[2, 2] = 2 / (r - l), 2 / (t - b), -2 / (f - n)
    M[0, 3], M[1, 3], M[2, 3] = -(r + l) / (r - l), -(t + b) / (t - b), -(f + n) / (f - n)
    return M


# ---------------------------------------------------------------- shaders
VS = """
#version 330
uniform mat4 vp; uniform mat4 light_vp;
in vec3 in_pos; in vec3 in_nrm; in vec3 in_col; in float in_emit; in float in_spec; in float in_heat; in float in_alpha; in float in_mask;
out vec3 v_pos; out vec3 v_nrm; out vec3 v_col; out float v_emit; out float v_spec; out float v_heat; out float v_alpha; out vec4 v_lpos; out float v_mask;
void main() {
    v_pos = in_pos; v_nrm = in_nrm; v_col = in_col; v_emit = in_emit; v_spec = in_spec; v_heat = in_heat; v_alpha = in_alpha; v_mask = in_mask;
    v_lpos = light_vp * vec4(in_pos, 1.0);
    gl_Position = vp * vec4(in_pos, 1.0);
}
"""

FS = """
#version 330
uniform sampler2D shadow_map;
uniform vec3 sun_dir; uniform vec3 sun_col; uniform vec3 sky_col; uniform vec3 ground_col; uniform vec3 cam_pos;
uniform int n_lights; uniform vec4 l_pos[6]; uniform vec3 l_col[6]; uniform vec3 l_min[6]; uniform vec3 l_max[6];
uniform float thermal; uniform float thermal_x;
in vec3 v_pos; in vec3 v_nrm; in vec3 v_col; in float v_emit; in float v_spec; in float v_heat; in float v_alpha; in vec4 v_lpos; in float v_mask;
out vec4 f_color;

vec3 heat_ramp(float h) {
    vec3 c0 = vec3(0.02, 0.02, 0.25), c1 = vec3(0.1, 0.35, 1.0), c2 = vec3(0.9, 0.1, 0.6), c3 = vec3(1.0, 0.45, 0.0), c4 = vec3(1.0, 1.0, 0.6);
    h = clamp(h, 0.0, 1.0) * 4.0;
    if (h < 1.0) return mix(c0, c1, h);
    if (h < 2.0) return mix(c1, c2, h - 1.0);
    if (h < 3.0) return mix(c2, c3, h - 2.0);
    return mix(c3, c4, h - 3.0);
}

float shadow(float bias) {
    vec3 p = v_lpos.xyz / v_lpos.w * 0.5 + 0.5;
    if (p.x < 0.0 || p.x > 1.0 || p.y < 0.0 || p.y > 1.0 || p.z > 1.0) return 1.0;
    vec2 ts = 1.0 / vec2(textureSize(shadow_map, 0));
    float s = 0.0;
    for (int i = -2; i <= 2; i++) for (int j = -2; j <= 2; j++) {
        float d = texture(shadow_map, p.xy + vec2(i, j) * ts * 1.2).r;
        s += (p.z - bias > d) ? 0.0 : 1.0;
    }
    return s / 25.0;
}

void main() {
    vec3 n = normalize(v_nrm);
    vec3 V = normalize(cam_pos - v_pos);
    if (!gl_FrontFacing && dot(n, V) < 0.0) n = -n;   // two-sided only where we really see the back
    float ndl = max(dot(n, -sun_dir), 0.0);
    float sh = shadow(0.002 + 0.006 * (1.0 - ndl));
    vec3 col = v_col * mix(ground_col, sky_col, n.y * 0.5 + 0.5);
    col += v_col * sun_col * ndl * sh;
    vec3 H = normalize(-sun_dir + V);
    col += sun_col * pow(max(dot(n, H), 0.0), 60.0) * v_spec * sh;
    for (int i = 0; i < n_lights; i++) {
        if (any(lessThan(v_pos, l_min[i])) || any(greaterThan(v_pos, l_max[i]))) continue;
        vec3 d = l_pos[i].xyz - v_pos;
        float dist = length(d);
        vec3 L = d / dist;
        float att = 1.0 / (1.0 + dist * dist / (l_pos[i].w * l_pos[i].w));
        col += v_col * l_col[i] * max(dot(n, L), 0.0) * att;
        col += l_col[i] * pow(max(dot(n, normalize(L + V)), 0.0), 40.0) * v_spec * att * 0.6;
    }
    // soft rim so silhouettes read against dark backgrounds
    col += v_col * sky_col * pow(1.0 - max(dot(n, V), 0.0), 3.0) * 0.25;
    col += v_col * v_emit;
    if (thermal > 0.0 && gl_FragCoord.x < thermal_x) {
        vec3 tc = heat_ramp(v_heat) * (0.55 + 0.45 * max(dot(n, V), 0.0)) * 1.4;
        col = mix(col, tc, thermal * v_mask);
        col = mix(col, vec3(dot(col, vec3(0.2, 0.5, 0.3))) * vec3(0.08, 0.1, 0.28), thermal * (1.0 - v_mask));
    }
    f_color = vec4(col, v_alpha);
}
"""

VS_SHADOW = """
#version 330
uniform mat4 light_vp;
in vec3 in_pos;
void main() { gl_Position = light_vp * vec4(in_pos, 1.0); }
"""
FS_SHADOW = """
#version 330
void main() {}
"""

ATTRS = ("in_pos", "in_nrm", "in_col", "in_emit", "in_spec", "in_heat", "in_alpha", "in_mask")
FMT = "3f 3f 3f 1f 1f 1f 1f 1f"


class Renderer:
    def __init__(self, w, h, ss=1.5, shadow_size=2048):
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
        self.static = None
        self.clear_col = (0.0, 0.0, 0.0)

    def _vao(self, prog, data, shadow=False):
        buf = self.ctx.buffer(data.astype(np.float32).tobytes())
        if shadow:
            return self.ctx.vertex_array(prog, [(buf, "3f 44x", "in_pos")]), buf
        return self.ctx.vertex_array(prog, [(buf, FMT, *ATTRS)]), buf

    def set_static(self, geo):
        data = geo.vbo()
        self.static = (self._vao(self.prog, data), self._vao(self.sprog, data, True))

    def render(self, cam, sun, lights, dyn_opaque=None, dyn_trans=None, thermal=0.0, thermal_x=0.0):
        """cam: dict(eye, target, fov, roll, near, far). sun: dict(dir, col, sky, ground, center, extent).
        lights: [(pos, radius, col, min, max)]. Returns (hdr rgb float32 (rh, rw, 3), linear depth (rh, rw))."""
        ctx = self.ctx
        tmp = []
        dyn = []
        for g in (dyn_opaque, dyn_trans):
            if g is not None and len(g):
                d = g.vbo()
                dyn.append((self._vao(self.prog, d), self._vao(self.sprog, d, True)))
            else:
                dyn.append(None)
        # --- shadow pass
        sd = np.asarray(sun["dir"], np.float64)
        sd /= np.linalg.norm(sd)
        c = np.asarray(sun["center"], np.float64)
        ext = sun["extent"]
        lv = look_at(c - sd * 40, c, up=(0, 0, 1) if abs(sd[1]) > 0.95 else (0, 1, 0))
        lvp = ortho(-ext, ext, -ext, ext, 1, 90) @ lv
        self.sfbo.use()
        self.sfbo.clear(depth=1.0)
        ctx.enable(moderngl.DEPTH_TEST)
        ctx.disable(moderngl.BLEND)
        ctx.disable(moderngl.CULL_FACE)
        self.sprog["light_vp"].write(lvp.T.copy().tobytes())
        self.static[1][0].render()
        if dyn[0]:
            dyn[0][1][0].render()
        # --- main pass
        aspect = self.rw / self.rh
        view = look_at(cam["eye"], cam["target"], roll=cam.get("roll", 0.0))
        proj = perspective(math.radians(cam["fov"]), aspect, cam.get("near", 0.05), cam.get("far", 120.0))
        p = self.prog
        p["vp"].write((proj @ view).T.copy().tobytes())
        p["light_vp"].write(lvp.T.copy().tobytes())
        p["sun_dir"].value = tuple(sd)
        p["sun_col"].value = tuple(sun["col"])
        p["sky_col"].value = tuple(sun["sky"])
        p["ground_col"].value = tuple(sun["ground"])
        p["cam_pos"].value = tuple(float(v) for v in cam["eye"])
        n = min(6, len(lights))
        p["n_lights"].value = n
        lp = np.zeros((6, 4), np.float32)
        lc, lmn, lmx = np.zeros((6, 3), np.float32), np.full((6, 3), -1e9, np.float32), np.full((6, 3), 1e9, np.float32)
        for i, (pos, rad, col, mn, mx) in enumerate(lights[:6]):
            lp[i] = (*pos, rad)
            lc[i] = col
            if mn is not None:
                lmn[i], lmx[i] = mn, mx
        p["l_pos"].write(lp.tobytes())
        p["l_col"].write(lc.tobytes())
        p["l_min"].write(lmn.tobytes())
        p["l_max"].write(lmx.tobytes())
        p["thermal"].value = float(thermal)
        p["thermal_x"].value = float(thermal_x * self.rw)
        self.smap.use(0)
        p["shadow_map"].value = 0
        self.fbo.use()
        self.fbo.clear(*self.clear_col, 1.0, depth=1.0)
        self.static[0][0].render()
        if dyn[0]:
            dyn[0][0][0].render()
        if dyn[1]:
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
            self.fbo.depth_mask = False      # see-through things never hide what is behind them
            dyn[1][0][0].render()
            self.fbo.depth_mask = True
            ctx.disable(moderngl.BLEND)
        img = np.frombuffer(self.color.read(), np.float32).reshape(self.rh, self.rw, 4)[::-1, :, :3]
        d = np.frombuffer(self.depth.read(), np.float32).reshape(self.rh, self.rw)[::-1]
        near, far = cam.get("near", 0.05), cam.get("far", 120.0)
        lin = (2 * near * far) / (far + near - (d * 2 - 1) * (far - near))
        for x in dyn:
            if x:
                for (vao, buf) in x:
                    vao.release()
                    buf.release()
        return img, lin


# ---------------------------------------------------------------- post
def downsample(img, w, h):
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)


def depth_of_field(img, depth, focus, strength, max_sigma=9.0):
    """Blend between blur levels by circle of confusion |1/focus - 1/z| * strength (in pixels of sigma)."""
    if strength <= 0:
        return img
    coc = np.clip(np.abs(1.0 / focus - 1.0 / np.maximum(depth, 1e-3)) * strength, 0, max_sigma)
    levels = [0.0, 2.0, 4.5, max_sigma]
    blurred = [img] + [cv2.GaussianBlur(img, (0, 0), s) for s in levels[1:]]
    out = np.zeros_like(img)
    wsum = np.zeros(depth.shape, np.float32)
    for i, s in enumerate(levels):
        lo = levels[i - 1] if i > 0 else -1
        hi = levels[i + 1] if i + 1 < len(levels) else max_sigma + 1
        w = np.where(coc <= s, np.clip((coc - lo) / max(s - lo, 1e-6), 0, 1), np.clip((hi - coc) / max(hi - s, 1e-6), 0, 1))
        out += blurred[i] * w[..., None]
        wsum += w
    return out / np.maximum(wsum, 1e-6)[..., None]


def bloom(img, threshold=1.0, amount=0.35):
    bright = np.maximum(img - threshold, 0)
    h, w = img.shape[:2]
    small = cv2.resize(bright, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    b = cv2.GaussianBlur(small, (0, 0), 6) + cv2.GaussianBlur(small, (0, 0), 18) * 0.7
    return img + cv2.resize(b, (w, h), interpolation=cv2.INTER_LINEAR) * amount


def tonemap(img, exposure=1.0):
    x = img * exposure
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14          # ACES fit
    y = np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)
    return np.where(y <= 0.0031308, y * 12.92, 1.055 * np.power(y, 1 / 2.4) - 0.055)


_VIG = {}


def vignette(img, amount=0.28):
    h, w = img.shape[:2]
    if (h, w) not in _VIG:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        _VIG[(h, w)] = (1 - amount * np.clip(r - 0.5, 0, 1) ** 1.5)[..., None]
    return img * _VIG[(h, w)]
