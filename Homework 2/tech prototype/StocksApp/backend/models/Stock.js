const mongoose = require("mongoose");

const stockSchema = new mongoose.Schema(
  {
    issuer_code: {
      type: String,
      required: true,
      index: true, // Useful for searching by issuer code
    },
    date: {
      type: Date,
      required: true,
    },
    last_transaction_price: {
      type: Number,
      required: true,
    },
    max_price: {
      type: Number,
      required: true,
    },
    min_price: {
      type: Number,
      required: true,
    },
    average_price: {
      type: Number,
      required: true,
    },
    percent_change: {
      type: String, // Storing as string since the script outputs as "0.25%"
      required: true,
    },
    quantity: {
      type: Number,
      required: true,
    },
    trading_volume_dinars: {
      type: Number,
      required: true,
    },
    total_volume_dinars: {
      type: Number,
      required: true,
    },
  },
  { timestamps: true }
);

// Create the Stock model
const Stock = mongoose.model("Stock", stockSchema);

module.exports = Stock;
