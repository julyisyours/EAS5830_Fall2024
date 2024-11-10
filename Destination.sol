// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./BridgeToken.sol";

contract Destination is AccessControl {
    bytes32 public constant WARDEN_ROLE = keccak256("WARDEN_ROLE");
    bytes32 public constant CREATOR_ROLE = keccak256("CREATOR_ROLE");

    // Maps a wrapped token address on the destination side to its underlying token address from the source chain
    mapping(address => address) public underlying_tokens;
    // Maps an underlying token address from the source chain to its corresponding wrapped token address on the destination side
    mapping(address => address) public wrapped_tokens;
    // Contains all unique underlying token addresses that have been registered in the contract
    address[] public tokens;

    event Creation(address indexed underlying_token, address indexed wrapped_token);
    event Wrap(address indexed underlying_token, address indexed wrapped_token, address indexed to, uint256 amount);
    event Unwrap(address indexed underlying_token, address indexed wrapped_token, address frm, address indexed to, uint256 amount);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(CREATOR_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

    function createToken(address _underlying_token, string memory name, string memory symbol) public onlyRole(CREATOR_ROLE) returns (address) {
        require(wrapped_tokens[_underlying_token] == address(0), "Token already registered");

        // Deploy new BridgeToken and set up the mappings
        BridgeToken newToken = new BridgeToken(_underlying_token, name, symbol, msg.sender);
        address wrappedAddress = address(newToken);

        // Map the underlying token to the wrapped token and vice versa
        wrapped_tokens[_underlying_token] = wrappedAddress;
        underlying_tokens[wrappedAddress] = _underlying_token;

        // Add to tokens array to keep track of all registered underlying tokens
        tokens.push(_underlying_token);

        // Emit Creation event with expected parameters
        emit Creation(_underlying_token, wrappedAddress);
        return wrappedAddress;
    }

    function wrap(address _underlying_token, address _recipient, uint256 _amount) public onlyRole(WARDEN_ROLE) {
        address wrappedTokenAddress = wrapped_tokens[_underlying_token];
        require(wrappedTokenAddress != address(0), "Token not registered");

        // Mint wrapped tokens to the recipient
        BridgeToken(wrappedTokenAddress).mint(_recipient, _amount);

        // Emit Wrap event with accurate parameters
        emit Wrap(_underlying_token, wrappedTokenAddress, _recipient, _amount);
    }

    function unwrap(address _wrapped_token, address _recipient, uint256 _amount) public onlyRole(WARDEN_ROLE) {
        address underlyingTokenAddress = underlying_tokens[_wrapped_token];
        require(underlyingTokenAddress != address(0), "Token not registered");

        // Ensure caller owns enough tokens to unwrap
        require(BridgeToken(_wrapped_token).balanceOf(msg.sender) >= _amount, "Insufficient balance");

        // Burn tokens from the sender
        BridgeToken(_wrapped_token).burnFrom(msg.sender, _amount);

        // Emit Unwrap event with accurate parameters
        emit Unwrap(underlyingTokenAddress, _wrapped_token, msg.sender, _recipient, _amount);
    }
}
