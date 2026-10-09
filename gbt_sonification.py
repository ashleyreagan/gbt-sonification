#!/usr/bin/env python3
"""
Green Bank Telescope Data Sonification Script
Turns radio telescope data into ambient soundscapes for music production.

Data comes from GBT SDFITS files you download from the NRAO Archive (see
README), or from built-in synthetic generators when no files are given.

Requirements:
    pip install -r requirements.txt

Usage:
    python gbt_sonification.py                          # 3 synthetic pieces, 5 min each
    python gbt_sonification.py --pieces 6 --minutes 2 --seed 42
    python gbt_sonification.py --fits my_observation.fits
"""

import argparse
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import soundfile as sf
from astropy.io import fits
from scipy import signal
from scipy.interpolate import interp1d

SYNTHETIC_TYPES = ('pulsar', 'spectrum', 'continuum')


class GBTSonifier:
    def __init__(self, output_dir="gbt_ambient_audio", sample_rate=44100, seed=None, bpm=80):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sample_rate = sample_rate
        self.bpm = bpm
        # One generator for all randomness, so a seed reproduces a whole run
        self.rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # Data sources
    # ------------------------------------------------------------------

    def load_fits(self, fits_path):
        """
        Load a FITS file and return a data dict ready for sonify_data(),
        or None if the file holds nothing usable.

        GBT data is distributed as SDFITS: a binary table with one spectrum
        per row in its DATA column. Those are averaged into a single spectrum.
        Plain image HDUs and other numeric tables fall back to generic mode.
        """
        name = Path(fits_path).stem
        try:
            with fits.open(fits_path) as hdul:
                print(f"\nProcessing: {fits_path} ({len(hdul)} HDU(s))")
                for i, hdu in enumerate(hdul):
                    if hdu.data is None or hdu.data.size == 0:
                        continue

                    if isinstance(hdu, (fits.BinTableHDU, fits.TableHDU)):
                        data_dict = self._table_to_data(hdu)
                    else:
                        data_dict = {'type': 'generic',
                                     'data': np.array(hdu.data, dtype=float)}

                    if data_dict is not None:
                        print(f"Using HDU {i} as {data_dict['type']} data")
                        data_dict['name'] = name
                        return data_dict
        except (OSError, ValueError) as e:
            print(f"Error reading FITS file {fits_path}: {e}")
            return None

        print(f"No usable data found in {fits_path}")
        return None

    def _table_to_data(self, hdu):
        columns = {c.upper(): c for c in hdu.columns.names}

        if 'DATA' in columns:
            values = np.array(hdu.data[columns['DATA']], dtype=float)
            if values.ndim == 1:
                # One number per row: a time series
                return {'type': 'continuum', 'data': values}
            # One spectrum per row (SDFITS); flagged channels are NaN
            spectra = values.reshape(values.shape[0], -1)
            with warnings.catch_warnings():
                # Channels flagged in every row average to NaN; that's expected
                warnings.simplefilter('ignore', RuntimeWarning)
                spectrum = np.nanmean(spectra, axis=0)
            return {'type': 'spectrum', 'data': spectrum}

        for col in hdu.columns.names:
            values = np.asarray(hdu.data[col])
            if np.issubdtype(values.dtype, np.number):
                return {'type': 'generic', 'data': values.astype(float)}
        return None

    def generate_synthetic_data(self, num_pieces=3):
        """
        Generate synthetic radio telescope datasets, cycling through pulsar,
        spectral line and continuum types until num_pieces exist.

        These are stylised stand-ins for real observations, built to give
        musically interesting material rather than to model the physics.
        """
        print(f"Generating {num_pieces} synthetic radio telescope dataset(s)...")
        generators = {
            'pulsar': self._synthetic_pulsar,
            'spectrum': self._synthetic_spectrum,
            'continuum': self._synthetic_continuum,
        }
        labels = {'pulsar': 'Pulsar', 'spectrum': 'Spectral Line', 'continuum': 'Continuum'}

        datasets = []
        for i in range(num_pieces):
            kind = SYNTHETIC_TYPES[i % len(SYNTHETIC_TYPES)]
            data_dict = generators[kind]()
            data_dict['name'] = f"Synthetic {labels[kind]} {i // len(SYNTHETIC_TYPES) + 1}"
            datasets.append(data_dict)
        return datasets

    def _synthetic_pulsar(self):
        """Pulse train with pulse-to-pulse brightness changes and occasional nulls."""
        data_rate = 1000  # samples per second
        duration = 120    # seconds
        period = self.rng.uniform(0.3, 1.5)
        duty = 0.03       # pulse width as a fraction of the period

        t = np.arange(duration * data_rate) / data_rate
        pulse_index = (t // period).astype(int)
        phase = (t / period) % 1.0
        profile = np.exp(-0.5 * ((phase - 0.5) / duty) ** 2)

        pulse_amps = self.rng.lognormal(0, 0.4, pulse_index[-1] + 1)
        pulse_amps[self.rng.random(len(pulse_amps)) < 0.05] = 0  # nulling

        intensity = profile * pulse_amps[pulse_index]
        intensity += self.rng.normal(0, 0.2, len(t))

        return {'type': 'pulsar', 'data': intensity,
                'data_rate': data_rate, 'period': period}

    def _synthetic_spectrum(self):
        """Emission lines on a noisy baseline around the 21 cm hydrogen line."""
        freq_axis = np.linspace(1420.0, 1421.0, 8192)  # MHz
        spectrum = np.zeros_like(freq_axis)

        for _ in range(5):
            center = self.rng.uniform(1420.1, 1420.9)
            width = self.rng.uniform(0.01, 0.05)
            amplitude = self.rng.uniform(0.5, 2.0)
            spectrum += amplitude * np.exp(-(freq_axis - center) ** 2 / (2 * width ** 2))

        spectrum += self.rng.normal(0, 0.1, len(freq_axis))
        return {'type': 'spectrum', 'data': spectrum, 'frequencies': freq_axis}

    def _synthetic_continuum(self):
        """One hour of total power with slow and fast variations."""
        time_series = np.linspace(0, 3600, 50000)
        continuum = 10 + 2 * np.sin(2 * np.pi * time_series / self.rng.uniform(300, 900))
        continuum += 0.5 * np.sin(2 * np.pi * time_series / self.rng.uniform(30, 90))
        continuum += self.rng.normal(0, 0.3, len(time_series))
        return {'type': 'continuum', 'data': continuum, 'time': time_series}

    # ------------------------------------------------------------------
    # Sonification
    # ------------------------------------------------------------------

    def sonify_data(self, data_dict, duration_minutes=5):
        """
        Convert telescope data into mono audio. The technique depends on
        data_dict['type']: 'pulsar', 'spectrum', 'continuum' or 'generic'.
        """
        duration_samples = int(duration_minutes * 60 * self.sample_rate)

        if data_dict['type'] == 'pulsar':
            return self._sonify_pulsar(data_dict, duration_samples)
        elif data_dict['type'] == 'spectrum':
            return self._sonify_spectrum(data_dict, duration_samples)
        elif data_dict['type'] == 'continuum':
            return self._sonify_continuum(data_dict, duration_samples)
        else:
            return self._sonify_generic(data_dict['data'], duration_samples)

    def _sonify_pulsar(self, data_dict, duration_samples):
        """
        One bass hit per beat at self.bpm. Each hit's loudness comes from the
        brightness of successive real pulses, and its timbre from the shape
        of the folded pulse profile.
        """
        print(f"Sonifying pulsar data (rhythmic mode, {self.bpm} BPM)...")

        intensity = np.nan_to_num(np.asarray(data_dict['data'], dtype=float))
        data_rate = data_dict['data_rate']
        period = data_dict['period']

        t_data = np.arange(len(intensity)) / data_rate
        pulse_index = (t_data // period).astype(int)

        # Fold at the pulse period to get the average profile
        n_bins = 128
        phase_bin = ((t_data / period) % 1.0 * n_bins).astype(int)
        counts = np.maximum(np.bincount(phase_bin, minlength=n_bins), 1)
        profile = np.bincount(phase_bin, weights=intensity, minlength=n_bins) / counts
        profile -= profile.min()

        # Brightness of each individual pulse becomes per-beat velocity
        energies = np.bincount(pulse_index, weights=intensity)
        energies = np.clip(energies / (np.percentile(energies, 95) + 1e-10), 0, 1)

        # Harmonic content of the profile shapes the bass timbre
        harmonics = np.abs(np.fft.rfft(profile))[1:9]
        harmonics /= harmonics.max() + 1e-10

        base_freq = 55  # A1
        beat_len = 60 / self.bpm * self.sample_rate
        hit_len = int(beat_len)
        t_hit = np.arange(hit_len) / self.sample_rate
        hit = sum(amp * np.sin(2 * np.pi * base_freq * (k + 1) * t_hit) / (k + 1)
                  for k, amp in enumerate(harmonics))
        hit *= np.exp(-t_hit / 0.25)
        hit *= np.minimum(t_hit / 0.005, 1.0)  # 5 ms attack to avoid clicks
        hit /= np.max(np.abs(hit)) + 1e-10

        audio = np.zeros(duration_samples)
        n_beats = int(np.ceil(duration_samples / beat_len))
        for i in range(n_beats):
            start = int(round(i * beat_len))
            end = min(start + hit_len, duration_samples)
            audio[start:end] += energies[i % len(energies)] * hit[:end - start]

        # Sustained pad on the same harmonic series, swelling slowly
        t = np.arange(duration_samples) / self.sample_rate
        pad = np.zeros(duration_samples)
        for k, amp in enumerate(harmonics):
            lfo = 0.5 + 0.5 * np.sin(2 * np.pi * self.rng.uniform(0.02, 0.1) * t
                                     + self.rng.uniform(0, 2 * np.pi))
            pad += amp * lfo * np.sin(2 * np.pi * 2 * base_freq * (k + 1) * t)
        pad /= np.max(np.abs(pad)) + 1e-10

        audio += 0.25 * pad
        audio += self.rng.normal(0, 0.01, duration_samples)
        return audio

    def _spectral_peaks(self, spectrum, max_voices=12):
        """Indices of the most prominent distinct peaks, strongest first."""
        peaks, props = signal.find_peaks(spectrum, prominence=0.05,
                                         distance=max(1, len(spectrum) // 200))
        if len(peaks) == 0:
            return np.array([int(np.argmax(spectrum))])
        order = np.argsort(props['prominences'])[::-1][:max_voices]
        return peaks[order]

    def _sonify_spectrum(self, data_dict, duration_samples):
        """
        One drone voice per spectral line, with the line's position mapped
        to pitch (snapped to the nearest semitone) and its strength to level.
        """
        print("Sonifying spectral data (ambient drone mode)...")

        spectrum = np.nan_to_num(np.asarray(data_dict['data'], dtype=float))
        spectrum = (spectrum - spectrum.min()) / (np.ptp(spectrum) + 1e-10)

        # Smooth before peak finding so noise spikes don't count as lines
        smooth = signal.savgol_filter(spectrum, min(51, len(spectrum) // 2 * 2 - 1), 3) \
            if len(spectrum) > 7 else spectrum
        peaks = self._spectral_peaks(smooth)

        min_audio_freq = 110  # A2
        max_audio_freq = 880  # A5
        audio_freqs = np.logspace(np.log10(min_audio_freq), np.log10(max_audio_freq),
                                  len(spectrum))

        t = np.arange(duration_samples) / self.sample_rate
        audio = np.zeros(duration_samples)

        for idx in peaks:
            semitones = np.round(12 * np.log2(audio_freqs[idx] / 440))
            freq = 440 * 2 ** (semitones / 12)
            amplitude = smooth[idx]

            mod_freq = self.rng.uniform(0.05, 0.2)
            envelope = 0.5 + 0.5 * np.sin(2 * np.pi * mod_freq * t
                                          + self.rng.uniform(0, 2 * np.pi))
            audio += amplitude * envelope * np.sin(2 * np.pi * freq * t)

        audio /= np.max(np.abs(audio)) + 1e-10
        audio += 0.4 * np.sin(2 * np.pi * 55 * t)  # A1 sub-bass drone

        sos = signal.butter(4, 2000, 'low', fs=self.sample_rate, output='sos')
        return signal.sosfilt(sos, audio)

    def _sonify_continuum(self, data_dict, duration_samples):
        """
        Sonify continuum variations as parameter modulation.
        """
        print("Sonifying continuum data (modulation mode)...")

        continuum = np.nan_to_num(np.asarray(data_dict['data'], dtype=float))
        continuum = (continuum - continuum.min()) / (np.ptp(continuum) + 1e-10)

        # Interpolate to audio sample rate
        x_old = np.linspace(0, 1, len(continuum))
        x_new = np.linspace(0, 1, duration_samples)
        kind = 'cubic' if len(continuum) >= 4 else 'linear'
        continuum_resampled = interp1d(x_old, continuum, kind=kind)(x_new)

        # Frequency modulation - continuum controls pitch
        base_freq = 220  # A3
        freq_variation = 50  # Hz variation range
        instantaneous_freq = base_freq + continuum_resampled * freq_variation

        phase = np.cumsum(2 * np.pi * instantaneous_freq / self.sample_rate)
        amp_mod = 0.3 + 0.7 * continuum_resampled
        audio = np.sin(phase) * amp_mod
        audio += 0.5 * np.sin(phase * 2) * amp_mod  # second voice an octave up

        # Filtered noise that follows the continuum
        noise = self.rng.normal(0, 1, duration_samples)
        noise_filtered = signal.lfilter([1], [1, -0.95], noise)
        noise_filtered /= np.max(np.abs(noise_filtered)) + 1e-10
        audio += 0.2 * noise_filtered * continuum_resampled

        return audio

    def _sonify_generic(self, data, duration_samples):
        """
        Generic sonification for unknown data types.
        """
        print("Sonifying data (generic mode)...")

        data = np.nan_to_num(np.asarray(data, dtype=float).ravel())

        if len(data) > 100000:
            data = data[::len(data) // 100000]

        data = (data - np.mean(data)) / (np.std(data) + 1e-10)

        x_old = np.linspace(0, 1, len(data))
        x_new = np.linspace(0, 1, duration_samples)
        audio = interp1d(x_old, data, kind='linear')(x_new)

        return audio * 0.3

    # ------------------------------------------------------------------
    # Effects and output
    # ------------------------------------------------------------------

    def add_effects(self, audio, reverb_seconds=2.5, reverb_mix=0.35):
        """
        Compress, then add a stereo reverb. Returns a (samples, 2) array.
        """
        print("Adding ambient effects (compression, reverb)...")

        # Level-match first so the compressor treats every mode alike
        audio = audio / (np.max(np.abs(audio)) + 1e-10)

        threshold = 0.7
        ratio = 3
        mask = np.abs(audio) > threshold
        audio[mask] = np.sign(audio[mask]) * (
            threshold + (np.abs(audio[mask]) - threshold) / ratio
        )

        # Reverb: convolve with exponentially decaying noise (-60 dB at
        # reverb_seconds). A different noise burst per channel decorrelates
        # left and right, which is what gives the stereo width.
        ir_len = int(reverb_seconds * self.sample_rate)
        t_ir = np.arange(ir_len) / self.sample_rate
        decay = np.exp(-6.9 * t_ir / reverb_seconds)
        damping = signal.butter(2, min(6000, self.sample_rate * 0.45), 'low',
                                fs=self.sample_rate, output='sos')

        channels = []
        for _ in range(2):
            ir = signal.sosfilt(damping, self.rng.normal(0, 1, ir_len)) * decay
            ir /= np.sqrt(np.sum(ir ** 2)) + 1e-10
            wet = signal.oaconvolve(audio, ir)[:len(audio)]
            channels.append((1 - reverb_mix) * audio + reverb_mix * wet)

        stereo = np.column_stack(channels)
        return stereo / (np.max(np.abs(stereo)) + 1e-10) * 0.9

    def save_audio(self, audio, name, subtype='PCM_24'):
        """
        Save audio to a WAV file (24-bit by default; pass subtype='FLOAT'
        for 32-bit float).
        """
        audio = np.clip(audio, -1.0, 1.0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"gbt_ambient_{name}_{timestamp}.wav"

        sf.write(filename, audio, self.sample_rate, subtype=subtype)
        print(f"\n✓ Saved: {filename}")
        print(f"  Duration: {len(audio)/self.sample_rate:.1f} seconds")
        print(f"  Format: {self.sample_rate} Hz, {subtype}, "
              f"{'stereo' if audio.ndim == 2 else 'mono'}")

        return filename

    def create_ambient_pieces(self, num_pieces=3, duration_minutes=5, fits_files=None,
                              subtype='PCM_24'):
        """
        Create ambient pieces: one per FITS file if fits_files is given,
        otherwise num_pieces from synthetic data.
        """
        print("=" * 60)
        print("GBT DATA SONIFICATION - AMBIENT LOFI GENERATOR")
        print("=" * 60)

        if fits_files:
            datasets = [d for d in (self.load_fits(p) for p in fits_files) if d is not None]
        else:
            datasets = self.generate_synthetic_data(num_pieces)

        audio_files = []
        for i, data_dict in enumerate(datasets):
            print(f"\n--- Processing dataset {i+1}/{len(datasets)}: {data_dict['name']} ---")

            audio = self.sonify_data(data_dict, duration_minutes)
            audio = self.add_effects(audio)

            dataset_name = data_dict['name'].replace(' ', '_').lower()
            audio_files.append(self.save_audio(audio, dataset_name, subtype=subtype))

        print("\n" + "=" * 60)
        print(f"✓ Created {len(audio_files)} ambient pieces!")
        print(f"✓ Files saved to: {self.output_dir}/")
        print("=" * 60)
        print("\nThese files are ready to use in your lofi production!")
        print("Try layering them, time-stretching, or adding your own beats.")

        return audio_files


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Turn Green Bank Telescope data into ambient audio.")
    parser.add_argument('--fits', nargs='+', metavar='FILE',
                        help="FITS/SDFITS files to sonify (one piece each). "
                             "Without this, synthetic data is used.")
    parser.add_argument('--pieces', type=int, default=3,
                        help="number of synthetic pieces (default: 3)")
    parser.add_argument('--minutes', type=float, default=5,
                        help="length of each piece in minutes (default: 5)")
    parser.add_argument('--seed', type=int,
                        help="random seed, to reproduce a run exactly")
    parser.add_argument('--bpm', type=float, default=80,
                        help="tempo of pulsar pieces (default: 80)")
    parser.add_argument('--sample-rate', type=int, default=44100,
                        help="output sample rate in Hz (default: 44100)")
    parser.add_argument('--float', action='store_true',
                        help="write 32-bit float WAVs instead of 24-bit")
    parser.add_argument('--out', default="gbt_ambient_audio",
                        help="output folder (default: gbt_ambient_audio)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    sonifier = GBTSonifier(output_dir=args.out, sample_rate=args.sample_rate,
                           seed=args.seed, bpm=args.bpm)
    sonifier.create_ambient_pieces(
        num_pieces=args.pieces,
        duration_minutes=args.minutes,
        fits_files=args.fits,
        subtype='FLOAT' if args.float else 'PCM_24',
    )

    print("\n🎵 Happy creating! These cosmic sounds are ready for your lofi beats.")


if __name__ == "__main__":
    main()
