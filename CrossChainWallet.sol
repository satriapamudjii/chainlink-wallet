// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IBlockchainBridge {
    function isTransactionFinalized(bytes32 txHash) external view returns (bool);
    function accountBalance(address account) external view returns (uint256);
}

contract ChainLinkWallet {
    address private owner;
    mapping(address => uint256) private accountBalances;
    mapping(address => bool) private supportedChains;
    mapping(bytes32 => bool) private transactionFinalityStatus;

    event FundsDeposited(address indexed sender, uint256 amount);
    event FundsWithdrawn(address indexed receiver, uint256 amount);
    event CrossChainFundsTransfer(
        address indexed sourceChain, 
        address indexed destinationChain, 
        address indexed user, 
        uint256 amount
    );
    
    error AccessDenied();
    error OperationFailed(string message);
    
    modifier onlyOwner() {
        if (msg.sender != owner) {
            revert AccessDenied();
        }
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function depositFunds() external payable {
        require(msg.value > 0, "Deposit must be above zero.");
        accountBalances[msg.sender] += msg.value;
        emit FundsDeposited(msg.sender, msg.value);
    }

    function withdrawFunds(uint256 amount) external {
        require(amount <= accountBalances[msg.sender], "Balance too low.");
        accountBalances[msg.sender] -= amount;
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent, "Ether transfer failed");
        emit FundsWithdrawn(msg.sender, amount);
    }

    function enableChainSupport(address blockchainAddress) external onlyOwner {
        supportedChains[blockchainAddress] = true;
    }

    function disableChainSupport(address blockchainAddress) external onlyOwner {
        supportedChains[blockchainAddress] = false;
    }

    function executeCrossChainTransfer(address originChain, address targetChain, uint256 amount, bytes32 txHash) external {
        require(supportedChains[originChain] && supportedChains[targetChain], "Unsupported chain(s).");
        
        if (!transactionFinalityStatus[txHash]) {
            require(IBlockchainBridge(originChain).isTransactionFinalized(txHash), "Transaction not finalized on origin.");
            transactionFinalityStatus[txHash] = true; // Cache this transaction as checked
        }

        uint256 originChainBalance = IBlockchainBridge(originChain).accountBalance(address(this));
        require(originChainBalance >= amount, "Insufficient origin chain balance.");

        emit CrossChainFundsTransfer(originChain, targetChain, msg.sender, amount);
    }

    function confirmTransactionFinality(address blockchain, bytes32 txHash) external view returns (bool) {
        require(supportedChains[blockchain], "Unsupported chain.");
        return transactionFinalityStatus[txHash] || IBlockchainBridge(blockchain).isTransactionFinalized(txHash);
    }

    function getAccountBalance(address account) external view returns (uint256) {
        return accountBalances[account];
    }
}