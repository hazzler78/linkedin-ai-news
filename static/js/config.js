const config = {
    development: {
        apiUrl: 'http://localhost:5000'
    },
    production: {
        apiUrl: 'https://linkedin-ai-news-backend.onrender.com' // This will be your Render URL
    }
};

// Determine if we're on GitHub Pages
const isGitHubPages = window.location.hostname.includes('github.io');

// Export the appropriate configuration
const currentConfig = isGitHubPages ? config.production : config.development;

export default currentConfig; 