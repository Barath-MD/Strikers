import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.title("Medsafe AI - Prescription Verifier")

st.markdown("Paste prescription text or upload audio (wav/mp3).")

# Text input
text = st.text_area("Prescription Text")

# Audio uploader
uploaded_file = st.file_uploader("Upload Audio Prescription", type=["wav", "mp3"])

if st.number_input("Patient Age", min_value=0, max_value=120, value=30):
    age = st.session_state.get("age", 30)

if st.button("Analyze"):
    if text.strip() == "" and uploaded_file is None:
        st.warning("Enter text or upload an audio file!")
    else:
        with st.spinner("Analyzing prescription..."):
            try:
                if uploaded_file is not None and text.strip() == "":
                    # Send audio to backend
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    res = requests.post(
                        BACKEND_URL + "/analyze/audio/",
                        files=files,
                        json={"patient": {"age": age}},
                    )
                else:
                    # Send text to backend
                    res = requests.post(
                        BACKEND_URL + "/analyze/text/",
                        json={"text": text, "patient": {"age": age}},
                    )

                if res.status_code == 200:
                    rj = res.json()
                    st.subheader("Extracted Drugs")
                    st.json(rj.get("structured", {}).get("drugs", []))
                    st.subheader("Deterministic Checks")
                    st.json(rj.get("checks", {}))
                    st.subheader("Top Evidence per Drug")
                    for ev in rj.get("evidence", []):
                        st.write("Drug:", ev["drug"])
                        for h in ev["hits"]:
                            st.write("-", h["doc_id"], f"(score: {h['score']:.3f})")
                            st.write(h["text"])
                    st.subheader("Explanation")
                    st.write(rj.get("explanation", ""))
                else:
                    st.error(f"Backend error: {res.status_code} - {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
