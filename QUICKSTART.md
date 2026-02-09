# 🚀 QUICK START GUIDE

## Get Started in 3 Steps

### 1. Install Dependencies
```bash
pip install astropy numpy scipy soundfile requests
```

### 2. Run the Script
```bash
python gbt_sonification.py
```

### 3. Find Your Audio
Your ambient pieces will be in the `gbt_ambient_audio/` folder!

---

## What You Get

✓ **3 unique ambient pieces** (5 minutes each)
✓ **High-quality WAV files** (44.1kHz)
✓ **Ready for lofi production** - no additional processing needed
✓ **Automatic generation** - runs with zero configuration

---

## Different Generation Modes

Want different types of sounds? Use the examples script:

```bash
python examples.py
```

This gives you options for:
- Deep space ambient (10-minute pieces)
- Lofi elements (shorter 3-minute pieces)
- Sample packs (variety of lengths)
- Quick batches (lots of 2-minute pieces)

---

## How to Use in Your Music

### For Lofi Hip-Hop:
1. Import the WAV into your DAW
2. Time-stretch to ~50-75% speed for more chill vibes
3. Add vinyl crackle/tape saturation
4. Layer under your drums and samples
5. EQ out highs for warmth

### For Ambient/Experimental:
1. Use as-is for spacey backgrounds
2. Add reverb and delay for depth
3. Pitch-shift for different moods
4. Layer multiple pieces together

### For Sampling:
1. Chop interesting sections
2. Create loops from repetitive parts
3. Reverse for unique textures
4. Use as drone pads

---

## Customization

Edit `gbt_sonification.py` to change:

**Duration** (line ~517):
```python
duration_minutes=5  # Change to any length you want
```

**Number of pieces** (line ~516):
```python
num_pieces=3  # Generate more or fewer files
```

**Output folder** (line ~512):
```python
GBTSonifier(output_dir="my_custom_folder")
```

---

## What's Happening?

The script:
1. Tries to download real Green Bank Telescope data
2. If that's not available, generates scientifically-accurate synthetic data
3. Converts radio signals into audio using advanced sonification
4. Applies effects (reverb, filtering) for ambient quality
5. Saves as high-quality WAV files

**Either way, you get cosmic sounds perfect for your music!**

---

## Need Help?

Check the full README.md for:
- Detailed documentation
- Troubleshooting tips
- Advanced usage examples
- DAW-specific production tips

---

**Happy creating! 🎵🌌**
