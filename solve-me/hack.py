import asyncio
import logging
from common import utils

logger = utils.setup_logger("solve-me")

async def main(hostname='127.0.0.1', port=31337):
    ctx = await utils.get_context(hostname, port)
    contract = ctx["contract"]
    acc_client = ctx["acc_client"]

    # attack
    logger.info("Invoke solve")
    invocation = await contract.functions["solve"].invoke(max_fee=int(4e16))
    await invocation.wait_for_acceptance()
    logger.info("Call withdraw")
    is_solved = (await contract.functions["is_solved"].call()).res
    logger.info(f"Is solved: {is_solved}")
    flag = utils.get_flag(hostname, port)
    logger.info(f"Flag: {flag}")
    return

asyncio.run(main())
