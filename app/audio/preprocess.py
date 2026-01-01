import numpy as np
import librosa

def load_and_preprocess_audio(
    file_path: str,
    target_sr: int = 16000,
    normalize: bool = True
) -> tuple[np.ndarray, int]:
    """
    Load an audio file and convert it into a standardized mono signal.

    Returns:
        audio (np.ndarray): 1D mono signal
        sr (int): sample rate (always target_sr)
    """
    # Load audio
    audio, sr = librosa.load(
        file_path,
        sr=target_sr,
        mono=True
    )

    # Ensure type consistency
    audio = audio.astype(np.float32)

    # Normalize amplitude
    if normalize:
        peak = np.max(np.abs(audio))
        if peak > 0:
            audio = audio / peak

    return audio, target_sr
