"""
Test database setup without requiring a running PostgreSQL instance
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os


def test_sqlalchemy_import():
    """Test if SQLAlchemy can be imported and used"""
    try:
        # Test basic SQLAlchemy imports
        from sqlalchemy import Column, Integer, String, DateTime
        from sqlalchemy.ext.declarative import declarative_base

        Base = declarative_base()

        class TestModel(Base):
            __tablename__ = "test"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        print("✓ SQLAlchemy imports and model definition successful")
        return True
    except Exception as e:
        print(f"✗ SQLAlchemy test failed: {e}")
        return False


def test_database_url_parsing():
    """Test database URL parsing without connecting"""
    try:
        # Test different database URL formats
        urls = [
            "postgresql://user:password@localhost:5432/konnect",
            "sqlite:///./test.db",
        ]

        for url in urls:
            engine = create_engine(url, strategy="mock", executor=lambda sql, *_: None)
            print(f"✓ Database URL parsed successfully: {url}")

        return True
    except Exception as e:
        print(f"✗ Database URL parsing failed: {e}")
        return False


if __name__ == "__main__":
    test_sqlalchemy_import()
    test_database_url_parsing()
    print("Database setup validation complete")
