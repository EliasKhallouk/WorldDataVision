const express = require('express');
const cors = require('cors');
require('dotenv').config();

const countriesRoutes = require('./routes/countries');
const populationRoutes = require('./routes/population');
const metadataRoutes = require('./routes/metadata');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  next();
});

// Routes
app.use('/api/countries', countriesRoutes);
app.use('/api/population', populationRoutes);
app.use('/api/metadata', metadataRoutes);

// Route de santé
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'WorldDataVision API is running',
    timestamp: new Date().toISOString()
  });
});

// Route par défaut
app.get('/', (req, res) => {
  res.json({
    message: 'Bienvenue sur l\'API WorldDataVision',
    version: '1.0.0',
    endpoints: {
      countries: '/api/countries',
      population: '/api/population',
      metadata: '/api/metadata',
      health: '/api/health'
    }
  });
});

// Gestion des erreurs 404
app.use((req, res) => {
  res.status(404).json({ error: 'Route non trouvée' });
});

// Gestion globale des erreurs
app.use((err, req, res, next) => {
  console.error('Erreur serveur:', err.stack);
  res.status(500).json({ 
    error: 'Erreur interne du serveur',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// Démarrage du serveur
app.listen(PORT, () => {
  console.log(`🚀 Serveur démarré sur http://localhost:${PORT}`);
  console.log(`📊 API disponible sur http://localhost:${PORT}/api`);
  console.log(`💚 Environnement: ${process.env.NODE_ENV || 'development'}`);
});

module.exports = app;
