from json import load


def read_cex_accounts_json() -> dict:
    with open('cex_accounts.json', 'r', encoding='utf-8-sig') as file:
        return load(file)
