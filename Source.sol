// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract Source is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");

    mapping(address => bool) public approved;
    address[] public tokens;

    event Deposit(address indexed token, address indexed recipient, uint256 amount);
    event Withdrawal(address indexed token, address indexed recipient, uint256 amount);
    event Registration(address indexed token);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

    function deposit(address _token, address _recipient, uint256 _amount) public {
        // Check if the token has been registered
        require(approved[_token], "Token not registered");

        // Transfer the tokens from the user to the deposit contract
        ERC20(_token).transferFrom(msg.sender, address(this), _amount);

        // Emit the Deposit event
        emit Deposit(_token, _recipient, _amount);
    }

    function withdraw(address _token, address _recipient, uint256 _amount) public onlyRole(WARDEN_ROLE) {
        // Transfer the tokens from the contract to the recipient
        ERC20(_token).transfer(_recipient, _amount);

        // Emit the Withdrawal event
        emit Withdrawal(_token, _recipient, _amount);
    }

    function registerToken(address _token) public onlyRole(ADMIN_ROLE) {
        // Ensure the token is not already registered
        require(!approved[_token], "Token already registered");

        // Register the token
        approved[_token] = true;
        tokens.push(_token);

        // Emit the Registration event
        emit Registration(_token);
    }
}
