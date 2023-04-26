import asyncio
from random import randint, uniform

import web3.main
from web3 import Web3
from web3.auto import w3
from web3.eth import AsyncEth

from utils import bypass_ratelimit
from utils import get_address
from utils import get_chain_id, get_nonce, get_gwei, read_abi
from utils import logger


class Claimer:
    def __init__(self,
                 current_data: dict) -> None:
        self.private_key: str = current_data['private_key']
        self.address_to: str = current_data['address_to']
        self.address: str = current_data['address']
        self.target_coin_type: int = current_data['target_coin_type']
        self.native_coin_min_percent: None | float = current_data['native_coin_min_percent']
        self.native_coin_max_percent: None | float = current_data['native_coin_max_percent']
        self.erc_coin_address: None | str = current_data['erc_coin_address']
        self.erc_coin_min_percent: None | float = current_data['erc_coin_min_percent']
        self.erc_coin_max_percent: None | float = current_data['erc_coin_max_percent']
        self.rpc_url: str = current_data['rpc_url']

        self.provider = None

    async def transfer_native_tokens(self):
        balance_units = await bypass_ratelimit(current_function=self.provider.eth.get_balance,
                                               account=self.address)

        tasks = [
            get_gwei(provider=self.provider),
            get_nonce(provider=self.provider,
                      address=self.address),
            get_chain_id(provider=self.provider),
        ]

        current_gwei, current_nonce, current_chain_id = await asyncio.gather(*tasks)

        tx_data = {
            'nonce': current_nonce,
            'to': w3.to_checksum_address(value=self.address_to),
            'gasPrice': current_gwei,
            'from': self.address,
            'value': 0,
            'chainId': current_chain_id
        }

        try:
            gas_limit = await bypass_ratelimit(current_function=self.provider.eth.estimate_gas,
                                               transaction=tx_data)

        except ValueError as error:
            logger.error(f'{self.address} | Wrong Estimate Gas: {error}')
            return

        tx_data['gas'] = gas_limit

        if str(self.native_coin_min_percent).isdigit() \
                and str(self.native_coin_max_percent).isdigit():
            current_random_percent: int = randint(self.native_coin_min_percent,
                                                  self.native_coin_max_percent)

        else:
            current_random_percent: float = uniform(self.native_coin_min_percent,
                                                    self.native_coin_max_percent)

        current_available_balance = float(
            w3.from_wei(balance_units, 'ether') - tx_data['gas'] * w3.from_wei(tx_data['gasPrice'], 'gwei') / 10 ** 9)
        current_random_value = current_available_balance * current_random_percent / 100

        tx_data['value'] = w3.to_wei(current_random_value, 'ether')

        signed_tx = self.provider.eth.account.sign_transaction(transaction_dict=tx_data,
                                                               private_key=self.private_key)

        tx_hash = w3.to_hex(await bypass_ratelimit(current_function=self.provider.eth.send_raw_transaction,
                                                   transaction=signed_tx.rawTransaction))

        tx_receipt = await bypass_ratelimit(current_function=self.provider.eth.wait_for_transaction_receipt,
                                            transaction_hash=tx_hash,
                                            timeout=300,
                                            poll_latency=1)

        if tx_receipt['status'] == 1:
            logger.success(f'{self.address} | {self.private_key} - Successfully Send {current_random_value} '
                           f'to {w3.to_checksum_address(value=self.address_to)} - {tx_hash}')
            return True

        else:
            logger.error(f'{self.address} | {self.private_key} - Error When Sending {current_random_value} '
                         f'to {w3.to_checksum_address(value=self.address_to)} - {tx_hash}')
            return False

    async def transfer_erc_tokens(self):
        contract_provider = self.provider.eth.contract(address=w3.to_checksum_address(value=self.erc_coin_address),
                                                       abi=await read_abi(filename='tokens_universal_abi.json'))
        token_decimals: int = int(await bypass_ratelimit(current_function=contract_provider.functions.decimals().call))

        current_coin_balance_units: int = int(await bypass_ratelimit(
            current_function=contract_provider.functions.balanceOf(self.address).call))

        tasks = [
            get_gwei(provider=self.provider),
            get_nonce(provider=self.provider,
                      address=self.address),
            get_chain_id(provider=self.provider),
        ]

        current_gwei, current_nonce, current_chain_id = await asyncio.gather(*tasks)

        tx_data = {
            'from': self.address,
            'gasPrice': current_gwei,
            'value': 0,
            'nonce': current_nonce,
            'chainId': current_chain_id
        }

        if str(self.erc_coin_min_percent).isdigit() \
                and str(self.erc_coin_max_percent).isdigit():
            current_random_percent: int = randint(self.erc_coin_min_percent,
                                                  self.erc_coin_max_percent)

        else:
            current_random_percent: float = uniform(self.erc_coin_min_percent,
                                                    self.erc_coin_max_percent)

        current_random_value: float = float(
            current_coin_balance_units / 10 ** token_decimals * current_random_percent / 100)

        transfer_data_params = [
            w3.to_checksum_address(value=self.address_to),
            int(current_random_value * 10 ** token_decimals)
        ]

        try:
            gas_limit = await bypass_ratelimit(current_function=contract_provider.functions.transfer(
                *transfer_data_params
            ).estimate_gas,
                                               transaction=tx_data)

        except ValueError as error:
            logger.error(f'{self.address} | Wrong Estimate Gas: {error}')
            return

        tx_data['gas']: int = gas_limit

        transaction = await bypass_ratelimit(current_function=contract_provider.functions.transfer(
            *transfer_data_params
        ).build_transaction,
                                             transaction=tx_data)

        signed_tx = self.provider.eth.account.sign_transaction(transaction_dict=transaction,
                                                               private_key=self.private_key)

        await bypass_ratelimit(current_function=self.provider.eth.send_raw_transaction,
                               transaction=signed_tx.rawTransaction)

        tx_hash = w3.to_hex(w3.keccak(signed_tx.rawTransaction))

        tx_receipt = await bypass_ratelimit(current_function=self.provider.eth.wait_for_transaction_receipt,
                                            transaction_hash=tx_hash,
                                            timeout=300,
                                            poll_latency=1)

        if tx_receipt['status'] == 1:
            logger.success(f'{self.address} | {self.private_key} - Successfully Send {current_random_value} '
                           f'to {w3.to_checksum_address(value=self.address_to)} - {tx_hash}')
            return True

        else:
            logger.error(f'{self.address} | {self.private_key} - Error When Sending {current_random_value} '
                         f'to {w3.to_checksum_address(value=self.address_to)} - {tx_hash}')
            return False

    async def main_work(self):
        self.provider = web3.main.Web3 = Web3(
            Web3.AsyncHTTPProvider(self.rpc_url),
            modules={'eth': (AsyncEth,)},
            middlewares=[])

        if self.target_coin_type == 1:
            await self.transfer_native_tokens()

        elif self.target_coin_type == 2:
            await self.transfer_erc_tokens()


def claimer(current_data: dict) -> None:
    current_data['address'] = get_address(private_key=current_data['private_key'])

    asyncio.run(Claimer(current_data=current_data).main_work())
