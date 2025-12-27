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

