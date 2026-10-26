"""
Lab 5.3 — Decompose the fee of a real type-2 (EIP-1559) transaction.

Usage:
    python decompose_tx.py 0xYourTxHash   # your own tx
    python decompose_tx.py                # no hash: use the most recent type-2 tx on chain
"""
import sys

from web3 import Web3

try:                                    # web3.py v7
    from web3.middleware import ExtraDataToPOAMiddleware as POA
except ImportError:                     # web3.py v6
    from web3.middleware import geth_poa_middleware as POA

w3 = Web3(Web3.HTTPProvider("https://l1testnet.trustkeys.network"))
w3.middleware_onion.inject(POA, layer=0)


def find_recent_type2(max_blocks=2000):
    """No hash given: scan back from the head for the most recent type-2 tx."""
    head = w3.eth.block_number
    for n in range(head, max(head - max_blocks, 0), -1):
        for t in w3.eth.get_block(n, full_transactions=True)["transactions"]:
            if t["type"] == 2:
                print(f"(no hash given -> using most recent type-2 tx on chain, block {n:,})\n")
                return t["hash"].to_0x_hex() if hasattr(t["hash"], "to_0x_hex") else t["hash"].hex()
    sys.exit(f"no type-2 tx found in the last {max_blocks} blocks; pass a tx hash instead")


h = sys.argv[1] if len(sys.argv) > 1 else find_recent_type2()
tx = w3.eth.get_transaction(h)
rcpt = w3.eth.get_transaction_receipt(h)
blk = w3.eth.get_block(rcpt["blockNumber"])

base_fee = blk["baseFeePerGas"]
gas_used = rcpt["gasUsed"]
eff_price = rcpt["effectiveGasPrice"]          # baseFee + min(tip, maxFee - baseFee)

paid = gas_used * eff_price
burned = gas_used * base_fee                   # leaves circulation
tip = gas_used * (eff_price - base_fee)        # to the block proposer

print(f"tx                 = {h}")
print(f"type               = {tx['type']}  (2 = EIP-1559)")
print(f"block              = {rcpt['blockNumber']:,}  status = {rcpt['status']} (1 = success)")
print(f"maxFeePerGas       = {tx['maxFeePerGas']} wei")
print(f"maxPriorityFee     = {tx['maxPriorityFeePerGas']} wei")
print(f"baseFee            = {base_fee} wei")
print(f"gasUsed            = {gas_used:,}")
print(f"effectiveGasPrice  = {eff_price} wei ({eff_price / 1e9:.9f} gwei)")
print(f"paid   = {paid} wei = {Web3.from_wei(paid, 'ether')} coin")
print(f"burned = {burned} wei  (leaves circulation)")
print(f"tip    = {tip} wei  (to proposer)")

expected = base_fee + min(tx["maxPriorityFeePerGas"], tx["maxFeePerGas"] - base_fee)
print(f"  CHECK type-2 tx: {'OK' if tx['type'] == 2 else 'FAIL'}")
print(f"  CHECK effectiveGasPrice == baseFee + min(tip, maxFee - baseFee): {'OK' if eff_price == expected else 'FAIL'}")
print(f"  CHECK paid == burned + tip: {'OK' if paid == burned + tip else 'FAIL'}")