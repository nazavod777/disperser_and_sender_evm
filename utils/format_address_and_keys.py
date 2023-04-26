import re

from eth_account import Account
from web3.auto import w3


def format_address_and_keys(value: str) -> dict:
    current_address: str | None = None
    current_key: str | None = None

    value.replace(';', ':').replace(' ', ':').replace('-', ':')

    for current_value in re.findall(r'\w+', value):
        if not current_value.startswith('0x'):
            current_value = f'0x{current_value}'

        try:
            current_address = w3.to_checksum_address(value=current_value)

        except ValueError:
            pass

        else:
            continue

        try:
            current_key = Account.from_key(current_value).key.hex()

        except ValueError:
            pass

    return {
        'private_key': current_key,
        'address': current_address
    }
