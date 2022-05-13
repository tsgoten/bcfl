const {
  to_fixed_number,
  to_float_number,
  float_multiplier,
  same_parameters_factory,
  expected_aggregated_model,
} = require("../utils");

async function main() {
  const model_structure = [62006];
  const init_model_parameters = same_parameters_factory(model_structure, 1);

  const [deployer] = await ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);

  console.log("Account balance:", (await deployer.getBalance()).toString());

  const Federator = await ethers.getContractFactory("Federator");
  const federator = await Federator.deploy(
    model_structure,
    init_model_parameters,
    10
  );
  console.log("Federator address:", federator.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
