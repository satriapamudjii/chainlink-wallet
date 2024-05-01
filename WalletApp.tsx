import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import { QueryClient, QueryClientProvider, useQuery } from 'react-query';
import './WalletApp.css'; 

const queryClient = new QueryClient();

const networks = [
  {
    name: 'Ethereum',
    rpcUrl: process.env.REACT_APP_ETHEREUM_RPC,
  },
  {
    name: 'Binance Smart Chain',
    rpcUrl: process.env.REACT_APP_BSC_RPC,
  },
  
];

const fetchBalance = async (address: string, rpcUrl: string) => {
  const provider = new ethers.providers.JsonRpcProvider(rpcUrl);
  const balance = await provider.getBalance(address);
  return ethers.utils.formatEther(balance);
};

const WalletApp: React.FC = () => {
  const [address, setAddress] = useState<string>('');
  const [selectedNetwork, setSelectedNetwork] = useState<string>(networks[0].rpcUrl);

  const { data: balance, isFetching } = useQuery(['balance', address, selectedNetwork], () => fetchBalance(address, selectedNetwork), {
    enabled: !!address,
  });

  const handleAddressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAddress(e.target.value);
  };

  const handleNetworkChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedNetwork(e.target.value);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="walletApp">
        <h1>Multi-Blockchain Wallet</h1>
        <input
          type="text"
          placeholder="Enter wallet address"
          value={address}
          onChange={handleAddressChange}
        />
        <select value={selectedNetwork} onChange={handleNetworkChange}>
          {networks.map((network) => (
            <option key={network.rpcUrl} value={network.rpcUrl}>
              {network.name}
            </option>
          ))}
        </select>
        <div>
          {isFetching ? (
            <p>Loading balance...</p>
          ) : (
            <p>Balance: {balance} ETH (or equivalent)</p>
          )}
        </div>
      </div>
    </QueryClientProvider>
  );
};

export default WalletApp;
