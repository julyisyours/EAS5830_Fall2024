pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC777/ERC777.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract MCITR is ERC777, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

	constructor(uint256 initialSupply, address admin ) ERC777("MCIT Re-entry", "MCITR", new address[](0) ) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(MINTER_ROLE, msg.sender );
		_mint(msg.sender, initialSupply, "", "");
	}

	function mint(address to, uint256 amount ) public onlyRole(MINTER_ROLE) {
		_mint( to, amount, "", "" );	
	}
}
