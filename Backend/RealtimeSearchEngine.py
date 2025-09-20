import datetime
import os
import re
import json
from groq import Groq, APIError
from dotenv import dotenv_values
import yfinance as yf
from tavily import TavilyClient

try:
    env_vars = dotenv_values(".env")
    Username = env_vars.get("Username", "User")
    Assistantname = env_vars.get("Assistantname", "J.A.R.V.I.S")
    GroqAPIKey = env_vars.get("GroqAPIKey")
    TavilyAPIKey = env_vars.get("TavilyAPIKey")
    ChatlogFile = r"Data\ChatLog.json"
    
    if not GroqAPIKey or not TavilyAPIKey:
        raise ValueError("An API key is missing from your .env file.")
    
except Exception as e:
    print(f"Configuration Error: {e}")
    exit()

client = Groq(api_key=GroqAPIKey)
tavily = TavilyClient(api_key=TavilyAPIKey)

SystemPrompt = f"""You are {Assistantname}, a world-class AI research assistant for {Username}. Your primary function is to provide accurate, real-time answers by synthesizing information from the web.

Instructions:
1. You will be given a user's query and a context containing search results from the internet.
2. Carefully analyze the provided context to form a comprehensive, professional, and accurate answer.
3. Your answer MUST be based on the real-time information provided in the context. Do not rely on your internal knowledge.
4. If the context is insufficient, clearly state that you could not find a definitive answer from the search results.
"""

def get_stock_price(query: str) -> str:
    match = re.search(r"stock price of\s+([a-zA-Z\s]+)", query, re.IGNORECASE)
    if not match:
        return None
    
    company_name = match.group(1).strip()
    print(f"Identified company for stock price lookup: '{company_name}'")
    
    ticker_map = {"apple": "AAPL", "google": "GOOGL", "microsoft": "MSFT", "tesla": "TSLA", "amazon": "AMZN"}
    ticker = ticker_map.get(company_name.lower())
    
    if not ticker: return f"Unknown company: {company_name}"
    
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return f"The current stock price for {company_name.capitalize()} ({ticker}) is ${price:.2f}."
    except Exception as e:
        return f"Error fetching stock data for {company_name}: {e}"
    
def load_chat_history() -> list:
    try:
        if not os.path.exists(ChatlogFile):
            with open(ChatlogFile, "w") as f:
                json.dump([], f)
                return []
        with open(ChatlogFile, "r", encoding='utf-8') as f:
            return json.load(f)
    
    except (json.JSONDecodeError, FileNotFoundError):
        return []
    
def save_chat_history(messages: list):
    try:
        with open(ChatlogFile, "w", encoding='utf-8') as f:
            json.dump(messages, f, indent=4)
        
    except Exception as e:
        print(f"Error saving chat log: {e}")
    
    
def RealtimeSearchEngine(prompt: str) -> str:
    
    # Check for specialized queries first
    stock_price = get_stock_price(prompt)
    if stock_price:
        return stock_price
    
    # USe tavily for deep search
    print(f"Performing Deep Search for: '{prompt}'")
    try:
        context = tavily.search(query=prompt, search_depth="advanced")
        scraped_content = "\n".join([c["content"] for c in context["results"]])
        
    except Exception as e:
        return f"Error during Deep Search: {e}"
    
    # Augment the prompt and send to LLm
    messages = [
        {"role": "system", "content": SystemPrompt},
        {"role": "user", "content": f"Based on the following real-time web content, please answer this query: '{prompt}'\n\n### Search Results Context:\n{scraped_content}"}
    ]
    
    Answer = ""
    try:
        print("Synthesizing answer from web content...")
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
            stream=True,
    )
    
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.strip().replace("</s>", "")
        
    except APIError as e:
        return f"Groq API Error: {e}"
    except Exception as e:
        return f"An Unexpected error occurred: {e}"
    
    chat_history = load_chat_history()
    chat_history.append({"role": "user", "content": prompt})
    if Answer:
        chat_history.append({"role": "assistant", "content": Answer})
    save_chat_history(chat_history)
    
    return Answer.strip()

if __name__ == "__main__":
    while True:
        prompt_input = input(f"{Username}: ")
        if prompt_input.lower() in ["exit", "quit"]:
            break
        response = RealtimeSearchEngine(prompt_input)
        print(f"\n{Assistantname}: {response}\n")
