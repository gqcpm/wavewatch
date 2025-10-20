# WaveWatch MERN Stack

A modern surf forecasting application built with MongoDB, Express.js, React, and Node.js.

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- MongoDB (local or MongoDB Atlas)
- npm or yarn

### Installation

1. **Install all dependencies:**
   ```bash
   npm run install-all
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and MongoDB URI
   ```

3. **Start the development servers:**
   ```bash
   npm run dev
   ```

This will start both the Express server (port 5000) and React client (port 3000).

## 📁 Project Structure

```
ui/
├── client/                 # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   ├── pages/         # Page components
│   │   ├── App.js         # Main app component
│   │   └── index.js       # React entry point
│   └── package.json
├── server/                # Express backend
│   ├── models/            # MongoDB models
│   ├── routes/            # API routes
│   ├── server.js          # Express server
│   └── package.json
├── package.json           # Root package.json
└── README.md
```

## 🛠️ Available Scripts

- `npm run dev` - Start both client and server in development mode
- `npm run server` - Start only the Express server
- `npm run client` - Start only the React client
- `npm run build` - Build the React app for production
- `npm run install-all` - Install dependencies for all packages

## 🔧 Features

- **Real-time surf data** from Stormglass API
- **AI-powered analysis** using Google Gemini
- **Interactive maps** with Leaflet
- **User authentication** with JWT
- **Responsive design** with styled-components
- **MongoDB integration** for data persistence

## 🌊 API Endpoints

### Surf Data
- `GET /api/surf/:beachName/:date` - Get surf data for specific beach and date
- `GET /api/surf/:beachName` - Get all surf data for a beach
- `POST /api/surf` - Create new surf data
- `PUT /api/surf/:id` - Update surf data
- `DELETE /api/surf/:id` - Delete surf data

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile

## 🎨 Styling

The app uses styled-components for CSS-in-JS styling with a modern glassmorphism design.

## 📱 Responsive Design

The application is fully responsive and works on desktop, tablet, and mobile devices.
