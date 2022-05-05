async function main() {
  const [deployer] = await ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);

  console.log("Account balance:", (await deployer.getBalance()).toString());

  const HelloWorld = await ethers.getContractFactory("HelloWorld");
  const helloworld = await HelloWorld.deploy("Hello World!");

  const Federator = await ethers.getContractFactory("Federator");
  const federator = await Federator.deploy([1, 2], [1, 2]);

  console.log("HelloWorld address:", HelloWorld.address);
  console.log("Federator address:", Federator.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });