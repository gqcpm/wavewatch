const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const dotenv = require('dotenv');

// Load environment variables from project root
dotenv.config({ path: '../../../../.env' });

// Import models
const SurfData = require('./models/SurfData');

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/wavewatch';
mongoose.connect(MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('✅ MongoDB connected successfully'))
.catch(err => console.error('❌ MongoDB connection error:', err));

// API Routes for caching surf data
app.get('/api/surf/:beach/:date', async (req, res) => {
  try {
    const { beach, date } = req.params;
    
    // Check if data exists in MongoDB
    const surfData = await SurfData.findOne({ 
      beach_name: beach.toLowerCase(), 
      date: date 
    });
    
    if (surfData) {
      console.log('📦 Returning cached data from MongoDB');
      return res.json(surfData);
    }
    
    // If not found, return null (frontend will fetch from Python API)
    res.json(null);
    
  } catch (error) {
    console.error('Error fetching surf data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Store surf data in MongoDB
app.post('/api/surf', async (req, res) => {
  try {
    const surfData = new SurfData(req.body);
    await surfData.save();
    console.log('💾 Saved surf data to MongoDB');
    res.json({ success: true, id: surfData._id });
  } catch (error) {
    console.error('Error saving surf data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Basic route
app.get('/', (req, res) => {
  res.json({ 
    message: '🌊 WaveWatch Express Server is running!',
    note: 'This server now caches surf data in MongoDB',
    mongodb: 'MongoDB connected for caching surf data and AI responses'
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ message: 'Something went wrong!' });
});

app.listen(PORT, () => {
  console.log(`🚀 Express server running on port ${PORT}`);
  console.log(`📡 Surf data comes from Python FastAPI on port 8001`);
  console.log(`🗄️ MongoDB connected for caching surf data and AI responses`);
  console.log(`💾 Cache expires after 24 hours`);
});
