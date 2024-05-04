import React, { useState } from 'react';
import { QueryClientProvider, useQuery } from 'react-query';
import { queryClient } from './yourQueryClientInitializationFile';

type Network = {
  name: string;
  rpcUrl: string | undefined;
  explorerUrl: string;
};

const networks: Network[] = [
  {
    name: 'Ethereum',
    rpcUrl: process.env.REACT_APP_ETHEREUM_RPC,
    explorerUrl: 'https://etherscan.io/address/',
  },
  {
    name: 'Binance Smart Chain',
    rpcUrl: process.env.REACT_APP_BSC_RPC,
    explorerUrl: 'https://bscscan.com/address/',
  },
];

const fetchTransactions = async (address: string, explorerUrl: string): Promise<string[]> => {
  const fakeTransactions = ['tx1', 'tx2', 'tx3'];
  return Promise.resolve(fakeTransactions);
};

const WalletApp: React.FC = () => {
  const [address, setAddress] = useState<string>('');
  const [selectedNetwork, setSelectedNetwork] = useState<string>(networks[0].rpcUrl || '');

  const selectedNetworkInfo = networks.find(n => n.rpcUrl === selectedNetwork);

  const { data: balance, isFetching } = useQuery(['balance', address, selectedNetwork], () => fetchBalance(address, selectedNetwork), {
    enabled: !!address,
  });

  const { data: transactions } = useQuery(['transactions', address, selectedNetwork], () => fetchTransactions(address, selectedNetworkInfo?.explorerUrl || ''), {
    enabled: !!address,
  });

  const handleAddressChange = (e: React.ChangeEvent<HTMLInputElement>) => setAddress(e.target.value);

  const handleNetworkChange = (e: React.ChangeEvent<HTMLSelectElement>) => setSelectedNetwork(e.target.value);

  const renderNetworkOptions = networks.map((network) => (
    <option key={network.rpcUrl} value={network.rpcUrl}>
      {network.name}
    </option>
  ));

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
          {renderNetworkOptions}
        </select>
        <div>
          {isFetching ? (
            <p>Loading balance...</p>
          ) : (
            <p>Balance: {balance} ETH (or equivalent)</p>
          )}
          <ul>
            {transactions?.map((tx, index) => (
              <li key={index}>Transaction: {tx}</li>
            ))}
          </ul>
        </div>
      </div>
    </QueryClientProvider>
  );
};

async function fetchBalance(address: string, networkUrl: string): Promise<number> {
  return Promise.resolve(0);
}

export default WalletApp;