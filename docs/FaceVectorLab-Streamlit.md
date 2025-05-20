# **FaceVectorLab-Streamlit**

Below is the initial prompt for Replit Agent to scaffold a Streamlit-based web application that performs latent‑space arithmetic on face images.

\# Project: FaceVectorLab-Streamlit  
\# Goal  
Build a Streamlit web app that lets a user on a smartphone:  
1\. Upload two face photos (A and B) via \`st.file\_uploader\` (accept "image/\*").  
2\. Send each image to an external inference API to obtain latent vectors w\_A and w\_B  
   (placeholder stub is fine for now; replace with real call later).  
3\. Compute Δ \= w\_A − w\_B  (vector arithmetic in NumPy / PyTorch).  
4\. Generate face C (= A minus B) using the same API and display it.  
5\. Provide a button “Reconstruct A” that adds Δ \+ w\_B to regenerate A' and  
   shows A' next to the original A for visual confirmation.  
6\. Keep all heavy inference off-device; the browser only uploads images and  
   receives generated images (PNG/WebP, ≤ 2 MB each).  
7\. Deploy on Replit so hitting the green \*\*“Run”\*\* button starts the Streamlit server  
   and exposes a public URL.

\# Tech stack  
\* \*\*Python 3.11\*\*  
\* \*\*Streamlit 1.34+\*\*  
\* Libraries: \`numpy\`, \`requests\`, \`Pillow\`, \`torch\` (CPU is fine for MVP)  
\* Use \*\*Replit Secrets\*\* for API keys (\`EXTERNAL\_API\_TOKEN\`).

\# Folder structure  
.  
├─ app/
│   ├─ main.py                     # Streamlit Main entry point & navigation
│   ├─ morph_page.py               # UI & logic for existing Face Morphing
│   ├─ face_vector_lab_page.py     # UI & logic for new FaceVectorLab
│   ├─ morph.py                    # Core morphing logic (existing)
│   └─ backend/
│       ├─ __init__.py
│       ├─ inference.py            # FaceVectorLab: encode(img) → w,  generate(w) → image
│       └─ utils.py                # FaceVectorLab: vector arithmetic helpers
├─ requirements.txt                # streamlit, numpy, requests, pillow, torch
├─ README.md                       # Combined setup & how-to for both features
└─ .replit

\# Functional requirements  
1\. \*\*Upload UI\*\*    
   \`\`\`python  
   img\_A \= st.file\_uploader("Choose Face A", type=\["jpg","jpeg","png"\])  
   img\_B \= st.file\_uploader("Choose Face B", type=\["jpg","jpeg","png"\])

After both are uploaded, show thumbnails with `st.image`.  
 2\. **Encode & compute**

 - On button press "Process Images":
     - For img_A and img_B:
       - with st.spinner(f"Encoding Face {A_or_B}..."):
         - image_bytes = uploaded_file.getvalue()
         - st.session_state[f"fvl_image_{a_or_b}_bytes"] = image_bytes # Store original
         - vector = app.backend.inference.encode(image_bytes)
         - st.session_state[f"fvl_w_{a_or_b}"] = vector
     - If both vectors obtained:
       - st.session_state.fvl_delta = st.session_state.fvl_w_a - st.session_state.fvl_w_b
       - Display success message or proceed to generate C.
3. **Generate C**

   - On button press "Generate Face C (A-B)":
     - with st.spinner("Generating Face C..."):
       - delta_vector = st.session_state.get("fvl_delta")
       - if delta_vector is not None:
         - generated_image_b64 = app.backend.inference.generate(delta_vector)
         - st.session_state.fvl_generated_c_b64 = generated_image_b64
         - st.image(f"data:image/png;base64,{generated_image_b64}", caption="Generated Face C (A-B)")
       - else:
         - st.warning("Please process images A and B first.")

4. **Reconstruct A**

   * Button `st.button("Reconstruct A")` → send `delta + w_B` → show side-by-side.

5. **Error handling**

   * If external API fails, show `st.error` message with guidance.

6. **Mobile friendliness**

   * Ensure all images `use_column_width=True`.

   * No fixed-width elements; rely on Streamlit’s responsive layout.

7. **README**

   * Explain how to set `EXTERNAL_API_TOKEN` in Replit Secrets.

   * Show how to replace the stub in `backend/inference.py` with a real endpoint  
      (e.g., Replicate, RunPod, or internal GPU).

# **Tasks for the agent**

1. Scaffold all files/folders exactly as above.

2. Fill `app.py` with working UI logic, using dummy images for now.

3. Implement `backend/inference.py` with placeholder functions that return  
    (a) random 512-D NumPy vectors and (b) a single-color PNG as dummy output.

4. Write concise docstrings **before** each function.

5. Add a minimal `requirements.txt`.

Create a `.replit` file so that pressing “Run” executes

 streamlit run app.py \--server.port 3000 \--server.enableCORS false

6.   
7. Run the app, verify it loads, and provide the public URL.

Start coding now. When finished, run the app and share the live link.

\---  
\*\*Next Steps\*\*  
1\. Review and tweak any wording or constraints in the prompt.  
2\. Once confirmed, send this prompt to the Replit Agent.  
3\. Iterate on the generated code directly in the Replit IDE or by further Agent instructions.

