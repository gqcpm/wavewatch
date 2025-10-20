# MongoDB Setup for Future User Accounts

## When to Add MongoDB Back

Add MongoDB when you need:
- 👤 User authentication and accounts
- 💾 User-specific data (favorite beaches, preferences)
- 📊 Analytics and user behavior tracking
- 🔄 Real-time updates to multiple users

## Quick Setup

1. **Install MongoDB:**
   ```bash
   # macOS
   brew install mongodb-community
   brew services start mongodb-community
   
   # Or use MongoDB Atlas (cloud)
   ```

2. **Uncomment in server.js:**
   ```javascript
   const mongoose = require('mongoose');
   const dotenv = require('dotenv');
   dotenv.config();
   
   // MongoDB connection code
   ```

3. **Add to package.json:**
   ```json
   "mongoose": "^8.0.3",
   "dotenv": "^16.3.1"
   ```

4. **Create .env file:**
   ```
   MONGODB_URI=mongodb://localhost:27017/wavewatch
   ```

## Models to Create

- `User.js` - User accounts and authentication
- `FavoriteBeach.js` - User's saved beaches
- `SurfSession.js` - User's surf logs
- `Analytics.js` - Usage statistics

## Current Architecture

```
React (3000) → Express (5001) → Python FastAPI (8001) → APIs
```

## Future Architecture

```
React (3000) → Express (5001) → MongoDB (27017)
                    ↓
              Python FastAPI (8001) → APIs
```

## Benefits of Adding MongoDB

- ✅ User accounts and authentication
- ✅ Personalized surf data
- ✅ User preferences and favorites
- ✅ Analytics and insights
- ✅ Multi-user support
- ✅ Data persistence
