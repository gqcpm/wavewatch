export const theme = {
  colors: {
    // Professional surf forecast palette
    primary: '#0066CC',        // Ocean blue
    secondary: '#003D7A',     // Deep blue
    white: '#FFFFFF',
    lightGray: '#F5F7FA',
    gray: '#E1E8ED',
    darkGray: '#657786',
    black: '#14171A',
    
    text: {
      primary: '#14171A',
      secondary: '#657786',
      muted: '#AAB8C2',
      white: '#FFFFFF',
      rating: '#FFFFFF',          // White text for rating cards
    },
    
    background: {
      primary: '#FFFFFF',
      secondary: '#F5F7FA',
      tertiary: '#E1E8ED',
      dark: '#003D7A',
    },
    
    surf: {
      excellent: '#00C853',   // Green for great conditions
      good: '#4CAF50',        // Light green
      fair: '#FFC107',        // Yellow/amber
      poor: '#FF5722',        // Orange/red
    },
    
    accent: {
      blue: '#0066CC',
      lightBlue: '#4A90E2',
      teal: '#00ACC1',
      orange: '#FF6B35',
      green: '#00C853',
    },
    
    border: {
      light: '#E1E8ED',
      medium: '#AAB8C2',
      dark: '#657786',
    },
    
    // Rating color scale (0-100) - Red to Green gradient
    rating: {
      dangerous: '#B71C1C',      // Deep Red (0-20)
      poor: '#D84315',            // Orange-Brown (21-40)
      fair: '#FFD740',            // Amber/Gold (41-60)
      good: '#8BC34A',            // Olive Green (61-80)
      optimal: '#2E7D32',         // Forest Green (81-100)
      unknown: '#6B7280',         // Gray for unknown
      unknownDark: '#4B5563',     // Darker gray for gradients
    },
    
    // Condition quality colors (matching rating scale)
    condition: {
      excellent: '#8BC34A',      // Olive Green - Good/Favorable
      moderate: '#FFD740',       // Amber/Gold - Fair/Moderate
      poor: '#D84315',            // Orange-Brown - Poor/Rough
    }
  },
  
  spacing: {
    xs: '0.5rem',
    sm: '1rem',
    md: '1.5rem',
    lg: '2rem',
    xl: '3rem',
    xxl: '4rem',
  },
  
  borderRadius: {
    sm: '6px',
    md: '10px',
    lg: '16px',
    xl: '24px',
    full: '9999px',
  },
  
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px rgba(0, 0, 0, 0.07)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px rgba(0, 0, 0, 0.1)',
  },
  
  breakpoints: {
    mobile: '768px',
    tablet: '1024px',
    desktop: '1200px',
    wide: '1440px',
  },
  
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    }
  }
};

