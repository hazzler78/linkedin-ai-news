# LinkedIn AI News Poster

An automated tool that fetches the latest AI-related news and posts updates to your LinkedIn profile on a regular schedule.

## Features

- Fetches the latest AI news from NewsAPI
- Filters out stock market news and focuses on technology and innovation
- Formats news into professional LinkedIn posts
- Posts automatically to your LinkedIn profile
- Runs on a daily schedule (configurable)
- Robust error handling and automatic retries

## Prerequisites

- Python 3.7+
- LinkedIn Developer Account
- NewsAPI Account

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/linkedin-ai-news.git
cd linkedin-ai-news
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API keys:
```
# LinkedIn API Credentials
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_PERSON_ID=your_linkedin_person_id

# News API Key
NEWS_API_KEY=your_news_api_key
```

## Configuration

The script is configured to post daily at 9:00 AM by default. You can modify the schedule in `ai_news_poster.py`.

## Usage

Run the script:
```bash
python ai_news_poster.py
```

The script will:
1. Post immediately when started
2. Continue running in the background
3. Post automatically at the scheduled time (default: 9:00 AM daily)

To stop the script, press Ctrl+C.

## Getting API Keys

### LinkedIn API
1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Create a new app
3. Request the necessary permissions:
   - `w_member_social` for posting
   - `r_liteprofile` for profile info
4. Generate an access token

### NewsAPI
1. Sign up at [NewsAPI](https://newsapi.org/)
2. Get your API key from the dashboard

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [NewsAPI](https://newsapi.org/) for providing the news data
- [LinkedIn API](https://developer.linkedin.com/) for the posting functionality 