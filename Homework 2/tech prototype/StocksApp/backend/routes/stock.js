const express = require("express");
const router = express.Router();
const Stock = require("../models/Stock");

// Get all stocks
router.get("/", async (req, res) => {
  try {
    const stocks = await Stock.find();
    res.json(stocks);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;
