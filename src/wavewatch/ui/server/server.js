const express = require('express');
const cors = require('cors');
// TODO: Add MongoDB when implementing user accounts
// const mongoose = require('mongoose');
// const dotenv = require('dotenv');

// TODO: Load environment variables when adding MongoDB
// dotenv.config();

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(cors());
app.use(express.json());

// TODO: MongoDB Connection (for future user accounts)
// const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/wavewatch';
// mongoose.connect(MONGODB_URI, {
//   useNewUrlParser: true,
//   useUnifiedTopology: true,
// })
// .then(() => console.log('✅ MongoDB connected successfully'))
// .catch(err => console.error('❌ MongoDB connection error:', err));

// TODO: Add routes when implementing user features
// app.use('/api/auth', require('./routes/auth'));
// app.use('/api/users', require('./routes/users'));

// Basic route
app.get('/', (req, res) => {
  res.json({ 
    message: '🌊 WaveWatch Express Server is running!',
    note: 'This server acts as a proxy. Surf data comes from Python FastAPI on port 8001',
    mongodb: 'MongoDB removed for simplicity. Add back when implementing user accounts.'
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
  console.log(`💡 MongoDB removed - add back when implementing user accounts`);
});
