# Hero video: AI generation brief

The home hero plays `assets/hero.mp4` behind the headline "Engineering, rebuilt around AI."
Generate a clip with any text-to-video tool (for example Google Veo, Runway, Kling, Sora or Higgsfield),
then run:

```bash
tools/prepare_hero_video.sh path/to/clip.mp4 pingpong   # 1080p, seamless loop, poster frame
python3 build.py
```

Check that your plan on the tool allows commercial use of what it generates.

## Spec for every direction

- 16:9, at least 1920×1080, 6 to 10 seconds, 24 or 30 fps, no audio
- Pure white, high-key background; soft, diffuse light; no harsh shadows
- Keep the **left half calm and nearly empty**: the headline and typewriter sit there
- Slow, continuous motion on the right; locked or very slow camera; no cuts
- Palette: white, soft greys, charcoal details, one warm amber accent (#C27A2C)
- No text, numbers, logos, screens or faces

**Negative prompt:** text, letters, numbers, watermark, logo, user interface, screens, faces, dark background, neon, cyberpunk, blue holograms, glitch, flicker, fast cuts, camera shake

## Direction A: Assembly (abstract, closest to the brand)

> A bright, minimal white studio. In the right half of the frame, thousands of tiny white and pale grey cubes float and slowly assemble, layer by layer, into a precise architectural structure of stacked platforms and connecting beams, like a system being engineered in mid-air. Thin amber light pulses travel along the beams as each section locks into place. Soft diffuse daylight, shallow depth of field, very slow camera push-in. Calm, precise, premium. The left half of the frame stays clean white negative space.

## Direction B: Rebuild (legacy to AI, the transformation story)

> A high-key white environment. On the right side, an intricate old machine of matte grey gears and blocks slowly breaks apart into small floating cubes, which reorganize into a clean, modern modular structure joined by glowing amber lines, as if an intelligent process is rebuilding it. Slow continuous motion, soft studio lighting, very slow orbiting camera. The left half of the frame is clean white negative space.

## Direction C: Craft (human and AI working together)

> Overhead view of a bright white desk in soft morning light. On the right side of the frame, a pair of hands places translucent glass tiles on the desk; as each tile is placed, thin amber lines of light connect it to the others, forming a network that grows beyond the tiles on its own. Slow, deliberate movement, shallow depth of field, calm and precise. The left half of the frame is empty white desk. No faces, no screens, no text.

Hands are where AI video most often goes wrong; check fingers frame by frame before using C.

## If the clip is busy

The site draws a cursor-reactive particle logo over the right side of the video. If your clip already
fills that area, set `'hero_particles': False` in `content.py` and rebuild.
