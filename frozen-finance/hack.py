import asyncio
import os
import pytest
from starknet_py.net.models import StarknetChainId
from starknet_py.net import AccountClient, KeyPair



RPC="http://c2049bde-bc63-456c-99c3-90120960225f@18.157.198.111:5057"
PRIV_KEY="0x653ce0df5c3157f710afafca1075fc32"
ACCOUNT_ADDRESS="0x53637964b2347fa9364e34b8ead243a40ee7ccdb3b5beccedfab6ac30c43eeb"
CONTRACT_ADDRESS="0x5a112c26337a0f7748d4c6dde9f04f7e6895c888dc2cced75a7775d6e7ab99d"

PRIV_KEY_FELT=int(PRIV_KEY, 16)
print(f'Private key: {PRIV_KEY_FELT}')
KEY_PAIR = KeyPair.from_private_key(key=PRIV_KEY_FELT)

async def main():
    # pylint: disable=import-outside-toplevel, duplicate-code, too-many-locals
    # add to docs: start
    from starknet_py.net import AccountClient
    from starknet_py.contract import Contract
    from starknet_py.net.gateway_client import GatewayClient

    # Creates an account on testnet and returns an instance
    client = GatewayClient(net=RPC)
    acc_client = AccountClient(
        client=client,
        address=ACCOUNT_ADDRESS,
        key_pair=KEY_PAIR,
        chain=StarknetChainId.TESTNET,
        supported_tx_version=1,
    )
    contract = await Contract.from_address(CONTRACT_ADDRESS, acc_client)
    for i in range(0, 10):
        invocation = await contract.functions["deposit"].invoke(amount={"low": 2<<128 - 1, "high":0}, max_fee=int(4e16))
        await invocation.wait_for_acceptance()
    invocation = await contract.functions["withdraw"].invoke(max_fee=int(4e16))
    await invocation.wait_for_acceptance()
    print(invocation)
    res = await contract.functions["readBalance"].call()
    print(f"Res: {res}")
    return


asyncio.run(main())
