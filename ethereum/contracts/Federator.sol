pragma solidity ^0.7.0;

import “stringUtils.sol”;

contract Federator {
    // data structure for global model parameters
    int256[][][][] public global_model_parameters;


    // updates existing federated learning model with new data
    function update_model(int256[][][][] new_model_parameters) public {
        global_model_parameters = new_model_parameters;
    }

}