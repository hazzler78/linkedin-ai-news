from ai_news_poster import AINewsPoster

def test_preview():
    poster = AINewsPoster()
    print(f"\nGenerating AI news post preview...")
    print("Fetching and analyzing AI news...")
    articles = poster.fetch_ai_news()
    
    if not articles:
        print("No articles found.")
        return
        
    print(f"Found and analyzed {len(articles)} articles.")
    post_content = poster.format_news_post(articles)
    
    if post_content:
        print("\nPost content preview:")
        print("-" * 50)
        print(post_content)
        print("-" * 50)
    else:
        print("Failed to format post content.")

if __name__ == "__main__":
    test_preview() 