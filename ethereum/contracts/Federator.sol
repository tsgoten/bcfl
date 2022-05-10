pragma solidity 0.8.13;

import "../node_modules/hardhat/console.sol";
import {ABDKMath64x64 as math} from "./math.sol";

contract Federator {
    int128 public max_batch_size;

    // data structure for global model parameters
    int128[] private global_model_parameters;
    int128[] private running_model_parameters;

    uint128[] public dimensions;
    int128 public batch_size;
    int16 batch_number;

    // two models - running and master
    constructor(
        uint128[] memory model_structure,
        int128[] memory model_parameters,
        int128 max_batch_size_
    ) public {
        max_batch_size = max_batch_size_;
        dimensions = new uint128[](model_structure.length);

        uint128 model_length_total = 0;
        for (uint16 i = 0; i < model_structure.length; i++) {
            dimensions[i] = model_structure[i];
            model_length_total += model_structure[i];
        }
        require(model_length_total == model_parameters.length);

        global_model_parameters = new int128[](model_parameters.length);
        running_model_parameters = new int128[](model_parameters.length);
        for (uint16 i = 0; i < model_parameters.length; i++) {
            global_model_parameters[i] = model_parameters[i];
            running_model_parameters[i] = model_parameters[i];
        }
        model_structure = model_structure;
        batch_size = 1;
        batch_number = 0;
    }

    // updates existing federated learning model with new data
    function update(int128[] calldata new_model_parameters) public {
        if (batch_size == max_batch_size) {
            global_model_parameters = running_model_parameters;
            batch_size = 1;
            batch_number = batch_number + 1;
            //console.log("I am here");
        }
        for (uint128 i = 0; i < new_model_parameters.length; i++) {
            running_model_parameters[i] = math.div(
                math.add(
                    new_model_parameters[i],
                    math.mul(running_model_parameters[i], math.fromInt(batch_size))
                ),
                math.fromInt(batch_size + 1)
            );
            //console.logInt(running_model_parameters[i]);
        }
        batch_size = batch_size + 1;
    }

    function write_running_parameters(int128[] memory weights) private {
        running_model_parameters = weights;
    }

    function get_weights() public view returns (int128[] memory weights) {
        return global_model_parameters;
    }

    function get_running_weights()
        public
        view
        returns (int128[] memory weights)
    {
        return running_model_parameters;
    }
}
