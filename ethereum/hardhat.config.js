/**
 * @type import('hardhat/config').HardhatUserConfig
 */
 require('dotenv').config();

 require("@nomiclabs/hardhat-ethers");
 const API_URL = process.env.API_URL;
 const PRIVATE_KEY = process.env.PRIVATE_KEY;
 
 /**
 * @type import('hardhat/config').HardhatUserConfig
 */
 module.exports = {
    solidity: "0.8.13",
    defaultNetwork: "hardhat",
    networks: {
       hardhat: {},
       ropsten: {
          url: API_URL,
          accounts: [`0x${PRIVATE_KEY}`]
       }
    },
    paths: {
      sources: "./contracts",
      tests: "./tests",
      cache: "./cache",
      artifacts: "./artifacts"
   },
 }
