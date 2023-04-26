from random import randint, uniform


def get_random_withdraw_amount(min_withdraw_amount: str,
                               max_withdraw_amount: str) -> int | float:
    if min_withdraw_amount.isdigit() and max_withdraw_amount.isdigit():
        return randint(a=int(min_withdraw_amount),
                       b=int(max_withdraw_amount))

    return uniform(a=float(min_withdraw_amount),
                   b=float(max_withdraw_amount))
