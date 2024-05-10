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
  type: "transaction" | "confirmation" | "alert";
  message: string;
  transaction?: Transaction;
}

const notifyUser = (walletId: string, status: WalletStatus) => {
  io.to(walletId).emit("wallet status", status);
};

io.on("connection", (socket) => {
  console.log(`User connected: ${socket.id}`);

  socket.on("register wallet", (walletId: string) => {
    console.log(`Wallet registered: ${walletId}`);
    socket.join(walletId);
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
  notifyUser(transaction.sender, {
    walletId: transaction.sender,
    type: "transaction",
    message: "Outgoing transaction sent",
    transaction,
  });

  notifyUser(transaction.receiver, {
    walletId: transaction.receiver,
    type: "transaction",
    message: "Incoming transaction received",
    transaction,
  });
}

function handleConfirmTransaction(transactionId: string) {
  console.error("Confirm transaction logic not implemented.");
}

httpServer.listen(port, () => {
  console.log(`Server running on port ${port}`);
});