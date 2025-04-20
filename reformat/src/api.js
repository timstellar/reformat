import axios from 'axios';

// Configure Axios instance
const api = axios.create({
  baseURL: 'http://localhost:3000', // Your Flask server
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Add request interceptor for logging
api.interceptors.request.use(config => {
  console.log('Sending request to:', config.url);
  return config;
}, error => {
  return Promise.reject(error);
});

// Add response interceptor
api.interceptors.response.use(response => {
  console.log('Received response from:', response.config.url);
  return response;
}, error => {
  console.error('API Error:', error);
  return Promise.reject(error);
});

export const submitWasteRequest = async (formData) => {
  try {
    const response = await api.post('/api/parsejson', formData);
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    // Handle different error scenarios
    if (error.response) {
      // Server responded with error status (4xx, 5xx)
      return {
        success: false,
        error: error.response.data?.message || 
              `Server error: ${error.response.status} ${error.response.statusText}`
      };
    } else if (error.request) {
      // Request was made but no response received
      return {
        success: false,
        error: 'No response received from server'
      };
    } else {
      // Something happened in setting up the request
      return {
        success: false,
        error: error.message
      };
    }
  }
};

export const downloadFile = async (fileUrl) => {
    try {
      const response = await api.get(fileUrl, {
        responseType: 'blob', // Important for file downloads
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Download failed');
    }
  };

export const getFilePath = async (requestNumber) => {
    try {
      const response = await api.get(`/api/get-file-path/${encodeURIComponent(requestNumber)}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 
              `Failed to get file path: ${error.message}`
      };
    }
  };