const mongoose = require('mongoose');

const surfDataSchema = new mongoose.Schema({
  beach_name: {
    type: String,
    required: true,
    lowercase: true,
    trim: true
  },
  date: {
    type: String,
    required: true
  },
  coordinates: {
    lat: Number,
    lng: Number
  },
  current_conditions: {
    wave_height: Number,
    wave_period: Number,
    wave_direction: Number,
    wind_speed: Number,
    wind_direction: Number,
    water_temperature: Number,
    air_temperature: Number,
    tide: { type: mongoose.Schema.Types.Mixed }, // Allow Number or String
    pressure: Number,
    humidity: Number,
    visibility: Number,
    cloud_cover: Number
  },
  hourly_conditions: [{
    time: String,
    wave_height: Number,
    wave_period: Number,
    wave_direction: Number,
    wind_speed: Number,
    wind_direction: Number,
    water_temperature: Number,
    air_temperature: Number,
    tide: { type: mongoose.Schema.Types.Mixed }, // Allow Number or String
    pressure: Number,
    humidity: Number,
    visibility: Number,
    cloud_cover: Number
  }],
  best_surf_times: [{
    time: String,
    wave_height: Number,
    wave_period: Number,
    wind_speed: Number,
    wind_direction: Number,
    water_temperature: Number,
    tide: { type: mongoose.Schema.Types.Mixed }, // Allow Number or String
    score: Number
  }],
  ai_analysis: {
    text: String,
    overall_rating: String,
    best_times: String,
    recommendations: String,
    notable_changes: String
  },
  one_sentence_summary: String,
  cached: {
    type: Boolean,
    default: true
  },
  created_at: {
    type: Date,
    default: Date.now
  },
  expires_at: {
    type: Date,
    default: function() {
      return new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours from now
    }
  }
});

// Index for efficient queries
surfDataSchema.index({ beach_name: 1, date: 1 });
surfDataSchema.index({ expires_at: 1 }, { expireAfterSeconds: 0 });

module.exports = mongoose.model('SurfData', surfDataSchema);
