# Lab 05 — Ethereum accounts, gas & the EVM

**Student:** Ngo Sy Thinh
**Network:** TrustKeys L1 testnet — RPC https://l1testnet.trustkeys.network, chainId 11968

---

## Lab 5.1 — Add TrustKeys L1 to MetaMask

Network added: name `TrustKeys L1 testnet`, RPC `https://l1testnet.trustkeys.network`, chainId `11968`, explorer left blank.

My address on TrustKeys L1: `0xCB21b9F929DFF33530f24Beb67A1334bca0F7d96`

### Q1. Why is chainId part of every signed transaction (EIP-155)?

Because a signature by itself is valid on **every** EVM chain that uses the same key/address format. Without chainId, a transaction signed for TrustKeys L1 could be copied and **replayed** on Ethereum mainnet, Sepolia or any other EVM chain where the same address holds funds. EIP-155 includes chainId in the signed data (and in `v`), so a transaction signed for chainId 11968 is invalid on any other chain. Adding a network in MetaMask only changes the RPC endpoint and chainId; the private key never leaves the device.

---

## Lab 5.2 — Read the chain with web3.py

### Output

```
Connected to https://l1testnet.trustkeys.network  chainId=11968  head block=718,096
  CHECK connected: OK

[eth_getBlockByNumber latest]
  number        = 718,096
  gasLimit      = 30,000,000
  gasUsed       = 302,870 (1.01% full)
  baseFeePerGas = 8 wei (0.000000008 gwei)  <- EIP-1559 active
  extraData     = 97 bytes  (>32 => PoA/clique)
  #txs          = 1
  CHECK baseFeePerGas present (EIP-1559): OK

[eth_getBalance]
  address = 0xCB21b9F929DFF33530f24Beb67A1334bca0F7d96
  balance = 0 wei = 0 coin

[eth_feeHistory] last 20 blocks (base fee series)
      block  baseFee (wei)  gasUsedRatio  tip p50 (gwei)
     718077              8        4.99%          2.0000
     718078              8        0.39%          2.0000
     718079              8        0.17%          2.0000
     718080              8        0.07%          2.0000
     718081              8        3.19%          2.0000
     718082              8        0.38%          2.0000
     718083              8        0.32%          2.0000
     718084              8        0.17%          2.0000
     718085              8        0.12%          2.0000
     718086              8        0.07%          2.0000
     718087              8       41.59%          2.0000
     718088              8        0.35%          2.0000
     718089              8        0.52%          2.0000
     718090              8        1.01%          2.0000
     718091              8        0.48%          2.0000
     718092              8        0.47%          2.0000
     718093              8        1.65%          2.0000
     718094              8        0.35%          2.0000
     718095              8        0.52%          2.0000
     718096              8        1.01%          2.0000
  next block's projected baseFee = 8 wei (0.000000008 gwei)
  average gasUsedRatio over window = 2.89% -> chain is quiet
  CHECK baseFeePerGas has N+1 entries: OK
  CHECK gasUsedRatio has N entries: OK
```

### Q2. The base fee is only a few wei and gasUsedRatio ≈ 2%. Why does it stay at the floor?

EIP-1559 adjusts the base fee every block depending on how full the previous block was, relative to a **target of 15M gas** (half the 30M gas limit):

- block more than half full → base fee rises (up to **+12.5%**)
- block less than half full → base fee falls (up to **−12.5%**)

newBaseFee = baseFee × (1 + 1/8 × (gasUsed − target) / target)

Measured on TrustKeys (blocks 718,077–718,096): base fee = **8 wei** in every block, average gasUsedRatio = **2.89%**, and even the busiest block (41.59%) was still below the 50% target.

With gasUsedRatio ≈ 2–3%, every block uses far less than the 50% target, so the formula pushes the base fee down by close to 12.5% each block. After many quiet blocks it decays to the minimum: at a few wei, a 12.5% decrease rounds down to less than 1 wei, so it stops moving (here it sits at 8 wei, the floor). Only sustained demand above 15M gas per block would push it up again.

### Q3. eth_feeHistory returns baseFeePerGas of length N+1 but gasUsedRatio of length N. What is the extra element? How does a wallet use it?

The extra (last) element is the **projected base fee of the next block** (the block not yet produced). It can be computed already because the base fee of block n+1 depends only on block n's base fee and gas usage.

A wallet uses it to set `maxFeePerGas`, typically with headroom for a few blocks of increases, e.g.:

maxFeePerGas = 2 × nextBaseFee + maxPriorityFeePerGas

Doubling covers about 6 consecutive full blocks (1.125⁶ ≈ 2.03), so the transaction stays valid even if the base fee rises before inclusion. The user only pays the actual base fee plus tip; the unused part of maxFee is not charged.

---

## Lab 5.3 — Send a type-2 tx and decompose the fee

My MetaMask test account had 0 TKC at the time of the lab, so instead of sending my own transaction I decomposed the most recent real type-2 (EIP-1559) transaction on TrustKeys L1 (`decompose_tx.py` scans back from the head block for it). The fee arithmetic is identical for any type-2 transaction.

Tx hash: `0x1d3eac44b7c8551ebf02a0e7c98e076b3fd28d4e25f9192a49867c8b4b67b9e4` (block 718,096)

### Output

```
(no hash given -> using most recent type-2 tx on chain, block 718,096)

tx                 = 0x1d3eac44b7c8551ebf02a0e7c98e076b3fd28d4e25f9192a49867c8b4b67b9e4
type               = 2  (2 = EIP-1559)
block              = 718,096  status = 1 (1 = success)
maxFeePerGas       = 2000000002 wei
maxPriorityFee     = 1999999992 wei
baseFee            = 8 wei
gasUsed            = 302,870
effectiveGasPrice  = 2000000000 wei (2.000000000 gwei)
paid   = 605740000000000 wei = 0.00060574 coin
burned = 2422960 wei  (leaves circulation)
tip    = 605739997577040 wei  (to proposer)
  CHECK type-2 tx: OK
  CHECK effectiveGasPrice == baseFee + min(tip, maxFee - baseFee): OK
  CHECK paid == burned + tip: OK
```

The invariant `paid == burned + tip` holds: 605,740,000,000,000 = 2,422,960 + 605,739,997,577,040 wei. Only **0.0000004%** of the fee was burned (base fee 8 wei/gas); the rest went to the proposer as tip. Note this tx used 302,870 gas, so it was a contract call, not a plain 21,000-gas transfer. Here maxFee − baseFee = 1,999,999,994 < maxPriorityFee would allow, so effectiveGasPrice = 8 + min(1,999,999,992, 1,999,999,994) = 2,000,000,000 wei, exactly matching the receipt.

On this testnet the base fee is only a few wei, so almost the entire fee is tip to the block proposer; on Ethereum mainnet during congestion the burned part dominates.

### Q4. If you raise max base fee but keep the priority fee, does effectiveGasPrice change?

**Normally no.** effectiveGasPrice = baseFee + min(maxPriorityFee, maxFee − baseFee).

The base fee is set by the protocol, not by the user. As long as the old maxFee already covered baseFee + maxPriorityFee, the `min(...)` already equals maxPriorityFee, so raising maxFee changes nothing: you still pay baseFee + the same tip. maxFee is only a **cap** (the most you are willing to pay); the unused part is refunded.

It would only change in the edge case where the old maxFee was too low to cover the full tip (maxFee − baseFee < maxPriorityFee); then raising maxFee lets more of the tip through, up to maxPriorityFee.

### Q5. Why does a simple transfer use exactly 21,000 gas, and why does a failed tx still cost gas?

**21,000** is the fixed **intrinsic gas** of every transaction (G_transaction in the Yellow Paper). It pays for the work every node must do for any transaction regardless of content: verifying the ECDSA signature, checking and incrementing the sender's nonce, checking and updating balances, and storing the transaction. A plain ETH transfer to an address with no code runs no EVM opcodes, so it costs exactly this base amount (plus calldata gas, which is zero here).

A **failed** transaction still costs gas because the network already did the work: the transaction was included in a block, the signature verified, and the EVM executed until it reverted. Gas pays for computation, not for success. Charging failed transactions also prevents DoS attacks (otherwise anyone could spam the network with expensive transactions designed to fail for free). State changes are rolled back, but the gas used is kept by the network, and the nonce still increments.

---

## Lab 5.4 — Trace a contract interaction on Sepolia Etherscan

Transaction traced: https://sepolia.etherscan.io/tx/0x714bacee7dd43003334836dfebabc1a533b6c27c1e9a8857a779bab64c4471a4 (a call to the Sepolia USDC contract `0x1c7d4b196cb0c7b01d743fbc6116a902379c7238`)

Decoded input:

| # | Name | Type | Data |
|---|---|---|---|
| 0 | spender | address | `0x93083f60F1877a6bA974d5eD88Bb74943deB8390` |
| 1 | value | uint256 | `2000000` (= 2 USDC, since USDC has 6 decimals) |

- Function: `approve(address spender, uint256 value)`, selector **`0x095ea7b3`** = first 4 bytes of `keccak256("approve(address,uint256)")`
- Logs: one `Approval(owner, spender, value)` event emitted by the USDC contract

Calldata layout: 4-byte selector, then each argument ABI-encoded as a 32-byte word (address left-padded with zeros, value as a big-endian uint256). Total = 4 + 2 × 32 = 68 bytes.

Observation: a first transaction I opened called an **unverified** contract; Etherscan could only show its input as raw hex ("View Input As" offered no decode option), which illustrates Q6 directly.

Screenshots:
- (a) Decoded Input Data (selector + arguments): `screenshot_input_data.png`
- (b) Logs tab: `screenshot_logs.png`

### Q6. How does the EVM use the 4-byte selector to reach the function, and why does Etherscan need the ABI?

The compiled contract starts with a **dispatcher**: it loads the first 4 bytes of calldata (`CALLDATALOAD` + shift), then compares them one by one against the selector of each public function (`PUSH4 0xa9059cbb`, `EQ`, `JUMPI`); on a match it jumps to that function's code, and if nothing matches it runs the fallback or reverts. Etherscan needs the **ABI** because calldata is only raw bytes: the selector is a one-way hash, and the remaining 32-byte words have no type information, so only the ABI tells it the function name and how to interpret each argument (address, uint256, string offset, etc.).