const config = {
    development: {
        apiUrl: 'http://localhost:5000'
    },
    production: {
        apiUrl: 'https://linkedin-ai-news-backend.onrender.com'
    }
};

// Determine if we're in production (either GitHub Pages or Render)
const isProduction = window.location.hostname.includes('github.io') || 
                    window.location.hostname.includes('onrender.com');

// Export the appropriate configuration
const currentConfig = isProduction ? config.production : config.development;

export default currentConfig; 