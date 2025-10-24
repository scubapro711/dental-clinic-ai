"""
Unit Tests for Green Invoice API Integration

Tests for app.integrations.green_invoice module including:
- GreenInvoiceAPI class
- Invoice creation
- Receipt creation
- Document management
- Helper functions
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.integrations.green_invoice import (
    GreenInvoiceAPI,
    create_invoice_from_appointment,
)


@pytest.mark.unit
@pytest.mark.integration
class TestGreenInvoiceAPIInit:
    """Test GreenInvoiceAPI initialization."""
    
    def test_init_production(self):
        """Test initialization with production environment."""
        api = GreenInvoiceAPI(api_key="test_key_123", sandbox=False)
        
        assert api.api_key == "test_key_123"
        assert api.base_url == GreenInvoiceAPI.PRODUCTION_URL
        assert api.headers["Authorization"] == "Bearer test_key_123"
        assert api.headers["Content-Type"] == "application/json"
    
    def test_init_sandbox(self):
        """Test initialization with sandbox environment."""
        api = GreenInvoiceAPI(api_key="sandbox_key", sandbox=True)
        
        assert api.api_key == "sandbox_key"
        assert api.base_url == GreenInvoiceAPI.SANDBOX_URL
        assert api.headers["Authorization"] == "Bearer sandbox_key"
    
    def test_constants(self):
        """Test API constants are defined."""
        assert GreenInvoiceAPI.DOC_TYPE_INVOICE == 320
        assert GreenInvoiceAPI.DOC_TYPE_RECEIPT == 400
        assert GreenInvoiceAPI.DOC_TYPE_CREDIT == 330
        assert GreenInvoiceAPI.DOC_TYPE_PROFORMA == 100
        
        assert GreenInvoiceAPI.VAT_REGULAR == 0
        assert GreenInvoiceAPI.VAT_EXEMPT == 1
        assert GreenInvoiceAPI.VAT_ZERO == 2


@pytest.mark.unit
@pytest.mark.integration
class TestGreenInvoiceAPIRequest:
    """Test _request method."""
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_request_success(self, mock_request):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "status": "success"}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = GreenInvoiceAPI(api_key="test_key")
        result = api._request("GET", "documents/123")
        
        assert result == {"id": "123", "status": "success"}
        mock_request.assert_called_once()
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_request_with_data(self, mock_request):
        """Test API request with data."""
        mock_response = Mock()
        mock_response.json.return_value = {"created": True}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = GreenInvoiceAPI(api_key="test_key")
        data = {"client": {"name": "Test"}}
        result = api._request("POST", "documents", data)
        
        assert result == {"created": True}
        
        # Verify request was called with data
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["json"] == data
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_request_error_with_response(self, mock_request):
        """Test API request error with response."""
        mock_response = Mock()
        mock_response.text = "Error details"
        error = requests.exceptions.HTTPError()
        error.response = mock_response
        mock_request.side_effect = error
        
        api = GreenInvoiceAPI(api_key="test_key")
        
        with pytest.raises(requests.exceptions.HTTPError):
            api._request("GET", "invalid")
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_request_error_without_response(self, mock_request):
        """Test API request error without response."""
        error = requests.exceptions.ConnectionError("Connection failed")
        mock_request.side_effect = error
        
        api = GreenInvoiceAPI(api_key="test_key")
        
        with pytest.raises(requests.exceptions.ConnectionError):
            api._request("GET", "documents")


@pytest.mark.unit
@pytest.mark.integration
class TestGreenInvoiceAPICreateInvoice:
    """Test create_invoice method."""
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_create_invoice_basic(self, mock_request):
        """Test basic invoice creation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "INV-123",
            "url": "https://example.com/invoice.pdf"
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = GreenInvoiceAPI(api_key="test_key")
        items = [{
            "description": "ניקוי שיניים",
            "quantity": 1,
            "price": 300,
            "currency": "ILS",
            "vatType": 0
        }]
        
        result = api.create_invoice(
            client_name="יוסי כהן",
            client_email="yossi@example.com",
            items=items
        )
        
        assert result["id"] == "INV-123"
        
        # Verify request data
        call_kwargs = mock_request.call_args[1]
        data = call_kwargs["json"]
        assert data["type"] == GreenInvoiceAPI.DOC_TYPE_INVOICE
        assert data["client"]["name"] == "יוסי כהן"
        assert data["client"]["emails"] == ["yossi@example.com"]
        assert data["income"] == items
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_create_invoice_with_optional_fields(self, mock_request):
        """Test invoice creation with optional fields."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "INV-456"}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = GreenInvoiceAPI(api_key="test_key")
        items = [{"description": "טיפול", "quantity": 1, "price": 500}]
        
        result = api.create_invoice(
            client_name="דני לוי",
            client_email="danny@example.com",
            items=items,
            client_phone="050-1234567",
            client_id="123456789",
            lang="en",
            currency="USD",
            notes="תשלום מראש"
        )
        
        assert result["id"] == "INV-456"
        
        # Verify optional fields were included
        data = mock_request.call_args[1]["json"]
        assert data["client"]["phone"] == "050-1234567"
        assert data["client"]["id"] == "123456789"
        assert data["lang"] == "en"
        assert data["currency"] == "USD"
        assert data["remarks"] == "תשלום מראש"


@pytest.mark.unit
@pytest.mark.integration
class TestGreenInvoiceAPICreateReceipt:
    """Test create_receipt method."""
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_create_receipt_basic(self, mock_request):
        """Test basic receipt creation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "REC-789",
            "url": "https://example.com/receipt.pdf"
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = GreenInvoiceAPI(api_key="test_key")
        
        result = api.create_receipt(
            client_name="רונית אברהם",
            client_email="ronit@example.com",
            amount=250.0
        )
        
        assert result["id"] == "REC-789"
        
        # Verify request data
        data = mock_request.call_args[1]["json"]
        assert data["type"] == GreenInvoiceAPI.DOC_TYPE_RECEIPT
        assert data["client"]["name"] == "רונית אברהם"
        assert data["payment"][0]["amount"] == 250.0
        assert data["payment"][0]["type"] == "credit_card"
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_create_receipt_with_custom_fields(self, mock_request):
        """Test receipt creation with custom fields."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "REC-999"}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = GreenInvoiceAPI(api_key="test_key")
        
        result = api.create_receipt(
            client_name="משה",
            client_email="moshe@example.com",
            amount=1000.0,
            description="תשלום עבור טיפול",
            payment_method="cash",
            lang="en",
            currency="EUR"
        )
        
        assert result["id"] == "REC-999"
        
        data = mock_request.call_args[1]["json"]
        assert data["payment"][0]["type"] == "cash"
        assert data["lang"] == "en"
        assert data["currency"] == "EUR"


@pytest.mark.unit
@pytest.mark.integration
class TestGreenInvoiceAPIGetDocument:
    """Test get_document method."""
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_get_document(self, mock_request):
        """Test getting document by ID."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "DOC-123",
            "type": 320,
            "status": "sent"
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = GreenInvoiceAPI(api_key="test_key")
        result = api.get_document("DOC-123")
        
        assert result["id"] == "DOC-123"
        assert result["type"] == 320
        
        # Verify correct endpoint was called
        call_args = mock_request.call_args
        assert "documents/DOC-123" in call_args[1]["url"]


@pytest.mark.unit
@pytest.mark.integration
class TestGreenInvoiceAPIGetDocumentPDF:
    """Test get_document_pdf method."""
    
    @patch('app.integrations.green_invoice.requests.get')
    def test_get_document_pdf(self, mock_get):
        """Test getting document PDF."""
        mock_response = Mock()
        mock_response.content = b"PDF content here"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        api = GreenInvoiceAPI(api_key="test_key")
        pdf_content = api.get_document_pdf("DOC-456")
        
        assert pdf_content == b"PDF content here"
        
        # Verify correct URL was called
        call_args = mock_get.call_args
        assert "documents/DOC-456/pdf" in call_args[0][0]


@pytest.mark.unit
@pytest.mark.integration
class TestGreenInvoiceAPIListDocuments:
    """Test list_documents method."""
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_list_documents_basic(self, mock_request):
        """Test basic document listing."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [{"id": "1"}, {"id": "2"}],
            "total": 2
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = GreenInvoiceAPI(api_key="test_key")
        result = api.list_documents()
        
        assert len(result["items"]) == 2
        
        # Verify default pagination
        url = mock_request.call_args[1]["url"]
        assert "page=1" in url
        assert "pageSize=25" in url
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_list_documents_with_filters(self, mock_request):
        """Test document listing with filters."""
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = GreenInvoiceAPI(api_key="test_key")
        from_date = datetime(2025, 1, 1)
        to_date = datetime(2025, 1, 31)
        
        result = api.list_documents(
            doc_type=320,
            page=2,
            page_size=50,
            from_date=from_date,
            to_date=to_date
        )
        
        # Verify filters were applied
        url = mock_request.call_args[1]["url"]
        assert "type=320" in url
        assert "page=2" in url
        assert "pageSize=50" in url
        assert "fromDate=2025-01-01" in url
        assert "toDate=2025-01-31" in url


@pytest.mark.unit
@pytest.mark.integration
class TestGreenInvoiceAPICreateCreditNote:
    """Test create_credit_note method."""
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_create_credit_note(self, mock_request):
        """Test credit note creation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "CREDIT-123",
            "type": 330
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = GreenInvoiceAPI(api_key="test_key")
        result = api.create_credit_note(
            original_invoice_id="INV-789",
            reason="ביטול טיפול"
        )
        
        assert result["id"] == "CREDIT-123"
        
        # Verify request data
        data = mock_request.call_args[1]["json"]
        assert data["type"] == GreenInvoiceAPI.DOC_TYPE_CREDIT
        assert data["linkedDocumentId"] == "INV-789"
        assert data["remarks"] == "ביטול טיפול"


@pytest.mark.unit
@pytest.mark.integration
class TestGreenInvoiceAPITestConnection:
    """Test test_connection method."""
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_connection_success(self, mock_request):
        """Test successful connection test."""
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = GreenInvoiceAPI(api_key="test_key")
        result = api.test_connection()
        
        assert result is True
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_connection_failure(self, mock_request):
        """Test failed connection test."""
        mock_request.side_effect = requests.exceptions.ConnectionError()
        
        api = GreenInvoiceAPI(api_key="test_key")
        result = api.test_connection()
        
        assert result is False


@pytest.mark.unit
@pytest.mark.integration
class TestCreateInvoiceFromAppointment:
    """Test create_invoice_from_appointment helper function."""
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_create_invoice_from_appointment(self, mock_request):
        """Test creating invoice from appointment."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "INV-APPT-123",
            "url": "https://example.com/invoice.pdf"
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = create_invoice_from_appointment(
            api_key="test_key",
            patient_name="שרה כהן",
            patient_email="sarah@example.com",
            service_name="ניקוי שיניים",
            service_price=350.0,
            patient_phone="052-9876543",
            notes="תשלום מלא",
            sandbox=True
        )
        
        assert result["id"] == "INV-APPT-123"
        
        # Verify invoice data
        data = mock_request.call_args[1]["json"]
        assert data["client"]["name"] == "שרה כהן"
        assert data["client"]["emails"] == ["sarah@example.com"]
        assert data["client"]["phone"] == "052-9876543"
        assert data["income"][0]["description"] == "ניקוי שיניים"
        assert data["income"][0]["price"] == 350.0
        assert data["income"][0]["vatType"] == GreenInvoiceAPI.VAT_REGULAR
        assert data["remarks"] == "תשלום מלא"
    
    @patch('app.integrations.green_invoice.requests.request')
    def test_create_invoice_from_appointment_minimal(self, mock_request):
        """Test creating invoice with minimal parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "INV-MIN-456"}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = create_invoice_from_appointment(
            api_key="test_key",
            patient_name="דוד",
            patient_email="david@example.com",
            service_name="בדיקה",
            service_price=200.0
        )
        
        assert result["id"] == "INV-MIN-456"
        
        # Verify minimal data
        data = mock_request.call_args[1]["json"]
        assert "phone" not in data["client"]
        assert "remarks" not in data

