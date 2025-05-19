# **技術仕様書 – Face Morphing Streamlit App**

## **1\. 目的**

本ドキュメントは、Streamlit 上で動作する顔モーフィングアプリ（以下、本アプリ）の構造・アルゴリズム・依存環境を包括的に記述し、今後の保守・拡張時に必要となる情報を 1 か所に集約することを目的とする。

## **2\. システム全体構成**

┌──────────────┐  
│ Browser (ユーザー) │  
└──────────────┘  
          │ HTTP  
┌─────────────────┐  
│   Streamlit Runtime  │  main.py  
└─────────────────┘  
          │ 呼び出し  
┌─────────────────┐  
│  morph.py (Core)     │  画像処理 & モーフィング  
└─────────────────┘  
          │ 依存  
\[OpenCV\] \[MediaPipe\] \[NumPy\]

* **main.py** : UI／ファイル I/O／ワークフロー制御

* **morph.py**: 画像処理ロジック（フェード, ランドマーク検出, 三角ワーピング）

* **pyproject.toml** : Poetry での依存管理（streamlit, opencv-python, mediapipe, numpy）

## **3\. 動作フロー (main.py)**

1. `st.file_uploader` で 2 枚の顔画像を受け取る

2. バイト列 → `cv2.imdecode` で BGR 画像へ

3. 解像度を img2 基準に揃える（将来的にはオプション化）

4. パラメータ入力

   * `alpha` – 静止画中間比率（デフォルト 0.5）

5. `morph_faces()` 呼び出し

6. 戻り値 (BGR) → RGB 変換して `st.image` 表示

## **4\. アルゴリズム詳細 (morph.py)**

| ステージ | 関数 | 説明 |  
 |

## **9\. 実装補足と不足項目**

本アプリは既存仕様だけでも最小構成が組めますが、**再現性・保守性**を高めるために以下の情報を追記します。

### **9.1 ディレクトリ／ファイル構成 (決定版)**

.  
├── app/                \# Python パッケージ化を想定  
│   ├── \_\_init\_\_.py  
│   ├── main.py         \# Streamlit UI (エントリーポイント)  
│   ├── morph.py        \# 画像処理ロジック  
│   └── utils.py        \# 汎用 I/O・前処理ヘルパー  
├── tests/              \# pytest テスト  
│   ├── test\_morph.py  
│   └── data/  
│       ├── face1.jpg   \# サンプル画像 (著作権クリア済み)  
│       └── face2.jpg  
├── pyproject.toml      \# Poetry 管理  
└── README.md           \# 環境構築 & 使い方

* `app/__init__.py` で `from .main import run` をエクスポートすると CLI で `python -m app` が可能。

### **9.2 ローカル実行・デプロイ手順**

| ステップ | コマンド | 備考 |
| ----- | ----- | ----- |
| 依存解決 | `poetry install` | Python 3.10.14 想定 |
| 開発実行 | `poetry run streamlit run app/main.py` | `--server.port` でポート指定可 |
| Replit | Run コマンドを上記に設定 | Poetry Build の自動キャッシュを活用 |
| Docker | `docker build -t face-morph .` | ベース: python:3.10-slim \+ `poetry install --no-dev` |

### **9.3 UI ワイヤーフレーム**

| コンポーネントID | type | 説明 |
| ----- | ----- | ----- |
| `file_src` | `st.file_uploader` | 元画像アップロード |
| `file_dst` | `st.file_uploader` | 変換先画像アップロード |
| `slider_alpha` | `st.slider` | α 値 0–1 (step=0.01) |
| `btn_process` | `st.button` | 実行トリガー |
| `img_result` | `st.image` | 出力プレビュー |

### **9.4 入力画像要件と前処理フロー**

1. **形式**: JPEG / PNG、RGB or BGR いずれも可

2. **長辺サイズ**: 1024px 以下を推奨 → 超過時はリサイズ

3. **アスペクト差**が大きい場合、中央トリミングで調整 (今後オプション化)

### **9.5 エラー処理 & ユーザー通知フロー**

* **顔検出失敗** → `st.warning("顔が検出できませんでした。別の画像をお試しください")`

* **異常終了** (例: MediaPipe 初期化失敗) → `st.exception(e)` \+ ログ出力 (`logging`)

### **9.6 コード断片 (関数シグネチャ保証)**

\# app/morph.py

def morph\_faces(img1: np.ndarray, img2: np.ndarray, alpha: float \= 0.5,  
                extra\_points: bool \= True, hull\_mask: bool \= True) \-\> np.ndarray:  
    """顔+髪型を含むワーピング画像を返す。"""

* 引数 `extra_points`, `hull_mask` で旧挙動 (顔のみ) との切替を保証。

### **9.7 サンプルデータ & テスト**

* `tests/data/` に Creative Commons 画像を収録

* `pytest -q` がグリーンになることを CI で担保

### **9.8 ライセンス・プライバシー**

* **OpenCV/MediaPipe**: Apache-2.0 準拠

* **入力画像の扱い**: 処理終了後に即メモリから削除・保存無し (GDPR/JIS Q 15001 対応)

\-----------|------|------|  
 | フェード | `simple_fade` | `cv2.addWeighted` で線形ブレンド |  
 | ランドマーク検出 | `get_landmarks` | MediaPipe Face Mesh (468 点) を 1 face 限定で取得 |  
 | 追加コーナー点 | `extra` | 画像四隅＋辺の中点 (8点) を追加し、髪型・背景の歪みを防止 |  
 | 中間形状計算 | 内包表記 | α 値で線形補間 |  
 | 三角分割 | `calculate_delaunay_triangles` | `cv2.Subdiv2D` で Delaunay、index 三つ組を返す |  
 | ワープ | `warp_triangle` | 三角形ごとにアフィン変換＋マスク合成 |  
 | 凸包マスク | `cv2.convexHull` | 顔＋髪を含む領域だけを最終出力に採用 |

## **5\. 環境・デプロイ**

* **Python** 3.10.x（Poetry により固定）

* **Run コマンド**: `streamlit run main.py`

* Replit (Poetry / 「Run」ボタン) でホスティング。外部環境の場合は `poetry install`→`streamlit run`。

## **6\. テスト指針**

* **単体** : `pytest` (+ `pytest-streamlit` 予定)

  * `morph.simple_fade` – 定数画像でブレンド比をアサート

  * `morph.get_landmarks` – 期待座標範囲の有無

* **E2E** : Selenium \+ Streamlit コンポーネントのスクリーンショット比較

## **7\. 既知の課題 & 今後の拡張候補**

### **7.1 パフォーマンス**

* MediaPipe が CPU でボトルネック → 複数フレーム生成時に 0.3–0.5 s/フレーム。→ キャッシュ or GPU (TensorRT, OpenVINO) 検証。

* OpenCV の Python ループ部分 (`warp_triangle`) がネック → Numba／Cython で高速化可能。

### **7.2 画質・自然さ**

* 三角形の境界にラインが残るケース → Poisson Image Editing への置換を検討。

* 照明差補正 (histogram matching) を前処理で入れる。

* 背景一体型モーフィング: セグメンテーション (MediaPipe Selfie Segmentation) を重ねて自然な合成に。

### **7.3 機能**

* **動画生成**: `cv2.VideoWriter` or `imageio` で MP4/GIF 出力 (UI に FPS・長さスライダー)

* **WebCam ライブ**: `streamlit-webrtc` でリアルタイムモーフィング

* **複数顔サポート**: `max_num_faces=n` と multi-face assignment

* **マスクカスタム**: ユーザーが筆でマスク領域を描き、髪型・帽子など任意に含む

* **API化**: FastAPI エンドポイントとして `POST /morph` → base64 画像返却

* **iOS/Android**: Streamlit は PWA 寄りだが、React Native \+ OpenCV.js バインディング案も検討

### **7.4 DevOps**

* CI (GitHub Actions) で `poetry install && pytest && streamlit --help`

* MLOps: ランドマーク精度向上のためのカスタム学習 (optional)

## **8\. 参考リンク**

* MediaPipe Face Mesh API: [https://developers.google.com/mediapipe/solutions/vision/face\_mesh](https://developers.google.com/mediapipe/solutions/vision/face_mesh)

* OpenCV Delaunay ドキュメント: [https://docs.opencv.org/4.x/d6/d17/classcv\_1\_1Subdiv2D.html](https://docs.opencv.org/4.x/d6/d17/classcv_1_1Subdiv2D.html)

* Poisson Blending: Pérez et al., *Poisson Image Editing*, 2003\.

---

**更新履歴**

| 日付 | 変更 | 著者 |
| ----- | ----- | ----- |
| 2025‑05‑20 | 初版作成 | ChatGPT |

