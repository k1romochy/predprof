from app.core.config import Settings


class TestSettings:
    def test_defaults(self):
        s = Settings(
            database_url="postgresql+asyncpg://u:p@localhost/db",
            jwt_secret="secret",
        )
        assert s.jwt_algorithm == "HS256"
        assert s.jwt_expire_minutes == 1440
        assert s.log_level == "INFO"

    def test_database_url_sync(self):
        s = Settings(
            database_url="postgresql+asyncpg://u:p@localhost/db",
            jwt_secret="s",
        )
        assert s.database_url_sync == "postgresql+psycopg2://u:p@localhost/db"

    def test_database_url_sync_no_asyncpg(self):
        s = Settings(
            database_url="postgresql+psycopg2://u:p@localhost/db",
            jwt_secret="s",
        )
        assert "+psycopg2" in s.database_url_sync

    def test_parse_cors_origins_string(self):
        result = Settings.parse_cors_origins("http://a.com, http://b.com")
        assert result == ["http://a.com", "http://b.com"]

    def test_parse_cors_origins_list(self):
        result = Settings.parse_cors_origins(["http://a.com"])
        assert result == ["http://a.com"]

    def test_cors_default(self):
        s = Settings(
            database_url="postgresql+asyncpg://u:p@localhost/db",
            jwt_secret="s",
        )
        assert "http://localhost:3000" in s.cors_origins

    def test_ml_service_url_default(self):
        s = Settings(
            database_url="postgresql+asyncpg://u:p@localhost/db",
            jwt_secret="s",
        )
        assert s.ml_service_url == "http://ml:8000"
