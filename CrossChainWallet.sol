// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IExternalBlockchain {
    function verifyTransactionFinality(bytes32 txHash) external view returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract CrossChainWallet {
    address owner;
    mapping(address => uint256) private _balances;
    mapping(address => bool) private _supportedBlockchains;

    // Caching the finality check results might minimize the need for repetitive checks
    mapping(bytes32 => bool) private _finalityCheckCache;

    event Deposit(address indexed sender, uint256 amount);
    event Withdrawal(address indexed receiver, uint256 amount);
    event CrossChainSwap(address indexed fromChain, address indexed toChain, address indexed user, uint256 amount);
    
    error Unauthorized();
    error InvalidOperation(string message);
    
    modifier onlyOwner() {
        if (msg.sender != owner) {
            revert Unauthorized();
        }
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function deposit() external payable {
        if (msg.value == 0) {
            revert InvalidOperation("Deposit amount must be greater than zero.");
        }
        _balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external {
        if (amount > _balances[msg.sender]) {
            revert InvalidOperation("Insufficient balance.");
        }
        _balances[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);
        emit Withdrawal(msg.sender, amount);
    }

    function addSupportedBlockchain(address blockchainAddress) external onlyOwner {
        _supportedBlockchains[blockchainAddress] = true;
    }

    function removeSupportedBlockchain(address blockchainAddress) external onlyOwner {
        _supportedBlockchains[blockchainAddress] = false;
    }

    // No direct optimization via "batching api calls" but minimizing unnecessary checks
    function crossChainSwap(address fromChain, address toChain, uint256 amount, bytes32 txHash) external {
        if (!_supportedBlockchains[fromChain] || !_supportedBlockchains[toChain]) {
            revert InvalidOperation("One or both chains are not supported.");
        }
        // Using cached results if available to avoid unnecessary external calls
        if (!_finalityCheckCache[txHash] && !IExternalBlockchain(fromChain).verifyTransactionFinality(txHash)) {
            revert InvalidOperation("Transaction finality could not be verified on fromChain.");
        }
        
        _finalityCheckCache[txHash] = true; // Cache this result

        uint256 fromChainBalance = IExternalBlockchain(fromChain).balanceOf(address(this));
        if (fromChainBalance < amount) {
            revert InvalidOperation("Insufficient balance on fromChain.");
        }
        
        emit CrossChainSwap(fromChain, toChain, msg.sender, amount);
    }

    function verifyTransactionFinalityOnBlockchain(address blockchain, bytes32 txHash) external view returns (bool) {
        if (!_supportedBlockchains[blockchain]) {
            revert InvalidOperation("Blockchain not supported.");
        }
        // Return cached result if present, otherwise make the "API call"
        return _finalityCheckCache[txHash] || IExternalBlockchain(blockchain).verifyTransactionFinality(txHash);
    }

    function checkBalance(address account) external view returns (uint256) {
       return _balances[account];
    }
}