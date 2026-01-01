import numpy as np
import librosa
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter

def compute_spectrogram(
    audio: np.ndarray,
    sr: int,
    n_fft: int = 2048,
    hop_length: int = 512
) -> np.ndarray:
    """
    Convert time-domain audio into a log-magnitude spectrogram.

    Returns:
        S_db (np.ndarray): shape (freq_bins, time_frames)
    """
    # Short-Time Fourier Transform
    S = librosa.stft(
        audio,
        n_fft=n_fft,
        hop_length=hop_length,
        window="hann"
    )

    # Magnitude
    S_mag = np.abs(S)

    # Convert to decibels
    S_db = librosa.amplitude_to_db(S_mag, ref=np.max)

    return S_db
