import os
from sqlalchemy.pool import StaticPool

class DefaultConfig:
    """Cấu hình mặc định theo 12-factor"""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-not-for-prod-secret-token-32bytes")
    JSON_SORT_KEYS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DB_URL", "sqlite:///dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

class TestConfig(DefaultConfig):
    """Cấu hình phục vụ kiểm thử pytest - dùng StaticPool cho in-memory SQLite"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": StaticPool,
        "connect_args": {"check_same_thread": False},
    }
    LOG_LEVEL = "WARNING"

class ProductionConfig(DefaultConfig):
    """Cấu hình môi trường Production với connection pool tối ưu"""
    LOG_LEVEL = "INFO"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }
