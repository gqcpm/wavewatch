const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const dotenv = require('dotenv');
const session = require('express-session');

// Load environment variables from project root FIRST, before requiring passport
dotenv.config({ path: '../../../../.env' });

const passport = require('./config/passport');

// Import models
const SurfData = require('./models/SurfData');

// Import routes
const authRoutes = require('./routes/auth');

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(
  cors({
    origin: process.env.CLIENT_URL || 'http://localhost:3000',
    credentials: true,
  })
);
app.use(express.json());

// Session configuration
if (!process.env.SESSION_SECRET && process.env.NODE_ENV === 'production') {
  throw new Error('SESSION_SECRET must be set in production');
}

app.use(
  session({
    secret: process.env.SESSION_SECRET || 'dev-secret-change-in-production',
    resave: false,
    saveUninitialized: false,
    cookie: {
      secure: process.env.NODE_ENV === 'production',
      httpOnly: true,
      maxAge: 24 * 60 * 60 * 1000, // 24 hours
    },
  })
);

// Initialize Passport
app.use(passport.initialize());
app.use(passport.session());

// MongoDB Connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/wavewatch';
mongoose
  .connect(MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => {
    if (process.env.NODE_ENV !== 'production') {
      console.log('MongoDB connected');
    }
  })
  .catch(err => console.error('MongoDB connection error:', err));

// API Routes for caching surf data
app.get('/api/surf/:beach/:date', async (req, res) => {
  try {
    // Check if MongoDB is connected
    if (mongoose.connection.readyState !== 1) {
      return res.json(null); // MongoDB not connected, return null to fetch fresh
    }

    const { beach, date } = req.params;

    // Check if data exists in MongoDB
    const surfData = await SurfData.findOne({
      beach_name: beach.toLowerCase(),
      date: date,
    });

    if (surfData) {
      return res.json(surfData);
    }

    // If not found, return null (frontend will fetch from Python API)
    res.json(null);
  } catch (error) {
    if (process.env.NODE_ENV !== 'production') {
      console.error('Error fetching surf data:', error.message);
    }
    res.json(null);
  }
});

// Store surf data in MongoDB
app.post('/api/surf', async (req, res) => {
  try {
    // Check if MongoDB is connected
    if (mongoose.connection.readyState !== 1) {
      return res.json({ success: false, message: 'MongoDB not connected' });
    }

    const surfData = new SurfData(req.body);
    await surfData.save();
    res.json({ success: true, id: surfData._id });
  } catch (error) {
    if (process.env.NODE_ENV !== 'production') {
      console.error('Error saving surf data:', error.message);
    }
    res.json({ success: false, message: 'Failed to save data' });
  }
});

// Authentication routes
app.use('/api/auth', authRoutes);

// Basic route
app.get('/', (req, res) => {
  res.json({ status: 'ok' });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Error handling middleware
app.use((err, req, res, _next) => {
  if (process.env.NODE_ENV !== 'production') {
    console.error(err.stack);
  }
  res.status(500).json({ message: 'Internal server error' });
});

app.listen(PORT, () => {
  if (process.env.NODE_ENV !== 'production') {
    console.log(`Server running on port ${PORT}`);
  }
});
