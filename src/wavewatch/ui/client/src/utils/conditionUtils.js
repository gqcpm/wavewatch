import { theme } from '../styles/theme';

/**
 * Gets the border color for wave height based on quality
 * @param {number|string} waveHeight - Wave height in feet
 * @returns {string|null} - Hex color code or null
 */
export const getWaveHeightColor = waveHeight => {
  if (!waveHeight || waveHeight === 'N/A') return null;

  const height = parseFloat(waveHeight);

  if (height >= 2 && height <= 8) {
    return theme.colors.condition.excellent; // Good/Favorable - Olive Green
  }
  if (height >= 1 && height < 2) {
    return theme.colors.condition.moderate; // Fair/Moderate - Amber
  }
  if (height > 8) {
    return theme.colors.condition.moderate; // Fair - Large but surfable
  }
  return theme.colors.condition.poor; // Poor/Rough - Too small
};

/**
 * Gets the border color for wave period based on quality
 * @param {number|string} period - Wave period in seconds
 * @returns {string|null} - Hex color code or null
 */
export const getWavePeriodColor = period => {
  if (!period || period === 'N/A') return null;

  const p = parseFloat(period);

  if (p >= 12) {
    return theme.colors.condition.excellent; // Good/Favorable - Long period, clean waves
  }
  if (p >= 8 && p < 12) {
    return theme.colors.condition.moderate; // Fair/Moderate - Decent period
  }
  return theme.colors.condition.poor; // Poor/Rough - Short period, choppy
};

/**
 * Gets the border color for wind speed based on quality
 * @param {number|string} windSpeed - Wind speed in mph
 * @returns {string|null} - Hex color code or null
 */
export const getWindSpeedColor = windSpeed => {
  if (!windSpeed || windSpeed === 'N/A') return null;

  const speed = parseFloat(windSpeed);

  if (speed < 10) {
    return theme.colors.condition.excellent; // Good/Favorable - Light winds
  }
  if (speed >= 10 && speed < 15) {
    return theme.colors.condition.moderate; // Fair/Moderate - Moderate winds
  }
  return theme.colors.condition.poor; // Poor/Rough - Strong winds
};

/**
 * Gets the border color for wind direction based on quality
 * @param {number|string} windDirection - Wind direction in degrees
 * @param {number|string} windSpeed - Wind speed in mph
 * @returns {string|null} - Hex color code or null
 */
export const getWindDirectionColor = (windDirection, windSpeed) => {
  // Wind direction quality depends on being offshore, but we'll use a neutral approach
  // If wind speed is low, direction matters less
  if (!windSpeed || windSpeed === 'N/A' || parseFloat(windSpeed) < 5) {
    return theme.colors.condition.excellent; // Light winds are generally good regardless of direction
  }
  // For stronger winds, we'd need beach orientation to determine if offshore
  // For now, use moderate color
  return theme.colors.condition.moderate;
};

/**
 * Gets the border color for temperature based on quality
 * @param {number|string} temp - Temperature in Fahrenheit
 * @param {string} type - 'water' or 'air'
 * @returns {string|null} - Hex color code or null
 */
export const getTemperatureColor = (temp, type = 'water') => {
  if (!temp || temp === 'N/A') return null;

  const t = parseFloat(temp);

  if (type === 'water') {
    // Comfortable water temp: 60-75°F
    if (t >= 60 && t <= 75) {
      return theme.colors.condition.excellent; // Good/Favorable
    }
    if (t >= 55 && t < 60) {
      return theme.colors.condition.moderate; // Fair - Cool but manageable
    }
    if (t > 75 && t <= 80) {
      return theme.colors.condition.moderate; // Fair - Warm
    }
    return theme.colors.condition.poor; // Poor - Too cold or too hot
  } else {
    // Air temperature - less critical, but comfort matters
    if (t >= 65 && t <= 80) {
      return theme.colors.condition.excellent; // Good/Favorable
    }
    if (t >= 55 && t < 65) {
      return theme.colors.condition.moderate; // Fair
    }
    if (t > 80 && t <= 85) {
      return theme.colors.condition.moderate; // Fair
    }
    return null; // Neutral for extreme temps
  }
};
