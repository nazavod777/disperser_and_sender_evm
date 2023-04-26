from copy import deepcopy
from multiprocessing.dummy import Pool

from web3.auto import w3

from core import claimer
from core import disperser
from utils import format_address_and_keys
from utils import logger

if __name__ == '__main__':
    evm_accounts: list = []

    with open('evm_accounts.txt', 'r', encoding='utf-8-sig') as file:
        for row in file:
            current_formatted_account_dict = format_address_and_keys(value=row)

            if current_formatted_account_dict['private_key'] \
                    and current_formatted_account_dict['address']:
                evm_accounts.append(current_formatted_account_dict)

    logger.info(f'Успешно загружено {len(evm_accounts)} EVM кошельков')

    user_action = int(input('\n1. Раскидать баланс по кошелькам\n'
                            '2. Собрать балансы с кошельков\n'
                            'Выберите ваше действие: '))

    threads: int = 1

    if user_action == 1:
        cex_type: int = int(input('1. Huobi\n'
                                  '2. MEXC\n'
                                  'Выберите биржу для вывода: '))
        withdraw_token_name: str = input('Введите название токена: ')
        withdraw_chain_name: str = input('Введите название сети токена: ')
        min_withdraw_amount: str = input('Введите минимальную сумму вывода на кошелек (ex: 1 // 1.5 // 1,5): ').replace(
            ',', '.')
        max_withdraw_amount: str = input('Введите минимальную сумму вывода на кошелек (ex: 1 // 1.5 // 1,5): ').replace(
            ',', '.')

        to_send_data: list = deepcopy(evm_accounts)

        for current_to_send_data in to_send_data:
            current_to_send_data.update({
                'withdraw_chain_name': withdraw_chain_name,
                'withdraw_token_name': withdraw_token_name,
                'min_withdraw_amount': min_withdraw_amount,
                'max_withdraw_amount': max_withdraw_amount,
                'cex_type': cex_type
            })

        with Pool(processes=threads) as executor:
            executor.map(disperser, to_send_data)

    elif user_action == 2:
        native_coin_min_percent, native_coin_max_percent, \
            erc_coin_address, erc_coin_min_percent, erc_coin_max_percent = [None for _ in range(5)]

        target_coin_type: int = int(input('1. Трансфер Native Coin (ETH)\n'
                                          '2. Трансфер ERC-20 Coin\n'
                                          'Выберите тип монеты, которую необходимо отправлять: '))

        if target_coin_type == 1:
            native_coin_min_percent: float = float(input('Введите минимальное количество процентов от '
                                                         'баланса переводить на кошельки: '))
            native_coin_max_percent: float = float(input('Введите максимальное количество процентов от '
                                                         'баланса переводить на кошельки: '))

        else:
            erc_coin_address = w3.to_checksum_address(value=input('Введите адрес монеты для отправки: '))
            erc_coin_min_percent: float = float(input('Введите минимальное количество процентов от '
                                                      'баланса переводить на кошельки: '))
            erc_coin_max_percent: float = float(input('Введите максимальное количество процентов от '
                                                      'баланса переводить на кошельки: '))

        RPC_URL: str = input('Введите адрес RPC URL: ')

        claimer_from_evm_data: list = [{
            'private_key': current_evm_account['private_key'],
            'address_to': current_evm_account['address'],
            'target_coin_type': target_coin_type,
            'native_coin_min_percent': native_coin_min_percent,
            'native_coin_max_percent': native_coin_max_percent,
            'erc_coin_address': erc_coin_address,
            'erc_coin_min_percent': erc_coin_min_percent,
            'erc_coin_max_percent': erc_coin_max_percent,
            'rpc_url': RPC_URL
        } for current_evm_account in evm_accounts]

        print()

        with Pool(processes=threads) as executor:
            executor.map(claimer, claimer_from_evm_data)
