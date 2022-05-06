const { expect } = require("chai");
const { ethers } = require("hardhat");

// factory to create array of the same number of length according to the structure
const same_parameters_factory = (structure, number) => {
    let length = 0;
    for (const item of structure) {
        length += item;
    }
    return new Array(length).fill(number);
}

// simulate the expected aggregation and return the expected result
const expected_aggregated_model = (structure, numbers, current_batch_size, max_batch_size = 10) => {
    let aggregated_value = 1;
    let length = 0;
    for (const item of structure) {
        length += item;
    }
    let curr = current_batch_size;
    for (const num in numbers) {
        if (curr == max_batch_size) {
            curr = 1;
        }
        aggregated_value = (aggregated_value * curr + num) / (curr + 1);
        curr ++;
    }
    return new Array(length).fill(aggregated_value)
}


describe("Aggregation", function () {
    it("Should initialize the weights and structures", async function () {
        const Federator = await ethers.getContractFactory("Federator");
        const model_structure = [6, 20, 40, 6];
        const model_parameters = same_parameters_factory(model_structure, 1);
        const federator = await Federator.deploy(model_structure, model_parameters);
        await federator.deployed();

        expect(await federator.global_model_parameters()).to.equal(model_parameters);
        expect(await federator.running_model_parameters()).to.equal(model_parameters);
        expect(await federator.batch_size()).to.equal(0);

        const model_parameters_2 = same_parameters_factory(model_structure, 2);
        const setGreetingTx = await federator.update_model("Hola, mundo!");

        // wait until the transaction is mined
        await setGreetingTx.wait();

        expect(await greeter.message()).to.equal("Hola, mundo!");
    });
});