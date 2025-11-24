import streamlit as st
from streamlit_mic_recorder import mic_recorder
from .transcript import get_transcripts
import tempfile
from .graph import build_graph

def run():
    # Initialize the graph
    graph = build_graph()

    # Initialize session state variables if they don't exist
    if "audio_bytes" not in st.session_state:
        st.session_state["audio_bytes"] = None
    if "process_audio" not in st.session_state:
        st.session_state["process_audio"] = False
    if "transcribed_result" not in st.session_state:
        st.session_state["transcribed_result"] = ""
    if "final_response" not in st.session_state:
        st.session_state["final_response"] = ""
    if "user_input" not in st.session_state:
        st.session_state["user_input"] = ""

    # --- Streamlit App UI ---
    st.title("🧠 Smart Q&A Database Query Assistant")

    # --- Text Input ---
    user_input = st.text_input("Enter your question about the database:")
    user_name = 'edwin@gain-hub.com'

    # Text submit button
    text_submit = st.button("Submit Text Question")

    # Clear button
    clear_clicked = st.button("Clear")

    if clear_clicked:
        st.session_state["audio_bytes"] = None
        st.session_state["process_audio"] = False
        st.session_state["transcribed_result"] = ""
        st.session_state["final_response"] = ""
        st.session_state["user_input"] = ""
        st.rerun()  # Refresh app to clear inputs visibly

    # --- Process Text Input ---
    if text_submit and user_input.strip():
        with st.spinner("Generating response..."):
            try:
                result = graph.invoke({"question": user_input,
                                    "user_name":user_name})
                st.markdown("### 💬 Final Answer")
                st.success(result["final_response"])
            except Exception as e:
                st.error(f"An error occurred: {e}")

    # --- Mic Recorder ---
    st.markdown("### 🎙️ Or ask your question by voice:")
    # Start/stop the mic recording
    audio_data = mic_recorder(
        start_prompt="Start recording",
        stop_prompt="Stop recording",
        just_once=False
    )

    # Add a separate button to process recorded audio
    process_voice = st.button("Submit Voice Question")

    if process_voice:
        if audio_data and audio_data["bytes"]:
            st.audio(audio_data["bytes"], format="audio/wav")

            # Save audio locally
            file_name = "recorded_audio.wav"
            with open(file_name, "wb") as f:
                f.write(audio_data["bytes"])

            st.success("Audio saved locally as 'recorded_audio.wav'")

            with st.spinner("Transcribing audio..."):
                transcribed_result = get_transcripts(output_file_path=file_name)
                st.success(f"Transcribed Question: \"{transcribed_result}\"")

                with st.spinner("Generating response..."):
                    try:
                        response = graph.invoke({"question": transcribed_result,
                                                "user_name":user_name})
                        st.markdown("### 💬 Final Answer")
                        st.success(response["final_response"])
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
        else:
            st.warning("No audio recording found. Please record your question first.")
