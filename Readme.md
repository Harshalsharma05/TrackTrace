# 🎵 TrackTrace - Distributed Audio Recognition System Using Fingerprint Matching

TrackTrace is an end-to-end **audio recognition system** that identifies songs from **short, noisy audio clips** by transforming music into compact **acoustic fingerprints** instead of **storing raw audio files**. Using the **_Short-Time Fourier Transform (STFT)_** to analyze audio in the **time–frequency domain**, the system extracts stable **spectral landmarks** and applies **offset-based voting** to match partial recordings against a **pre-indexed fingerprint catalog**, achieving high robustness to background noise and recording quality. TrackTrace is built around **real-world constraints** such as **unreliable input**, **confidence-based rejection**, and a **scalable backend architecture**, offering a practical view into how modern **large-scale audio identification** systems operate

🔗 **[Live Demo Checkout](https://tracktrace-frontend.onrender.com)**

---

## 🚀 What TrackTrace Does

- Identifies a song from a **5–10 second audio clip**
- Works with:

  - microphone recordings
  - uploaded audio files

- Robust to:

  - background noise
  - imperfect recordings
  - partial clips

- Returns:

  - song title
  - artist
  - confidence score

- Correctly refuses to guess when input is insufficient

---

## 🧠 Core Idea (High Level)

> Songs are not stored.
> **Acoustic fingerprints are stored.**

Each song is first transformed using the **_Short-Time Fourier Transform (STFT)_**, which represents audio as a **time–frequency map** and reveals **stable spectral patterns** that persist despite noise or recording quality. From this representation, TrackTrace extracts thousands of **compact fingerprint hashes** based on robust spectral landmarks. Incoming audio is processed through the same pipeline and matched using **time-offset voting**, allowing reliable identification from partial or noisy clips.

This approach reflects how modern large-scale audio identification systems are designed to balance **robustness, efficiency, and scalability**.

---

## 🧱 System Architecture

```
[ User / Browser ]
        |
        |  (audio clip)
        v
[ Streamlit Frontend ]
        |
        |  POST /identify
        v
[ FastAPI Backend ]
        |
        |-- Preprocessing (mono, resample)
        |-- Spectrogram & peak detection
        |-- Fingerprint generation
        |
        |-- Redis (fast hash lookup)
        |-- PostgreSQL (persistent storage)
        |
        v
[ Match Decision Engine ]
        |
        v
[ Result + Confidence ]
```

---

## 🔊 Audio Processing Pipeline

1. **Load & Preprocess**

   - Convert to mono
   - Resample to fixed sample rate
   - Normalize format for DSP stability

2. **Spectrogram**

   - Short-Time Fourier Transform (STFT)
   - Power spectrum in dB

3. **Peak Detection**

   - Identify stable spectral landmarks
   - Filter out noise and low-energy regions

4. **Fingerprint Generation**

   - Pair peaks across time–frequency space
   - Generate hashes of `(freq1, freq2, delta_time)`

These hashes are:

- compact
- noise-robust
- invariant to volume changes

---

## 🔗 Matching Algorithm (Key Part)

For an incoming clip:

1. Generate fingerprints
2. For each hash:

   - Look up matching hashes in Redis/PostgreSQL

3. Compute **time offset differences**
4. Vote per `(song_id, song_offset)`
5. The strongest offset cluster wins

This approach:

- tolerates noise
- tolerates missing segments
- scales well with database size

---

## 🛑 Why TrackTrace Sometimes Refuses to Match (By Design)

A real recognition system is defined by **when it refuses to answer**.

TrackTrace includes multiple rejection guards:

- ❌ Audio too short (< 5 seconds)
- ❌ Insufficient spectral peaks (silence / noise)
- ❌ Weak match score
- ❌ Ambiguous results (no dominant winner)

This prevents:

- random matches from silence
- unstable results from noise
- false confidence

---

## 📊 Confidence Scoring

Raw fingerprint vote counts are normalized into a **user-friendly confidence score (0–100)**.

- High confidence → strong offset cluster
- Low confidence → weak or noisy match
- Ambiguous → no result returned

The system prefers **honesty over guessing**.

---

## 🗄️ Data Storage Design

### PostgreSQL

- Persistent storage
- Tables:

  - `songs`
  - `fingerprints`

- Stores:

  - metadata
  - hashes
  - time offsets

### Redis

- High-speed hash lookup cache
- Reduces database load during identification
- Improves response time significantly

---

## 📦 Demo Dataset

- Curated catalog of ~30 songs
- ~3 million fingerprints total
- Songs are **not included in the repository** (copyright)
- Only fingerprints are stored

A Spotify playlist is provided in the UI so users can easily test known tracks.

---

## 🧪 Bulk Indexing

Songs are indexed offline using a bulk ingestion script:

```
scripts/
└── bulk_index.py
```

This simulates real ingestion pipelines used by production systems.

Indexing is:

- one-time
- idempotent
- scalable

---

## 🌐 API Endpoints

### `POST /identify`

Identify a song from an audio clip.

**Input**

- audio file (`wav`, `mp3`, `ogg`)

**Output**

```json
{
  "match": true,
  "song": {
    "title": "One Dance",
    "artist": "Drake"
  },
  "confidence": 82
}
```

Or, if rejected:

```json
{
  "match": false,
  "reason": "Insufficient audio signal"
}
```

---

### `GET /stats`

System observability endpoint.

```json
{
  "songs_indexed": 30,
  "total_fingerprints": 2854321,
  "avg_fingerprints_per_song": 95144
}
```

---

### `GET /health`

Dependency health check.

```json
{
  "status": "ok",
  "postgres": "ok",
  "redis": "ok"
}
```

---

## 🖥️ Frontend

- Built with **Streamlit**
- Features:

  - microphone recording
  - audio upload
  - real-time feedback
  - confidence visualization
  - system stats view

The frontend is intentionally minimal to keep focus on system behavior.

---

## 🛠️ Tech Stack

- **Python 3.11**
- **FastAPI** — backend API
- **PostgreSQL** — persistent storage
- **Redis** — cache
- **NumPy / SciPy / Librosa** — DSP
- **Streamlit** — frontend UI

---

## ⚖️ Legal & Privacy Notes

- No copyrighted audio files are stored
- Only non-reversible acoustic fingerprints are persisted
- Audio uploads are processed temporarily and discarded

---

## 🎯 What This Project Demonstrates

- Practical DSP knowledge
- Scalable backend design
- Cache-aware architecture
- Failure-first system thinking
- Honest confidence handling
- Real-world constraints awareness

This is **not** a toy demo — it’s a simplified but principled version of a production-grade recognition system.

---

## 📌 Future Improvements

- Async FastAPI + connection pooling
- Better fingerprint density tuning
- Adaptive confidence thresholds
- Deployment (Docker / cloud)
- Melody-based matching (separate problem)

---

## 👤 Author

Built as a deep-dive systems project to understand how real-world audio recognition works under noisy, imperfect conditions.
