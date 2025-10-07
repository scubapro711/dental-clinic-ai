"""
SQLAlchemy Encrypted Field Types
Automatically encrypt/decrypt fields in database
"""

from sqlalchemy import String, TypeDecorator
from sqlalchemy.types import Text
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy type for encrypted strings.
    
    Automatically encrypts on write and decrypts on read.
    Stores encrypted data as TEXT in database.
    
    Usage:
        class Patient(Base):
            __tablename__ = "patients"
            
            id = Column(Integer, primary_key=True)
            name = Column(String(255))
            ssn = Column(EncryptedString(255))  # Encrypted!
            credit_card = Column(EncryptedString(255))  # Encrypted!
    """
    
    impl = Text
    cache_ok = True
    
    def __init__(self, length: Optional[int] = None):
        """
        Initialize encrypted string field.
        
        Args:
            length: Maximum length of DECRYPTED string (for validation)
        """
        self.length = length
        super().__init__()
    
    def process_bind_param(self, value, dialect):
        """
        Encrypt value before storing in database.
        
        Args:
            value: Plain text value
            dialect: SQL dialect
            
        Returns:
            Encrypted value
        """
        if value is not None:
            from .encryption_service import get_encryption_service
            
            try:
                # Validate length
                if self.length and len(value) > self.length:
                    raise ValueError(f"Value exceeds maximum length of {self.length}")
                
                # Encrypt
                encrypted = get_encryption_service().encrypt(value)
                logger.debug(f"Encrypted field (length: {len(value)} -> {len(encrypted)})")
                return encrypted
            except Exception as e:
                logger.error(f"Failed to encrypt field: {e}")
                raise
        
        return value
    
    def process_result_value(self, value, dialect):
        """
        Decrypt value after reading from database.
        
        Args:
            value: Encrypted value
            dialect: SQL dialect
            
        Returns:
            Decrypted plain text value
        """
        if value is not None:
            from .encryption_service import get_encryption_service
            
            try:
                # Decrypt
                decrypted = get_encryption_service().decrypt(value)
                logger.debug(f"Decrypted field (length: {len(value)} -> {len(decrypted)})")
                return decrypted
            except Exception as e:
                logger.error(f"Failed to decrypt field: {e}")
                raise
        
        return value


class MaskedString(TypeDecorator):
    """
    SQLAlchemy type for masked strings.
    
    Returns masked version by default, requires explicit decrypt() call for full value.
    Useful for SSN, credit cards where you want to show last 4 digits only.
    
    Usage:
        class Patient(Base):
            __tablename__ = "patients"
            
            id = Column(Integer, primary_key=True)
            ssn = Column(MaskedString(11, mask_char='*', show_last=4))
            
        # Reading
        patient.ssn  # Returns: "*******6789"
        patient.ssn.decrypt()  # Returns: "123-45-6789"
    """
    
    impl = Text
    cache_ok = True
    
    def __init__(self, length: Optional[int] = None, mask_char: str = '*', show_last: int = 4):
        """
        Initialize masked string field.
        
        Args:
            length: Maximum length of DECRYPTED string
            mask_char: Character to use for masking
            show_last: Number of characters to show at end
        """
        self.length = length
        self.mask_char = mask_char
        self.show_last = show_last
        super().__init__()
    
    def process_bind_param(self, value, dialect):
        """Encrypt before storing."""
        if value is not None:
            from .encryption_service import get_encryption_service
            
            try:
                if self.length and len(value) > self.length:
                    raise ValueError(f"Value exceeds maximum length of {self.length}")
                
                return get_encryption_service().encrypt(value)
            except Exception as e:
                logger.error(f"Failed to encrypt masked field: {e}")
                raise
        
        return value
    
    def process_result_value(self, value, dialect):
        """Return masked version by default."""
        if value is not None:
            from .encryption_service import get_encryption_service
            
            try:
                # Decrypt
                decrypted = get_encryption_service().decrypt(value)
                
                # Mask
                if len(decrypted) <= self.show_last:
                    return decrypted  # Too short to mask
                
                masked = self.mask_char * (len(decrypted) - self.show_last) + decrypted[-self.show_last:]
                
                # Return MaskedValue object that allows explicit decrypt
                return MaskedValue(masked, value)
            except Exception as e:
                logger.error(f"Failed to decrypt masked field: {e}")
                raise
        
        return value


class MaskedValue:
    """
    Wrapper for masked values that allows explicit decryption.
    """
    
    def __init__(self, masked: str, encrypted: str):
        self._masked = masked
        self._encrypted = encrypted
    
    def __str__(self):
        """Return masked value by default."""
        return self._masked
    
    def __repr__(self):
        return f"MaskedValue('{self._masked}')"
    
    def decrypt(self) -> str:
        """Explicitly decrypt and return full value."""
        from .encryption_service import get_encryption_service
        return get_encryption_service().decrypt(self._encrypted)
    
    @property
    def masked(self) -> str:
        """Get masked value."""
        return self._masked


# Example usage
if __name__ == "__main__":
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    import os
    
    # Set encryption key
    os.environ['ENCRYPTION_KEY'] = 'test-key-for-development-only'
    
    # Create in-memory database
    Base = declarative_base()
    engine = create_engine('sqlite:///:memory:', echo=True)
    
    class Patient(Base):
        __tablename__ = "patients"
        
        id = Column(Integer, primary_key=True)
        name = Column(String(255))
        ssn = Column(EncryptedString(11))
        credit_card = Column(EncryptedString(19))
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Insert patient with encrypted fields
    patient = Patient(
        name="John Doe",
        ssn="123-45-6789",
        credit_card="4111-1111-1111-1111"
    )
    session.add(patient)
    session.commit()
    
    # Read patient - fields are automatically decrypted
    retrieved_patient = session.query(Patient).first()
    print(f"\nName: {retrieved_patient.name}")
    print(f"SSN: {retrieved_patient.ssn}")
    print(f"Credit Card: {retrieved_patient.credit_card}")
    
    # Check raw database value (encrypted)
    result = engine.execute("SELECT ssn FROM patients WHERE id = 1")
    raw_ssn = result.fetchone()[0]
    print(f"\nRaw SSN in database (encrypted): {raw_ssn}")
