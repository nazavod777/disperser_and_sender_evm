from asynchuobi.api.clients.wallet import WalletHuobiClient
from web3.auto import w3

from utils import get_random_withdraw_amount
from utils import logger


class HuobiDisperser:
    def __init__(self,
                 access_key: str,
                 secret_key: str,
                 withdraw_token_name: str,
                 withdraw_chain_name: str,
                 target_address: str,
                 min_withdraw_amount: str,
                 max_withdraw_amount: str) -> None:
        self.access_key: str = access_key
        self.secret_key: str = secret_key
        self.withdraw_token_name: str = withdraw_token_name
        self.withdraw_chain_name: str = withdraw_chain_name
        self.target_address: str = w3.to_checksum_address(value=target_address)
        self.min_withdraw_amount: str = min_withdraw_amount
        self.max_withdraw_amount: str = max_withdraw_amount

    async def bypass_rate_limit(self,
                                current_function,
                                **kwargs) -> dict:
        withdraw_response = await current_function(**kwargs)

        if withdraw_response.get('err-msg') and withdraw_response['err-msg'] == 'exceeded rate limit':
            return await self.bypass_rate_limit(current_function=current_function,
                                                **kwargs)

        return withdraw_response

    async def main_work(self):
        async with WalletHuobiClient(
                access_key=self.access_key,
                secret_key=self.secret_key,
        ) as client:
            random_withdraw_amount = get_random_withdraw_amount(min_withdraw_amount=self.min_withdraw_amount,
                                                                max_withdraw_amount=self.max_withdraw_amount)

            withdraw_response = await self.bypass_rate_limit(current_function=client.create_withdraw_request,
                                                             address=self.target_address,
                                                             chain=self.withdraw_chain_name,
                                                             currency=self.withdraw_token_name,
                                                             amount=random_withdraw_amount)

            if withdraw_response.get('err-msg'):
                if 'Insufficient balance' in withdraw_response['err-msg']:
                    logger.error(f'{self.target_address} | Insufficient Balance')

                elif 'API withdrawal does not support temporary addresses' in withdraw_response['err-msg']:
                    logger.error(f'{self.target_address} | Address Not in WhiteList')

                elif 'currency not open, please waiting' in withdraw_response['err-msg']:
                    logger.error(f'{self.target_address} | Invalid Token Name')

                elif 'The current currency chain does not exist' in withdraw_response['err-msg']:
                    logger.error(f'{self.target_address} | Invalid Chain Name')

                else:
                    logger.error(f'{self.target_address} | Unexpected Error, response: {withdraw_response}')

            elif withdraw_response.get('data'):
                logger.success(f'{self.target_address} | {withdraw_response["data"]}')

            else:
                logger.error(f'{self.target_address} | Unexpected Response: {withdraw_response}')
