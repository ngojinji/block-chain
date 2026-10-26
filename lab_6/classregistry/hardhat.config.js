require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

const PRIVATE_KEY = process.env.PRIVATE_KEY;

module.exports = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: { enabled: true, runs: 200 },
      evmVersion: "paris", // TrustKeys' Geth runs the paris EVM
    },
  },
  networks: {
    trustkeys: {
      url: "https://l1testnet.trustkeys.network",
      chainId: 11968,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [], // dedicated TEST account only
    },
  },
};
