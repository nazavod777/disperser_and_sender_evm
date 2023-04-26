import asyncio

from core.disperser_huobi import HuobiDisperser
from utils import read_cex_accounts_json


def disperser(input_data: dict) -> None:
    cex_accounts_json: dict = read_cex_accounts_json()

    match input_data['cex_type']:
        case 1:
            asyncio.run(HuobiDisperser(access_key=cex_accounts_json['huobi']['access_key'],
                                       secret_key=cex_accounts_json['huobi']['secret_key'],
                                       withdraw_token_name=input_data['withdraw_token_name'],
                                       target_address=input_data['address'],
                                       min_withdraw_amount=input_data['min_withdraw_amount'],
                                       max_withdraw_amount=input_data['max_withdraw_amount'],
                                       withdraw_chain_name=input_data['withdraw_chain_name']).main_work())

        case _:
            pass
