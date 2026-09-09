from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac

from .receipts import EvalReceipt


@dataclass(frozen=True)
class SignedReceipt:
    content_hash: str
    signature: str
    algorithm: str = "hmac-sha256"


class ReceiptSigner:
    """Trusted-control-plane signer for evaluation receipts.

    The key must be supplied outside candidate-readable source control. HMAC is
    intentionally simple and stdlib-only; deployments may replace this with an
    asymmetric/KMS signer without changing the receipt content hash contract.
    """

    def __init__(self, secret: bytes) -> None:
        if len(secret) < 32:
            raise ValueError("Signing secret must be at least 32 bytes")
        self._secret = secret

    def sign(self, receipt: EvalReceipt) -> SignedReceipt:
        sig = hmac.new(self._secret, receipt.content_hash.encode("ascii"), hashlib.sha256).hexdigest()
        return SignedReceipt(receipt.content_hash, sig)

    def verify(self, receipt: EvalReceipt, signed: SignedReceipt) -> bool:
        if signed.algorithm != "hmac-sha256" or signed.content_hash != receipt.content_hash:
            return False
        expected = hmac.new(self._secret, receipt.content_hash.encode("ascii"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signed.signature)
