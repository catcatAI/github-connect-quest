import os
import uuid
try:
    from cryptography.fernet import Fernet
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
    from cryptography.fernet import Fernet
try:
    from secretsharing import SecretSharer
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "secret-sharing"])
    from secretsharing import SecretSharer
from typing import List, Tuple, Optional

class GenesisManager:
    """
    Manages the creation and recovery of the AI's core identity components
    using a (2, 3) Shamir's Secret Sharing scheme.
    """

    @staticmethod
    def create_genesis_secret() -> Tuple[str, str]:
        """
        Generates the core components and combines them into a single secret string.

        Returns:
            A tuple containing:
            - The Genesis Secret string (format: "UID:HAM_KEY").
            - The UID part of the secret.
        """
        uid = f"uid_{uuid.uuid4().hex}"
        ham_key = Fernet.generate_key().decode('utf-8')
        genesis_secret = f"{uid}:{ham_key}"
        return genesis_secret, uid

    @staticmethod
    def split_secret_into_shards(secret: str) -> List[str]:
        """
        Splits the Genesis Secret into three shards using a (2, 3) scheme.

        Args:
            secret: The combined secret string to split.

        Returns:
            A list of three hex-encoded secret shards.
        """
        # The hex format is more robust for copy-pasting and QR codes.
        secret_hex = secret.encode('utf-8').hex()
        return SecretSharer.split_secret(secret_hex, 2, 3)

    @staticmethod
    def recover_secret_from_shards(shards: List[str]) -> Optional[str]:
        """
        Recovers the Genesis Secret from a list of two or more shards.

        Args:
            shards: A list containing two or more hex-encoded secret shards.

        Returns:
            The recovered secret string, or None if recovery fails.
        """
        if len(shards) < 2:
            return None
        try:
            recovered_hex = SecretSharer.recover_secret(shards[:2])
            return bytes.fromhex(recovered_hex).decode('utf-8')
        except Exception as e:
            print(f"[GenesisManager] Error recovering secret: {e}")
            return None

    @staticmethod
    def parse_genesis_secret(secret: str) -> Optional[Tuple[str, str]]:
        """
        Parses the recovered secret string to extract the UID and HAM Key.

        Args:
            secret: The recovered genesis secret.

        Returns:
            A tuple (UID, HAM_KEY), or None if parsing fails.
        """
        parts = secret.split(':', 1)
        if len(parts) == 2 and parts[0].startswith("uid_"):
            return parts[0], parts[1]
        return None

if __name__ == '__main__':
    print("--- GenesisManager Test ---")

    # 1. Create a new genesis secret
    genesis_secret, uid = GenesisManager.create_genesis_secret()
    print(f"Generated UID: {uid}")
    print(f"Generated Genesis Secret: {genesis_secret}")
    assert genesis_secret.startswith(uid)

    # 2. Split the secret into shards
    shards = GenesisManager.split_secret_into_shards(genesis_secret)
    print(f"\nGenerated 3 Shards (any 2 are needed):")
    for i, shard in enumerate(shards):
        print(f"  Shard {i+1}: {shard}")
    assert len(shards) == 3

    # 3. Test recovery from different combinations of shards
    print("\n--- Testing Recovery ---")

    # Combination 1: Shards 1 & 2
    recovered12 = GenesisManager.recover_secret_from_shards([shards[0], shards[1]])
    print(f"Recovered from Shards 1 & 2: {recovered12 == genesis_secret}")
    assert recovered12 == genesis_secret

    # Combination 2: Shards 1 & 3
    recovered13 = GenesisManager.recover_secret_from_shards([shards[0], shards[2]])
    print(f"Recovered from Shards 1 & 3: {recovered13 == genesis_secret}")
    assert recovered13 == genesis_secret

    # Combination 3: Shards 2 & 3
    recovered23 = GenesisManager.recover_secret_from_shards([shards[1], shards[2]])
    print(f"Recovered from Shards 2 & 3: {recovered23 == genesis_secret}")
    assert recovered23 == genesis_secret

    # Combination 4: All 3 shards (should still work)
    recovered_all = GenesisManager.recover_secret_from_shards(shards)
    print(f"Recovered from all 3 Shards: {recovered_all == genesis_secret}")
    assert recovered_all == genesis_secret

    # Combination 5: Only 1 shard (should fail)
    recovered_one = GenesisManager.recover_secret_from_shards([shards[0]])
    print(f"Recovered from 1 Shard: {'Failed as expected' if recovered_one is None else 'Test Failed'}")
    assert recovered_one is None

    # 4. Test parsing the recovered secret
    print("\n--- Testing Parsing ---")
    parsed_uid, parsed_key = GenesisManager.parse_genesis_secret(recovered12)
    print(f"Parsed UID: {parsed_uid}")
    print(f"Parsed Key: {parsed_key}")
    assert parsed_uid == uid
    assert recovered12.endswith(parsed_key)

    print("\n--- GenesisManager Test Complete ---")
