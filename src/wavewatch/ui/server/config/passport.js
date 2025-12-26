const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const User = require('../models/User');

// Only initialize Google OAuth if credentials are provided
if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
  passport.use(
    new GoogleStrategy(
      {
        clientID: process.env.GOOGLE_CLIENT_ID,
        clientSecret: process.env.GOOGLE_CLIENT_SECRET,
        callbackURL: '/api/auth/google/callback',
      },
      async (accessToken, refreshToken, profile, done) => {
        try {
          // Check if user already exists
          let user = await User.findOne({ googleId: profile.id });

          if (user) {
            // Update last login
            user.last_login = new Date();
            await user.save();
            return done(null, user);
          } else {
            // Create new user
            user = await User.create({
              googleId: profile.id,
              email: profile.emails[0].value,
              name: profile.displayName,
              picture: profile.photos[0]?.value,
            });
            return done(null, user);
          }
        } catch (error) {
          return done(error, null);
        }
      }
    )
  );
}

// Serialize user for session
passport.serializeUser((user, done) => {
  done(null, user._id);
});

// Deserialize user from session
passport.deserializeUser(async (id, done) => {
  try {
    const user = await User.findById(id);
    done(null, user);
  } catch (error) {
    done(error, null);
  }
});

module.exports = passport;

