import asyncio
 
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.networks import TESTNET
 
uuid = "79279570-b59d-4fa7-a01f-7e68f250d05c"
 
async def run():
    #rpc_endpoint = f"http://{uuid}@127.0.0.1:5050"
    rpc_endpoint = "http://01c9f10d-5dfc-4f25-a439-22ac3bff102c@18.157.198.111:5054"
    gateway_client = GatewayClient(rpc_endpoint, TESTNET)
    block = await gateway_client.get_block(0)
 
    print(block)
 
 
if __name__ == "__main__":
    asyncio.run(run())
