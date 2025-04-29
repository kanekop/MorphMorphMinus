
# Face Morphing Demo

A Streamlit-based web application that performs face morphing between two images using facial landmarks detection and triangulation.

## Features

- Upload two images for morphing
- Real-time morphing preview
- Adjustable morphing intensity using a slider
- Local image processing (no external API calls)
- Secure file handling

## Technical Stack

- **Python 3.10**
- **Streamlit**: Web interface
- **OpenCV**: Image processing
- **MediaPipe**: Facial landmark detection
- **NumPy**: Numerical computations

## How It Works

1. **Face Detection**: Uses MediaPipe Face Mesh to detect facial landmarks in both images
2. **Triangulation**: Applies Delaunay triangulation to create corresponding triangles
3. **Warping**: Performs piece-wise affine transformation on triangles
4. **Blending**: Cross-dissolves between warped images

## Installation

The project uses Poetry for dependency management. All required packages are specified in `pyproject.toml`:

- streamlit
- opencv-python
- mediapipe
- numpy

## Usage

1. Click the Run button to start the Streamlit server
2. Upload two images using the file uploaders:
   - "元画像" (Source image)
   - "変換先画像" (Target image)
3. Adjust the "フェード度合い" (Fade amount) slider
4. The morphed result will display automatically

## Project Structure

```
├── main.py           # Streamlit interface
├── morph.py         # Core morphing functions
├── security.md      # Security documentation
└── pyproject.toml   # Dependencies
```

## Security

- No API keys or sensitive data required
- Local image processing
- Secure file uploads via Streamlit
- No external service dependencies

For detailed security information, see `security.md`.

## Error Handling

The application includes error handling for:
- Face detection failures
- Image processing errors
- File upload issues

## Development

The application runs on port 5000 and is configured for deployment on Replit.

## License

This project is part of a Replit implementation.

## Authors

Created as a Face Morphing Demo project on Replit.
