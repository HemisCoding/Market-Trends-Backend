from bs4 import BeautifulSoup
import requests
import csv

def scrape_news_articles(news_data):
        """
        Scrapes content from news article URLs found in the fetched data.
        """
        articles = []
        headers = {'User-Agent': 'Mozilla/5.0'}
        content_tags = ['div.caas-body', 'div.morpheusGridBody', 'article', 'div#main-content']

        for news_item in news_data:
            url = news_item['link']
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raises HTTPError for bad responses
                soup = BeautifulSoup(response.content, 'html.parser')
                content = None

                for tag in content_tags:
                    content = soup.select_one(tag)
                    if content:
                        break

                if content:
                    articles.append({
                        'title': news_item['title'],
                        'content': content.get_text(separator=' ', strip=True),
                        'link': url,
                        'publisher': news_item.get('publisher', 'Unknown')
                    })
                else:
                    articles.append({
                        'title': news_item['title'],
                        'content': 'Content not found using predefined tags.',
                        'link': url,
                        'publisher': news_item.get('publisher', 'Unknown')
                    })
            except requests.exceptions.RequestException as e:
                articles.append({
                    'title': news_item['title'],
                    'content': f'Failed to retrieve the article due to an error: {str(e)}',
                    'link': url,
                    'publisher': news_item.get('publisher', 'Unknown')
                })
        # print('articles', articles)
            # Write to CSV
        with open('scraped_news_articles.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['title', 'content', 'link', 'publisher'])
            writer.writeheader()
            writer.writerows(articles)
        return articles