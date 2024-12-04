require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const stockRoutes = require("./routes/stock");

const app = express();
app.use(cors());
app.use(express.json());
const PORT = process.env.PORT || 5000;
// Database connection
mongoose
  .connect(process.env.MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() =>
    app.listen(PORT, () => console.log(`Server running on port ${PORT}`))
  )
  .catch((err) => console.error(err));

// Routes
app.use("/api/stocks", stockRoutes);
