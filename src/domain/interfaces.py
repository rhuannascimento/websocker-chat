from abc import ABC, abstractmethod
from typing import Tuple


class ICryptographyService(ABC):
    @abstractmethod
    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        pass

    @abstractmethod
    def derive_shared_key(self, private_key: bytes, peer_public_key: bytes) -> bytes:
        pass

    @abstractmethod
    def encrypt_message(self, message: str, key: bytes) -> Tuple[str, str, str]:
        pass

    @abstractmethod
    def decrypt_message(self, ciphertext: str, iv: str, tag: str, key: bytes) -> str:
        pass
