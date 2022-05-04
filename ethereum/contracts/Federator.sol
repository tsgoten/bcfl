pragma solidity ^0.7.0;

import “stringUtils.sol”;

contract Federator {
    uint16 constant MAX_BATCH_SIZE = 10;

    // data structure for global model parameters
    int256[] public global_model_parameters;
    int256[] public running_model_parameters;

    int256[] public dimensions;
    uint16 public batch_size;
    uint16 batch_number;



    // two models - running and master 

    // updates existing federated learning model with new data
    function update_model(int256[] new_model_parameters) public {
        if (batch_size == MAX_BATCH_SIZE) {
            global_model_parameters = running_model_parameters
        } else {
            for (int i = 0; i < new_model_parameters.length; i++) {
                running_model_parameters[i] = (new_model_parameters[i] + running_model_parameters[i] * batch_count) / (batch_count + 1);
            }
        }
    };

    function get_weights() public view returns (int256[] weights) {
        return global_model_parameters;
    };

}