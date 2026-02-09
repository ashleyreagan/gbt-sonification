# 🛰️ Green Bank Telescope Sonification for Lofi Production

Transform radio astronomy data from the Green Bank Telescope in West Virginia into ambient soundscapes perfect for lofi music production.

## 🎵 What This Does

This script automatically:
- Downloads publicly available Green Bank Telescope data (or generates synthetic radio telescope data)
- Processes radio signals using multiple sonification techniques
- Creates 5-minute ambient audio pieces ready for your music production
- Outputs high-quality WAV files (44.1kHz, CD quality)

## 🚀 Quick Start

### Installation

```bash
# Install required packages
pip install astropy numpy scipy soundfile requests

# Make the script executable (optional)
chmod +x gbt_sonification.py
```

### Run It

```bash
python gbt_sonification.py
```

That's it! The script will automatically:
1. Try to download real GBT data from the archive
2. If that fails (due to network/availability), generate synthetic radio telescope data
3. Create 3 different ambient pieces (5 minutes each)
4. Save them to the `gbt_ambient_audio/` folder

## 📁 Output

Your audio files will be saved to:
```
gbt_ambient_audio/
├── gbt_ambient_synthetic_pulsar_20260209_143022.wav
├── gbt_ambient_synthetic_spectral_line_20260209_143025.wav
└── gbt_ambient_synthetic_continuum_20260209_143028.wav
```

## 🎛️ Customization

You can modify the script to change:

### Duration
```python
# In the main() function, change duration_minutes
audio_files = sonifier.create_ambient_pieces(
    num_pieces=3,
    duration_minutes=10  # Change to 10 minutes
)
```

### Number of Pieces
```python
audio_files = sonifier.create_ambient_pieces(
    num_pieces=5,  # Generate 5 different pieces
    duration_minutes=5
)
```

### Sample Rate
```python
# In the __init__ method of GBTSonifier class
self.sample_rate = 48000  # Use 48kHz instead of 44.1kHz
```

## 🎚️ Sonification Techniques Used

### Pulsar Mode
- Creates rhythmic, bass-heavy pulses
- Perfect for adding groove to lofi beats
- Uses actual pulsar timing data to create repeating patterns
- Adds harmonic richness and evolving pads

### Spectral Line Mode
- Generates ambient drones from spectral data
- Maps radio frequencies to musical frequencies
- Creates lush, evolving soundscapes
- Excellent for atmospheric pads

### Continuum Mode
- Uses signal variations for parameter modulation
- Creates slow-moving, meditative textures
- Frequency and amplitude modulation based on telescope data
- Great for background ambience

## 🎹 Using in Your Lofi Production

### Tips for Music Production

1. **Layering**: These files work great as atmospheric layers under your beats
2. **Time-stretching**: Use your DAW's time-stretch to slow them down 50-200% for even more ambient vibes
3. **EQ**: Roll off highs for a warmer, more vintage sound
4. **Reverb**: Already has some reverb, but adding more creates deeper space
5. **Looping**: Find interesting 4 or 8-bar sections and loop them
6. **Pitch-shifting**: Shift down a few semitones for darker moods

### DAW-Specific Ideas

**Ableton Live:**
- Drop into a Simpler/Sampler for granular manipulation
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

## 📡 About the Data

### Real GBT Data
When available, the script attempts to download:
- Pulsar observations (spinning neutron stars)
- Spectral line data (molecules in space)
- Continuum observations (cosmic radio emissions)

### Synthetic Data
If real data isn't accessible, the script generates scientifically-accurate synthetic radio telescope data that mimics:
- Pulsar dispersion and timing
- Spectral line emission/absorption
- Continuum variations

Both create equally interesting sounds for music production!

## 🔧 Troubleshooting

### No internet/Can't download data
The script automatically falls back to synthetic data generation - you'll still get great results!

### Files too large
Reduce `duration_minutes` parameter:
```python
duration_minutes=3  # Create 3-minute pieces instead
```

### Want different sounds
Run the script multiple times! Each run creates different variations due to:
- Different data sources
- Random noise patterns
- Varying modulation parameters

### Memory issues
The script is optimized to handle large datasets, but if you encounter issues:
- Reduce `num_pieces` parameter
- Reduce `duration_minutes`
- The script automatically downsamples very large datasets

## 🌌 The Science Behind the Sound

Radio telescopes like the Green Bank Telescope detect electromagnetic radiation from space. This script converts that data into audio by:

1. **Direct mapping**: Radio signal intensities → audio amplitudes
2. **Frequency translation**: Radio frequencies → audible frequencies
3. **Time compression**: Hours of observations → minutes of audio
4. **Parameter modulation**: Data variations → musical parameters

The result is a unique blend of cosmic data and musical creativity!

## 📝 Advanced Usage

### Use as a Module

```python
from gbt_sonification import GBTSonifier

# Create custom sonifier
sonifier = GBTSonifier(output_dir="my_cosmic_sounds")

# Generate with custom settings
files = sonifier.create_ambient_pieces(
    num_pieces=5,
    duration_minutes=8
)
```

### Access Individual Methods

```python
# Generate just synthetic data
data = sonifier._generate_synthetic_data()

# Sonify with specific technique
audio = sonifier._sonify_pulsar(data[0], duration_samples=44100*60)

# Add effects
audio = sonifier.add_effects(audio)

# Save
sonifier.save_audio(audio, "my_custom_piece")
```

## 🎓 Educational Use

This script is also great for:
- Learning about radio astronomy
- Understanding sonification techniques
- Teaching signal processing
- Demonstrating data visualization through sound

## 🙏 Credits

- **Green Bank Telescope**: National Radio Astronomy Observatory (NRAO)
- **Data Sources**: NRAO Data Archive
- **Inspiration**: The cosmic sounds of the universe!

## 📜 License

This script is provided as-is for creative and educational use. GBT data is publicly available through NRAO.

## 🚀 What's Next?

Ideas for expansion:
- [ ] Real-time streaming of GBT data
- [ ] MIDI output for controlling synthesizers
- [ ] Visual spectrogram generation
- [ ] Web interface for parameter control
- [ ] Batch processing of entire observation sessions
- [ ] Integration with specific lofi VSTs/plugins

---

**Made with cosmic love for lofi producers** 🌌🎵

*"The universe has always been making music. Now you can produce with it."*
