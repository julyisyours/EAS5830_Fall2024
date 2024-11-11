pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC777/ERC777.sol";
import "@openzeppelin/contracts/token/ERC777/IERC777Recipient.sol";
import "@openzeppelin/contracts/interfaces/IERC1820Registry.sol";
import "./MCITR.sol";

/*
	A simple Bank contract that is vulnerable to reentrancy attacks
	The Bank functions similarly to Wrapped ETH (WETH)
	Users can deposit ETH, and in return they receive an MCITR token (the R is for Reentrancy)
	Users can then redeem their MCITR tokens in exchange for the ETH held by the contract

	This happens in 3 step process:
	1) Deposit ETH (get a local balance)
	2) Withdraw MCITR tokens (reducing your local balance)
	3) Redeem MCITR tokens for ETH held by the contract
*/
contract Bank is AccessControl, IERC777Recipient {
	MCITR public token;
	IERC1820Registry private _erc1820 = IERC1820Registry(0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24); //This is the address of the EIP1820 registry contract on *every* chain https://eips.ethereum.org/EIPS/eip-1820
	bytes32 constant private TOKENS_RECIPIENT_INTERFACE_HASH = keccak256("ERC777TokensRecipient"); //This is the Interface we'll register with the 1820 registry

	event Deposit( address indexed depositor, uint256 amount );
	event Claim( address indexed withdrawer, uint256 amount );
	event Withdrawal( address indexed withdrawer, uint256 amount );

	mapping( address => uint256 ) public balances;
	
	/*
	   We will track the deposits and withdrawals from each user separately (rather than just their net balance).
	   A real-world contract probably wouldn't do this, as it's not necessary when everything works correctly, 
	   but it makes it easy for the autograder to identify the quantity of the theft.
	*/
	mapping( address => uint256 ) public deposits;
	mapping( address => uint256 ) public withdrawals;

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
		token = new MCITR( 0, admin);
		_erc1820.setInterfaceImplementer(address(this),TOKENS_RECIPIENT_INTERFACE_HASH,address(this)); //Register as an ERC777TokensRecipient
    }

	/*
	   Before executing a reentrancy attack, you must deposit some ETH 
	   Depositing ETH updates your local balance at the bank
	*/
	function deposit() public payable {
		uint256 amount = msg.value;
		require( amount > 0 );
		balances[msg.sender] += amount;
		deposits[msg.sender] += amount;
		emit Deposit( msg.sender, amount );
	}

	/*
	   If you have a positive balance, you can "claim" MCITR tokens 
	   Note, this natural variant of the claim function is *not* vulnerable to reentrancy
	   Can you see why?
	*/
	function claim(uint256 amount) public {
		require( balances[msg.sender] >= amount );
		token.mint( msg.sender, amount );
		balances[msg.sender] -= amount;
		withdrawals[msg.sender] += amount;
		emit Claim( msg.sender, amount );
	}

	/*
		Like "claim" (above), this function allows you to claim MCITR tokens if you have a positive balance
	   This function is vulnerable to a reentrancy attack
	*/
	function claimAll() public { 
		uint256 amount = balances[msg.sender];
		require( amount > 0, 'Cannot withdraw 0' );
		emit Claim( msg.sender, amount );
		token.mint( msg.sender, amount );
		balances[msg.sender] = 0;
		withdrawals[msg.sender] += amount;
	}

	/*
		Redeem MCITR tokens for ETH
	*/
	function redeem(uint256 amount) public {
		token.transferFrom( msg.sender, address(this), amount );
		(bool sent, bytes memory data) = msg.sender.call{value: amount}(""); //In practice, you'd want a reentrancy guard here as well
        require(sent, "Failed to send Ether");
		emit Withdrawal( msg.sender, amount );
	}


	/*
	   This function is necessary in order for the Bank contract to receive ERC777 tokens
	   The *only* ERC777 the bank is willing to accept is its own MCITR token
	*/
	function tokensReceived( address operator, address from, address to, uint256 amount, bytes calldata userData, bytes calldata operatorData) external view {
		require(msg.sender == address(token), "Invalid token");
	}


}
