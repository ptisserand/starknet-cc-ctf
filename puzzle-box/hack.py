import asyncio
import logging
from common import utils

logger = utils.setup_logger("puzzle-box")

async def main(hostname='127.0.0.1', port=31337):
    ctx = await utils.get_context(hostname, port)
    contract = ctx["contract"]
    acc_client = ctx["acc_client"]
    contract_address = ctx["contract_address"]

    # attack
    logger.info("Solve step1")
    res_step1 = 3609145100 + 12345 + int(acc_client.address)
    invocation = await contract.functions["solve_step_1"].invoke(_mult=res_step1, max_fee=int(4e16))
    await invocation.wait_for_acceptance()

    logger.info("Solve step2")
    res_step2 = 1010886179 + 965647271 + int(contract_address, 16)
    invocation = await contract.functions["solve_step_2"].invoke(product=res_step2, max_fee=int(4e16))
    await invocation.wait_for_acceptance()

    logger.info("Solve step3")
    res_step3 = 588 * 636
    invocation = await contract.functions["solve_step_3"].invoke(value=res_step3, max_fee=int(4e16))
    await invocation.wait_for_acceptance()

    logger.info("Solve step4")
    res_step4 = 84092830
    invocation = await contract.functions["solve_step_4"].invoke(input=res_step4, max_fee=int(4e16))
    await invocation.wait_for_acceptance()

    logger.info("Invoke solve")
    invocation = await contract.functions["solve"].invoke(max_fee=int(4e16))
    await invocation.wait_for_acceptance()

    res = (await contract.functions["is_solved"].call()).res
    logger.info(f"Solved: {res}")

    flag = utils.get_flag(hostname, port)
    logger.info(f"Flag: {flag}")
    return

asyncio.run(main())
