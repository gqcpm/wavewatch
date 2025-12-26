const express = require('express');
const passport = require('passport');
const router = express.Router();

// Check if Google OAuth is configured
const isGoogleOAuthConfigured = () => {
  return !!(process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET);
};

// Google OAuth login route
router.get('/google', (req, res, next) => {
  if (!isGoogleOAuthConfigured()) {
    return res.status(503).json({
      success: false,
      message: 'Authentication service unavailable',
    });
  }
  passport.authenticate('google', {
    scope: ['profile', 'email'],
  })(req, res, next);
});

// Google OAuth callback route
router.get(
  '/google/callback',
  (req, res, next) => {
    if (!isGoogleOAuthConfigured()) {
      return res.status(503).json({
        success: false,
        message: 'Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file.',
      });
    }
    const clientUrl = process.env.CLIENT_URL || 'http://localhost:3000';
    passport.authenticate('google', {
      failureRedirect: `${clientUrl}/login`,
      session: true,
    })(req, res, next);
  },
  (req, res) => {
    // Successful authentication, redirect to React app home page
    const clientUrl = process.env.CLIENT_URL || 'http://localhost:3000';
    res.redirect(clientUrl);
  }
);

// Get current user profile
router.get('/profile', (req, res) => {
  if (req.isAuthenticated()) {
    res.json({
      success: true,
      user: {
        id: req.user._id,
        email: req.user.email,
        name: req.user.name,
        picture: req.user.picture,
      },
    });
  } else {
    res.status(401).json({
      success: false,
      message: 'Not authenticated',
    });
  }
});

// Logout route
router.post('/logout', (req, res) => {
  req.logout((err) => {
    if (err) {
      return res.status(500).json({
        success: false,
        message: 'Error logging out',
      });
    }
    req.session.destroy((err) => {
      if (err) {
        return res.status(500).json({
          success: false,
          message: 'Error destroying session',
        });
      }
      res.clearCookie('connect.sid');
      res.json({
        success: true,
        message: 'Logged out successfully',
      });
    });
  });
});

// Check authentication status
router.get('/status', (req, res) => {
  res.json({
    authenticated: req.isAuthenticated(),
    user: req.isAuthenticated()
      ? {
          id: req.user._id,
          email: req.user.email,
          name: req.user.name,
          picture: req.user.picture,
        }
      : null,
  });
});

module.exports = router;

