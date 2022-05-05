pragma solidity 0.8.13;

contract Federator {
    int256 constant MAX_BATCH_SIZE = 10;
    uint256 constant float_multiplier = 1e32;

    // data structure for global model parameters
    int256[] public global_model_parameters;
    int256[] public running_model_parameters;

    int256[] public dimensions;
    int256 public batch_size;
    uint16 batch_number;

    // two models - running and master 
    constructor(int256[] memory model_parameters, int256[] memory model_structure) public {
        global_model_parameters = model_parameters;
        running_model_parameters = model_parameters;
        dimensions = new int256[](model_structure.length);
        for (uint16 i = 0; i < model_structure.length; i++) {
            dimensions[i] = model_structure[i];
        }
        model_structure = model_structure;
        batch_size = 0;
        batch_number = 0;
    }


    // updates existing federated learning model with new data
    function update_model(int256[] calldata new_model_parameters) public {
        if (batch_size == MAX_BATCH_SIZE) {
            global_model_parameters = running_model_parameters;
            batch_size = 0;
            batch_number = batch_number + 1;
        } else {
            for (uint i = 0; i < new_model_parameters.length; i++) {
                running_model_parameters[i] = (new_model_parameters[i] + running_model_parameters[i] * batch_size) / (batch_size + 1);
            }
        }
    }

    function get_weights() public view returns (int256[] memory weights) {
        return global_model_parameters;
    }

}