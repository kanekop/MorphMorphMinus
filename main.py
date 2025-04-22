
import streamlit as st
import cv2
import numpy as np
from morph import morph_faces

st.title("Face Morphing Demo")

img1 = st.file_uploader("元画像", type=["jpg","png"])
img2 = st.file_uploader("変換先画像", type=["jpg","png"])
alpha = st.slider("フェード度合い", 0.0, 1.0, 0.5)

if img1 and img2:
    # --- ① アップロード → OpenCV画像変換 （省略） ---
    bytes1 = img1.read()
    bytes2 = img2.read()
    arr1 = np.frombuffer(bytes1, np.uint8)
    arr2 = np.frombuffer(bytes2, np.uint8)
    img1_array = cv2.imdecode(arr1, cv2.IMREAD_COLOR)
    img2_array = cv2.imdecode(arr2, cv2.IMREAD_COLOR)
    h, w = img2_array.shape[:2]
    img1_array = cv2.resize(img1_array, (w, h))

    # ② 連番フレーム生成 → 動画化 ← ここ！  
    frame_count = 30  # 例：30フレーム  
    frames = []
    for i in range(frame_count):
        a = i / (frame_count - 1)
        f = morph_faces(img1_array, img2_array, a)
        frames.append(f)

    # A) Streamlit上でアニメーションとして表示する場合  
    rgb_frames = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in frames]
    st.image(rgb_frames, use_column_width=True)

    # B) MP4に書き出して再生したい場合  
    # writer = cv2.VideoWriter("morph.mp4", cv2.VideoWriter_fourcc(*"mp4v"),24, (w, h))
    # for f in frames:
    #     writer.write(f)
    # writer.release()
    # st.video("morph.mp4")
