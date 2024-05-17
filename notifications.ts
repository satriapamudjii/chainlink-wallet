import { Server } from "socket.io";
import { createServer } from "http";
import { Transaction, verifyTransaction } from "./transaction";
import dotenv from "dotenv";

dotenv.config();

const port = process.env.PORT || 3000;
const httpServer = createServer();
const socketServer = new Server(httpServer, {
  cors: {
    origin: "*",
  },
});

interface WalletNotification {
  walletId: string;
  notificationType: "transaction" | "confirmation" | "alert" | "balanceUpdate" | "transactionFee";
  message: string;
  transactionDetails?: Transaction;
  updatedBalance?: number;
  transactionFee?: number;
}

const walletBalances: Record<string, number> = {};

const sendWalletNotification = (walletId: string, notification: WalletNotification) => {
  socketServer.to(walletId).emit("wallet notification", notification);
};

socketServer.on("connection", (socket) => {
  console.log(`User connected: ${socket.id}`);

  socket.on("register wallet", (walletId: string) => {
    console.log(`Wallet registered: ${walletId}`);
    socket.join(walletId);

    if (!(walletId in walletBalances)) {
      walletBalances[walletId] = 1000; // assigning a demo initial balance
      informBalanceChange(walletId, walletBalances[walletId]);
    }
  });

  socket.on("send transaction", (transaction: Transaction) => {
    executeTransaction(transaction);
  });

  socket.on("confirm transaction", (transactionId: string) => {
    confirmTransaction(transactionId);
  });
});

function calculateTransactionFee(amount: number): number {
  return amount * 0.01; // Example: 1% of the transaction amount
}

function executeTransaction(transaction: Transaction) {
  const isTransactionValid = verifyTransaction(transaction);
  if (isTransactionValid) {
    const transactionFee = calculateTransactionFee(transaction.amount);
    transaction.amount -= transactionFee; // Subtracting the transaction fee from the amount sent

    processTransactionSuccessfully(transaction, transactionFee);
  } else {
    sendWalletNotification(transaction.sender, {
      walletId: transaction.sender,
      notificationType: "alert",
      message: "Transaction verification failed",
    });
  }
}

function processTransactionSuccessfully(transaction: Transaction, transactionFee: number) {
  walletBalances[transaction.sender] -= transaction.amount + transactionFee;
  walletBalances[transaction.receiver] = (walletBalances[transaction.receiver] || 0) + transaction.amount;
  
  sendWalletNotification(transaction.sender, {
    walletId: transaction.sender,
    notificationType: "transaction",
    message: "Outgoing transaction sent",
    transactionDetails: transaction,
    transactionFee: transactionFee,
  });
  informBalanceChange(transaction.sender, walletBalances[transaction.sender]);

  sendWalletNotification(transaction.receiver, {
    walletId: transaction.receiver,
    notificationType: "transaction",
    message: "Incoming transaction received",
    transactionDetails: transaction,
  });
  informBalanceChange(transaction.receiver, walletBalances[transaction.receiver]);
}

function confirmTransaction(transactionId: string) {
  console.error("Confirm transaction logic not implemented.");
}

function informBalanceChange(walletId: string, newBalance: number) {
  sendWalletNotification(walletId, {
    walletId: walletId,
    notificationType: "balanceUpdate",
    message: `Your new balance is ${newBalance}`,
    updatedBalance: newBalance,
  });
}

httpServer.listen(port, () => {
  console.log(`Server running on port ${port}`);
});