import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder
import os

# --- CONFIGURATION ---
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")
IDENTIFY_ENDPOINT = f"{BACKEND_BASE_URL}/identify"
STATS_ENDPOINT = f"{BACKEND_BASE_URL}/stats"

MAX_DURATION_SEC = 20
# Approx bytes for 20s at 48kHz, 16-bit mono (48000 * 2 * 20)
MAX_BYTES_LIMIT = 48000 * 2 * MAX_DURATION_SEC 
MIN_BYTES_FOR_IDENTIFICATION = 48000 * 2 * 2 # Minimum 2 seconds

st.set_page_config(
    page_title="TrackTrace",
    page_icon="🎵",
    layout="centered"
)

# --- CUSTOM CSS ---
st.markdown(
    """
    <style>
    /* Main Background & Fonts */
    .stApp {
        background: linear-gradient(to bottom right, #0e0e0e, #1a1a2e);
        color: #ffffff;
    }
    
    /* Custom Title */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* Result Card Styling */
    .song-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin-top: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Recorder Alignment */
    div[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [style*="flex-direction: column;"] {
        align-items: center;
    }
    
    /* Status indicators */
    .status-text {
        font-size: 0.8rem;
        color: #aaa;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- HELPER FUNCTIONS ---
def normalize_confidence(score: int) -> int:
    if score <= 20: return 20
    if score >= 200: return 95
    return int(20 + (score - 20) * (75 / 180))

def trim_audio_bytes(audio_data: bytes) -> bytes:
    """Truncate audio bytes to the max limit to simulate a 20s cutoff."""
    if len(audio_data) > MAX_BYTES_LIMIT:
        return audio_data[:MAX_BYTES_LIMIT]
    return audio_data

# --- SESSION STATE INITIALIZATION ---
if 'show_stats_page' not in st.session_state:
    st.session_state.show_stats_page = False

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    mode = st.radio("Input Source", ["🎤 Microphone", "📁 Upload File"], index=0)
    st.markdown("---")
    
    if st.button("View System Stats"):
        st.session_state.show_stats_page = True
        st.rerun()

    st.info("**Instructions:**\n1. Tap Mic to start (Turns Red).\n2. Tap again to stop.\n3. Try to capture clear audio for best results.")
    
if st.session_state.show_stats_page:
    st.markdown("## System Statistics")

    try:
        with st.spinner("Fetching system stats..."):
            stats_response = requests.get(STATS_ENDPOINT, timeout=5)

        if stats_response.status_code == 200:
            stats = stats_response.json()

            col1, col2, col3 = st.columns(3)

            col1.metric(
                label="🎵 Songs Indexed",
                value=stats.get("songs_indexed", 0)
            )

            col2.metric(
                label="🔗 Total Fingerprints",
                value=f"{stats.get('total_fingerprints', 0):,}"
            )

            col3.metric(
                label="📈 Avg / Song",
                value=f"{stats.get('avg_fingerprints_per_song', 0):,}"
            )
            
            st.markdown("---")
            
            st.info(
                """
                **How it works:**
                
                TrackTrace doesn't store or compare raw audio files.
                
                When you record a clip, it's converted into a compact audio fingerprint. 
                That fingerprint is matched against an indexed catalog stored in **PostgreSQL**.
                
                Frequently used fingerprints and lookup results are cached in **Redis** 
                to keep identification fast and consistent, even as the catalog grows.
                """
            )
        else:
            st.error("Failed to fetch stats from backend.")
            st.text(stats_response.text)

    except Exception as e:
        st.error("Could not connect to stats endpoint.")
        st.text(str(e))

    st.markdown("---")
    
    # Back button to return to main screen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Back to Identifier", type="primary", use_container_width=True):
            st.session_state.show_stats_page = False
            st.rerun()

    # Stop further UI rendering when stats are shown
    st.stop()

# --- SESSION STATE INITIALIZATION ---
if 'last_audio_data' not in st.session_state:
    st.session_state.last_audio_data = None
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'current_audio_bytes' not in st.session_state:
    st.session_state.current_audio_bytes = None
if 'current_audio_name' not in st.session_state:
    st.session_state.current_audio_name = None
if 'current_audio_type' not in st.session_state:
    st.session_state.current_audio_type = None

# --- MAIN UI ---
st.markdown('<div class="main-title">TrackTrace 🎵</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; color: #bbb; font-size: 0.95rem; margin-bottom: 10px;'>
        <b>Demo notice:</b> TrackTrace currently recognizes songs from a curated demo catalog.<br>
        Audio is indexed using fingerprints (hashes), not raw song files.<br>
        Try playing tracks from this 
        <a href="https://open.spotify.com/playlist/1ioQRTRJk08zXQdL3UaYnt?si=01e3caf70f014316" target="_blank" style="color:#00d2ff;">
            Spotify playlist
        </a>
        to test identification.
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("<div style='text-align: center; color: #aaa; margin-bottom: 30px;'>Identify any song in seconds.</div>", unsafe_allow_html=True)

audio_bytes = None
audio_name = None
audio_type = None

# --- INPUT HANDLING ---
if mode == "🎤 Microphone":
    # Center the recorder
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("<h4 style='text-align: center;'>Tap to Record</h4>", unsafe_allow_html=True)
            
            # The library handles the recording UI. 
            # Python waits here until the user clicks stop.
            audio_data = audio_recorder(
                text="", 
                recording_color="#ff4b4b", # Red when recording
                neutral_color="#303030",   # Dark grey when idle
                icon_name="microphone",
                icon_size="5x",
                pause_threshold=2.0,
                sample_rate=16000
            )
            
            st.markdown(
                f"""
                <div class="status-text">
                    Max duration: {MAX_DURATION_SEC}s (Auto-trimmed)<br>
                    Button turns <span style='color:#ff4b4b'><b>RED</b></span> when live.
                </div>
                """, 
                unsafe_allow_html=True
            )

    # PROCESS RECORDING IMMEDIATELY AFTER USER STOPS
    if audio_data is not None:
        # Check if this is a new recording (different from last one)
        if audio_data != st.session_state.last_audio_data:
            # Reset everything for new recording
            st.session_state.last_audio_data = audio_data
            st.session_state.show_results = False
            st.session_state.current_audio_bytes = None
            st.session_state.current_audio_name = None
            st.session_state.current_audio_type = None
            st.rerun()
        
        if len(audio_data) < MIN_BYTES_FOR_IDENTIFICATION:
             st.warning("Recording too short. Please record at least 2 seconds.")
        else:
            # Enforce the 20-second limit immediately
            audio_bytes = trim_audio_bytes(audio_data)
            audio_name = "mic_capture.wav"
            audio_type = "audio/wav"
            
            # Store in session state
            st.session_state.current_audio_bytes = audio_bytes
            st.session_state.current_audio_name = audio_name
            st.session_state.current_audio_type = audio_type
            
            # Calculate actual duration captured
            duration = len(audio_bytes) / (16000 * 2)
            
            st.audio(audio_bytes, format="audio/wav")

elif mode == "📁 Upload File":
    uploaded_file = st.file_uploader("Drop your audio file here", type=["wav", "mp3", "ogg"])
    if uploaded_file is not None:
        audio_bytes = uploaded_file.getvalue()
        audio_name = uploaded_file.name
        audio_type = uploaded_file.type
        
        # Store in session state
        st.session_state.current_audio_bytes = audio_bytes
        st.session_state.current_audio_name = audio_name
        st.session_state.current_audio_type = audio_type
        
        st.audio(uploaded_file)

# Use session state values for identification
audio_bytes = st.session_state.current_audio_bytes
audio_name = st.session_state.current_audio_name
audio_type = st.session_state.current_audio_type

# --- IDENTIFICATION LOGIC ---
if audio_bytes and (len(audio_bytes) >= MIN_BYTES_FOR_IDENTIFICATION):
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        identify_btn = st.button("Identify Song", type="primary", use_container_width=True)

    if identify_btn:
        with st.status("🔍 Listening to fingerprint...", expanded=True) as status:
            files = {"file": (audio_name or "audio.wav", audio_bytes, audio_type or "audio/wav")}
            
            try:
                # 1. Sending Request
                st.write("📤 Identifying...")
                response = requests.post(IDENTIFY_ENDPOINT, files=files, timeout=60)
                
                # 2. Handling Response
                if response.status_code == 200:
                    result = response.json()
                    status.update(label="Analysis complete!", state="complete", expanded=True)
                    
                    if not result.get("match"):
                        st.error("No match found")
                        st.info("Try recording a clearer clip.")
                    else:
                        song = result['song']
                        conf = normalize_confidence(result['confidence'])
                        
                        st.balloons()
                        st.markdown(
                            f"""
                            <div class="song-card">
                                <h1 style='margin-bottom: 0;'>{song['title']}</h1>
                                <h3 style='color: #00d2ff; margin-top: 5px;'>{song['artist']}</h3>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.write("") 
                        st.caption(f"Match Confidence: {conf}%")
                        st.progress(conf)
                        if conf < 40: st.warning("⚠️ Low confidence match.")
                            
                else:
                    status.update(label="Server Error", state="error")
                    st.error(f"Error: {response.text}")

            except Exception as e:
                status.update(label="Connection Error", state="error")
                st.error(f"Failed to connect: {e}")
