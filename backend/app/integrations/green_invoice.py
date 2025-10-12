"""
Green Invoice API Integration
https://www.greeninvoice.co.il/api-docs/
"""
import requests
from typing import Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GreenInvoiceAPI:
    """Green Invoice API client"""
    
    PRODUCTION_URL = "https://api.greeninvoice.co.il/api/v1"
    SANDBOX_URL = "https://sandbox.d.greeninvoice.co.il/api/v1"
    
    # Document types
    DOC_TYPE_INVOICE = 320  # חשבונית מס
    DOC_TYPE_RECEIPT = 400  # קבלה
    DOC_TYPE_CREDIT = 330   # זיכוי
    DOC_TYPE_PROFORMA = 100 # הצעת מחיר
    
    # VAT types
    VAT_REGULAR = 0   # מע"מ רגיל 17%
    VAT_EXEMPT = 1    # פטור ממע"מ
    VAT_ZERO = 2      # מע"מ 0%
    
    def __init__(self, api_key: str, sandbox: bool = False):
        """
        Initialize Green Invoice API client
        
        Args:
            api_key: Green Invoice API key
            sandbox: Use sandbox environment for testing
        """
        self.api_key = api_key
        self.base_url = self.SANDBOX_URL if sandbox else self.PRODUCTION_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Green Invoice API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
    
    def create_invoice(
        self,
        client_name: str,
        client_email: str,
        items: List[Dict],
        client_phone: Optional[str] = None,
        client_id: Optional[str] = None,
        lang: str = "he",
        currency: str = "ILS",
        notes: Optional[str] = None
    ) -> Dict:
        """
        Create a tax invoice (חשבונית מס)
        
        Args:
            client_name: Customer name
            client_email: Customer email
            items: List of invoice items
                [{
                    "description": "ניקוי שיניים",
                    "quantity": 1,
                    "price": 300,
                    "currency": "ILS",
                    "vatType": 0
                }]
            client_phone: Customer phone (optional)
            client_id: Customer ID number (optional)
            lang: Language (he/en)
            currency: Currency (ILS/USD/EUR)
            notes: Additional notes
        
        Returns:
            Invoice data with ID and PDF URL
        """
        data = {
            "type": self.DOC_TYPE_INVOICE,
            "lang": lang,
            "currency": currency,
            "client": {
                "name": client_name,
                "emails": [client_email]
            },
            "income": items
        }
        
        if client_phone:
            data["client"]["phone"] = client_phone
        
        if client_id:
            data["client"]["id"] = client_id
        
        if notes:
            data["remarks"] = notes
        
        return self._request("POST", "documents", data)
    
    def create_receipt(
        self,
        client_name: str,
        client_email: str,
        amount: float,
        description: str = "תשלום",
        payment_method: str = "credit_card",
        lang: str = "he",
        currency: str = "ILS"
    ) -> Dict:
        """
        Create a receipt (קבלה)
        
        Args:
            client_name: Customer name
            client_email: Customer email
            amount: Payment amount
            description: Payment description
            payment_method: Payment method (credit_card/cash/bank_transfer/check)
            lang: Language (he/en)
            currency: Currency (ILS/USD/EUR)
        
        Returns:
            Receipt data with ID and PDF URL
        """
        data = {
            "type": self.DOC_TYPE_RECEIPT,
            "lang": lang,
            "currency": currency,
            "client": {
                "name": client_name,
                "emails": [client_email]
            },
            "payment": [{
                "type": payment_method,
                "amount": amount,
                "currency": currency
            }]
        }
        
        return self._request("POST", "documents", data)
    
    def get_document(self, document_id: str) -> Dict:
        """Get document by ID"""
        return self._request("GET", f"documents/{document_id}")
    
    def get_document_pdf(self, document_id: str) -> bytes:
        """Get document PDF"""
        url = f"{self.base_url}/documents/{document_id}/pdf"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.content
    
    def list_documents(
        self,
        doc_type: Optional[int] = None,
        page: int = 1,
        page_size: int = 25,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict:
        """
        List documents
        
        Args:
            doc_type: Document type (320=invoice, 400=receipt, etc.)
            page: Page number (1-indexed)
            page_size: Items per page
            from_date: Filter from date
            to_date: Filter to date
        
        Returns:
            List of documents
        """
        params = {
            "page": page,
            "pageSize": page_size
        }
        
        if doc_type:
            params["type"] = doc_type
        
        if from_date:
            params["fromDate"] = from_date.strftime("%Y-%m-%d")
        
        if to_date:
            params["toDate"] = to_date.strftime("%Y-%m-%d")
        
        # Build query string
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        
        return self._request("GET", f"documents?{query}")
    
    def create_credit_note(
        self,
        original_invoice_id: str,
        reason: str = "ביטול"
    ) -> Dict:
        """
        Create a credit note (זיכוי) for an invoice
        
        Args:
            original_invoice_id: ID of the original invoice
            reason: Reason for credit note
        
        Returns:
            Credit note data
        """
        data = {
            "type": self.DOC_TYPE_CREDIT,
            "linkedDocumentId": original_invoice_id,
            "remarks": reason
        }
        
        return self._request("POST", "documents", data)
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            self._request("GET", "documents?page=1&pageSize=1")
            return True
        except Exception as e:
            logger.error(f"Green Invoice connection test failed: {e}")
            return False


# Helper function to create invoice from appointment
def create_invoice_from_appointment(
    api_key: str,
    patient_name: str,
    patient_email: str,
    service_name: str,
    service_price: float,
    patient_phone: Optional[str] = None,
    notes: Optional[str] = None,
    sandbox: bool = False
) -> Dict:
    """
    Create an invoice for a dental appointment
    
    Args:
        api_key: Green Invoice API key
        patient_name: Patient name
        patient_email: Patient email
        service_name: Service description (e.g., "ניקוי שיניים")
        service_price: Service price in ILS
        patient_phone: Patient phone (optional)
        notes: Additional notes (optional)
        sandbox: Use sandbox environment
    
    Returns:
        Invoice data
    """
    client = GreenInvoiceAPI(api_key, sandbox=sandbox)
    
    items = [{
        "description": service_name,
        "quantity": 1,
        "price": service_price,
        "currency": "ILS",
        "vatType": GreenInvoiceAPI.VAT_REGULAR  # 17% VAT
    }]
    
    return client.create_invoice(
        client_name=patient_name,
        client_email=patient_email,
        items=items,
        client_phone=patient_phone,
        notes=notes,
        lang="he",
        currency="ILS"
    )

