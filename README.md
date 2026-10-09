# 🛰️ Green Bank Telescope Sonification for Lofi Production

Turn radio astronomy data from the Green Bank Telescope (GBT) in West Virginia into ambient soundscapes for lofi music production.

## 🎵 What This Does

- Sonifies GBT data files you download from the NRAO Archive, **or** generates synthetic radio-telescope-style data when you don't have any
- Uses a different sonification technique for each kind of data: pulsar, spectral line and continuum
- Writes stereo, 24-bit WAV files (44.1 kHz by default) ready to drop into a DAW

## 🚀 Quick Start

```bash
pip install -r requirements.txt
python gbt_sonification.py
```

This creates 3 five-minute pieces from synthetic data in `gbt_ambient_audio/`.

### Command-line options

```bash
python gbt_sonification.py --pieces 6 --minutes 2      # 6 two-minute pieces
python gbt_sonification.py --seed 42                   # reproduce a run exactly
python gbt_sonification.py --bpm 72                    # tempo of pulsar pieces
python gbt_sonification.py --fits obs1.fits obs2.fits  # sonify real data, one piece per file
python gbt_sonification.py --sample-rate 48000 --float # 48 kHz, 32-bit float WAVs
python gbt_sonification.py --out my_cosmic_sounds      # choose the output folder
```

Run `python gbt_sonification.py --help` for the full list.

For preset collections (deep-space drones, lofi elements, a sample pack of mixed lengths), run `python examples.py`.

## 📁 Output

```
gbt_ambient_audio/
├── gbt_ambient_synthetic_pulsar_1_20261009_143022.wav
├── gbt_ambient_synthetic_spectral_line_1_20261009_143025.wav
└── gbt_ambient_synthetic_continuum_1_20261009_143028.wav
```

Synthetic pieces cycle through pulsar → spectral line → continuum, so `--pieces 6` gives two of each.

## 📡 Using Real GBT Data

The script doesn't download data itself. Get it from the NRAO Archive:

1. Search the archive at <https://data.nrao.edu> for Green Bank Telescope observations. Data is public once its proprietary period ends, so older observations are the ones you can download.
2. Download the calibrated SDFITS (`.fits`) files.
3. Run `python gbt_sonification.py --fits path/to/file.fits`.

How each file is read:
- **SDFITS** (the standard GBT format: a table with one spectrum per row in a `DATA` column): rows are averaged into one spectrum and played in spectral-line mode. Flagged (NaN) channels are ignored.
- **Tables whose `DATA` is one number per row**: treated as a time series and played in continuum mode.
- **Anything else numeric** (images, other tables): played in generic mode, which maps the values straight to a waveform.

## 🎚️ Sonification Techniques

### Pulsar Mode
- One bass hit per beat at `--bpm` (default 80)
- Each hit's loudness follows the brightness of successive pulses, including the occasional "nulled" pulse that drops out
- The bass tone's harmonics come from the shape of the folded pulse profile
- A slowly swelling pad on the same harmonic series sits underneath

### Spectral Line Mode
- Finds the distinct emission lines in the spectrum
- Each line becomes a drone voice: its position sets the pitch (110–880 Hz, snapped to semitones) and its strength sets the level
- Slow, independent swells on each voice, plus a 55 Hz sub-bass drone

### Continuum Mode
- Signal variations modulate pitch and loudness of a two-voice tone
- Filtered noise rises and falls with the signal
- Slow-moving, meditative textures

All modes then go through gentle compression and a stereo convolution reverb.

### About the synthetic data

The synthetic generators are **stylised stand-ins**, not physical simulations. They're designed to have the features that make each mode interesting (periodic pulses with variable brightness, several emission lines near the 21 cm hydrogen line, slow and fast continuum drifts), not to model real instruments or sources.

## 🎹 Using in Your Lofi Production

1. **Layering**: use as atmospheric layers under your beats
2. **Time-stretching**: slow them down 50–200% for even more ambient vibes
3. **EQ**: roll off highs for a warmer, more vintage sound
4. **Reverb**: already has some, but more creates deeper space
5. **Looping**: pulsar pieces are on a fixed tempo, so 4- or 8-bar loops line up with your project BPM if you match `--bpm`
6. **Pitch-shifting**: shift down a few semitones for darker moods

### DAW-Specific Ideas

**Ableton Live:**
- Drop into Simpler/Sampler for granular manipulation
- Use as texture in Erosion or Redux for degraded cosmic sounds
- Freeze & Flatten with effects for unique samples

**FL Studio:**
- Load into Fruity Slicer for rhythmic chopping
- Use with Gross Beat for stutter effects
- Layer with piano/guitar loops

**Logic Pro:**
- Use Spectral Gate to isolate interesting frequencies
- Apply Retro Synth's cloud mode for extra texture
- Alchemy granular mode for evolving pads

## 📝 Use as a Module

```python
from gbt_sonification import GBTSonifier

sonifier = GBTSonifier(output_dir="my_cosmic_sounds", seed=42, bpm=72)

# Whole pipeline
files = sonifier.create_ambient_pieces(num_pieces=5, duration_minutes=8)
files = sonifier.create_ambient_pieces(duration_minutes=8, fits_files=["obs.fits"])

# Step by step
data = sonifier.generate_synthetic_data(3)      # or: [sonifier.load_fits("obs.fits")]
audio = sonifier.sonify_data(data[0], duration_minutes=1)   # mono
audio = sonifier.add_effects(audio)                         # stereo
sonifier.save_audio(audio, "my_custom_piece")
```

## 🔧 Troubleshooting

**Want different sounds?** Each run without `--seed` is different. When you like one, note its seed next time so you can recreate it.

**Files too large or running out of memory?** Use shorter `--minutes`. A full default run (three 5-minute pieces) needs about 1.5 GB of RAM.

**A FITS file is skipped?** The script prints why. It needs at least one HDU with numeric data.

## 🧪 Development

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## 🌌 The Science Behind the Sound

Radio telescopes like the GBT detect radio waves from space. This script turns that data into audio by:

1. **Frequency translation**: radio frequencies of spectral lines → audible pitches
2. **Time compression**: hours of observation → minutes of audio
3. **Rhythm mapping**: pulsar pulses → beats, pulse brightness → velocity
4. **Parameter modulation**: data variations → pitch, loudness and texture

## 🙏 Credits

- **Green Bank Telescope**: Green Bank Observatory / National Radio Astronomy Observatory (NRAO)
- **Data**: NRAO Archive

## 📜 License

MIT. See [LICENSE](LICENSE).

## 🚀 What's Next?

- [ ] Automatic download from the NRAO Archive
- [ ] MIDI output for controlling synthesizers
- [ ] Visual spectrogram generation
- [ ] Web interface for parameter control
- [ ] Time-resolved spectral data (play how a spectrum changes over a session)

---

**Made with cosmic love for lofi producers** 🌌🎵

*"The universe has always been making music. Now you can produce with it."*
