from app.auth.security import create_access_token, create_refresh_token, decode_token


def test_token_type_is_enforced():
    access = create_access_token("admin@example.com")
    refresh = create_refresh_token("admin@example.com")

    assert decode_token(access, "access") == "admin@example.com"
    assert decode_token(access, "refresh") is None
    assert decode_token(refresh, "refresh") == "admin@example.com"

