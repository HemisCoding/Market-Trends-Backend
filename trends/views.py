import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
import yfinance as yf
from bs4 import BeautifulSoup
import csv
import pandas as pd
from .utils.scrape_news_articles import scrape_news_articles
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "siebert/sentiment-roberta-large-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

logger = logging.getLogger(__name__)

class StockNewsViewSet(viewsets.ViewSet):
    def create(self, request):
        print('Sentiment Score')
        logger.debug("Received request with data: %s", request.data)
        ticker_symbol = request.data.get('ticker')
        if not ticker_symbol:
            logger.error("Ticker symbol is missing.")
            return Response({"error": "Ticker symbol is required."}, status=status.HTTP_400_BAD_REQUEST)

        ticker = yf.Ticker(ticker_symbol)
        news_data = ticker.news
        if not news_data:
            logger.error("No news data found for ticker: %s", ticker_symbol)
            return Response({"error": "No news data found for the provided ticker."}, status=status.HTTP_404_NOT_FOUND)

        try:
            scraped_news = scrape_news_articles(news_data)
            contents = [news['content'] for news in scraped_news]
            encoding = tokenizer(contents, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = model(**encoding)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_classes = predictions.argmax(dim=1).tolist()
            # Combine news with their predicted sentiment
            for news, sentiment in zip(scraped_news, predicted_classes):
                news['sentiment'] = 'positive' if sentiment == 1 else 'negative'
                # print(news)  
            # df = pd.DataFrame(scraped_news)
            # df.to_csv('news_sentiment.csv')
            positive_news = sum(1 for news in scraped_news if news['sentiment']=='positive')
            total_news = len(scraped_news)
            sentiment_score = (positive_news / total_news) * 100 if total_news > 0 else 0
            return Response({'news': scraped_news, 'sentiment_score': sentiment_score}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Error while scraping news articles")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AveragePricesGraph(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        ticker_symbol = pk
        print('Average Prices')
        if not ticker_symbol:
            logger.error("Ticker symbol is missing.")
            return Response({"error": "Ticker symbol is required."}, status=status.HTTP_400_BAD_REQUEST)

        ticker = yf.Ticker(ticker_symbol)
        try:
            historical_data = ticker.history(period="max")
            # Filter data from 2010 onwards and calculate yearly averages
            historical_data = historical_data['2010':]
            yearly_averages = historical_data['Close'].resample('Y').mean()

            # Format the results for JSON response
            average_prices = {year.strftime('%Y'): price for year, price in yearly_averages.items()}
            print('aveerages', average_prices)
            return Response(average_prices, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompanyDescription(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        ticker_symbol = pk
        print('Average Prices')
        if not ticker_symbol:
            logger.error("Ticker symbol is missing.")
            return Response({"error": "Ticker symbol is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        ticker = yf.Ticker(ticker_symbol)
        try:
            company_info = ticker.info
            company_description = company_info.get('longBusinessSummary', 'Description not available')
            return Response(company_description, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FinancialMetricsViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        ticker_symbol = pk
        if not ticker_symbol:
            return Response({"error": "Ticker symbol is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        ticker = yf.Ticker(ticker_symbol)
        try:
            info = ticker.info
            financial_data = {
                "marketCap": info.get("marketCap"),
                "peRatio": info.get("trailingPE"),
                "fwRatio": info.get("forwardPE"),
                "dividendYield": info.get("dividendYield") * 100 if info.get("dividendYield") else None,
                "eps": info.get("epsTrailingTwelveMonths"),
                "grossProfit": info.get("grossProfits"),
                "ebitda": info.get("ebitda"),
                "revenue": info.get("totalRevenue"),
                "netIncome": info.get("netIncomeToCommon"),
            }
            return Response(financial_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @csrf_exempt
# def get_restaurant_data(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         location_query = data.get('location')
#         search_type = data.get('search_type')
#         api_key = "887fe402e504098b1883712d47029f9e5f77f0a2449a67dd787f787ec9f0fb18"  # Your actual SerpAPI key
#         base_url = "https://serpapi.com/search.json"

#         params = {
#             "engine": "google_maps",
#             "q": f"{search_type} in {location_query}",
#             "type": "search",
#             "api_key": api_key
#         }

#         response = requests.get(base_url, params=params)

#         if response.status_code == 200:
#             return JsonResponse(response.json(), safe=False)
#         else:
#             return JsonResponse({"error": f"Received status code {response.status_code}"})

#     return JsonResponse({"error": "Invalid request method"}, status=400)
