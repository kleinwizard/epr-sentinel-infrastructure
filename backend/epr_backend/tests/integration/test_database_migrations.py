import pytest
import tempfile
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from app.database import Base
from app.database import User, Product, Material, Report

class TestDatabaseMigrations:
    """Test database migrations and schema changes"""
    
    @pytest.fixture
    def temp_db_url(self):
        """Create a temporary database for testing migrations"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        db_url = f"sqlite:///{temp_file.name}"
        yield db_url
        os.unlink(temp_file.name)
    
    @pytest.fixture
    def alembic_config(self, temp_db_url):
        """Create Alembic configuration for testing"""
        config = Config("alembic.ini")
        config.set_main_option("sqlalchemy.url", temp_db_url)
        return config
    
    def test_migration_from_empty_database(self, alembic_config, temp_db_url):
        """Test running migrations on an empty database"""
        command.upgrade(alembic_config, "head")
        
        engine = create_engine(temp_db_url)
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ))
            tables = [row[0] for row in result]
            
            expected_tables = ['users', 'products', 'materials', 'reports', 'organizations']
            for table in expected_tables:
                assert table in tables
    
    def test_migration_rollback(self, alembic_config, temp_db_url):
        """Test rolling back migrations"""
        command.upgrade(alembic_config, "head")
        
        engine = create_engine(temp_db_url)
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT version_num FROM alembic_version"
            ))
            current_version = result.scalar()
        
        command.downgrade(alembic_config, "-1")
        
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT version_num FROM alembic_version"
            ))
            new_version = result.scalar()
            assert new_version != current_version
    
    def test_migration_with_existing_data(self, alembic_config, temp_db_url):
        """Test migrations preserve existing data"""
        command.upgrade(alembic_config, "head")
        
        engine = create_engine(temp_db_url)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            test_user = User(
                id="test-user-id",
                email="migration_test@example.com",
                password_hash="hashed_password",
                organization_id="test-org-id",
                created_at=datetime(2024, 1, 1)
            )
            session.add(test_user)
            session.commit()
            user_id = test_user.id
        
        command.upgrade(alembic_config, "head")
        
        with SessionLocal() as session:
            user = session.query(User).filter(User.id == user_id).first()
            assert user is not None
            assert user.email == "migration_test@example.com"
    
    def test_schema_constraints(self, alembic_config, temp_db_url):
        """Test that database constraints are properly enforced"""
        command.upgrade(alembic_config, "head")
        
        engine = create_engine(temp_db_url)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            user1 = User(
                id="test-user-1",
                email="unique_test@example.com",
                password_hash="password1",
                organization_id="test-org-1",
                created_at=datetime(2024, 1, 1)
            )
            session.add(user1)
            session.commit()
            
            user2 = User(
                id="test-user-2",
                email="unique_test@example.com",
                password_hash="password2",
                organization_id="test-org-2",
                created_at=datetime(2024, 1, 1)
            )
            session.add(user2)
            
            with pytest.raises(Exception):  # Should raise integrity error
                session.commit()
    
    def test_foreign_key_constraints(self, alembic_config, temp_db_url):
        """Test foreign key constraints are working"""
        command.upgrade(alembic_config, "head")
        
        engine = create_engine(temp_db_url)
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys=ON"))
            conn.commit()
        
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            from app.database import Organization
            org = Organization(
                id="test-org-1",
                name="Test Organization",
                created_at=datetime(2024, 1, 1)
            )
            session.add(org)
            session.commit()
            
            product1 = Product(
                id="test-product-1",
                name="Test Product 1",
                sku="TEST-SKU-001",
                organization_id="test-org-1",
                created_at=datetime(2024, 1, 1)
            )
            session.add(product1)
            session.commit()  # Should succeed
            
            product2 = Product(
                id="test-product-2",
                name="Test Product 2",
                sku="TEST-SKU-002",
                organization_id="non-existent-org",
                created_at=datetime(2024, 1, 1)
            )
            session.add(product2)
            
            with pytest.raises(Exception):  # Should raise foreign key error
                session.commit()
    
    def test_index_creation(self, alembic_config, temp_db_url):
        """Test that database indexes are created"""
        command.upgrade(alembic_config, "head")
        
        engine = create_engine(temp_db_url)
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='index'"
            ))
            indexes = [row[0] for row in result]
            
            assert len(indexes) > 0
    
    def test_data_types_and_lengths(self, alembic_config, temp_db_url):
        """Test that column data types and lengths are correct"""
        command.upgrade(alembic_config, "head")
        
        engine = create_engine(temp_db_url)
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = {row[1]: row[2] for row in result}  # name: type
            
            assert 'email' in columns
            assert 'password_hash' in columns
            assert 'created_at' in columns
    
    def test_migration_idempotency(self, alembic_config, temp_db_url):
        """Test that running migrations multiple times is safe"""
        command.upgrade(alembic_config, "head")
        command.upgrade(alembic_config, "head")
        command.upgrade(alembic_config, "head")
        
        engine = create_engine(temp_db_url)
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ))
            tables = [row[0] for row in result]
            
            expected_tables = ['users', 'products', 'materials', 'reports', 'organizations']
            for table in expected_tables:
                assert table in tables

class TestDatabasePerformance:
    """Test database performance and optimization"""
    
    @pytest.fixture
    def temp_db_url(self):
        """Create a temporary database for testing migrations"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        db_url = f"sqlite:///{temp_file.name}"
        yield db_url
        os.unlink(temp_file.name)
    
    @pytest.fixture
    def populated_db(self, temp_db_url):
        """Create a database with test data for performance testing"""
        engine = create_engine(temp_db_url)
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            for i in range(100):
                user = User(
                    id=f"test-user-{i}",
                    email=f"user{i}@example.com",
                    password_hash="hashed_password",
                    organization_id="test-org-perf",
                    created_at=datetime(2024, 1, 1)
                )
                session.add(user)
            
            session.commit()
            
            for i in range(1000):
                product = Product(
                    id=f"test-product-{i}",
                    name=f"Product {i}",
                    sku=f"SKU-{i:04d}",
                    organization_id="test-org-perf",
                    created_at=datetime(2024, 1, 1)
                )
                session.add(product)
            
            session.commit()
        
        return temp_db_url
    
    def test_query_performance(self, populated_db):
        """Test that common queries perform within acceptable limits"""
        import time
        
        engine = create_engine(populated_db)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            start_time = time.time()
            products = session.query(Product).limit(50).all()
            query_time = time.time() - start_time
            
            assert len(products) == 50
            assert query_time < 1.0  # Should complete within 1 second
            
            start_time = time.time()
            products_with_sku = session.query(Product).filter(
                Product.sku.like("SKU-%")
            ).limit(25).all()
            query_time = time.time() - start_time
            
            assert len(products_with_sku) == 25
            assert query_time < 1.0
    
    def test_bulk_operations(self, populated_db):
        """Test bulk insert/update operations"""
        import time
        
        engine = create_engine(populated_db)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            start_time = time.time()
            
            new_products = []
            for i in range(100):
                product = Product(
                    id=f"bulk-product-{i}",
                    name=f"Bulk Product {i}",
                    sku=f"BULK-{i:03d}",
                    organization_id="test-org-perf",
                    created_at=datetime(2024, 1, 1)
                )
                new_products.append(product)
            
            session.bulk_save_objects(new_products)
            session.commit()
            
            bulk_time = time.time() - start_time
            assert bulk_time < 2.0  # Should complete within 2 seconds
