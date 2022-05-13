/**
 * @type import('hardhat/config').HardhatUserConfig
 */
require("dotenv").config();

require("@nomiclabs/hardhat-ethers");
const API_URL = process.env.API_URL;
const PRIVATE_KEY = process.env.PRIVATE_KEY;

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
module.exports = {
  solidity: {
     version: "0.8.13",
     optimizer: {
      enabled: true,
      runs: 200
      }
   },
  defaultNetwork: "hardhat",
  networks: {
    hardhat: {
      throwOnTransactionFailures: true,
      throwOnCallFailures: true,
      allowUnlimitedContractSize: true,
      blockGasLimit: 10000000000,
      gas: 1000000000000,
    },
    ropsten: {
      url: API_URL,
      accounts: [`0x${PRIVATE_KEY}`],
    },
  },
  paths: {
    sources: "./contracts",
    tests: "./tests",
    cache: "./cache",
    artifacts: "./artifacts",
  },
  mocha: {
     timeout: 10000000,
  }
};
