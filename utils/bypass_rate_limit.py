import asyncio.exceptions

import aiohttp.client_exceptions


async def bypass_ratelimit(current_function,
                           **kwargs) -> any:
    try:
        return await current_function(**kwargs)

    except (asyncio.exceptions.TimeoutError, TimeoutError):
        return await bypass_ratelimit(current_function=current_function)

    except aiohttp.client_exceptions.ClientResponseError as error:
        if error.status in [429, 502]:
            return bypass_ratelimit(current_function=current_function)

        raise error


    except Exception as error:
        if not str(error):
            return bypass_ratelimit(current_function=current_function)

        raise error
