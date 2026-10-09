# 🚀 QUICK START GUIDE

## Get Started in 3 Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Script
```bash
python gbt_sonification.py
```

### 3. Find Your Audio
Your ambient pieces will be in the `gbt_ambient_audio/` folder!

---

## What You Get

✓ **3 ambient pieces** (5 minutes each): pulsar beat, spectral-line drone, continuum texture
✓ **Stereo 24-bit WAV files** (44.1 kHz)
✓ **Ready for lofi production**: no additional processing needed
✓ **Zero configuration**: uses synthetic data unless you give it real files

---

## Customization

Everything is a command-line flag, so you don't need to edit the code:

```bash
python gbt_sonification.py --minutes 10            # longer pieces
python gbt_sonification.py --pieces 6              # more pieces
python gbt_sonification.py --bpm 72                # match your project tempo
python gbt_sonification.py --seed 42               # same result every time
python gbt_sonification.py --out my_custom_folder  # different output folder
python gbt_sonification.py --fits obs.fits         # use real GBT data
```

See all options with `python gbt_sonification.py --help`.

---

## Different Generation Modes

Want preset collections? Use the examples script:

```bash
python examples.py
```

This gives you options for:
- Deep space ambient (3 × 10-minute pieces)
- Lofi elements (5 × 3-minute pieces)
- Sample packs (a variety of lengths)
- Quick batches (10 × 2-minute pieces)

---

## How to Use in Your Music

### For Lofi Hip-Hop:
1. Generate with `--bpm` set to your project tempo
2. Import the WAV into your DAW
3. Time-stretch to ~50–75% speed for more chill vibes
4. Add vinyl crackle/tape saturation
5. Layer under your drums and samples, and EQ out highs for warmth

### For Ambient/Experimental:
1. Use as-is for spacey backgrounds
2. Add reverb and delay for depth
3. Pitch-shift for different moods
4. Layer multiple pieces together

### For Sampling:
1. Chop interesting sections
2. Loop pulsar beats (they're on a fixed tempo)
3. Reverse for unique textures
4. Use as drone pads

---

## What's Happening?

The script:
1. Loads the GBT data files you give it with `--fits`, or generates synthetic stand-in data
2. Turns pulsars into beats, spectral lines into drones, and continuum drifts into slow modulation
3. Adds compression and stereo reverb for ambient quality
4. Saves stereo 24-bit WAV files

See README.md for how to download real GBT data.

---

## Need Help?

Check the full README.md for:
- Using real GBT data
- How each sonification mode works
- Using it as a Python module
- DAW-specific production tips

---

**Happy creating! 🎵🌌**
