import re
import asyncio
import json
from typing import Tuple
from utils.companyCompleter import CompanyInput
from utils.newsUtil import get_past_news
from utils.finUtil import get_stock_prices, get_company_list, format_stock_event_string, save_stock_event_to_cache, format_stock_event_string_to_table
from utils.timeUtil import find_workdays
from llama_index.llms.deepseek import DeepSeek
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.agent.workflow import (
    AgentOutput,
    ToolCall,
    ToolCallResult,
)
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
    logger.info(f"Saving stock events to context")

    stockEventsDict = json.loads(stockEvents)
    if(stockEventsDict['stock_total_events'] == 0):
        print(f"Failed to find any news, please check logs for more details.")
        return "No stock events found."
    
    current_state = await ctx.get("state")
    if "stock_events" not in current_state:
        current_state["stock_events"] = ""

    current_state["stock_events"] = stockEvents
    await ctx.set("state", current_state)
    return "Stock events saved."
    


async def myWorkFlow(systemPromt, formatPrompt, cachePrompt, llm, toolList):
    #check if user query hit cache:
    keyGenerator = StockNewsKeyGenerator()
    stockNewsCache = CacheUtil(100, 'data/stockNewsCache.json', keyGenerator)
    await stockNewsCache.load_cache()
    queryResult = await stockNewsCache.get(companyTicker, pastDays)
    if(queryResult != None):
        logger.info(f"Found stock news in cache by: {companyTicker}, {pastDays}")
        format_stock_event_string_to_table(queryResult)
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
        tools=[format_stock_event_string]
    )

    cache_event_agent = FunctionAgent(
        name="CacheEventAgent",
        description="Useful for saving the stock price change related news to a cache file",
        system_prompt=cachePrompt,
        llm=llm,
        tools=[save_stock_event_to_cache]
    )

    agent_workflow = AgentWorkflow(
        agents=[stock_event_agent, event_format_agent, cache_event_agent],
        root_agent=stock_event_agent.name,
        initial_state={
            "stock_events": ""
        }
    )

    handler = agent_workflow.run(user_msg="Show me stock price change related news")

    #To enable debug logging, set logging level to DEBUG in utils/logUtil.py. It's very useful to hunt down bugs:
    current_agent = None
    async for event in handler.stream_events():
        if (
            hasattr(event, "current_agent_name")
            and event.current_agent_name != current_agent
        ):
            current_agent = event.current_agent_name
            logger.debug(f"{'='*50}")
            logger.debug(f"🤖 Agent: {current_agent}")
            logger.debug(f"{'='*50}\n")
        elif isinstance(event, AgentOutput):
            if event.response.content:
                logger.debug(f"📤 Output: {event.response.content}")
            if event.tool_calls:
                logger.debug(f"🛠️  Planning to use tools: {[call.tool_name for call in event.tool_calls]}")
        elif isinstance(event, ToolCallResult):
            logger.debug(f"🔧 Tool Result ({event.tool_name}) Arguments: ({event.tool_kwargs}) Output: {event.tool_output}")
        elif isinstance(event, ToolCall):
            logger.debug(f"🔨 Calling Tool: ({event.tool_name}) With arguments: {event.tool_kwargs}")
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