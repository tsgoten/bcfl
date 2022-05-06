const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Sanity Check", function () {
  it("Should be online and pingable", async function () {
    const Greeter = await ethers.getContractFactory("HelloWorld");
    const greeter = await Greeter.deploy("Hello, world!");
    await greeter.deployed();

    expect(await greeter.message()).to.equal("Hello, world!");

    const setGreetingTx = await greeter.update("Hola, mundo!");

    // wait until the transaction is mined
    await setGreetingTx.wait();

    expect(await greeter.message()).to.equal("Hola, mundo!");
  });
});