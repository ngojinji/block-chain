// Read any deployed ClassRegistry without an explorer (no key needed for reads).
// Usage (PowerShell):
//   $env:REGISTRY="0x..."; npx hardhat run scripts/read-registrations.js --network trustkeys
const { ethers } = require("hardhat");

async function main() {
  const addr = process.env.REGISTRY;
  if (addr && !ethers.isAddress(addr)) throw new Error(`REGISTRY is not a valid address: "${addr}"`);
  if (!addr) throw new Error("Set the REGISTRY environment variable");
  const registry = await ethers.getContractAt("ClassRegistry", addr);

  const count = await registry.memberCount();
  console.log(`ClassRegistry ${addr}  owner=${await registry.owner()}  members=${count}`);
  for (let i = 0n; i < count; i++) {
    const who = await registry.memberAt(i);
    console.log(`  #${i}  ${who}  "${await registry.nameOf(who)}"`);
  }

  // Same data from the event log (what a website would use for a live list)
  const events = await registry.queryFilter(registry.filters.Registered());
  console.log(`\nRegistered events: ${events.length}`);
  for (const e of events) console.log(`  block ${e.blockNumber}  ${e.args.who}  "${e.args.name}"`);
}

main().catch((e) => { console.error(e); process.exitCode = 1; });
