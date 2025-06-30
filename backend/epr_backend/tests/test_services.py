import pytest
from unittest.mock import Mock, patch
from app.services.email_service import EmailService
from app.services.sms_service import SMSService


class TestEmailService:
    """Test email service functionality."""
    
    @patch.dict('os.environ', {'SENDGRID_API_KEY': 'test_key'})
    @patch('sendgrid.SendGridAPIClient.send')
    @pytest.mark.asyncio
    async def test_send_email_success(self, mock_send):
        """Test successful email sending."""
        mock_send.return_value = Mock(status_code=202)
        
        email_service = EmailService()
        result = await email_service.send_email(
            to_emails=["test@example.com"],
            subject="Test Subject",
            html_content="<p>Test content</p>"
        )
        
        assert result is True
        mock_send.assert_called_once()
    
    @patch.dict('os.environ', {'SENDGRID_API_KEY': 'test_key'})
    @patch('sendgrid.SendGridAPIClient.send')
    @pytest.mark.asyncio
    async def test_send_email_failure(self, mock_send):
        """Test email sending failure handling."""
        mock_send.side_effect = Exception("SendGrid error")
        
        email_service = EmailService()
        result = await email_service.send_email(
            to_emails=["test@example.com"],
            subject="Test Subject",
            html_content="<p>Test content</p>"
        )
        
        assert result is False


class TestSMSService:
    """Test SMS service functionality."""
    
    @patch('twilio.rest.Client')
    @pytest.mark.asyncio
    async def test_send_sms_success(self, mock_client):
        """Test successful SMS sending."""
        mock_message = Mock(sid="SM123456789")
        mock_client.return_value.messages.create.return_value = mock_message
        
        sms_service = SMSService()
        result = await sms_service.send_sms(
            to_number="+1234567890",
            message="Test message"
        )
        
        assert result is True
    
    @patch.dict('os.environ', {'TWILIO_ACCOUNT_SID': 'test_sid', 'TWILIO_AUTH_TOKEN': 'test_token', 'TWILIO_FROM_NUMBER': '+1234567890'})
    @patch('twilio.rest.Client')
    @pytest.mark.asyncio
    async def test_send_sms_failure(self, mock_client):
        """Test SMS sending failure handling."""
        from twilio.base.exceptions import TwilioRestException
        
        mock_client.return_value.messages.create.side_effect = TwilioRestException(
            status=400,
            uri="/Messages",
            msg="Invalid phone number"
        )
        
        sms_service = SMSService()
        result = await sms_service.send_sms(
            to_number="invalid_number",
            message="Test message"
        )
        
        assert result is False


class TestFileStorageService:
    """Test file storage service functionality."""
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self, mock_s3):
        """Test successful file upload to S3."""
        mock_s3.upload_fileobj.return_value = None
        
        result = mock_s3.upload_fileobj("test_file", "test_bucket", "test_key")
        assert result is None
        mock_s3.upload_fileobj.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_presigned_url(self, mock_s3):
        """Test presigned URL generation."""
        url = mock_s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": "test_bucket", "Key": "test_key"},
            ExpiresIn=3600
        )
        
        assert "https://test-bucket.s3.amazonaws.com/test-file.pdf" in url
