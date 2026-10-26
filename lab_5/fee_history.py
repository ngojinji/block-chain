"""
Lab 5.2 — Read the chain with web3.py (read-only).
Connects to TrustKeys L1, reads the latest block, a balance, and the
base-fee history of the last 20 blocks (eth_feeHistory).

Usage:
    python fee_history.py                      # TrustKeys L1
    python fee_history.py 0xYourAddress        # also show that address's balance
    RPC_URL=https://ethereum-sepolia-rpc.publicnode.com python fee_history.py   # Sepolia (homework)
"""
import os
import sys

from web3 import Web3

try:                                    # web3.py v7
    from web3.middleware import ExtraDataToPOAMiddleware as POA
except ImportError:                     # web3.py v6
    from web3.middleware import geth_poa_middleware as POA

RPC_URL = os.environ.get("RPC_URL", "https://l1testnet.trustkeys.network")
ADDRESS = sys.argv[1] if len(sys.argv) > 1 else "0x5A351A9280e2e5b9324408EC5769D0745d7aB512"
N = 20


def check(name, ok):
    print(f"  CHECK {name}: {'OK' if ok else 'FAIL'}")


def gwei(wei):
    return wei / 1e9


w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(POA, layer=0)   # PoA (clique): extraData = 97 bytes, not 32

chain_id = w3.eth.chain_id
head = w3.eth.block_number
print(f"Connected to {RPC_URL}  chainId={chain_id}  head block={head:,}")
check("connected", w3.is_connected())

# ---------------------------------------------------------------- latest block
blk = w3.eth.get_block("latest")
print("\n[eth_getBlockByNumber latest]")
print(f"  number        = {blk['number']:,}")
print(f"  gasLimit      = {blk['gasLimit']:,}")
print(f"  gasUsed       = {blk['gasUsed']:,} ({blk['gasUsed'] / blk['gasLimit']:.2%} full)")
print(f"  baseFeePerGas = {blk['baseFeePerGas']} wei ({gwei(blk['baseFeePerGas']):.9f} gwei)  <- EIP-1559 active")
extra = blk.get("proofOfAuthorityData", blk.get("extraData", b""))   # PoA middleware renames the field
print(f"  extraData     = {len(extra)} bytes  (>32 => PoA/clique)")
print(f"  #txs          = {len(blk['transactions'])}")
check("baseFeePerGas present (EIP-1559)", "baseFeePerGas" in blk)

# ---------------------------------------------------------------- balance
addr = Web3.to_checksum_address(ADDRESS)
bal = w3.eth.get_balance(addr)
print("\n[eth_getBalance]")
print(f"  address = {addr}")
print(f"  balance = {bal} wei = {Web3.from_wei(bal, 'ether')} coin")

# ---------------------------------------------------------------- fee history
fh = w3.eth.fee_history(N, "latest", [10, 50, 90])
bases = fh["baseFeePerGas"]
ratios = fh["gasUsedRatio"]
print(f"\n[eth_feeHistory] last {N} blocks (base fee series)")
print(f"  {'block':>9} {'baseFee (wei)':>14} {'gasUsedRatio':>13} {'tip p50 (gwei)':>15}")
for i in range(len(ratios)):
    print(f"  {fh['oldestBlock'] + i:>9} {bases[i]:>14} {ratios[i]:>12.2%} {gwei(fh['reward'][i][1]):>15.4f}")
avg = sum(ratios) / len(ratios)
print(f"  next block's projected baseFee = {bases[-1]} wei ({gwei(bases[-1]):.9f} gwei)")
print(f"  average gasUsedRatio over window = {avg:.2%} -> chain is {'BUSY' if avg > 0.5 else 'quiet'}")
check("baseFeePerGas has N+1 entries", len(bases) == len(ratios) + 1)
check("gasUsedRatio has N entries", len(ratios) == N)