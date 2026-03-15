import os
import time

import pytest

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-unit-tests")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")

from app.services.auth import (
    create_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestHashPassword:
    def test_returns_string(self):
        h = hash_password("mypassword")
        assert isinstance(h, str)

    def test_not_plaintext(self):
        h = hash_password("mypassword")
        assert h != "mypassword"

    def test_different_hashes(self):
        h1 = hash_password("password")
        h2 = hash_password("password")
        assert h1 != h2  # bcrypt salts differ


class TestVerifyPassword:
    def test_correct(self):
        h = hash_password("secret")
        assert verify_password("secret", h) is True

    def test_wrong(self):
        h = hash_password("secret")
        assert verify_password("wrong", h) is False

    def test_empty_password(self):
        h = hash_password("")
        assert verify_password("", h) is True
        assert verify_password("x", h) is False


class TestCreateAndDecodeToken:
    def test_round_trip(self):
        token = create_token(user_id=42, role="admin")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["role"] == "admin"

    def test_contains_exp(self):
        token = create_token(user_id=1, role="user")
        payload = decode_token(token)
        assert "exp" in payload

    def test_different_users(self):
        t1 = create_token(user_id=1, role="user")
        t2 = create_token(user_id=2, role="admin")
        assert t1 != t2

    def test_invalid_token(self):
        assert decode_token("not.a.valid.token") is None

    def test_tampered_token(self):
        token = create_token(user_id=1, role="user")
        tampered = token[:-4] + "XXXX"
        assert decode_token(tampered) is None
