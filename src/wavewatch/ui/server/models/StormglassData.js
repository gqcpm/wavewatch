const mongoose = require('mongoose');

const stormglassDataSchema = new mongoose.Schema({
  beach_name: { type: String, required: true, index: true },
  date: { type: String, required: true, index: true },
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
    pressure: Number,
    humidity: Number,
    visibility: Number,
    cloud_cover: Number
  },
  hourly_forecast: [{
    time: String,
    wave_height: Number,
    wave_period: Number,
    wave_direction: Number,
    wind_speed: Number,
    wind_direction: Number,
    water_temperature: Number,
    air_temperature: Number,
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
  cached: { type: Boolean, default: true },
  timestamp: { type: Date, default: Date.now },
  expires_at: { type: Date, default: () => new Date(Date.now() + 24 * 60 * 60 * 1000) } // 24 hours
});

// Create compound index for efficient queries
stormglassDataSchema.index({ beach_name: 1, date: 1 });

// TTL index to automatically delete expired documents
stormglassDataSchema.index({ expires_at: 1 }, { expireAfterSeconds: 0 });

module.exports = mongoose.model('StormglassData', stormglassDataSchema);
