import streamlit as st
import cv2
import numpy as np
from morph import morph_faces

st.title("Face Morphing Demo")

img1 = st.file_uploader("元画像", type=["jpg","png"])
img2 = st.file_uploader("変換先画像", type=["jpg","png"])
alpha = st.slider("フェード度合い", 0.0, 1.0, 0.5)

if img1 and img2:
    # 1) アップロード → OpenCV 画像
    bytes1 = img1.read()
    bytes2 = img2.read()
    arr1 = np.frombuffer(bytes1, np.uint8)
    arr2 = np.frombuffer(bytes2, np.uint8)
    img1_array = cv2.imdecode(arr1, cv2.IMREAD_COLOR)
    img2_array = cv2.imdecode(arr2, cv2.IMREAD_COLOR)

    # 2) サイズを揃える（任意）
    h2, w2 = img2_array.shape[:2]
    img1_array = cv2.resize(img1_array, (w2, h2))

    # 3) モーフィング実行
    try:
        with st.spinner("Morphing..."):
            result = morph_faces(img1_array, img2_array, alpha)
        # OpenCV は BGR なので、Streamlit に渡す際は RGB に変換しても OK
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        st.image(result_rgb, caption="Morph Result", use_column_width=True)
    except RuntimeError as e:
        st.error(f"Error: {e}")

