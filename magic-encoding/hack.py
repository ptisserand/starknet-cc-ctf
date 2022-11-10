import asyncio
import logging
from common import utils

logger = utils.setup_logger("magic-encoding")

async def main(hostname='127.0.0.1', port=31337):
    ctx = await utils.get_context(hostname, port)
    contract = ctx["contract"]
    acc_client = ctx["acc_client"]

    # attack
    # Use thot and disassemble test_password  
    logger.info("Invoke 'test_password'")
    invocation = await contract.functions["test_password"].invoke(password=31718,max_fee=int(4e16))
    await invocation.wait_for_acceptance()
    is_done = (await contract.functions["is_challenge_done"].call()).res
    logger.info(f"Is done: {is_done}")

    flag = utils.get_flag(hostname, port)
    logger.info(f"Flag: {flag}")
    return

asyncio.run(main())
