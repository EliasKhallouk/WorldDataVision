import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// ===== COUNTRIES =====
export const getCountries = async () => {
  const response = await api.get('/countries');
  return response.data;
};

export const getCountryMapping = async () => {
  const response = await api.get('/countries/mapping/iso2-to-iso3');
  return response.data;
};

export const getCountry = async (iso3) => {
  const response = await api.get(`/countries/${iso3}`);
  return response.data;
};

export const getCountriesByRegion = async (region) => {
  const response = await api.get(`/countries/region/${region}`);
  return response.data;
};

// ===== POPULATION =====
export const getPopulationSummary = async (params = {}) => {
  const response = await api.get('/population/summary', { params });
  return response.data;
};

export const getCountryPopulation = async (iso3, params = {}) => {
  const response = await api.get(`/population/country/${iso3}`, { params });
  return response.data;
};

export const getPopulationTrend = async (iso3, params = {}) => {
  const response = await api.get(`/population/trend/${iso3}`, { params });
  return response.data;
};

export const getPopulationPyramid = async (iso3, params = {}) => {
  const response = await api.get(`/population/pyramid/${iso3}`, { params });
  return response.data;
};

// ===== METADATA =====
export const getYears = async () => {
  const response = await api.get('/metadata/years');
  return response.data;
};

export const getAgeGroups = async () => {
  const response = await api.get('/metadata/age-groups');
  return response.data;
};

export const getSexCategories = async () => {
  const response = await api.get('/metadata/sex-categories');
  return response.data;
};

export const getRegions = async () => {
  const response = await api.get('/metadata/regions');
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/metadata/stats');
  return response.data;
};

export default api;
