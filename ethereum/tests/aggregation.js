const { expect } = require("chai");
const { ethers } = require("hardhat");

const float_multiplier = 1;

// factory to create array of the same number of length according to the structure
const same_parameters_factory = (structure, number) => {
    let length = 0;
    for (const item of structure) {
        length += item;
    }
    return new Array(length).fill(number * float_multiplier);
}

// simulate the expected aggregation and return the expected result
const expected_aggregated_model = (structure, numbers, current_batch_size, max_batch_size = 10) => {
    let aggregated_value = 1.;
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
        curr++;
    }
    return new Array(length).fill(aggregated_value * float_multiplier);
}

async function deploy_federator(structure, init_model_parameters, max_batch_size = 10) {
    const Federator = await ethers.getContractFactory("Federator");
    const model_structure = structure;
    const federator = await Federator.deploy(model_structure, init_model_parameters, max_batch_size);
    await federator.deployed();
    return federator;
}


describe("Aggregation", function () {
    const model_structure = [6, 20, 40, 6];
    const init_model_parameters = same_parameters_factory(model_structure, 1.);
    it("Should initialize the weights and structures", async function () {

        const federator = await deploy_federator(model_structure, init_model_parameters);

        expect((await federator.get_weights()).map((x) => {
            return parseFloat(x) / float_multiplier;
        })).to.eql(init_model_parameters);

        expect(parseFloat(await federator.batch_size())).to.equal(0);

        expect(parseFloat(await federator.max_batch_size())).to.equal(10);
    });

    it("Should update the weights and structures", async function () {
        const federator = await deploy_federator(model_structure, init_model_parameters);

        const new_model_parameters = same_parameters_factory(model_structure, 2.);
        await federator.update(new_model_parameters);

        expect((await federator.get_weights()).map((x) => {
            return parseFloat(x) / float_multiplier;
        })).to.eql(same_parameters_factory(model_structure, 1.));
    });

    it("Should average repeated updates under limit", async function () {
        const federator = await deploy_federator(model_structure, init_model_parameters);
        const weights_to_update = [1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11.];
        for (const weight of weights_to_update) {
            const parameters = same_parameters_factory(model_structure, weight);
            await federator.update(parameters);
        }

        expect((await federator.get_weights()).map((x) => {
            return parseFloat(x) / float_multiplier;
        })).to.eql(expected_aggregated_model(model_structure, weights_to_update, 0));    
        
        
    
    });

});