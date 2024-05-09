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
    error UnsupportedChain();
    error InsufficientBalance();
    error TransactionNotFinalized();
    error EtherTransferFailed();
    error DepositValueTooLow();
    
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
        if(msg.value <= 0) {
            revert DepositValueTooLow();
        }
        accountBalances[msg.sender] += msg.value;
        emit FundsDeposited(msg.sender, msg.value);
    }

    function withdrawFunds(uint256 amount) external {
        if(amount > accountBalances[msg.sender]) {
            revert InsufficientBalance();
        }
        accountBalances[msg.sender] -= amount;
        (bool sent, ) = msg.sender.call{value: amount}("");
        if (!sent) {
            revert EtherTransferFailed();
        }
        emit FundsWithdrawn(msg.sender, amount);
    }

    function enableChainSupport(address blockchainAddress) external onlyOwner {
        supportedChains[blockchainAddress] = true;
    }

    function disableChainSupport(address blockchainAddress) external onlyOwner {
        supportedChains[blockchainAddress] = false;
    }

    function executeCrossChainTransfer(address originChain, address targetChain, uint256 amount, bytes32 txHash) external {
        if(!(supportedChains[originChain] && supportedChains[targetChain])) {
            revert UnsupportedChain();
        }
        
        if (!transactionFinalityStatus[txHash]) {
            bool isFinalized = IBlockchainBridge(originChain).isTransactionFinalized(txHash);
            if (!isFinalized) {
                revert TransactionNotFinalized();
            }
            transactionFinalityStatus[txHash] = true; // Cache this transaction as checked
        }

        uint256 originChainBalance = IBlockchainBridge(originChain).accountBalance(address(this));
        if (originChainBalance < amount) {
            revert InsufficientBalance();
        }

        emit CrossChainFundsTransfer(originChain, targetChain, msg.sender, amount);
    }

    function confirmTransactionFinality(address blockchain, bytes32 txHash) external view returns (bool) {
        if (!supportedChains[blockchain]) {
            revert UnsupportedChain();
        }
        return transactionFinalityStatus[txHash] || IBlockchainBridge(blockchain).isTransactionFinalized(txHash);
    }

    function getAccountBalance(address account) external view returns (uint256) {
        return accountBalances[account];
    }
}