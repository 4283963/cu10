import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple
import base64
import io
from PIL import Image


@dataclass
class AnalysisResult:
    vein_count: int
    serration_area: float
    serration_count: int
    petal_area: float
    petal_perimeter: float
    circularity: float
    contours: List[List[Tuple[int, int]]] = field(default_factory=list)
    vein_points: List[Tuple[int, int]] = field(default_factory=list)
    serration_points: List[Tuple[int, int]] = field(default_factory=list)
    original_width: int = 0
    original_height: int = 0

    def to_dict(self):
        return {
            "vein_count": self.vein_count,
            "serration_area": self.serration_area,
            "serration_count": self.serration_count,
            "petal_area": self.petal_area,
            "petal_perimeter": self.petal_perimeter,
            "circularity": self.circularity,
            "contours": [[list(point) for point in contour] for contour in self.contours],
            "vein_points": [list(point) for point in self.vein_points],
            "serration_points": [list(point) for point in self.serration_points],
            "original_width": self.original_width,
            "original_height": self.original_height,
        }


class PetalAnalyzer:
    def __init__(self):
        self.kernel_size = 3
        self.threshold_block_size = 11
        self.threshold_c = 2

    def analyze(self, image_bytes: bytes) -> AnalysisResult:
        img_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("无法解析图片")

        original_height, original_width = img.shape[:2]

        gray = self._grayscale(img)
        binary = self._threshold(gray)
        cleaned = self._morphological_clean(binary)

        contours, hierarchy = self._find_contours(cleaned)
        petal_contour = self._find_largest_contour(contours)

        if petal_contour is None:
            return AnalysisResult(
                vein_count=0,
                serration_area=0,
                serration_count=0,
                petal_area=0,
                petal_perimeter=0,
                circularity=0,
                original_width=original_width,
                original_height=original_height,
            )

        petal_area = cv2.contourArea(petal_contour)
        petal_perimeter = cv2.arcLength(petal_contour, True)

        circularity = 0
        if petal_perimeter > 0:
            circularity = 4 * np.pi * petal_area / (petal_perimeter * petal_perimeter)

        vein_count, vein_points = self._detect_veins(gray, petal_contour)
        serration_area, serration_count, serration_points = self._calculate_serration(
            petal_contour
        )

        result = AnalysisResult(
            vein_count=vein_count,
            serration_area=serration_area,
            serration_count=serration_count,
            petal_area=petal_area,
            petal_perimeter=petal_perimeter,
            circularity=circularity,
            contours=[petal_contour.reshape(-1, 2).tolist()],
            vein_points=vein_points,
            serration_points=serration_points,
            original_width=original_width,
            original_height=original_height,
        )

        return result

    def _grayscale(self, img: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        return gray

    def _threshold(self, gray: np.ndarray) -> np.ndarray:
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            self.threshold_block_size,
            self.threshold_c,
        )
        return binary

    def _morphological_clean(self, binary: np.ndarray) -> np.ndarray:
        kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
        return cleaned

    def _find_contours(self, binary: np.ndarray) -> Tuple[List[np.ndarray], np.ndarray]:
        contours, hierarchy = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contours, hierarchy

    def _find_largest_contour(self, contours: List[np.ndarray]) -> np.ndarray:
        if not contours:
            return None
        return max(contours, key=cv2.contourArea)

    def _detect_veins(
        self, gray: np.ndarray, petal_contour: np.ndarray
    ) -> Tuple[int, List[Tuple[int, int]]]:
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [petal_contour], -1, 255, -1)

        masked_gray = cv2.bitwise_and(gray, gray, mask=mask)

        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(masked_gray)

        kernel_vert = np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]])
        kernel_horiz = np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]])
        kernel_45 = np.array([[-1, -1, 2], [-1, 2, -1], [2, -1, -1]])
        kernel_135 = np.array([[2, -1, -1], [-1, 2, -1], [-1, -1, 2]])

        edges_vert = cv2.filter2D(enhanced, -1, kernel_vert)
        edges_horiz = cv2.filter2D(enhanced, -1, kernel_horiz)
        edges_45 = cv2.filter2D(enhanced, -1, kernel_45)
        edges_135 = cv2.filter2D(enhanced, -1, kernel_135)

        edges = cv2.addWeighted(edges_vert, 0.25, edges_horiz, 0.25, 0)
        edges = cv2.addWeighted(edges, 0.5, edges_45, 0.25, 0)
        edges = cv2.addWeighted(edges, 0.75, edges_135, 0.25, 0)

        edges = cv2.bitwise_and(edges, edges, mask=mask)

        _, vein_binary = cv2.threshold(edges, 30, 255, cv2.THRESH_BINARY)

        vein_kernel = np.ones((2, 2), np.uint8)
        vein_binary = cv2.dilate(vein_binary, vein_kernel, iterations=1)

        vein_contours, _ = cv2.findContours(
            vein_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        min_vein_length = 15
        valid_veins = [
            cnt
            for cnt in vein_contours
            if cv2.arcLength(cnt, False) > min_vein_length
        ]

        vein_points = []
        for vein in valid_veins:
            M = cv2.moments(vein)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                vein_points.append((cx, cy))

        return len(valid_veins), vein_points

    def _calculate_serration(
        self, contour: np.ndarray
    ) -> Tuple[float, int, List[Tuple[int, int]]]:
        if len(contour) < 5:
            return 0.0, 0, []

        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        contour_area = cv2.contourArea(contour)
        serration_area = hull_area - contour_area

        serration_count = 0
        serration_points = []

        if len(approx) >= 3:
            approx_points = approx.reshape(-1, 2)
            hull_points = cv2.convexHull(approx, returnPoints=True)
            hull_points = hull_points.reshape(-1, 2)

            for i in range(len(approx_points)):
                p1 = approx_points[i]
                p2 = approx_points[(i + 1) % len(approx_points)]
                p3 = approx_points[(i + 2) % len(approx_points)]

                angle = self._calculate_angle(p1, p2, p3)

                if angle < 160:
                    serration_count += 1
                    serration_points.append(tuple(p2.tolist()))

        if serration_count == 0:
            serration_count = max(len(approx) - 4, 0)
            if serration_count > 0:
                step = max(1, len(approx) // serration_count)
                for i in range(0, len(approx), step):
                    if len(serration_points) < serration_count:
                        point = approx[i][0]
                        serration_points.append((int(point[0]), int(point[1])))

        return serration_area, serration_count, serration_points

    def _calculate_angle(
        self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray
    ) -> float:
        v1 = p1 - p2
        v2 = p3 - p2

        cosine = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
        cosine = np.clip(cosine, -1, 1)
        angle = np.arccos(cosine) * 180 / np.pi

        return angle

    def generate_overlay_image(
        self, image_bytes: bytes, result: AnalysisResult
    ) -> bytes:
        img_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        overlay = img.copy()

        if result.contours and len(result.contours) > 0:
            contour = np.array(result.contours[0], dtype=np.int32).reshape(-1, 1, 2)
            cv2.drawContours(overlay, [contour], -1, (0, 255, 0), 2)

            cv2.drawContours(overlay, [contour], -1, (0, 255, 0), 1)

        for point in result.vein_points:
            cv2.circle(overlay, (point[0], point[1]), 3, (255, 0, 0), -1)

        for point in result.serration_points:
            cv2.circle(overlay, (point[0], point[1]), 4, (0, 0, 255), -1)

        alpha = 0.6
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

        _, buffer = cv2.imencode(".png", img)
        return buffer.tobytes()


def image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")
