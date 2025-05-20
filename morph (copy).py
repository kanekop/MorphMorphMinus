# morph.py
# Face morphing utilities: simple cross-dissolve, landmark detection, Delaunay triangulation, and warping.

import cv2
import numpy as np
import mediapipe as mp

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh


def simple_fade(img1: np.ndarray, img2: np.ndarray, alpha: float) -> np.ndarray:
    """
    Perform a simple cross-dissolve between two images.
    img1, img2: same shape BGR images
    alpha: blending factor (0.0: only img1, 1.0: only img2)
    """
    return cv2.addWeighted(img1, 1.0 - alpha, img2, alpha, 0)


def get_landmarks(image: np.ndarray) -> list[tuple[int,int]]:
    """
    Detect facial landmarks using MediaPipe Face Mesh.
    Returns a list of (x, y) integer coordinates for each landmark.
    """
    h, w = image.shape[:2]
    with mp_face_mesh.FaceMesh(static_image_mode=True,
                               max_num_faces=1,
                               refine_landmarks=False) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            raise RuntimeError("No face detected")
        landmarks = results.multi_face_landmarks[0].landmark
        pts = [(int(p.x * w), int(p.y * h)) for p in landmarks]
        return pts


def calculate_delaunay_triangles(rect: tuple[int,int,int,int], 
                                 points: list[tuple[int,int]]) -> list[tuple[int,int,int]]:
    """
    Compute Delaunay triangulation for a set of points within rect.
    rect: (x, y, width, height), points: list of (x,y)
    Returns list of index triplets into points.
    """
    subdiv = cv2.Subdiv2D(rect)
    for p in points:
        subdiv.insert(p)
    triangleList = subdiv.getTriangleList()
    delaunay = []
    for t in triangleList:
        pts = [(t[0], t[1]), (t[2], t[3]), (t[4], t[5])]
        idx = []
        for p in pts:
            for i, point in enumerate(points):
                if abs(p[0] - point[0]) < 1 and abs(p[1] - point[1]) < 1:
                    idx.append(i)
                    break
        if len(idx) == 3:
            delaunay.append(tuple(idx))
    return delaunay


def apply_affine_transform(src: np.ndarray,
                           src_tri: list[tuple[float,float]],
                           dst_tri: list[tuple[float,float]],
                           size: tuple[int,int]) -> np.ndarray:
    """
    Apply an affine transform from src_tri to dst_tri on src image patch.
    size: (width, height) of output patch
    """
    warp_mat = cv2.getAffineTransform(np.float32(src_tri), np.float32(dst_tri))
    return cv2.warpAffine(src, warp_mat, size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def warp_triangle(src: np.ndarray,
                  dst: np.ndarray,
                  tri_src: list[tuple[int,int]],
                  tri_dst: list[tuple[int,int]]):
    """
    Warp a triangular region from src to dst.
    tri_src, tri_dst: lists of three (x,y) points
    Modifies dst in place.
    """
    # Bounding rectangles
    r1 = cv2.boundingRect(np.float32([tri_src]))
    r2 = cv2.boundingRect(np.float32([tri_dst]))
    # Offset coordinates
    src_offset = []
    dst_offset = []
    for i in range(3):
        src_offset.append((tri_src[i][0] - r1[0], tri_src[i][1] - r1[1]))
        dst_offset.append((tri_dst[i][0] - r2[0], tri_dst[i][1] - r2[1]))
    # Crop patch
    src_patch = src[r1[1]:r1[1]+r1[3], r1[0]:r1[0]+r1[2]]
    # Warp patch
    warped = apply_affine_transform(src_patch, src_offset, dst_offset, (r2[2], r2[3]))
    # Create mask
    mask = np.zeros((r2[3], r2[2], 3), dtype=np.float32)
    cv2.fillConvexPoly(mask, np.int32(dst_offset), (1.0, 1.0, 1.0), 16, 0)
    # Blend into dst
    dst_region = dst[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]]
    dst[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = \
        dst_region * (1 - mask) + warped * mask


def morph_faces(img1: np.ndarray,
               img2: np.ndarray,
               alpha: float = 0.5) -> np.ndarray:
    """
    Perform full face morphing between img1 and img2.
    Steps: detect landmarks, compute intermediate shape, warp triangles, blend.
    alpha: controls blending (0=img1 shape/texture, 1=img2 shape/texture)
    """
    # Detect landmarks
    pts1 = get_landmarks(img1)
    pts2 = get_landmarks(img2)
    # Compute intermediate landmark positions
    pts = [( (1-alpha)*p1[0] + alpha*p2[0], (1-alpha)*p1[1] + alpha*p2[1] ) 
           for p1, p2 in zip(pts1, pts2)]
    # Prepare empty warped images
    img1_warped = np.zeros_like(img1, dtype=np.float32)
    img2_warped = np.zeros_like(img2, dtype=np.float32)
    # Delaunay triangulation
    h, w = img1.shape[:2]
    rect = (0, 0, w, h)
    triangles = calculate_delaunay_triangles(rect, pts)
    # Warp each triangle
    for tri in triangles:
        x, y, z = tri
        t1 = [pts1[x], pts1[y], pts1[z]]
        t2 = [pts2[x], pts2[y], pts2[z]]
        t = [pts[x], pts[y], pts[z]]
        warp_triangle(img1, img1_warped, t1, t)
        warp_triangle(img2, img2_warped, t2, t)
    # Blend warped images
    img1_warped = np.uint8(img1_warped)
    img2_warped = np.uint8(img2_warped)
    morphed = simple_fade(img1_warped, img2_warped, alpha)
    return morphed
