"""
Security utilities for authentication and authorization.

This module provides password hashing, JWT token generation, and verification.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
# Use bcrypt with specific backend to avoid wrap bug detection issues
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12,
    bcrypt__ident="2b",  # Use 2b identifier to avoid wrap bug detection
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    # Import bcrypt directly to avoid passlib issues
    import bcrypt
    
    # Truncate password to 72 bytes for bcrypt compatibility
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def dummy_verify_password() -> bool:
    """
    Dummy password verification for constant-time comparison.
    
    This function performs a real bcrypt hash verification with dummy data
    to match the timing of real password verification. This prevents timing
    attacks that could be used to enumerate valid user emails.
    
    Returns:
        Always returns False
    """
    # Use a pre-computed dummy hash to avoid generating it every time
    dummy_password = "dummy_password_for_timing_attack_mitigation"
    dummy_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYKKz3QJe3u"  # Hash of "dummy"
    
    # Perform actual bcrypt verification (takes ~50ms)
    import bcrypt
    password_bytes = dummy_password.encode('utf-8')[:72]
    hash_bytes = dummy_hash.encode('utf-8')
    bcrypt.checkpw(password_bytes, hash_bytes)
    
    return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    
    Note:
        Bcrypt has a 72-byte limit. Passwords are truncated if longer.
    """
    # Import bcrypt directly to avoid passlib wrap bug detection issues
    import bcrypt
    
    # Truncate password to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token data if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None



# ============================================================================
# Prompt Injection Protection (Bug #27 Fix)
# ============================================================================

import re
import unicodedata
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


# Prompt injection attack patterns
PROMPT_INJECTION_PATTERNS = [
    # System prompt override
    (r'ignore\s+(all\s+)?(previous|prior|earlier)\s+instructions?', 'prompt_override'),
    (r'disregard\s+(all\s+)?(previous|prior)\s+instructions?', 'prompt_override'),
    (r'forget\s+(everything|all)\s+you\s+were\s+told', 'prompt_override'),
    (r'התעלם\s+מכל\s+ההוראות', 'prompt_override'),  # Hebrew
    
    # Role escalation
    (r'you\s+are\s+now\s+(an?\s+|the\s+)?(admin|administrator|owner|doctor|superuser|clinic\s+owner)', 'role_escalation'),
    (r'i\s+am\s+(an?\s+|the\s+)?(admin|administrator|owner|system\s+admin|clinic\s+owner)', 'role_escalation'),
    (r'act\s+as\s+(if\s+)?(i\'m|i\s+am|you\s+are)', 'role_escalation'),
    (r'pretend\s+(i\s+have|you\s+have)\s+.*privileges?', 'role_escalation'),
    
    # Jailbreak attempts
    (r'\bdan\s+mode\b', 'jailbreak'),
    (r'do\s+anything\s+now', 'jailbreak'),
    (r'(debug|developer|admin)\s+mode', 'jailbreak'),
    (r'jailbreak\s+(successful|activated)', 'jailbreak'),
    
    # Data exfiltration
    (r'show\s+me\s+all\s+(patient|user|customer)\s+(data|records|information)', 'data_exfiltration'),
    (r'list\s+all\s+(patients|users|customers)', 'data_exfiltration'),
    (r'(give\s+me|what\s+are)\s+(everyone\'s|all|the)\s+(ssn|credit\s+card|password)', 'data_exfiltration'),
    (r'(all|the)\s+credit\s+card\s+numbers?', 'data_exfiltration'),
    
    # SQL injection indicators
    (r'(select|insert|update|delete|drop)\s+.*\s+from\s+', 'sql_injection'),
    (r';\s*drop\s+table', 'sql_injection'),
    (r'\'\s*or\s*\'1\'\s*=\s*\'1', 'sql_injection'),
    (r'--\s*$', 'sql_injection'),
    
    # System/debug commands
    (r'\[system\s+override\]', 'system_command'),
    (r'\[escalate:', 'system_command'),
    (r'execute\s+(sql|query|command):', 'system_command'),
]


def normalize_unicode(text: str) -> str:
    """
    Normalize unicode characters to detect obfuscation.
    
    Converts lookalike characters (Greek, Cyrillic, etc.) to their
    ASCII equivalents to prevent unicode obfuscation attacks.
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    # Normalize to NFKD form (compatibility decomposition)
    normalized = unicodedata.normalize('NFKD', text)
    
    # Convert to ASCII, ignoring non-ASCII characters
    ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
    
    return ascii_text


def detect_prompt_injection(text: str) -> Dict[str, Any]:
    """
    Detect prompt injection attacks in user input.
    
    Args:
        text: User input text
        
    Returns:
        Dictionary with detection results:
        - is_malicious: bool
        - threat_types: List[str]
        - confidence: float (0.0 to 1.0)
        - matched_patterns: List[str]
    """
    # Normalize unicode to detect obfuscation
    normalized_text = normalize_unicode(text)
    
    threat_types = set()
    matched_patterns = []
    
    # Check against all patterns on both original and normalized text
    for pattern, threat_type in PROMPT_INJECTION_PATTERNS:
        # Check original text
        if re.search(pattern, text, re.IGNORECASE):
            threat_types.add(threat_type)
            matched_patterns.append(pattern)
        # Also check normalized text (for unicode obfuscation)
        elif normalized_text and re.search(pattern, normalized_text, re.IGNORECASE):
            threat_types.add(threat_type)
            threat_types.add('unicode_obfuscation')
            matched_patterns.append(pattern)
    
    # Calculate confidence based on number of matches
    confidence = min(len(matched_patterns) * 0.3, 1.0)
    if len(matched_patterns) > 0:
        confidence = max(confidence, 0.8)  # High confidence for any match
    
    # Check for unicode obfuscation (only if text contains ASCII-like characters)
    # Don't flag legitimate non-ASCII text (Hebrew, Arabic, etc.)
    if normalized_text != text and normalized_text:
        # Check if the text contains lookalike characters (Greek/Cyrillic mixed with ASCII)
        has_ascii = any(ord(c) < 128 for c in text)
        has_non_ascii = any(ord(c) >= 128 for c in text)
        
        # Only flag as obfuscation if mixing ASCII with lookalikes
        if has_ascii and has_non_ascii and len(matched_patterns) > 0:
            if 'unicode_obfuscation' not in threat_types:
                threat_types.add('unicode_obfuscation')
            confidence = max(confidence, 0.9)
    
    is_malicious = len(threat_types) > 0
    
    return {
        'is_malicious': is_malicious,
        'threat_types': list(threat_types),
        'confidence': confidence,
        'matched_patterns': matched_patterns,
    }


def sanitize_input(
    text: str,
    user_role: Optional[str] = None,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sanitize user input to prevent prompt injection attacks.
    
    This function:
    1. Detects prompt injection attempts
    2. Normalizes unicode obfuscation
    3. Provides context-aware validation
    4. Returns sanitized input or blocks malicious input
    
    Args:
        text: User input text
        user_role: Optional user role for context-aware validation
        context: Optional context (e.g., 'viewing_own_records')
        
    Returns:
        Dictionary with sanitization results:
        - is_safe: bool
        - sanitized_input: str (original or sanitized)
        - original_input: str
        - threat_type: List[str]
        - confidence: float
        - action: str ('allow', 'sanitize', 'block')
    """
    # Preserve original input
    original_input = text
    
    # Detect prompt injection
    detection_result = detect_prompt_injection(text)
    
    # Context-aware validation
    if context == 'viewing_own_records' and user_role == 'patient':
        # Reduce false positives for legitimate patient requests
        if 'show me my patient records' in text.lower():
            detection_result['confidence'] *= 0.5
    
    # Determine action based on threat level
    if detection_result['is_malicious']:
        if detection_result['confidence'] >= 0.8:
            # High confidence - block completely
            action = 'block'
            is_safe = False
            sanitized_input = ""
            
            # Log the attack attempt
            logger.warning(
                f"Prompt injection attack blocked: {detection_result['threat_types']} "
                f"(confidence: {detection_result['confidence']:.2f})"
            )
        elif detection_result['confidence'] >= 0.5:
            # Medium confidence - sanitize
            action = 'sanitize'
            is_safe = False
            # Remove matched patterns
            sanitized_input = text
            for pattern, _ in PROMPT_INJECTION_PATTERNS:
                sanitized_input = re.sub(pattern, '[REDACTED]', sanitized_input, flags=re.IGNORECASE)
            
            logger.info(
                f"Prompt injection attempt sanitized: {detection_result['threat_types']} "
                f"(confidence: {detection_result['confidence']:.2f})"
            )
        else:
            # Low confidence - allow with warning
            action = 'allow'
            is_safe = True
            sanitized_input = text
            
            logger.debug(
                f"Low confidence prompt injection detected: {detection_result['threat_types']} "
                f"(confidence: {detection_result['confidence']:.2f})"
            )
    else:
        # No threats detected
        action = 'allow'
        is_safe = True
        sanitized_input = text
    
    return {
        'is_safe': is_safe,
        'sanitized_input': sanitized_input,
        'original_input': original_input,
        'threat_type': detection_result['threat_types'],
        'confidence': detection_result['confidence'],
        'action': action,
    }

