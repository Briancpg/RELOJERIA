from app.storage.r2 import detect_image_content_type


def test_detect_image_content_type():
    assert detect_image_content_type(b"\xff\xd8\xff\xe0data") == "image/jpeg"
    assert detect_image_content_type(b"\x89PNG\r\n\x1a\ndata") == "image/png"
    assert detect_image_content_type(b"RIFF0000WEBPdata") == "image/webp"
    assert detect_image_content_type(b"not-an-image") is None
