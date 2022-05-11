const { expect } = require("chai");
const { ethers } = require("hardhat");

const {
  to_fixed_number,
  to_float_number,
  float_multiplier,
  same_parameters_factory,
  expected_aggregated_model,
} = require("../utils");

async function deploy_federator(
  structure,
  init_model_parameters,
  max_batch_size = 10
) {
  const Federator = await ethers.getContractFactory("Federator");
  const model_structure = structure;
  const federator = await Federator.deploy(
    model_structure,
    init_model_parameters,
    max_batch_size
  );
  await federator.deployed();
  return federator;
}

describe("Aggregation", function () {
  const model_structure = [6, 20, 40, 6];
  const init_model_parameters = same_parameters_factory(model_structure, 1);
  it("Should initialize the weights and structures", async function () {
    const federator = await deploy_federator(
      model_structure,
      init_model_parameters
    );

    expect(
      (await federator.get_weights()).map((x) => {
        return x;
      })
    ).to.eql(init_model_parameters);

    expect(parseFloat(await federator.batch_size())).to.equal(1);

    expect(parseFloat(await federator.max_batch_size())).to.equal(10);
  });

  it("Should update the weights and structures", async function () {
    const federator = await deploy_federator(
      model_structure,
      init_model_parameters
    );

    const new_model_parameters = same_parameters_factory(model_structure, 2);
    await federator.update(new_model_parameters);

    expect(await federator.get_weights()).to.eql(
      same_parameters_factory(model_structure, 1)
    );

    expected = expected_aggregated_model(model_structure, 1, [2], 1);
    // console.log(
    //   "expected",
    //   expected.map((x) => {
    //     return to_float_number(x);
    //   })
    // );
    expect(await federator.get_running_weights()).to.eql(expected);
  });

  it("Should have correct running average after repeated updates", async function () {
    const model_parameters = same_parameters_factory(model_structure, 1);
    const federator = await deploy_federator(model_structure, model_parameters);
    const weights_to_update = [
      2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    ];
    weights_to_update.forEach(async (weight) => {
      const parameters = same_parameters_factory(model_structure, weight);
      await federator.update(parameters);
    });

    expected_parameters = expected_aggregated_model(
      model_structure,
      1,
      weights_to_update,
      1
    );
    expect(await federator.get_running_weights()).to.eql(expected_parameters);
  });

  it("Should have correct global average, after repeated updates", async function () {
    const model_parameters = same_parameters_factory(model_structure, 1);
    const federator = await deploy_federator(model_structure, model_parameters);
    const weights_to_update = [
      2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21
    ];
    weights_to_update.forEach(async (weight) => {
      const parameters = same_parameters_factory(model_structure, weight);
      await federator.update(parameters);
    });

    expected_parameters = expected_aggregated_model(
      model_structure,
      1,
      weights_to_update,
      1
    );
    // console.log(
    //   expected_parameters.map((x) => {
    //     return to_float_number(x);
    //   })
    // );
    // console.log(
    //   (await federator.get_running_weights()).map((x) => {
    //     return to_float_number(x);
    //   })
    // );
    expect(to_float_number((await federator.get_weights())[0])).to.equal(14.05);
  });
});
