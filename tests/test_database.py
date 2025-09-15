"""
Test database setup without requiring a running PostgreSQL instance
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.engine import create_mock_engine
from sqlalchemy.orm import declarative_base


def test_sqlalchemy_import():
    """Test if SQLAlchemy can be imported and used"""
    Base = declarative_base()

    class TestModel(Base):
        __tablename__ = "test"
        id = Column(Integer, primary_key=True)
        name = Column(String(50))

    assert issubclass(TestModel, Base)


def test_database_url_parsing():
    """Test database URL parsing without connecting"""
    urls = [
        "postgresql://user:password@localhost:5432/konnect",
        "sqlite:///./test.db",
    ]

    def executor(sql, *args, **kwargs):
        pass

    for url in urls:
        engine = create_mock_engine(url, executor=executor)
        assert engine is not None


if __name__ == "__main__":
    test_sqlalchemy_import()
    test_database_url_parsing()
    print("Database setup validation complete")
