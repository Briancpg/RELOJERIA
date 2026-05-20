from app.api.v1.repairs import ALLOWED_IMAGE_UPLOAD_TYPES
from app.models.repair_image import RepairImageType


def test_repair_image_types_are_limited_to_watch_and_envelope():
    assert ALLOWED_IMAGE_UPLOAD_TYPES == {RepairImageType.watch, RepairImageType.envelope}
