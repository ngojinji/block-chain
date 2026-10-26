# Lab 04 — Real Bitcoin Blocks: PoW, Fees & Merkle Root

**Student:** Ngo Sy Thinh
**Anchor block:** #840,000 (4th halving, 2024-04-20)

## Output

```
block #840,000: 0000000000000000000320283a032748cef8227873ff4872689bf23f1cda83a5  bits=0x17034219
  CHECK recomputed hash == block id: OK
target = 0000000000000000000342190000000000000000000000000000000000000000
  CHECK PoW: int(hash) < target: OK
tx 2bb85f4b004be6da…  fee = 673,200,000 sat  vsize = 187 vB  rate = 3,600,000.0 sat/vB
  CHECK our fee == API 'fee' field: OK
computed root: 031b417c3a1828ddf3d6527fc210daafcc9218e81f98257f88d4d43bd7a5894f
header root  : 031b417c3a1828ddf3d6527fc210daafcc9218e81f98257f88d4d43bd7a5894f
  CHECK computed merkle root == header merkle_root: OK
```

---

## Task 4.1 — Proof-of-Work

### Q1. How many leading zero hex digits does the target have? How many bits of work does one valid header represent?

For block #840,000, `bits = 0x17034219`:

- exponent = `0x17` = 23, mantissa = `0x034219`
- target = `0x034219 × 256^(23−3)` =
  `0000000000000000000342190000000000000000000000000000000000000000`

The target has **19 leading zero hex digits** (18 from the 9 leading zero bytes, plus the leading `0` of `034219`), i.e. about 76 leading zero bits.

Expected work = 2²⁵⁶ / target ≈ **2⁷⁸ hashes** (log₂ ≈ 78.3). A random hash is below the target with probability target / 2²⁵⁶, so on average the network must try about 2⁷⁸ headers to find one valid block.

### Q2. Verifying took 2 hash calls; finding took the network ~10 minutes. What property of SHA-256 creates this asymmetry?

**Preimage resistance (one-wayness)** of SHA-256. Given a target, there is no way to construct a header whose hash falls below it other than brute-force trying nonces; the output is effectively random and unpredictable. Computing the hash forward, however, is cheap. So finding a valid header costs ~2⁷⁸ hashes for the whole network, while any node verifies it with just 2 SHA-256 calls (one double-SHA-256).

---

## Task 4.2 — Transaction anatomy & fee rate

### Q3. This tx paid ~3,600,000 sat/vB (≈ 6.73 BTC for 187 vB). What was happening, and what does it teach about how fees are set?

Measured: fee = 673,200,000 sat = **6.732 BTC** for a **187 vB** transaction → **3,600,000 sat/vB**.

Block #840,000 was mined on **20 April 2024, the 4th halving**, which was also the moment the **Runes protocol launched**. Many users wanted their transaction (e.g. etching the first runes) to be included in this historic block specifically, so they bid extremely high fees to win a spot.

Lesson: Bitcoin fees are set by a **market auction for limited block space**, not by the amount transferred. Block space is capped, miners pick transactions with the highest fee rate (sat/vB) first, so when demand spikes the price of inclusion spikes too. Today, with normal demand, high-priority fees on mempool.space are typically only single or double-digit sat/vB.

### Q4. Coinbase outputs total 4,075,061,499 sat; subsidy is 312,500,000 sat. Where does the difference come from?

4,075,061,499 − 312,500,000 = **3,762,561,499 sat ≈ 37.63 BTC**.

This difference is the **sum of the transaction fees** of all transactions in the block. The miner collects the block subsidy (3.125 BTC after the halving) plus every fee (inputs − outputs) left by the block's transactions, through the coinbase transaction. In this block the fees were about 12× the subsidy because of the halving-day fee auction.

---

## Task 4.3 — Merkle root

### Q5. The computed root matches the header exactly. What does this prove?

It proves that the list of 3,050 txids we downloaded is **exactly** the transaction set the block commits to: same transactions, same order, nothing added or removed. Because SHA-256 is **collision resistant**, it is infeasible to find a different list of transactions that produces the same Merkle root; changing, adding, removing or reordering even one transaction changes the root. And since the Merkle root sits inside the header that is protected by Proof-of-Work, tampering with any transaction would also require re-mining the block.