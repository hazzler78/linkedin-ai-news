# LinkedIn AI News Poster

A modern web application that automatically posts AI-related news updates to your LinkedIn profile. Stay ahead of the curve with daily AI news updates and maintain an active professional presence.

## Features

- 🔄 Automated daily AI news updates
- 🎯 Smart content filtering
- ⏰ Customizable posting schedule
- 🔒 Secure API integration
- 📊 Analytics dashboard
- 📱 Responsive design

## Getting Started

### Prerequisites

- Python 3.8 or higher
- LinkedIn Developer Account
- NewsAPI key
- Node.js and npm (for development)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/hazzler78/linkedin-ai-news.git
cd linkedin-ai-news
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
NEWS_API_KEY=your_news_api_key
```

4. Configure LinkedIn OAuth:
- Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
- Create a new app
- Add the required OAuth 2.0 scopes:
  - `r_liteprofile`
  - `r_emailaddress`
  - `w_member_social`

### Usage

1. Start the application:
```bash
python app.py
```

2. Access the web interface at `http://localhost:5000`

3. Log in with your LinkedIn account

4. Configure your preferences:
   - Posting schedule
   - Content filters
   - Notification settings

## Landing Page

The project includes a modern landing page with:

- Responsive design
- Interactive chatbot
- Feature highlights
- How it works section
- Pricing plans
- Newsletter subscription
- Contact form

Visit the landing page at: [https://hazzler78.github.io/linkedin-ai-news/](https://hazzler78.github.io/linkedin-ai-news/)

## Development

### Project Structure

```
linkedin-ai-news/
├── app.py              # Main application file
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── static/            # Static assets
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── script.js
│   └── images/
├── templates/         # HTML templates
│   └── index.html
└── utils/            # Utility functions
    ├── linkedin.py
    └── news.py
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LinkedIn API](https://developer.linkedin.com/)
- [NewsAPI](https://newsapi.org/)
- [Font Awesome](https://fontawesome.com/)
- [Formspree](https://formspree.io/)

## Support

For support, email support@linkedinainews.com or join our [Discord community](https://discord.gg/linkedinainews).

## Roadmap

- [ ] AI-powered content curation
- [ ] Multi-platform support (Twitter, Facebook)
- [ ] Advanced analytics dashboard
- [ ] Custom content templates
- [ ] API rate limiting optimization
- [ ] Automated content scheduling
- [ ] Social media engagement tracking
- [ ] Content performance analytics

## Authors

- Mikael Söderberg - Initial work - [hazzler78](https://github.com/hazzler78)

## Version History

- 1.0.0
  - Initial release
  - Basic LinkedIn integration
  - News API integration
  - Web interface 