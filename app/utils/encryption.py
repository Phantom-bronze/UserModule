"""
Encryption Utilities
====================

This module provides functions for encrypting and decrypting sensitive data
such as Google credentials, access tokens, and API keys.

Encryption Method:
- Algorithm: AES-256 in GCM mode (Galois/Counter Mode)
- Key derivation: PBKDF2 with SHA-256
- Authentication: Built-in with GCM mode
- Encoding: Base64 for storage

Security Features:
- Each encryption uses a unique random nonce (IV)
- Authentication tag prevents tampering
- Key is derived from ENCRYPTION_KEY environment variable
- Constant-time comparison prevents timing attacks

IMPORTANT:
- The ENCRYPTION_KEY must be kept secure and never committed to version control
- Changing the key will make all existing encrypted data unreadable
- In production, consider using a key management service (KMS)
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import secrets
import logging

from app.config import settings

# ============================================================
# Logger Configuration
# ============================================================
logger = logging.getLogger(__name__)


# ============================================================
# Key Derivation
# ============================================================

def _derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """
    Derive a cryptographic key from the password using PBKDF2.

    This function uses PBKDF2 (Password-Based Key Derivation Function 2)
    to derive a strong encryption key from the ENCRYPTION_KEY setting.

    Args:
        password: The password/key from settings
        salt: Salt for key derivation (generated if None)

    Returns:
        tuple: (derived_key, salt) - Both as bytes

    Security Notes:
        - Uses 100,000 iterations (OWASP recommendation)
        - SHA-256 hash algorithm
        - 32-byte (256-bit) key length for AES-256
        - Random 16-byte salt
    """
    if salt is None:
        salt = secrets.token_bytes(16)  # 16 bytes = 128 bits

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 32 bytes = 256 bits for AES-256
        salt=salt,
        iterations=100000,  # OWASP recommendation
    )

    key = kdf.derive(password.encode())
    return key, salt


# ============================================================
# Encryption Functions
# ============================================================

def encrypt_data(plaintext: str) -> str:
    """
    Encrypt sensitive data using AES-256-GCM.

    This function encrypts data using AES-256 in GCM mode, which provides
    both confidentiality and authenticity. The encrypted data includes:
    - Salt (for key derivation)
    - Nonce (IV for AES-GCM)
    - Ciphertext
    - Authentication tag (built into GCM)

    Args:
        plaintext: The data to encrypt (as string)

    Returns:
        str: Base64-encoded encrypted data

    Raises:
        ValueError: If plaintext is empty or encryption fails

    Example:
        >>> encrypted = encrypt_data("my-secret-token")
        >>> print(encrypted)
        'YWJjZGVmZ2hpamtsbW5vcA...'  # Base64 encoded

    Security:
        - Each encryption uses a unique random nonce
        - GCM mode provides authenticated encryption
        - Cannot be decrypted without the correct key
        - Tampering is detected via authentication tag
    """
    if not plaintext:
        raise ValueError("Cannot encrypt empty data")

    try:
        # Convert plaintext to bytes
        plaintext_bytes = plaintext.encode('utf-8')

        # Derive key with random salt
        key, salt = _derive_key(settings.ENCRYPTION_KEY)

        # Generate random nonce (12 bytes recommended for GCM)
        nonce = secrets.token_bytes(12)

        # Create AESGCM cipher
        aesgcm = AESGCM(key)

        # Encrypt the data
        # GCM mode automatically adds authentication tag to ciphertext
        ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)

        # Combine salt + nonce + ciphertext
        # Format: [16 bytes salt][12 bytes nonce][variable ciphertext+tag]
        encrypted_data = salt + nonce + ciphertext

        # Encode as base64 for storage
        encoded = base64.b64encode(encrypted_data).decode('utf-8')

        return encoded

    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise ValueError(f"Failed to encrypt data: {e}")


def decrypt_data(ciphertext: str) -> str:
    """
    Decrypt data that was encrypted with encrypt_data().

    This function reverses the encryption process, extracting the salt,
    nonce, and ciphertext, then decrypting using AES-256-GCM.

    Args:
        ciphertext: Base64-encoded encrypted data

    Returns:
        str: Decrypted plaintext

    Raises:
        ValueError: If ciphertext is invalid or decryption fails
        Exception: If authentication tag verification fails (data tampered)

    Example:
        >>> plaintext = decrypt_data(encrypted)
        >>> print(plaintext)
        'my-secret-token'

    Security:
        - Verifies authentication tag before decryption
        - Fails if data has been tampered with
        - Constant-time comparison prevents timing attacks
    """
    if not ciphertext:
        raise ValueError("Cannot decrypt empty data")

    try:
        # Decode from base64
        encrypted_data = base64.b64decode(ciphertext.encode('utf-8'))

        # Extract components
        # Format: [16 bytes salt][12 bytes nonce][variable ciphertext+tag]
        salt = encrypted_data[:16]
        nonce = encrypted_data[16:28]
        ciphertext_bytes = encrypted_data[28:]

        # Derive key using the same salt
        key, _ = _derive_key(settings.ENCRYPTION_KEY, salt)

        # Create AESGCM cipher
        aesgcm = AESGCM(key)

        # Decrypt the data
        # GCM automatically verifies authentication tag
        # Raises exception if tag verification fails (data tampered)
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_bytes, None)

        # Convert bytes back to string
        plaintext = plaintext_bytes.decode('utf-8')

        return plaintext

    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise ValueError(f"Failed to decrypt data: {e}")


# ============================================================
# Helper Functions
# ============================================================

def is_encrypted(data: str) -> bool:
    """
    Check if data appears to be encrypted.

    This is a simple heuristic check - it doesn't guarantee the data
    is encrypted with our system, just that it looks like base64.

    Args:
        data: String to check

    Returns:
        bool: True if data appears to be encrypted, False otherwise

    Example:
        >>> encrypted = encrypt_data("secret")
        >>> print(is_encrypted(encrypted))
        True
        >>> print(is_encrypted("plain text"))
        False
    """
    try:
        # Try to decode as base64
        decoded = base64.b64decode(data.encode('utf-8'))
        # Check if it has minimum length (salt + nonce + some data)
        # 16 (salt) + 12 (nonce) + 16 (min ciphertext) = 44 bytes minimum
        return len(decoded) >= 44
    except Exception:
        return False


def rotate_encryption_key(old_key: str, new_key: str, encrypted_data: str) -> str:
    """
    Re-encrypt data with a new encryption key.

    This function is used for key rotation - when you need to change
    the encryption key, use this to decrypt with old key and re-encrypt
    with new key.

    Args:
        old_key: The old encryption key
        new_key: The new encryption key
        encrypted_data: Data encrypted with old key

    Returns:
        str: Data encrypted with new key

    Raises:
        ValueError: If re-encryption fails

    Example:
        >>> # Rotate all encrypted data in database
        >>> credentials = db.query(GoogleCredential).all()
        >>> for cred in credentials:
        >>>     cred.client_secret = rotate_encryption_key(
        >>>         old_key=old_encryption_key,
        >>>         new_key=new_encryption_key,
        >>>         encrypted_data=cred.client_secret
        >>>     )
        >>> db.commit()

    WARNING:
        - This is a sensitive operation
        - Make sure you have backups before rotating keys
        - All encrypted data must be re-encrypted atomically
    """
    try:
        # Temporarily set old key
        original_key = settings.ENCRYPTION_KEY
        settings.ENCRYPTION_KEY = old_key

        # Decrypt with old key
        plaintext = decrypt_data(encrypted_data)

        # Set new key
        settings.ENCRYPTION_KEY = new_key

        # Encrypt with new key
        new_encrypted = encrypt_data(plaintext)

        # Restore original key
        settings.ENCRYPTION_KEY = original_key

        return new_encrypted

    except Exception as e:
        # Restore original key on error
        settings.ENCRYPTION_KEY = original_key
        logger.error(f"Key rotation failed: {e}")
        raise ValueError(f"Failed to rotate encryption key: {e}")


# ============================================================
# Validation
# ============================================================

def validate_encryption_key() -> bool:
    """
    Validate that the encryption key is properly configured.

    Checks:
    - Key exists
    - Key is not the default value
    - Key is strong enough (minimum length)

    Returns:
        bool: True if key is valid, False otherwise

    Example:
        >>> if not validate_encryption_key():
        >>>     raise ValueError("Invalid encryption key configuration")
    """
    key = settings.ENCRYPTION_KEY

    # Check if key exists
    if not key:
        logger.error("ENCRYPTION_KEY is not set")
        return False

    # Check if using default key (dangerous!)
    if "your-encryption-key" in key.lower() or "change-this" in key.lower():
        logger.error("Using default ENCRYPTION_KEY - please change it!")
        return False

    # Check minimum length (at least 32 characters recommended)
    if len(key) < 32:
        logger.warning("ENCRYPTION_KEY is too short - use at least 32 characters")
        return False

    logger.info("Encryption key validation passed")
    return True


# ============================================================
# Test Functions (for development only)
# ============================================================

def test_encryption():
    """
    Test encryption and decryption functionality.

    This function is for development/testing purposes only.
    DO NOT use in production code.

    Example:
        >>> test_encryption()
        Encryption test: PASSED
    """
    test_data = "Test sensitive data 123!@#"

    try:
        # Encrypt
        encrypted = encrypt_data(test_data)
        print(f"Encrypted: {encrypted[:50]}...")

        # Decrypt
        decrypted = decrypt_data(encrypted)
        print(f"Decrypted: {decrypted}")

        # Verify
        if decrypted == test_data:
            print("✓ Encryption test: PASSED")
            return True
        else:
            print("✗ Encryption test: FAILED - Data mismatch")
            return False

    except Exception as e:
        print(f"✗ Encryption test: FAILED - {e}")
        return False


# ============================================================
# Initialize encryption key validation on module load
# ============================================================

# Validate encryption key when module is imported
# This ensures the key is valid before any encryption operations
if settings.APP_ENV == "production":
    if not validate_encryption_key():
        raise ValueError(
            "Invalid encryption key configuration. "
            "Please set a strong ENCRYPTION_KEY in environment variables."
        )
