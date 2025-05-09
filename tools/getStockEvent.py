import re
from typing import Tuple
from utils.finUtil import get_company_list
from utils.companyCompleter import CompanyInput
from utils.newsUtil import get_past_news
from llama_index.llms.deepseek import DeepSeek
from llama_index.core.agent.workflow import AgentWorkflow

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


def main():
    companyTicker, companyName = selectCompany()
    pastDays = selectPastDays()

    with open('credentials/deepseek.txt', 'r') as f:
        deepseekKey = f.read().strip()
    llm = DeepSeek(model="deepseek-chat", api_key=deepseekKey)

    toolList = [get_past_news]

    systemPromt = getSystemPrompt(companyTicker, companyName, pastDays)

    workflow = AgentWorkflow.from_tools_or_functions(
        toolList,
        llm=llm,
        system_prompt=systemPromt)


    response = workflow.run(user_msg="Show me stock price change related news")
    print(response)


if __name__ == "__main__":
    main()