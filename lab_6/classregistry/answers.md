# Lab 06 — ClassRegistry on Hardhat + TrustKeys

**Student:** Ngo Sy Thinh

## Deployment on TrustKeys L1 (chainId 11968)

- Deployer (my test account): `0xCB21b9F929DFF33530f24Beb67A1334bca0F7d96`
- ClassRegistry address: `0xA29044f1118587fEdd70c1046834E6413eF38942`
- Deploy tx hash: `0x99b739f8459cdd1bb4ca0ddc3d462da78f46a6fbdd4644f958b0a27a6325fbd0`
- Register tx hash: `0x44ff42c94360c9bfaf5e997b2c99898fd04adeb418cbd51373f4a1f4ca45e4de` (block 718,101, gasUsed 113,372)

## Register + read back on TrustKeys (Lab 6.2–6.3)

```
register tx: 0x44ff42c94360c9bfaf5e997b2c99898fd04adeb418cbd51373f4a1f4ca45e4de  (waiting...)
mined in block 718101, gasUsed 113372
on-chain name of 0xCB21b9F929DFF33530f24Beb67A1334bca0F7d96: "Ngo Sy Thinh"
memberCount = 1

ClassRegistry 0xA29044f1118587fEdd70c1046834E6413eF38942  owner=0xCB21b9F929DFF33530f24Beb67A1334bca0F7d96  members=1
  #0  0xCB21b9F929DFF33530f24Beb67A1334bca0F7d96  "Ngo Sy Thinh"

Registered events: 1
  block 718101  0xCB21b9F929DFF33530f24Beb67A1334bca0F7d96  "Ngo Sy Thinh"
```

## Test output

```
Compiled 1 Solidity file successfully (evm target: paris).

  ClassRegistry
    deployment
      ✔ sets the deployer as owner and starts empty (256ms)
    register
      ✔ stores the name and emits Registered
      ✔ reverts on an empty name
      ✔ reverts on a second registration
    deregister
      ✔ reverts for a non-owner with NotOwner
      ✔ reverts for an unknown address with NotRegistered
      ✔ owner removes a member with swap-and-pop, keeping the array dense
    many signers
      ✔ registers every signer with a different name and all round-trip (81ms)

  8 passing (398ms)
```

---

### Q1. Where did the sample test run — on TrustKeys or a local chain? What did it cost in gas?

On a **local chain**: the in-process **Hardhat Network** (chainId 31337) that Hardhat starts automatically when no `--network` is given. It is created fresh for each test run and gives 20 pre-funded accounts with 10,000 fake ETH each. Transactions still consume gas inside that simulated EVM (useful for `REPORT_GAS`), but it cost **nothing real**: no TKC was spent and nothing touched TrustKeys.

### Q2. Why is `register(string calldata name)` cheaper than `string memory name`?

`calldata` is the read-only area holding the transaction's input. With `calldata`, the function reads the string **directly from the input**, with no copy. With `memory`, the ABI decoder must first **copy** the whole string from calldata into memory (extra `CALLDATACOPY` work + memory expansion gas), and memory cost grows with length. Since `register` only reads `name` (checks its length, stores it), `calldata` avoids that copy. It is only possible for `external` functions that don't need to modify the argument.

### Q3. Why keep a separate `address[]` when the mapping already stores names?

A Solidity **mapping cannot be iterated or counted**: it has no list of keys and no length; every key "exists" and maps to a default value. So with only `mapping(address => string)` you cannot answer "who are all the members?" or "how many are there?". The `address[]` array records the keys, enabling `memberCount()` and `memberAt(i)`. Swap-and-pop in `deregister` keeps the array dense in O(1) gas (move the last element into the removed slot, then `pop()`) instead of shifting every element; an extra `mapping(address => uint256)` stores each member's index so the removal doesn't need a loop.

### Q4. Deploying is a transaction — who paid the gas, and in which coin?

The **deployer account** (the test key in `.env`, `0xCB21b...F7d96`) signed and paid for the deployment transaction, in the network's native coin **TKC** (TrustKeys Coin). Contract creation is a transaction with no `to` address whose data is the bytecode; it costs the 32,000-gas creation fee plus the bytecode/storage cost, paid as gasUsed × effectiveGasPrice from the deployer's TKC balance. The same holds for `register`: whoever calls it pays the gas.

### Q5. How would a website use `queryFilter` to show a live member list?

`queryFilter(registry.filters.Registered())` reads the `Registered` events from the chain's **event logs** (`eth_getLogs`) through any RPC node, for free and without a wallet. A website would:

1. On page load, call `queryFilter` from the deployment block to `latest` (also `Deregistered`) to build the current list, or simply read `memberCount()` / `memberAt(i)`.
2. Subscribe to new events (`registry.on("Registered", ...)` or polling `getLogs` for new blocks) and append new members in real time without reloading.

Because `who` is `indexed`, the site can also filter logs by a specific address. For large histories, production apps query in bounded block ranges or use an indexer (The Graph, Ponder) instead of scanning from block 0.