"""Runs a real image model (Stable Diffusion 1.5, CPU) and saves what happens inside it, as data for the video.

For every run it saves, under data/runs/<name>/:
  final.png              the finished picture
  steps/NN.png           the picture at every step: the current noisy state, decoded to pixels
  x0/NN.png              the model's guess of the final picture at that step (decoded)
  attn.npz               cross-attention per token (16x16 maps, averaged over heads and layers), per step
  meta.json              prompt, seed, steps, guidance, tokens

  python3 gen.py hero              # one named run (see RUNS)
  python3 gen.py all
  python3 gen.py search "prompt" 1 2 3 4   # quick finals for a few seeds (picks a hero seed)
  python3 gen.py words             # text-encoder vectors for the meaning map -> data/words.npz
"""
import json
import os
import sys

import numpy as np
import torch
from diffusers import DDIMScheduler, StableDiffusionPipeline
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = "stable-diffusion-v1-5/stable-diffusion-v1-5"
STEPS = 30
CAT = "a cat wearing an astronaut suit riding a bicycle on the moon, digital art"
HERO_SEED = 1883   # set after the seed search

RUNS = {   # name: (prompt, seed, guidance)
    "hero": (CAT, HERO_SEED, 7.5),
    "seed_a": (CAT, 11, 7.5),
    "seed_b": (CAT, 22, 7.5),
    "seed_c": (CAT, 33, 7.5),
    "paris": ("a cat wearing an astronaut suit riding a bicycle in Paris, digital art", HERO_SEED, 7.5),
    "noguide": (CAT, HERO_SEED, 1.0),
    "train_dog": ("a photo of a golden retriever on the grass", 5, 7.5),
    "train_mountain": ("a photo of a snowy mountain at sunrise", 6, 7.5),
    "train_lighthouse": ("a photo of a lighthouse by the sea", 7, 7.5),
}
# meaning map: groups of related words (cat things, space things, vehicles, places, food)
WORDS = ["cat", "kitten", "tiger", "dog", "puppy", "moon", "planet", "mars", "star", "astronaut", "rocket",
         "bicycle", "car", "train", "paris", "london", "city", "pizza", "apple", "bread"]
torch.set_num_threads(os.cpu_count())


class AttnStore:
    """Attention processor that records cross-attention probabilities (text -> image) at 16x16."""

    def __init__(self):
        self.maps = []

    def __call__(self, attn, hidden_states, encoder_hidden_states=None, attention_mask=None, **kw):
        cross = encoder_hidden_states is not None
        ctx = encoder_hidden_states if cross else hidden_states
        q = attn.head_to_batch_dim(attn.to_q(hidden_states))
        k = attn.head_to_batch_dim(attn.to_k(ctx))
        v = attn.head_to_batch_dim(attn.to_v(ctx))
        probs = attn.get_attention_scores(q, k, attention_mask)
        if cross and probs.shape[1] == 256:          # 16x16 layers only; keep the conditional half
            h = attn.heads
            p = probs.reshape(-1, h, 256, probs.shape[-1])[-1].mean(0)
            self.maps.append(p.detach().float().numpy())
        out = attn.batch_to_head_dim(torch.bmm(probs, v))
        return attn.to_out[1](attn.to_out[0](out))

    def pop(self):
        m = np.mean(self.maps, 0) if self.maps else None
        self.maps = []
        return m


def pipe():
    p = StableDiffusionPipeline.from_pretrained(MODEL, torch_dtype=torch.float32, safety_checker=None)
    p.scheduler = DDIMScheduler.from_config(p.scheduler.config)
    p.set_progress_bar_config(disable=True)
    return p


def decode(p, lat):
    with torch.no_grad():
        img = p.vae.decode(lat / p.vae.config.scaling_factor).sample
    img = ((img[0].clamp(-1, 1) + 1) * 127.5).permute(1, 2, 0).round().byte().numpy()
    return Image.fromarray(img)


def run(p, name, prompt, seed, guidance, detail=True):
    out = os.path.join(HERE, "data", "runs", name)
    os.makedirs(os.path.join(out, "steps"), exist_ok=True)
    os.makedirs(os.path.join(out, "x0"), exist_ok=True)
    store = AttnStore()
    p.unet.set_attn_processor(store)
    attn = []
    sched = p.scheduler

    def on_step(pp, i, t, kw):
        lat = kw["latents"]
        m = store.pop()
        if m is not None:
            attn.append(m)
        if detail:
            decode(pp, lat).save(os.path.join(out, "steps", f"{i:02d}.png"))
            # the model's current guess of the clean picture (predicted x0) from the new latent's noise level
            nxt = sched.timesteps[i + 1] if i + 1 < len(sched.timesteps) else None
            if nxt is not None:
                ab = sched.alphas_cumprod[nxt]
                with torch.no_grad():
                    emb = kw["prompt_embeds"]
                    li = torch.cat([lat] * 2) if guidance > 1 else lat
                    eps = pp.unet(li, nxt, encoder_hidden_states=emb).sample
                    if guidance > 1:
                        u, c = eps.chunk(2)
                        eps = u + guidance * (c - u)
                x0 = (lat - (1 - ab).sqrt() * eps) / ab.sqrt()
                store.pop()
                decode(pp, x0).save(os.path.join(out, "x0", f"{i:02d}.png"))
        return kw

    g = torch.Generator().manual_seed(seed)
    lat0 = torch.randn((1, 4, 64, 64), generator=g)
    np.save(os.path.join(out, "start_latent.npy"), lat0.numpy())
    if detail:
        decode(p, lat0 * sched.init_noise_sigma).save(os.path.join(out, "steps", "start.png"))
    img = p(prompt, num_inference_steps=STEPS, guidance_scale=guidance, latents=lat0.clone(),
            callback_on_step_end=on_step, callback_on_step_end_tensor_inputs=["latents", "prompt_embeds"]).images[0]
    img.save(os.path.join(out, "final.png"))
    ids = p.tokenizer(prompt).input_ids
    toks = [p.tokenizer.decoder[i] for i in ids]
    with torch.no_grad():
        emb = p.text_encoder(torch.tensor([ids]))[0][0].numpy()
    np.savez_compressed(os.path.join(out, "attn.npz"), attn=np.array(attn, np.float16), emb=emb.astype(np.float16))
    json.dump(dict(prompt=prompt, seed=seed, guidance=guidance, steps=STEPS, model=MODEL, scheduler="DDIM",
                   tokens=toks), open(os.path.join(out, "meta.json"), "w"), indent=1)
    print(name, "done")


if __name__ == "__main__":
    p = pipe()
    if sys.argv[1] == "words":
        with torch.no_grad():
            ids = p.tokenizer(WORDS, padding=True, return_tensors="pt").input_ids
            out = p.text_encoder(ids)
        # pooled vector = the end-of-text token, which summarises the whole input
        np.savez_compressed(os.path.join(HERE, "data", "words.npz"), words=np.array(WORDS),
                            vec=out.pooler_output.numpy())
        print("words done")
    elif sys.argv[1] == "search":
        os.makedirs(os.path.join(HERE, "data", "search"), exist_ok=True)
        for s in sys.argv[3:]:
            g = torch.Generator().manual_seed(int(s))
            p(sys.argv[2], num_inference_steps=STEPS, guidance_scale=7.5, generator=g).images[0].save(
                os.path.join(HERE, "data", "search", f"{s}.png"))
            print(s, flush=True)
    else:
        for n in (RUNS if sys.argv[1] == "all" else sys.argv[1:]):
            run(p, n, *RUNS[n], detail=n in ("hero", "noguide", "train_dog") or len(sys.argv) > 2)
