"""Image preprocessing for traffic surveillance frames."""

import cv2
import numpy as np


def _estimate_blur_score(gray: np.ndarray) -> float:
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def _deblur_sharpen(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if _estimate_blur_score(gray) > 120:
        return img
    blurred = cv2.GaussianBlur(img, (0, 0), 3)
    return cv2.addWeighted(img, 1.4, blurred, -0.4, 0)


def _reduce_rain_haze(img: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    return cv2.fastNlMeansDenoisingColored(enhanced, None, 6, 6, 7, 21)


def _normalize_shadows(img: np.ndarray) -> np.ndarray:
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    channels = list(cv2.split(ycrcb))
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    channels[0] = clahe.apply(channels[0])
    return cv2.cvtColor(cv2.merge(channels), cv2.COLOR_YCrCb2BGR)


def _boost_low_light(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if gray.mean() > 80:
        return img
    gamma = 1.6
    table = np.array([((i / 255.0) ** (1 / gamma)) * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(img, table)


def preprocess_image(image_path: str, max_dim: int = 1080) -> tuple[np.ndarray, np.ndarray]:
    """
    Load and enhance a traffic image.
    Returns (original_resized, processed) BGR arrays.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Source frame missing at: {image_path}")

    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    original = img.copy()
    processed = _boost_low_light(img)
    processed = _normalize_shadows(processed)
    processed = _reduce_rain_haze(processed)
    processed = _deblur_sharpen(processed)
    processed = cv2.bilateralFilter(processed, 5, 50, 50)
    return original, processed
