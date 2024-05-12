import { Server } from "socket.io";
import { createServer } from "http";
import { Transaction, verifyTransaction } from "./transaction";
import dotenv from "dotenv";

dotenv.config();

const port = process.env.PORT || 3000;
const httpServer = createServer();
const io = new Server(httpServer, {
  cors: {
    origin: "*",
  },
});

interface WalletStatus {
  walletId: string;
  type: "transaction" | "confirmation" | "alert" | "balanceUpdate";
  message: string;
  transaction?: Transaction;
  balance?: number; // Added to update users about their new balance
}

const walletBalances: Record<string, number> = {};

const notifyUser = (walletId: string, status: WalletStatus) => {
  io.to(walletId).emit("wallet status", status);
};

io.on("connection", (socket) => {
  console.log(`User connected: ${socket.id}`);

  socket.on("register wallet", (walletId: string) => {
    console.log(`Wallet registered: ${walletId}`);
    socket.join(walletId);

    if (!(walletId in walletBalances)) {
      walletBalances[walletId] = 1000; // assigning a demo initial balance
      notifyBalanceChange(walletId, walletBalances[walletId]);
    }
  });

  socket.on("send transaction", (transaction: Transaction) => {
    handleSendTransaction(transaction);
  });

  socket.on("confirm transaction", (transactionId: string) => {
    handleConfirmTransaction(transactionId);
  });
});

function handleSendTransaction(transaction: Transaction) {
  const isValid = verifyTransaction(transaction);
  if (isValid) {
    processValidTransaction(transaction);
  } else {
    notifyUser(transaction.sender, {
      walletId: transaction.sender,
      type: "alert",
      message: "Transaction verification failed",
    });
  }
}

function processValidTransaction(transaction: Transaction) {
  walletBalances[transaction.sender] -= transaction.amount;
  walletBalances[transaction.receiver] = (walletBalances[transaction.receiver] || 0) + transaction.amount;
  
  notifyUser(transaction.sender, {
    walletId: transaction.sender,
    type: "transaction",
    message: "Outgoing transaction sent",
    transaction,
  });
  notifyBalanceChange(transaction.sender, walletBalances[transaction.sender]);

  notifyUser(transaction.receiver, {
    walletId: transaction.receiver,
    type: "transaction",
    message: "Incoming transaction received",
    transaction,
  });
  notifyBalanceChange(transaction.receiver, walletBalances[transaction.receiver]);
}

function handleConfirmTransaction(transactionId: string) {
  console.error("Confirm transaction logic not implemented.");
}

function notifyBalanceChange(walletId: string, balance: number) {
  notifyUser(walletId, {
    walletId: walletId,
    type: "balanceUpdate",
    message: `Your new balance is ${balance}`,
    balance,
  });
}

httpServer.listen(port, () => {
  console.log(`Server running on port ${port}`);
});