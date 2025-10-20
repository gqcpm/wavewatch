const express = require('express');
const router = express.Router();
const SurfData = require('../models/SurfData');

// Get surf data for a specific beach and date
router.get('/:beachName/:date', async (req, res) => {
  try {
    const { beachName, date } = req.params;
    
    const surfData = await SurfData.findOne({
      beachName: beachName.toLowerCase(),
      date: new Date(date)
    });
    
    if (!surfData) {
      return res.status(404).json({ message: 'No surf data found for this beach and date' });
    }
    
    res.json(surfData);
  } catch (error) {
    console.error('Error fetching surf data:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get all surf data for a beach
router.get('/:beachName', async (req, res) => {
  try {
    const { beachName } = req.params;
    const { limit = 10 } = req.query;
    
    const surfData = await SurfData.find({
      beachName: beachName.toLowerCase()
    })
    .sort({ date: -1 })
    .limit(parseInt(limit));
    
    res.json(surfData);
  } catch (error) {
    console.error('Error fetching surf data:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Create new surf data
router.post('/', async (req, res) => {
  try {
    const surfData = new SurfData(req.body);
    await surfData.save();
    
    res.status(201).json(surfData);
  } catch (error) {
    console.error('Error creating surf data:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Update surf data
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const surfData = await SurfData.findByIdAndUpdate(
      id,
      req.body,
      { new: true, runValidators: true }
    );
    
    if (!surfData) {
      return res.status(404).json({ message: 'Surf data not found' });
    }
    
    res.json(surfData);
  } catch (error) {
    console.error('Error updating surf data:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Delete surf data
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const surfData = await SurfData.findByIdAndDelete(id);
    
    if (!surfData) {
      return res.status(404).json({ message: 'Surf data not found' });
    }
    
    res.json({ message: 'Surf data deleted successfully' });
  } catch (error) {
    console.error('Error deleting surf data:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
