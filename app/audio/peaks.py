import numpy as np
import librosa
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter

def find_spectral_peaks(
    S_db: np.ndarray,
    amp_min: float = -40,
    neighborhood_size: int = 20
) -> list[tuple[int, int]]:
    """
    Find local spectral peaks in a log-magnitude spectrogram.

    Returns:
        peaks: list of (time_index, freq_index)
    """
    # Apply local maximum filter
    local_max = maximum_filter(
        S_db,
        size=(neighborhood_size, neighborhood_size)
    ) == S_db

    # Apply amplitude threshold
    detected_peaks = local_max & (S_db >= amp_min)

    # Get indices
    freq_idxs, time_idxs = np.where(detected_peaks)

    # Convert to (time, freq) tuples
    peaks = list(zip(time_idxs, freq_idxs))

    return peaks
