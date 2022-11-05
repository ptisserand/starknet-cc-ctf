import asyncio
import logging
from common import utils

logger = utils.setup_logger("cairo-intro")

async def main(hostname='127.0.0.1', port=31337):
    ctx = await utils.get_context(hostname, port)
    contract = ctx["contract"]
    acc_client = ctx["acc_client"]

    # attack
    balance = (await contract.functions["get_balance"].call()).res
    logger.info(f"Balance: {balance}")
    # amount must be multiple of 14
    # amount must be grater than 31333333377
    # amount must be less than 31333333391
    # so amount after increase must be 31333333388
    amount = 31333333388 - balance
    logger.debug(f"Amount: {amount}")
    logger.info("Invoke increase_balance")
    invocation = await contract.functions["increase_balance"].invoke(amount=amount,max_fee=int(4e16))
    await invocation.wait_for_acceptance()
    logger.info("Invoke solve_challenge")
    invocation = await contract.functions["solve_challenge"].invoke(max_fee=int(4e16))
    await invocation.wait_for_acceptance()
    is_solved = (await contract.functions["is_solved"].call()).res
    logger.info(f"Is solved: {is_solved}")

    flag = utils.get_flag(hostname, port)
    logger.info(f"Flag: {flag}")
    return

asyncio.run(main())
