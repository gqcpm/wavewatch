import { theme } from '../styles/theme';

/**
 * Extracts the overall surf rating (0-100) from AI analysis text
 * @param {string|object} aiAnalysis - The AI analysis text or object
 * @returns {number|null} - The rating value or null if not found
 */
export const extractOverallRating = (aiAnalysis) => {
  if (!aiAnalysis) return null;
  
  const text = typeof aiAnalysis === 'string' ? aiAnalysis : JSON.stringify(aiAnalysis);
  
  // Look for patterns like:
  // "Overall Surf Rating: 88/100" or "Overall Surf Rating:** 88/100"
  // "Rating: 88/100" or "88/100"
  const ratingPatterns = [
    /overall\s+surf\s+rating[:\*\s]*(\d{1,3})(?:\s*\/?\s*100)?/i,
    /(?:^|\n)\s*(?:overall\s+)?rating[:\*\s]*(\d{1,3})(?:\s*\/?\s*100)?/i,
    /(\d{1,3})\s*\/\s*100/,
  ];
  
  for (const pattern of ratingPatterns) {
    const match = text.match(pattern);
    if (match) {
      const rating = parseInt(match[1], 10);
      if (rating >= 0 && rating <= 100) {
        return rating;
      }
    }
  }
  
  return null;
};

/**
 * Gets the color for a given rating (0-100)
 * @param {number|null} rating - The rating value
 * @returns {string} - Hex color code
 */
export const getRatingColor = (rating) => {
  if (rating === null || rating === undefined) {
    return theme.colors.rating.unknown;
  }
  
  if (rating <= 20) return theme.colors.rating.dangerous;
  if (rating <= 40) return theme.colors.rating.poor;
  if (rating <= 60) return theme.colors.rating.fair;
  if (rating <= 80) return theme.colors.rating.good;
  return theme.colors.rating.optimal;
};

/**
 * Gets the condition label for a given rating
 * @param {number|null} rating - The rating value
 * @returns {string} - Condition label
 */
export const getConditionLabel = (rating) => {
  if (rating === null || rating === undefined) return 'Unknown';
  if (rating <= 20) return 'Dangerous/Flat';
  if (rating <= 40) return 'Poor/Rough';
  if (rating <= 60) return 'Fair/Moderate';
  if (rating <= 80) return 'Good/Favorable';
  return 'Epic/Optimal';
};

/**
 * Darkens a hex color by a specified amount
 * @param {string} hex - Hex color code
 * @param {number} amount - Amount to darken (0-1)
 * @returns {string} - Darkened hex color code
 */
const darkenColor = (hex, amount) => {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.max(0, Math.min(255, (num >> 16) - Math.round(255 * amount)));
  const g = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) - Math.round(255 * amount)));
  const b = Math.max(0, Math.min(255, (num & 0x0000FF) - Math.round(255 * amount)));
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
};

/**
 * Gets the gradient background for a rating card
 * @param {number|null} rating - The rating value
 * @returns {string} - CSS gradient string
 */
export const getRatingGradient = (rating) => {
  if (rating === null || rating === undefined) {
    return `linear-gradient(135deg, ${theme.colors.rating.unknown} 0%, ${theme.colors.rating.unknownDark} 100%)`;
  }
  
  const baseColor = getRatingColor(rating);
  return `linear-gradient(135deg, ${baseColor} 0%, ${darkenColor(baseColor, 0.1)} 100%)`;
};

/**
 * Text color constant for rating cards
 */
export const RATING_TEXT_COLOR = theme.colors.text.rating;

