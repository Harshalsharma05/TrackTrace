import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter

def generate_fingerprints(
    peaks: list[tuple[int, int]],
    fan_value: int = 5,
    min_time_delta: int = 1,
    max_time_delta: int = 200
) -> list[tuple[str, int]]:
    """
    Generate fingerprint hashes from spectral peaks.

    Args:
        peaks: list of (time_idx, freq_idx)
        fan_value: number of target peaks per anchor
        min_time_delta: minimum time difference (frames)
        max_time_delta: maximum time difference (frames)

    Returns:
        fingerprints: list of (hash, offset)
    """
    fingerprints = []

    # Sort peaks by time
    peaks = sorted(peaks, key=lambda x: x[0])

    for i in range(len(peaks)):
        t1, f1 = peaks[i]

        for j in range(1, fan_value + 1):
            if i + j >= len(peaks):
                break

            t2, f2 = peaks[i + j]
            delta_t = t2 - t1

            if min_time_delta <= delta_t <= max_time_delta:
                # Create hash (string for now, DB-friendly)
                hash_key = f"{f1}|{f2}|{delta_t}"

                fingerprints.append((hash_key, int(t1)))

    return fingerprints
