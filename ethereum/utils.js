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
        //console.log(num);
        if (curr == max_batch_size) {
            curr = 1;
        }
        aggregated_value = aggregated_value.mul(curr).add(to_fixed_number(num)).div(curr + 1);
        //console.log("aggregated_value", to_float_number(aggregated_value));
        curr++;
    });
    return new Array(length).fill(aggregated_value);
}

module.exports = {
    to_fixed_number,
    to_float_number,
    float_multiplier,
    same_parameters_factory,
    expected_aggregated_model
}