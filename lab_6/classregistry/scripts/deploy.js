const { ethers, network } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  if (!deployer) throw new Error("No account: set PRIVATE_KEY in .env");
  console.log(`network  : ${network.name} (chainId ${network.config.chainId ?? 31337})`);
  console.log(`deployer : ${deployer.address}`);
  console.log(`balance  : ${ethers.formatEther(await ethers.provider.getBalance(deployer.address))} TKC`);

  const registry = await ethers.deployContract("ClassRegistry");
  const tx = registry.deploymentTransaction();
  console.log(`deploy tx: ${tx.hash}  (waiting for confirmation...)`);
  await registry.waitForDeployment();

  console.log(`ClassRegistry deployed at: ${await registry.getAddress()}`);
}

main().catch((e) => { console.error(e); process.exitCode = 1; });
