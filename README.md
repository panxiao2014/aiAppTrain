# 🗂️ aiAppTrain

Try to create some applications by ways of AI agent. The agent framework is [`LlamaIndex`](https://github.com/run-llama/llama_index).

## 🚀 Overview

I am trying to create some useful apps which are using AI agent technology. The 'usefulness' of an app is based on two things:

1. The available tools which LLM can utilize.

2. The power of a LLM model.

So there are some limitations of the AI apps that I created:

1. I used some API services to get useful data. Since I only use free versions of these services, there are limitation on requests per day or content length of returned data.

2. LLM is not perfect, it would make inaccurate conclusion or not strictly follow the prompt.

These limitations could be solved by using paid API service, keep improving prompts, or waiting to use new version of LLM model. DO NOT rely on these tools for reliable response but we can always learn from the code implementation.

## 🔧 Preparation

This application needs to access some of the API services. You need to apply each of the key to access the service. In folder *credentials*, create a txt file for each of the service, and put the key string to the file. Current needed files:

alpha.vantage.txt: [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)

finnhub.txt: [https://finnhub.io/dashboard](https://finnhub.io/dashboard)

newsapi.txt: [https://newsapi.org/account](https://newsapi.org/account)

deepseek.txt: [https://platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys)

I use DeepSeek as the LLM, you can choose any other model.

## 💻 getStockEvent

`python tools/getStockEvent.py`

This application let user choose a company by its name or stock symbol, then specify a number as the days. The application will search all company related news within that past days, sift out any news that are relevant to stock price change. It will then get the stock price before and after that event happened. This application helps people understand how an event will affect a company's stock price.

(*Note: the maximum days to look for is 30 days due to limitation of free API service.)