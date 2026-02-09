#!/usr/bin/env python3
"""
Green Bank Telescope Data Sonification Script
Automatically downloads GBT data and creates ambient soundscapes for music production.

Requirements:
    pip install astropy numpy scipy soundfile requests

Usage:
    python gbt_sonification.py
"""

import numpy as np
from scipy import signal
from scipy.interpolate import interp1d
import soundfile as sf
import requests
from astropy.io import fits
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class GBTSonifier:
    def __init__(self, output_dir="gbt_ambient_audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.sample_rate = 44100  # CD quality
        
    def download_gbt_data(self, max_files=3):
        """
        Download publicly available GBT data.
        Using the GBT Archive API to get recent observations.
        """
        print("Searching for Green Bank Telescope data...")
        
        # GBT Archive search URL
        archive_url = "https://archive.nrao.edu/archive/advquery.jsp"
        
        # Parameters for pulsar and spectral line observations (most interesting for sonification)
        search_params = {
            'TELESCOPE': 'GBT',
            'ARCHIVE': 'GBT',
            'MAX_ROWS': max_files,
            'FORMAT': 'JSON'
        }
        
        try:
            response = requests.get(archive_url, params=search_params, timeout=30)
            
            if response.status_code == 200:
                # Try to parse the response
                try:
                    data = response.json()
                    print(f"Found {len(data)} observations")
                    return data
                except:
                    print("Using alternative method to access GBT data...")
                    # Fallback: Try direct FITS file access from known public datasets
                    return self._get_sample_data()
            else:
                print(f"Archive returned status {response.status_code}, using sample data approach")
                return self._get_sample_data()
                
        except Exception as e:
            print(f"Connection error: {e}")
            print("Generating synthetic radio telescope data for demonstration...")
            return self._generate_synthetic_data()
    
    def _get_sample_data(self):
        """
        Try to access publicly available GBT FITS files directly.
        These are often available from NRAO's public data releases.
        """
        # Known public GBT data URLs (examples)
        sample_urls = [
            "https://data.nrao.edu/gbt/sample_pulsar_data.fits",
            "https://archive.nrao.edu/pub/gbt/sample_spectral.fits",
        ]
        
        data_files = []
        for url in sample_urls:
            try:
                print(f"Attempting to download from {url}...")
                response = requests.get(url, timeout=20, stream=True)
                if response.status_code == 200:
                    filename = self.output_dir / url.split('/')[-1]
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    data_files.append(filename)
                    print(f"Downloaded: {filename}")
            except Exception as e:
                print(f"Could not download from {url}: {e}")
        
        if not data_files:
            # If no downloads work, generate synthetic data
            return self._generate_synthetic_data()
        
        return data_files
    
    def _generate_synthetic_data(self):
        """
        Generate synthetic radio telescope data that mimics real observations.
        Useful for testing and when real data isn't accessible.
        """
        print("Generating synthetic radio telescope data...")
        
        synthetic_datasets = []
        
        # Dataset 1: Pulsar-like signal
        print("Creating pulsar-like signal dataset...")
        time = np.linspace(0, 100, 100000)
        pulsar_period = 0.5  # 500ms period
        pulsar_signal = np.sin(2 * np.pi * time / pulsar_period)
        pulsar_signal += np.random.normal(0, 0.3, len(time))  # Add noise
        
        # Add dispersion-like effects
        frequencies = np.linspace(1200, 1600, 1000)  # MHz
        dispersed = np.zeros((len(frequencies), len(time)))
        for i, freq in enumerate(frequencies):
            delay = 100 * (1/freq**2 - 1/frequencies[-1]**2)
            delay_samples = int(delay * 100)
            if delay_samples < len(time):
                dispersed[i, delay_samples:] = pulsar_signal[:-delay_samples if delay_samples > 0 else None]
        
        synthetic_datasets.append({
            'type': 'pulsar',
            'data': dispersed,
            'frequencies': frequencies,
            'time': time,
            'name': 'Synthetic Pulsar'
        })
        
        # Dataset 2: Spectral line emission
        print("Creating spectral line dataset...")
        freq_axis = np.linspace(1420.0, 1421.0, 8192)  # Around hydrogen line
        spectrum = np.zeros_like(freq_axis)
        
        # Add multiple emission/absorption lines
        for _ in range(5):
            center = np.random.uniform(1420.1, 1420.9)
            width = np.random.uniform(0.01, 0.05)
            amplitude = np.random.uniform(0.5, 2.0)
            spectrum += amplitude * np.exp(-(freq_axis - center)**2 / (2 * width**2))
        
        spectrum += np.random.normal(0, 0.1, len(freq_axis))  # Noise
        
        synthetic_datasets.append({
            'type': 'spectrum',
            'data': spectrum,
            'frequencies': freq_axis,
            'name': 'Synthetic Spectral Line'
        })
        
        # Dataset 3: Continuum with variations
        print("Creating continuum variation dataset...")
        time_series = np.linspace(0, 3600, 50000)  # 1 hour observation
        continuum = 10 + 2 * np.sin(2 * np.pi * time_series / 600)  # 10-minute variation
        continuum += 0.5 * np.sin(2 * np.pi * time_series / 60)  # 1-minute variation
        continuum += np.random.normal(0, 0.3, len(time_series))
        
        synthetic_datasets.append({
            'type': 'continuum',
            'data': continuum,
            'time': time_series,
            'name': 'Synthetic Continuum'
        })
        
        print(f"Generated {len(synthetic_datasets)} synthetic datasets")
        return synthetic_datasets
    
    def process_fits_file(self, fits_path):
        """
        Process a FITS file and extract data for sonification.
        """
        try:
            with fits.open(fits_path) as hdul:
                print(f"\nProcessing: {fits_path}")
                print(f"File contains {len(hdul)} HDU(s)")
                
                # Look for data in the primary HDU or first extension
                for i, hdu in enumerate(hdul):
                    if hdu.data is not None and hdu.data.size > 0:
                        print(f"Found data in HDU {i}: shape {hdu.data.shape}")
                        return hdu.data
                
        except Exception as e:
            print(f"Error reading FITS file: {e}")
            return None
    
    def sonify_data(self, data_dict, duration_minutes=5):
        """
        Convert telescope data into audio using multiple sonification techniques.
        Creates rich, ambient soundscapes.
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
        Sonify pulsar data with rhythmic elements - great for lofi beats!
        """
        print("Sonifying pulsar data (rhythmic mode)...")
        
        # Extract pulsar timing
        pulsar_data = data_dict['data']
        
        # Get time-integrated profile
        if len(pulsar_data.shape) > 1:
            profile = np.mean(pulsar_data, axis=0)
        else:
            profile = pulsar_data
        
        # Normalize
        profile = (profile - np.mean(profile)) / (np.std(profile) + 1e-10)
        
        # Create audio by repeating and varying the pulsar pulse
        num_periods = duration_samples // len(profile) + 1
        
        # Generate base pulse train
        audio = np.tile(profile, num_periods)[:duration_samples]
        
        # Map to audio frequency range (creating a bass pulse)
        base_freq = 55  # A1 note - deep bass
        audio = audio * 0.5  # Amplitude modulation
        
        # Add harmonic richness
        t = np.linspace(0, duration_samples / self.sample_rate, duration_samples)
        
        # Bass tone that follows the pulse
        carrier = np.sin(2 * np.pi * base_freq * t)
        audio = audio * carrier
        
        # Add evolving pad (using FFT of pulsar data for spectral content)
        if len(pulsar_data.shape) > 1:
            spectrum = np.mean(np.abs(np.fft.fft(pulsar_data, axis=1)), axis=0)
            spectrum = spectrum[:len(spectrum)//2]  # Positive frequencies only
            
            # Map spectrum to musical frequencies
            pad = np.zeros(duration_samples)
            for i, amp in enumerate(spectrum[:50]):  # Use first 50 bins
                freq = base_freq * (1 + i * 0.5)  # Harmonic series
                pad += amp * np.sin(2 * np.pi * freq * t)
            
            pad = pad / (np.max(np.abs(pad)) + 1e-10) * 0.3
            audio = audio + pad
        
        # Add subtle noise texture
        noise = np.random.normal(0, 0.05, duration_samples)
        audio = audio + noise
        
        return audio
    
    def _sonify_spectrum(self, data_dict, duration_samples):
        """
        Sonify spectral line data as evolving drone/ambient texture.
        """
        print("Sonifying spectral data (ambient drone mode)...")
        
        spectrum = data_dict['data']
        frequencies = data_dict['frequencies']
        
        # Normalize spectrum
        spectrum = (spectrum - np.min(spectrum)) / (np.max(spectrum) - np.min(spectrum) + 1e-10)
        
        # Map radio frequencies to audio frequencies
        # Use logarithmic mapping for musical intervals
        min_audio_freq = 110  # A2
        max_audio_freq = 880  # A5
        
        audio_freqs = np.logspace(
            np.log10(min_audio_freq),
            np.log10(max_audio_freq),
            len(spectrum)
        )
        
        # Create time axis
        t = np.linspace(0, duration_samples / self.sample_rate, duration_samples)
        
        # Build the audio as a sum of sine waves (additive synthesis)
        audio = np.zeros(duration_samples)
        
        # Use top 20 spectral features to avoid too much clutter
        top_indices = np.argsort(spectrum)[-20:]
        
        for idx in top_indices:
            freq = audio_freqs[idx]
            amplitude = spectrum[idx] * 0.3
            
            # Add slow amplitude modulation for movement
            mod_freq = np.random.uniform(0.05, 0.2)  # Very slow modulation
            envelope = 0.5 + 0.5 * np.sin(2 * np.pi * mod_freq * t)
            
            audio += amplitude * envelope * np.sin(2 * np.pi * freq * t)
        
        # Add sub-bass drone
        sub_bass = 0.4 * np.sin(2 * np.pi * 55 * t)  # A1
        audio += sub_bass
        
        # Apply gentle low-pass filter for smoothness
        sos = signal.butter(4, 2000, 'low', fs=self.sample_rate, output='sos')
        audio = signal.sosfilt(sos, audio)
        
        return audio
    
    def _sonify_continuum(self, data_dict, duration_samples):
        """
        Sonify continuum variations as parameter modulation.
        """
        print("Sonifying continuum data (modulation mode)...")
        
        continuum = data_dict['data']
        
        # Normalize to 0-1 range
        continuum = (continuum - np.min(continuum)) / (np.max(continuum) - np.min(continuum) + 1e-10)
        
        # Interpolate to audio sample rate
        x_old = np.linspace(0, 1, len(continuum))
        x_new = np.linspace(0, 1, duration_samples)
        interp = interp1d(x_old, continuum, kind='cubic')
        continuum_resampled = interp(x_new)
        
        # Use continuum to modulate multiple parameters
        t = np.linspace(0, duration_samples / self.sample_rate, duration_samples)
        
        # Frequency modulation - continuum controls pitch
        base_freq = 220  # A3
        freq_variation = 50  # Hz variation range
        instantaneous_freq = base_freq + continuum_resampled * freq_variation
        
        # Create frequency-modulated carrier
        phase = np.cumsum(2 * np.pi * instantaneous_freq / self.sample_rate)
        audio = np.sin(phase)
        
        # Amplitude modulation - add slow swell
        amp_mod = 0.3 + 0.7 * continuum_resampled
        audio = audio * amp_mod
        
        # Add second voice an octave up
        audio += 0.5 * np.sin(phase * 2) * amp_mod
        
        # Add filtered noise that follows the continuum
        noise = np.random.normal(0, 1, duration_samples)
        noise_filtered = signal.lfilter([1], [1, -0.95], noise)  # Low-pass
        noise_filtered = noise_filtered / (np.max(np.abs(noise_filtered)) + 1e-10)
        audio += 0.2 * noise_filtered * continuum_resampled
        
        return audio
    
    def _sonify_generic(self, data, duration_samples):
        """
        Generic sonification for unknown data types.
        """
        print("Sonifying data (generic mode)...")
        
        # Flatten if multi-dimensional
        if len(data.shape) > 1:
            data = data.flatten()
        
        # Use a subset if data is too large
        if len(data) > 100000:
            step = len(data) // 100000
            data = data[::step]
        
        # Normalize
        data = (data - np.mean(data)) / (np.std(data) + 1e-10)
        
        # Interpolate to audio length
        x_old = np.linspace(0, 1, len(data))
        x_new = np.linspace(0, 1, duration_samples)
        interp = interp1d(x_old, data, kind='linear')
        audio = interp(x_new)
        
        # Scale to reasonable amplitude
        audio = audio * 0.3
        
        return audio
    
    def add_effects(self, audio):
        """
        Add reverb and other effects for ambient quality.
        """
        print("Adding ambient effects (reverb, filtering)...")
        
        # Simple reverb using comb filters
        delay_samples = int(0.05 * self.sample_rate)  # 50ms delay
        reverb = np.zeros_like(audio)
        reverb[delay_samples:] = audio[:-delay_samples] * 0.3
        
        delay_samples_2 = int(0.07 * self.sample_rate)
        reverb[delay_samples_2:] += audio[:-delay_samples_2] * 0.2
        
        audio = audio + reverb
        
        # Gentle compression (simple)
        threshold = 0.7
        ratio = 3
        mask = np.abs(audio) > threshold
        audio[mask] = np.sign(audio[mask]) * (
            threshold + (np.abs(audio[mask]) - threshold) / ratio
        )
        
        # Final normalization
        audio = audio / (np.max(np.abs(audio)) + 1e-10) * 0.9
        
        return audio
    
    def save_audio(self, audio, name):
        """
        Save audio to WAV file.
        """
        # Ensure audio is in valid range
        audio = np.clip(audio, -1.0, 1.0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"gbt_ambient_{name}_{timestamp}.wav"
        
        sf.write(filename, audio, self.sample_rate)
        print(f"\n✓ Saved: {filename}")
        print(f"  Duration: {len(audio)/self.sample_rate:.1f} seconds")
        print(f"  Sample rate: {self.sample_rate} Hz")
        
        return filename
    
    def create_ambient_pieces(self, num_pieces=3, duration_minutes=5):
        """
        Main function to download data and create ambient pieces.
        """
        print("=" * 60)
        print("GBT DATA SONIFICATION - AMBIENT LOFI GENERATOR")
        print("=" * 60)
        
        # Get data (real or synthetic)
        data_sources = self.download_gbt_data(max_files=num_pieces)
        
        audio_files = []
        
        # Process each dataset
        for i, data_source in enumerate(data_sources):
            print(f"\n--- Processing dataset {i+1}/{len(data_sources)} ---")
            
            if isinstance(data_source, dict):
                # Synthetic data
                dataset_name = data_source['name'].replace(' ', '_').lower()
                audio = self.sonify_data(data_source, duration_minutes)
            else:
                # Real FITS file
                fits_data = self.process_fits_file(data_source)
                if fits_data is not None:
                    dataset_name = f"real_data_{i}"
                    data_dict = {
                        'type': 'generic',
                        'data': fits_data
                    }
                    audio = self.sonify_data(data_dict, duration_minutes)
                else:
                    continue
            
            # Add effects
            audio = self.add_effects(audio)
            
            # Save
            filename = self.save_audio(audio, dataset_name)
            audio_files.append(filename)
        
        print("\n" + "=" * 60)
        print(f"✓ Created {len(audio_files)} ambient pieces!")
        print(f"✓ Files saved to: {self.output_dir}/")
        print("=" * 60)
        print("\nThese files are ready to use in your lofi production!")
        print("Try layering them, time-stretching, or adding your own beats.")
        
        return audio_files


def main():
    """
    Main execution function.
    """
    # Create sonifier
    sonifier = GBTSonifier(output_dir="gbt_ambient_audio")
    
    # Generate 3 ambient pieces, each 5 minutes long
    audio_files = sonifier.create_ambient_pieces(
        num_pieces=3,
        duration_minutes=5
    )
    
    print("\n🎵 Happy creating! These cosmic sounds are ready for your lofi beats.")


if __name__ == "__main__":
    main()
