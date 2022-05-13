const {
  to_fixed_number,
  to_float_number,
  float_multiplier,
  same_parameters_factory,
  expected_aggregated_model,
} = require("../utils");

async function main() {
  const model_structure = [6, 20, 40, 6];
  const [deployer] = await ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);

  console.log("Account balance:", (await deployer.getBalance()).toString());

  const Federator = await ethers.getContractFactory("Federator");
  const federator = await Federator.attach(
    "0xc6e7DF5E7b4f2A278906862b61205850344D4e7d"
  );

  const weights_to_update = [
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
  ];

  for (let i = 0; i < weights_to_update.length; i++) {
    const weight = weights_to_update[i];
    console.log("Updating with weight:", weight);
    const parameters = same_parameters_factory(model_structure, weight);
    await federator.update(parameters);
    console.log((await federator.get_running_weights())[0]);
  }

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
