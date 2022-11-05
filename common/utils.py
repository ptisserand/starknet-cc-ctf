import re
import socket
import logging
import shlex
from subprocess import Popen, PIPE

from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.net.gateway_client import GatewayClient

TEAM_ID="42"

# rpc endpoint:   http://3023bbac-5618-471e-b9f5-c8981f94e03d@127.0.0.1:5050
RPC_ENDPOINT_RE = re.compile(r'^rpc endpoint:\s*(?P<uri>https?://.*:\d+).*')
# private key:    0xb4996995475d57cdbb2cdca8ad92669f
PRIVATE_KEY_RE = re.compile(r'^private key:\s*(?P<key>[x0-9a-fA-F]+).*')
# player address: 0x8afb61a48290320ad7463bf61bf4ac38b98f38170af9bf9183e7b32133e381
PLAYER_ADDR_RE = re.compile(r'^player address:\s*(?P<address>[x0-9a-fA-F]+).*')
# contract:       0x1bfd87274f4dcd655625f1f794167542d82a5df29ed7d3d232f815c28e927f3
CONTRACT_ADDR_RE = re.compile(r'^contract:\s*(?P<address>[x0-9a-fA-F]+).*')

logger = None

def setup_logger(name, level='DEBUG'):
    global logger
    if logger is not None:
        return logger
    log_level = logging.getLevelName(level)
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')    
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def _kill_instance(hostname, port, team=TEAM_ID):
    logger.info(f"Kill instance for team: {team}")
    nc_output = ""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((hostname, port))
        s.send("2\n".encode())
        s.send(f"{team}\n".encode())
        while 1 == 1:
            data = s.recv(1024).decode()
            if not data:
                break
            nc_output += data
    logger.debug(nc_output)
    return nc_output

def _start_instance(hostname, port, team=TEAM_ID):
    logger.info(f"Start instance for team: {team}")
    nc_output = ""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((hostname, port))
        s.send("1\n".encode())
        s.send(f"{team}\n".encode())
        while 1 == 1:
            data = s.recv(1024).decode()
            if not data:
                break
            nc_output += data
    logger.debug(nc_output)
    return nc_output

def start_instance_docker_exec(hostname, port, team=TEAM_ID):
    logger.info(f"(docker exec) Start instance for team: {team}")
    # docker exec  -u ctf common-devnet-1 /bin/bash -c "echo -e '1\n42\n' | /home/ctf/handler.sh"
    container_name = "common-devnet-1"
    cmd = f"docker exec -u ctf {container_name} /bin/bash -c \"echo -e '1\n{team}\n' | /home/ctf/handler.sh\""
    cmd = shlex.split(cmd)
    p = Popen(cmd, stdin=PIPE, stdout=PIPE)
    output, err = p.communicate()
    return output.decode()

def get_flag(hostname, port, team=TEAM_ID):
    logger.info(f"Get flag for team: {team}")
    nc_output = ""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((hostname, port))
        s.send("3\n".encode())
        s.send(f"{team}\n".encode())
        while 1 == 1:
            data = s.recv(1024).decode()
            if not data:
                break
            nc_output += data
    logger.debug(nc_output)
    # flag is last line
    return nc_output.split()[-1]


async def get_context(hostname, port, team=TEAM_ID, start_instance=_start_instance, kill_instance=_kill_instance):
    logger.info(f"Get context for team: {team}")
    # First kill last instance if any
    kill_instance(hostname, port, team)
    # Start a new instance
    nc_output = start_instance(hostname, port, team)
    logger.debug(nc_output)
    rpc = None
    privateKey = None
    playerAddress = None
    contractAddress = None
    for nn in nc_output.split('\n'):
        if RPC_ENDPOINT_RE.match(nn):
            rpc = RPC_ENDPOINT_RE.match(nn)['uri']
        if PRIVATE_KEY_RE.match(nn):
            privateKey = PRIVATE_KEY_RE.match(nn)['key']
        if PLAYER_ADDR_RE.match(nn):
            playerAddress = PLAYER_ADDR_RE.match(nn)['address']
        if CONTRACT_ADDR_RE.match(nn):
            contractAddress = CONTRACT_ADDR_RE.match(nn)['address']
    if not rpc:
        msg = "RPC parsing failed"
        logger.error(msg)
        raise Exception(msg)
    if not privateKey:
        msg = "PrivateKey parsing failed"
        logger.error(msg)
        raise Exception(msg)
    if not playerAddress:
        msg = "Player address parsing failed"
        logger.error(msg)
        raise Exception(msg)
    if not contractAddress:
        msg = "Contract address failed"
        logger.error(msg)
        raise Exception(msg)
    keyPair = KeyPair.from_private_key(key=int(privateKey, 16))
    client = GatewayClient(net=rpc)
    acc_client = AccountClient(
        client=client,
        address=playerAddress,
        key_pair=keyPair,
        chain=StarknetChainId.TESTNET,
        supported_tx_version=1,
    )
    contract = await Contract.from_address(contractAddress, acc_client)
    
    return {
        'client': client,
        'acc_client': acc_client,
        'contract': contract,
        'player': playerAddress,
        'contract_address': contractAddress,
    }
