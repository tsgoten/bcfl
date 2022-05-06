pragma solidity 0.8.13;

contract Federator {
    int256 public max_batch_size;

    // data structure for global model parameters
    int256[] public global_model_parameters;
    int256[] running_model_parameters;

    uint256[] public dimensions;
    int256 public batch_size;
    uint16 batch_number;

    // two models - running and master
    constructor(
        uint256[] memory model_structure,
        int256[] memory model_parameters,
        int256 max_batch_size_
    ) public {
        global_model_parameters = model_parameters;
        running_model_parameters = model_parameters;
        max_batch_size = max_batch_size_;
        dimensions = new uint256[](model_structure.length);
        uint256 model_length_total = 0;
        for (uint16 i = 0; i < model_structure.length; i++) {
            dimensions[i] = model_structure[i];
            model_length_total += model_structure[i];
        }
        require(model_length_total == model_parameters.length);
        model_structure = model_structure;
        batch_size = 0;
        batch_number = 0;
    }

    // updates existing federated learning model with new data
    function update(int256[] calldata new_model_parameters) public {
        if (batch_size == max_batch_size) {
            global_model_parameters = running_model_parameters;
            batch_size = 1;
            batch_number = batch_number + 1;
        }
        for (uint256 i = 0; i < new_model_parameters.length; i++) {
            running_model_parameters[i] =
                (new_model_parameters[i] +
                    running_model_parameters[i] *
                    batch_size) /
                (batch_size + 1);
        }
        batch_size = batch_size + 1;
    }

    function get_weights() public view returns (int256[] memory weights) {
        return global_model_parameters;
    }
}
