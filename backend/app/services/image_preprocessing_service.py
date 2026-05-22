from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from app.core.exceptions import AppError


@dataclass(frozen=True)
class PreprocessedImage:
    label: str
    content: bytes
    content_type: str


class ImagePreprocessingService:
    def prepare_for_vision(self, content: bytes, *, max_width: int = 1800) -> list[PreprocessedImage]:
        try:
            with Image.open(BytesIO(content)) as image:
                oriented = ImageOps.exif_transpose(image).convert("RGB")
                resized = self._resize(oriented, max_width=max_width)
                original = self._compress_jpeg(resized, quality=88)
                enhanced = self._enhance(resized)
        except Exception as exc:
            raise AppError("No se pudo preprocesar la imagen del sobre") from exc

        return [
            PreprocessedImage(label="original", content=original, content_type="image/jpeg"),
            PreprocessedImage(label="enhanced", content=enhanced, content_type="image/jpeg"),
        ]

    def _resize(self, image: Image.Image, *, max_width: int) -> Image.Image:
        if image.width <= max_width:
            return image.copy()
        ratio = max_width / image.width
        return image.resize((max_width, max(1, int(image.height * ratio))), Image.Resampling.LANCZOS)

    def _enhance(self, image: Image.Image) -> bytes:
        grayscale = ImageOps.grayscale(image)
        grayscale = ImageOps.autocontrast(grayscale)

        try:
            grayscale = self._denoise_with_opencv(grayscale)
        except Exception:
            # Pillow fallback keeps the feature usable even if OpenCV cannot process an unusual image.
            grayscale = grayscale.filter(ImageFilter.MedianFilter(size=3))

        grayscale = ImageEnhance.Contrast(grayscale).enhance(1.85)
        grayscale = grayscale.filter(ImageFilter.UnsharpMask(radius=1.1, percent=140, threshold=3))
        return self._compress_jpeg(grayscale.convert("RGB"), quality=92)

    def _denoise_with_opencv(self, image: Image.Image) -> Image.Image:
        import cv2
        import numpy as np

        array = np.array(image)
        denoised = cv2.fastNlMeansDenoising(array, None, h=8, templateWindowSize=7, searchWindowSize=21)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrasted = clahe.apply(denoised)
        return Image.fromarray(contrasted)

    def _compress_jpeg(self, image: Image.Image, *, quality: int) -> bytes:
        output = BytesIO()
        image.save(output, format="JPEG", quality=quality, optimize=True)
        return output.getvalue()
