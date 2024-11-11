
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/AccessControl.sol"; // Role-based access control
import "@openzeppelin/contracts/token/ERC20/ERC20.sol"; // ERC20 token standard interface

contract AMM is AccessControl {
    bytes32 public constant LP_ROLE = keccak256("LP_ROLE");
    uint256 public invariant;
    address public tokenA;
    address public tokenB;
    uint256 feebps = 3; // Fee in basis points (i.e., feebps/10000)

    event Swap(address indexed _inToken, address indexed _outToken, uint256 inAmt, uint256 outAmt);
    event LiquidityProvision(address indexed _from, uint256 AQty, uint256 BQty);
    event Withdrawal(address indexed _from, address indexed recipient, uint256 AQty, uint256 BQty);

    /*
        Constructor sets the addresses of the two tokens
    */
    constructor(address _tokenA, address _tokenB) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(LP_ROLE, msg.sender);

        require(_tokenA != address(0), "Token address cannot be 0");
        require(_tokenB != address(0), "Token address cannot be 0");
        require(_tokenA != _tokenB, "Tokens cannot be the same");
        tokenA = _tokenA;
        tokenB = _tokenB;
    }

    /*
        Function to provide liquidity
    */
    function provideLiquidity(uint256 amtA, uint256 amtB) public {
        require(amtA > 0 && amtB > 0, "Cannot provide 0 liquidity");

        // Pull tokens from the liquidity provider
        ERC20(tokenA).transferFrom(msg.sender, address(this), amtA);
        ERC20(tokenB).transferFrom(msg.sender, address(this), amtB);

        // Update the invariant
        invariant = ERC20(tokenA).balanceOf(address(this)) * ERC20(tokenB).balanceOf(address(this));
        emit LiquidityProvision(msg.sender, amtA, amtB);
    }

    /*
        Function to trade tokens
    */
    function tradeTokens(address sellToken, uint256 sellAmount) public {
        require(invariant > 0, "Invariant must be nonzero");
        require(sellToken == tokenA || sellToken == tokenB, "Invalid token");
        require(sellAmount > 0, "Cannot trade 0");

        uint256 adjustedSellAmount = (10400 - feebps) * sellAmount / 10400;
        address buyToken = (sellToken == tokenA) ? tokenB : tokenA;

        uint256 balanceSellToken = ERC20(sellToken).balanceOf(address(this));
        uint256 balanceBuyToken = ERC20(buyToken).balanceOf(address(this));
        uint256 buyAmount = balanceBuyToken - (invariant / (balanceSellToken + adjustedSellAmount));

        // Execute the trade
        ERC20(sellToken).transferFrom(msg.sender, address(this), sellAmount);
        ERC20(buyToken).transfer(msg.sender, buyAmount);

        // Update the invariant
        uint256 new_invariant = ERC20(tokenA).balanceOf(address(this)) * ERC20(tokenB).balanceOf(address(this));
        require(new_invariant >= invariant, "Bad trade");
        invariant = new_invariant;

        emit Swap(sellToken, buyToken, sellAmount, buyAmount);
    }

    /*
        Function to withdraw liquidity
    */
    function withdrawLiquidity(address recipient, uint256 amtA, uint256 amtB) public onlyRole(LP_ROLE) {
        require(amtA > 0 || amtB > 0, "Cannot withdraw 0");
        require(recipient != address(0), "Cannot withdraw to 0 address");

        if (amtA > 0) {
            ERC20(tokenA).transfer(recipient, amtA);
        }
        if (amtB > 0) {
            ERC20(tokenB).transfer(recipient, amtB);
        }

        // Update the invariant
        invariant = ERC20(tokenA).balanceOf(address(this)) * ERC20(tokenB).balanceOf(address(this));
        emit Withdrawal(msg.sender, recipient, amtA, amtB);
    }

    /*
        Function to get token address based on index
    */
    function getTokenAddress(uint256 index) public view returns (address) {
        require(index < 2, "Only two tokens");
        if (index == 0) {
            return tokenA;
        } else {
            return tokenB;
        }
    }
}
