import os
from typing import Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization

from src.domain.interfaces import ICryptographyService


class CryptoService(ICryptographyService):
    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """
        Gera um par de chaves ECDH (SECP256R1).
        Retorna (private_key_bytes, public_key_bytes) em formato PEM.
        """
        private_key = ec.generate_private_key(ec.SECP256R1())

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return private_pem, public_pem

    def derive_shared_key(
        self, private_key_pem: bytes, peer_public_key_pem: bytes
    ) -> bytes:
        """
        Deriva uma chave simétrica de 32 bytes (AES-256) a partir das chaves ECDH.
        """
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)

        peer_public_key = serialization.load_pem_public_key(peer_public_key_pem)

        shared_secret = private_key.exchange(ec.ECDH(), peer_public_key)

        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"handshake data",
        ).derive(shared_secret)

        return derived_key

    def encrypt_message(self, message: str, key: bytes) -> Tuple[str, str, str]:
        """
        Criptografa usando AES-GCM.
        Retorna (ciphertext_hex, iv_hex, tag_hex).
        Nota: A biblioteca cryptography retorna ciphertext + tag juntos no encrypt do AESGCM?
        Verificando: AESGCM.encrypt retorna ciphertext + tag concatenados.
        """
        aesgcm = AESGCM(key)
        iv = os.urandom(12)

        ciphertext_with_tag = aesgcm.encrypt(iv, message.encode("utf-8"), None)

        tag = ciphertext_with_tag[-16:]
        ciphertext = ciphertext_with_tag[:-16]

        return ciphertext.hex(), iv.hex(), tag.hex()

    def decrypt_message(
        self, ciphertext_hex: str, iv_hex: str, tag_hex: str, key: bytes
    ) -> str:
        aesgcm = AESGCM(key)
        iv = bytes.fromhex(iv_hex)
        tag = bytes.fromhex(tag_hex)
        ciphertext = bytes.fromhex(ciphertext_hex)

        data_to_decrypt = ciphertext + tag

        plaintext_bytes = aesgcm.decrypt(iv, data_to_decrypt, None)
        return plaintext_bytes.decode("utf-8")
