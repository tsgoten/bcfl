const { expect } = require("chai");
const { ethers } = require("hardhat");
const divide = require("divide-bigint");

const float_multiplier = ethers.BigNumber.from(2).pow(64);

const to_fixed_number = (number) => {
    return ethers.BigNumber.from(number).mul(float_multiplier);
}

const to_float_number = (number) => {
    return divide(number.toBigInt(), float_multiplier.toBigInt());
}

// factory to create array of the same number of length according to the structure
const same_parameters_factory = (structure, number) => {
    let length = 0;
    for (const item of structure) {
        length += item;
    }
    return new Array(length).fill(to_fixed_number(number));
}

// simulate the expected aggregation and return the expected result
const expected_aggregated_model = (structure, init_num, numbers, current_batch_size, max_batch_size = 10) => {
    let aggregated_value = to_fixed_number(init_num);
    let length = 0;
    for (const item of structure) {
        length += item;
    }

    let curr = current_batch_size;
    numbers.forEach((num) => {
        console.log(num);
        if (curr == max_batch_size) {
            curr = 1;
        }
        aggregated_value = aggregated_value.mul(curr).add(to_fixed_number(num)).div(curr + 1);
        console.log("aggregated_value", to_float_number(aggregated_value));
        curr++;
    });
    return new Array(length).fill(aggregated_value);
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
            return x;
        })).to.eql(init_model_parameters);

        expect(parseFloat(await federator.batch_size())).to.equal(1);

        expect(parseFloat(await federator.max_batch_size())).to.equal(10);
    });

    it("Should update the weights and structures", async function () {
        const federator = await deploy_federator(model_structure, init_model_parameters);

        const new_model_parameters = same_parameters_factory(model_structure, 2.);
        await federator.update(new_model_parameters);

        expect(await federator.get_weights()).to.eql(same_parameters_factory(model_structure, 1.));
        
        expected = expected_aggregated_model(model_structure, 1., [2.], 1);
        console.log("expected", expected.map(
            (x) => {
                return to_float_number(x);
            }
        ));
        expect(await federator.get_running_weights()).to.eql(expected); 
    
    });


    // it("Should average repeated updates under limit", async function () {
    //     const model_parameters = same_parameters_factory(model_structure, 1);
    //     const federator = await deploy_federator(model_structure, model_parameters);
    //     const weights_to_update = [2, 3];
    //     weights_to_update.forEach(async (weight) => {
    //         const parameters = same_parameters_factory(model_structure, weight);
    //         await federator.update(parameters);
    //     });

    //     expected_parameters = expected_aggregated_model(model_structure, 1, weights_to_update, 1);
    //     console.log(expected_parameters.map((x) => {
    //         return to_float_number(x);
    //     }));
    //     console.log((await federator.get_running_weights()).map((x) => {
    //         return to_float_number(x);
    //     }));
    //     expect(await federator.get_running_weights()).to.eql(expected_parameters);    
    
    // });

});