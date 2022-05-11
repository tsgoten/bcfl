const {
  to_fixed_number,
  to_float_number,
  float_multiplier,
  same_parameters_factory,
  expected_aggregated_model,
} = require("../utils");

async function main() {
  const model_structure = [6, 20, 40, 6];
  const init_model_parameters = same_parameters_factory(model_structure, 1);

  const [deployer] = await ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);

  console.log("Account balance:", (await deployer.getBalance()).toString());

  const Math = await ethers.getContractFactory("ABDKMath64x64");
  const math = await Math.deploy();

  const Federator = await ethers.getContractFactory("Federator");
  const federator = await Federator.attach(
    "0x5FC8d32690cc91D4c39d9d3abcBD16989F875707"
  );

  const weights_to_update = [
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
  ];
  weights_to_update.forEach(async (weight) => {
    const parameters = same_parameters_factory(model_structure, weight);
    await federator.update(parameters);
  });

  const expected_parameters = expected_aggregated_model(
    model_structure,
    1,
    weights_to_update,
    1
  );
  console.log(
    "expected",
    expected_parameters.map((x) => {
      return to_float_number(x);
    })
  );

  const actual_parameters = await federator.get_weights();
  console.log(
    "actual",
    actual_parameters.map((x) => {
      return to_float_number(x);
    })
  );
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
