import re
import asyncio
from typing import Tuple
from utils.companyCompleter import CompanyInput
from utils.newsUtil import get_past_news
from utils.finUtil import get_stock_prices, get_company_list, format_stock_event_string, save_stock_event_to_cache
from utils.timeUtil import find_workdays
from llama_index.llms.deepseek import DeepSeek
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context
from llama_index.core.agent.workflow import FunctionAgent
from utils.cacheUtil import CacheUtil, StockNewsKeyGenerator
from utils.logUtil import setup_logger

logger = setup_logger("getStockEvent")


MaxPastDays = 30

def cleanCompanyName(comppanyName: str) -> str:
    pattern = r'\s*(?:-\s*Class\s+[A-Za-z]+|Company|Inc|Corp|Ltd|LLC|\.?)\s*$'
    return re.sub(pattern, '', comppanyName, flags=re.IGNORECASE)


def selectCompany() -> Tuple[str, str]:
    companyList = get_company_list()
    while(True):
        companyInput = CompanyInput(companyList)
        companyOutput = companyInput.run()

        if(companyOutput == None):
            continue

        return (companyOutput[0], cleanCompanyName(companyOutput[1]))
    

def selectPastDays() -> int:
    while(True):
        userInput = input(f"How many past days you want to look up for (maximum of {MaxPastDays} days)?: ")
        if userInput.isdigit():
            if(int(userInput) <= MaxPastDays):
                return int(userInput)
        else:
            continue


def getSystemPrompt(companyTicker: str, companyName: str, pastDays: int) -> str:
    with open('prompts/getStockEvent.txt', 'r', encoding='utf-8') as file:
            content: str = file.read()

    return content.format(companyTicker=companyTicker, companyName=companyName, pastDays=pastDays) 


async def save_events(ctx: Context, stockEvents: str) -> str:
    """
    Useful for saving stock events. The events are representd in a string with json format.
    
    """
    logger.info(f"Saving stock events to context: {stockEvents}")
    
    current_state = await ctx.get("state")
    if "stock_events" not in current_state:
        current_state["stock_events"] = ""

    current_state["stock_events"] = stockEvents
    await ctx.set("state", current_state)
    return "Stock events saved."



async def get_events(ctx: Context) -> str:
    """
    Useful for getting stock events. The events are representd in a string with json format.
    
    """
    current_state = await ctx.get("state")
    if "stock_events" not in current_state:
        logger.error("No stock events found in context.")
        return ""
    
    logger.info(f"Getting stock events from context: {current_state['stock_events']}")

    return current_state["stock_events"]
    


async def myWorkFlow(systemPromt, formatPrompt, cachePrompt, llm, toolList):
    #check if user query hit cache:
    keyGenerator = StockNewsKeyGenerator()
    stockNewsCache = CacheUtil(100, 'data/stockNewsCache.json', keyGenerator)
    await stockNewsCache.load_cache()
    queryResult = await stockNewsCache.get(companyTicker, pastDays)
    if(queryResult != None):
        logger.info(f"Found stock news in cache by: {companyTicker}, {pastDays}")
        format_stock_event_string(queryResult)
        return

    stock_event_agent = FunctionAgent(
        name="StockEventAgent",
        description="Useful for searching the web for stock price change related news",
        system_prompt=systemPromt,
        llm=llm,
        tools=toolList,
        can_handoff_to=["EventFormatAgent"]
    )

    event_format_agent = FunctionAgent(
        name="EventFormatAgent",
        description="Useful for calling a tool to format the stock price change related news into a table",
        system_prompt=formatPrompt,
        llm=llm,
        tools=[get_events, format_stock_event_string]
    )

    cache_event_agent = FunctionAgent(
        name="CacheEventAgent",
        description="Useful for saving the stock price change related news to a cache file",
        system_prompt=cachePrompt,
        llm=llm,
        tools=[get_events, save_stock_event_to_cache]
    )

    agent_workflow = AgentWorkflow(
        agents=[stock_event_agent, event_format_agent, cache_event_agent],
        root_agent=stock_event_agent.name,
        initial_state={
            "stock_events": ""
        }
    )

    await agent_workflow.run(user_msg="Show me stock price change related news")
    return





if __name__ == "__main__":
    companyTicker, companyName = selectCompany()
    pastDays = selectPastDays()

    with open('credentials/deepseek.txt', 'r') as f:
        deepseekKey = f.read().strip()
    llm = DeepSeek(model="deepseek-chat", api_key=deepseekKey)

    toolList = [get_past_news, get_stock_prices, find_workdays, save_events]

    systemPromt = getSystemPrompt(companyTicker, companyName, pastDays)

    with open('prompts/formatStockEvent.txt', 'r', encoding='utf-8') as file:
        formatPrompt: str = file.read()

    with open('prompts/cacheStockEvent.txt', 'r', encoding='utf-8') as file:
        cachePrompt: str = file.read()


    asyncio.run(myWorkFlow(systemPromt, formatPrompt, cachePrompt, llm, toolList))