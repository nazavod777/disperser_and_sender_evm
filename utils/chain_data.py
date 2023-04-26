import asyncio.exceptions

import web3.auto
from eth_account import Account


async def get_chain_id(provider: web3.auto.Web3) -> int:
    try:
        return await provider.eth.chain_id

    except (asyncio.exceptions.TimeoutError, TimeoutError):
        return await get_chain_id(provider=provider)

    except Exception as error:
        if not str(error):
            return get_chain_id(provider=provider)


async def get_nonce(provider: web3.auto.Web3,
                    address: str) -> int:
    try:
        return await provider.eth.get_transaction_count(address)

    except (asyncio.exceptions.TimeoutError, TimeoutError):
        return await get_nonce(provider=provider,
                               address=address)

    except Exception as error:
        if not str(error):
            return get_nonce(provider=provider,
                             address=address)


async def get_gwei(provider: web3.auto.Web3) -> int:
    try:
        return int(await provider.eth.gas_price)

    except (asyncio.exceptions.TimeoutError, TimeoutError):
        return await get_gwei(provider=provider)

    except Exception as error:
        if not str(error):
            return get_gwei(provider=provider)


def get_address(private_key: str):
    if not private_key.startswith('0x'):
        private_key = f'0x{private_key}'

    try:
        return Account.from_key(private_key=private_key).address

    except (asyncio.exceptions.TimeoutError, TimeoutError):
        return get_address(private_key=private_key)

    except Exception as error:
        if not str(error):
            return get_address(private_key=private_key)
