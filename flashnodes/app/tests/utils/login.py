import functools

from eth_account import Account, messages
from eth_utils import encode_hex

Account.enable_unaudited_hdwallet_features()
MNEMONIC = "toss body settle small rescue dry angry air cage genuine clinic reveal"


@functools.lru_cache(1)
def spawn_account() -> Account:
    return Account.from_mnemonic(MNEMONIC)


def sign_message(account: Account, nonce: str) -> str:
    return encode_hex(account.sign_message(messages.encode_defunct(text=nonce)).signature)


if __name__ == '__main__':
    account = spawn_account()
    print(sign_message(account, "12345678"))
