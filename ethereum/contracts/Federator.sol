pragma solidity 0.8.13;

import "../node_modules/hardhat/console.sol";

library math {
    int128 private constant MIN_64x64 = -0x80000000000000000000000000000000;

    int128 private constant MAX_64x64 = 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;

    function fromInt(int256 x) internal pure returns (int128) {
        unchecked {
            require(x >= -0x8000000000000000 && x <= 0x7FFFFFFFFFFFFFFF);
            return int128(x << 64);
        }
    }

    function mul(int128 x, int128 y) internal pure returns (int128) {
        unchecked {
            int256 result = (int256(x) * y) >> 64;
            require(result >= MIN_64x64 && result <= MAX_64x64);
            return int128(result);
        }
    }

    function add(int128 x, int128 y) internal pure returns (int128) {
        unchecked {
            int256 result = int256(x) + y;
            require(result >= MIN_64x64 && result <= MAX_64x64);
            return int128(result);
        }
    }

    function div(int128 x, int128 y) internal pure returns (int128) {
        unchecked {
            require(y != 0, "Division by zero");
            int256 result = (int256(x) << 64) / y;
            require(
                result >= MIN_64x64 && result <= MAX_64x64,
                "Division overflow"
            );
            return int128(result);
        }
    }
}

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
        // dimensions = new uint128[](model_structure.length);

        // uint128 model_length_total = 0;
        // for (uint16 i = 0; i < model_structure.length; i++) {
        //     dimensions[i] = model_structure[i];
        //     model_length_total += model_structure[i];
        // }
        // require(model_length_total == model_parameters.length);

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
            for (uint16 i = 0; i < running_model_parameters.length; i++) {
                global_model_parameters[i] = running_model_parameters[i];
            }
            batch_size = 1;
            //console.log("I am here");
        }
        for (uint128 i = 0; i < new_model_parameters.length; i++) {
            running_model_parameters[i] = math.div(
                math.add(
                    new_model_parameters[i],
                    math.mul(
                        running_model_parameters[i],
                        math.fromInt(batch_size)
                    )
                ),
                math.fromInt(batch_size + 1)
            );
            //console.logInt(running_model_parameters[i]);
        }
        batch_size = batch_size + 1;
        //console.logInt(batch_size);
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
