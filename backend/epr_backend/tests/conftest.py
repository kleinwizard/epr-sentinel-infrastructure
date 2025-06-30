import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, patch
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

with patch('app.services.scheduler.RedisJobStore') as mock_redis_store:
    mock_redis_store.return_value = Mock()
    with patch('app.services.scheduler.task_scheduler') as mock_scheduler:
        mock_scheduler.start = Mock()
        mock_scheduler.stop = Mock()
        class MockTrustedHostMiddleware:
            def __init__(self, app, allowed_hosts=None):
                self.app = app
            
            async def __call__(self, scope, receive, send):
                await self.app(scope, receive, send)
        
        with patch('fastapi.middleware.trustedhost.TrustedHostMiddleware', MockTrustedHostMiddleware):
            from app.main import app

from app.database import get_db, Base
from app.auth import get_current_user
from app.schemas import User

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def anyio_backend():
    """Use asyncio backend for anyio."""
    return "asyncio"


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def override_get_db(db_session):
    """Override the get_db dependency to use test database."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """Create a test user."""
    return User(
        id="test-user-id",
        email="test@example.com",
        organization_id="test-org-id",
        created_at="2024-01-01T00:00:00"
    )


@pytest.fixture
def authenticated_user(test_user):
    """Override authentication to return test user."""
    from app.schemas import User as UserSchema
    
    user_obj = UserSchema(
        id="test-user-id",
        email="test@example.com",
        organization_id="test-org-id",
        created_at="2024-01-01T00:00:00"
    )
    
    def _get_current_user():
        return user_obj
    
    app.dependency_overrides[get_current_user] = _get_current_user
    yield user_obj
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    from fastapi.testclient import TestClient
    from httpx import AsyncClient
    import httpx
    
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_stripe():
    """Mock Stripe API calls."""
    with patch('stripe.PaymentIntent') as mock_payment_intent, \
         patch('stripe.Customer') as mock_customer, \
         patch('stripe.Subscription') as mock_subscription:
        
        mock_payment_intent.create.return_value = Mock(
            id="pi_test_123",
            client_secret="pi_test_123_secret_test",
            status="requires_payment_method"
        )
        
        mock_customer.create.return_value = Mock(
            id="cus_test_123",
            email="test@example.com"
        )
        
        mock_subscription.create.return_value = Mock(
            id="sub_test_123",
            status="active"
        )
        
        yield {
            'payment_intent': mock_payment_intent,
            'customer': mock_customer,
            'subscription': mock_subscription
        }


@pytest.fixture
def mock_sendgrid():
    """Mock SendGrid email service."""
    with patch('sendgrid.SendGridAPIClient') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.send.return_value = Mock(status_code=202)
        yield mock_instance


@pytest.fixture
def mock_twilio():
    """Mock Twilio SMS service."""
    with patch('twilio.rest.Client') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.messages.create.return_value = Mock(
            sid="SM_test_123",
            status="sent"
        )
        yield mock_instance


@pytest.fixture
def mock_s3():
    """Mock AWS S3 service."""
    with patch('boto3.client') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.upload_fileobj.return_value = None
        mock_instance.generate_presigned_url.return_value = "https://test-bucket.s3.amazonaws.com/test-file.pdf"
        yield mock_instance


@pytest.fixture
def mock_redis():
    """Mock Redis service."""
    with patch('redis.Redis') as mock_redis:
        mock_instance = Mock()
        mock_redis.return_value = mock_instance
        mock_instance.get.return_value = None
        mock_instance.set.return_value = True
        mock_instance.delete.return_value = 1
        yield mock_instance


@pytest.fixture
def mock_celery():
    """Mock Celery background tasks."""
    with patch('celery.Celery') as mock_celery:
        mock_instance = Mock()
        mock_celery.return_value = mock_instance
        mock_task = Mock()
        mock_task.delay.return_value = Mock(id="task_123", status="PENDING")
        mock_instance.task = lambda func: mock_task
        yield mock_instance


@pytest.fixture
def mock_scheduler():
    """Mock the task scheduler to prevent Redis dependency issues."""
    with patch('app.services.scheduler.task_scheduler') as mock_scheduler:
        mock_scheduler.start.return_value = None
        mock_scheduler.stop.return_value = None
        yield mock_scheduler


@pytest.fixture(autouse=True)
def disable_scheduler_startup():
    """Automatically disable scheduler startup for all tests."""
    with patch('app.main.task_scheduler') as mock_scheduler:
        mock_scheduler.start.return_value = None
        mock_scheduler.stop.return_value = None
        yield mock_scheduler


@pytest.fixture(autouse=True)
def disable_trusted_host_middleware():
    """Disable TrustedHostMiddleware for testing."""
    import os
    with patch.dict(os.environ, {'ALLOWED_HOSTS': 'localhost,127.0.0.1,testserver,test'}):
        yield
