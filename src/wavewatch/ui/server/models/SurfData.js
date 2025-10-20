const mongoose = require('mongoose');

const surfDataSchema = new mongoose.Schema({
  beachName: {
    type: String,
    required: true,
    trim: true
  },
  coordinates: {
    lat: { type: Number, required: true },
    lng: { type: Number, required: true }
  },
  date: {
    type: Date,
    required: true
  },
  currentConditions: {
    waveHeight: Number,
    wavePeriod: Number,
    waveDirection: Number,
    windSpeed: Number,
    windDirection: Number,
    waterTemperature: Number,
    airTemperature: Number,
    tide: Number,
    pressure: Number,
    humidity: Number,
    visibility: Number,
    cloudCover: Number,
    precipitation: Number
  },
  hourlyForecast: [{
    time: String,
    waveHeight: Number,
    wavePeriod: Number,
    windSpeed: Number,
    tide: Number,
    airTemperature: Number,
    humidity: Number,
    waterTemperature: Number
  }],
  bestSurfTimes: [{
    time: String,
    rating: Number,
    reason: String
  }],
  aiAnalysis: {
    overallRating: String,
    bestTimes: String,
    recommendations: String,
    notableChanges: String,
    oneSentenceSummary: String
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// Update the updatedAt field before saving
surfDataSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

module.exports = mongoose.model('SurfData', surfDataSchema);
