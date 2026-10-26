// Usage (PowerShell):
//   $env:REGISTRY="0x..."; $env:NAME="Your Name"; npx hardhat run scripts/register.js --network trustkeys
const { ethers } = require("hardhat");

async function main() {
  const addr = process.env.REGISTRY;
  const name = process.env.NAME;
  if (addr && !ethers.isAddress(addr)) throw new Error(`REGISTRY is not a valid address: "${addr}"`);
  if (!addr || !name) throw new Error("Set REGISTRY and NAME environment variables");

  const [me] = await ethers.getSigners();
  const registry = await ethers.getContractAt("ClassRegistry", addr);

  if (await registry.isRegistered(me.address)) {
    console.log(`${me.address} is already registered as "${await registry.nameOf(me.address)}"`);
    return;
  }

  const tx = await registry.register(name);
  console.log(`register tx: ${tx.hash}  (waiting...)`);
  const rcpt = await tx.wait();
  console.log(`mined in block ${rcpt.blockNumber}, gasUsed ${rcpt.gasUsed}`);
  console.log(`on-chain name of ${me.address}: "${await registry.nameOf(me.address)}"`);
  console.log(`memberCount = ${await registry.memberCount()}`);
}

main().catch((e) => { console.error(e); process.exitCode = 1; });
