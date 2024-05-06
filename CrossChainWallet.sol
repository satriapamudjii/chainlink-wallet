// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IExternalBlockchain {
    function verifyTransactionFinality(bytes32 txHash) external view returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract CrossChainWallet {
    address private _owner;
    mapping(address => uint256) private _balances;
    mapping(address => bool) private _supportedBlockchains;
    mapping(bytes32 => bool) private _finalityCheckCache;

    event Deposit(address indexed sender, uint256 amount);
    event Withdrawal(address indexed receiver, uint256 amount);
    event CrossChainSwap(
        address indexed fromChain, 
        address indexed toChain, 
        address indexed user, 
        uint256 amount
    );
    
    error Unauthorized();
    error InvalidOperation(string message);
    
    modifier onlyOwner() {
        if (msg.sender != _owner) {
            revert Unauthorized();
        }
        _;
    }

    constructor() {
        _owner = msg.sender;
    }

    function deposit() external payable {
        require(msg.value > 0, "Deposit amount must be greater than zero.");
        _balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external {
        require(amount <= _balances[msg.sender], "Insufficient balance.");
        _balances[msg.sender] -= amount;
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent, "Failed to send Ether");
        emit Withdrawal(msg.sender, amount);
    }

    function addSupportedBlockchain(address blockchainAddress) external onlyOwner {
        _supportedBlockchains[blockchainAddress] = true;
    }

    function removeSupportedBlockchain(address blockchainAddress) external onlyOwner {
        _supportedBlockchains[blockchainAddress] = false;
    }

    function crossChainSwap(address fromChain, address toChain, uint256 amount, bytes32 txHash) external {
        require(_supportedBlockchains[fromChain] && _supportedBlockchains[toChain], "One or both chains are not supported.");
        
        if (!_finalityCheckCache[txHash]) {
            require(IExternalBlockchain(fromChain).verifyTransactionFinality(txHash), "Transaction finality could not be verified on fromChain.");
            _finalityCheckCache[txHash] = true; // Cache result
        }

        uint256 fromChainBalance = IExternalBlockchain(fromChain).balanceOf(address(this));
        require(fromChainBalance >= amount, "Insufficient balance on fromChain.");

        emit CrossChainSwap(fromChain, toChain, msg.sender, amount);
    }

    function verifyTransactionFinalityOnBlockchain(address blockchain, bytes32 txHash) external view returns (bool) {
        require(_supportedBlockchains[blockchain], "Blockchain not supported.");
        return _finalityCheckCache[txHash] || IExternalBlockchain(blockchain).verifyTransactionFinality(txHash);
    }

    function checkBalance(address account) external view returns (uint256) {
        return _balances[account];
    }
}