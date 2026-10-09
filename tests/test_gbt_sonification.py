import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf
from astropy.io import fits

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gbt_sonification import GBTSonifier, main  # noqa: E402

SR = 8000  # low sample rate keeps the tests fast


def make_sonifier(tmp_path, **kwargs):
    kwargs.setdefault('sample_rate', SR)
    kwargs.setdefault('seed', 1)
    return GBTSonifier(output_dir=tmp_path / 'out', **kwargs)


def write_sdfits(path, n_rows=4, n_chan=512):
    """Minimal SDFITS-style file: a binary table with a DATA spectrum per row."""
    chan = np.arange(n_chan)
    line = np.exp(-0.5 * ((chan - 200) / 5) ** 2) + 0.5 * np.exp(-0.5 * ((chan - 350) / 5) ** 2)
    spectra = np.tile(line, (n_rows, 1)) + np.random.default_rng(0).normal(0, 0.01, (n_rows, n_chan))
    spectra[:, :10] = np.nan  # flagged channels
    cols = [
        fits.Column(name='DATA', format=f'{n_chan}E', array=spectra.astype(np.float32)),
        fits.Column(name='TSYS', format='E', array=np.full(n_rows, 20.0, dtype=np.float32)),
    ]
    fits.HDUList([fits.PrimaryHDU(), fits.BinTableHDU.from_columns(cols)]).writeto(path)


def test_synthetic_respects_num_pieces(tmp_path):
    datasets = make_sonifier(tmp_path).generate_synthetic_data(5)
    assert [d['type'] for d in datasets] == ['pulsar', 'spectrum', 'continuum', 'pulsar', 'spectrum']
    assert len({d['name'] for d in datasets}) == 5


def test_seed_reproduces_audio(tmp_path):
    def render(seed):
        s = make_sonifier(tmp_path, seed=seed)
        return [s.add_effects(s.sonify_data(d, 0.05)) for d in s.generate_synthetic_data(3)]

    a, b, c = render(7), render(7), render(8)
    assert all(np.array_equal(x, y) for x, y in zip(a, b))
    assert not np.array_equal(a[0], c[0])


def test_pulsar_hits_land_on_the_beat(tmp_path):
    s = make_sonifier(tmp_path, bpm=120)
    pulsar = s.generate_synthetic_data(1)[0]
    audio = s.sonify_data(pulsar, 0.25)

    beat = int(60 / 120 * SR)
    window = int(0.05 * SR)
    starts = [np.abs(audio[i:i + window]).mean() for i in range(0, len(audio) - beat, beat)]
    tails = [np.abs(audio[i + beat - window:i + beat]).mean() for i in range(0, len(audio) - beat, beat)]
    # Each beat should open louder than it ends, except on nulled pulses
    assert np.mean(np.array(starts) > np.array(tails)) > 0.8


def test_spectral_peaks_are_distinct_lines(tmp_path):
    s = make_sonifier(tmp_path)
    x = np.arange(8192)
    spectrum = sum(np.exp(-0.5 * ((x - c) / 40) ** 2) for c in (1000, 4000, 7000))
    peaks = sorted(s._spectral_peaks(spectrum))
    assert len(peaks) == 3
    assert all(abs(p - c) < 5 for p, c in zip(peaks, (1000, 4000, 7000)))


def test_load_sdfits_with_nans(tmp_path):
    path = tmp_path / 'obs.fits'
    write_sdfits(path)
    data = make_sonifier(tmp_path).load_fits(path)
    assert data['type'] == 'spectrum'
    assert data['name'] == 'obs'
    assert data['data'].shape == (512,)


def test_load_fits_bad_file_returns_none(tmp_path):
    path = tmp_path / 'junk.fits'
    path.write_text('not a fits file')
    assert make_sonifier(tmp_path).load_fits(path) is None


def test_end_to_end_writes_stereo_24bit(tmp_path):
    path = tmp_path / 'obs.fits'
    write_sdfits(path)
    s = GBTSonifier(output_dir=tmp_path / 'nested' / 'dir', sample_rate=SR, seed=1)
    files = s.create_ambient_pieces(duration_minutes=0.05, fits_files=[path])

    assert len(files) == 1
    info = sf.info(files[0])
    assert info.channels == 2
    assert info.subtype == 'PCM_24'
    audio, _ = sf.read(files[0])
    assert 0.5 < np.max(np.abs(audio)) <= 0.9 + 1e-3


@pytest.mark.parametrize('pieces', [1, 4])
def test_cli_synthetic(tmp_path, pieces):
    out = tmp_path / 'cli'
    main(['--pieces', str(pieces), '--minutes', '0.02', '--seed', '3',
          '--sample-rate', str(SR), '--float', '--out', str(out)])
    files = list(out.glob('*.wav'))
    assert len(files) == pieces
    assert all(sf.info(f).subtype == 'FLOAT' for f in files)
