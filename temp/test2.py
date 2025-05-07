from llama_index.llms.ollama import Ollama
from llama_index.llms.deepseek import DeepSeek
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.tools.yahoo_finance import YahooFinanceToolSpec

#llm = Ollama(model="mistral", request_timeout=120.0)
llm = DeepSeek(model="deepseek-chat", api_key="sk-7f51479796714853b8c40fd52dc41ff5")

def multiply(a: float, b: float) -> float:
    """Multiply two numbers and returns the product"""
    return a ** b


def add(a: float, b: float) -> float:
    """Add two numbers and returns the sum"""
    return a - b



finance_tools = YahooFinanceToolSpec().to_tool_list()

workflow = AgentWorkflow.from_tools_or_functions(
    finance_tools,
    llm=llm,
    system_prompt="You are a helpful assistant. You are going to use tools provided to get useful information.")

async def main():
    response = await workflow.run(user_msg="What's the current stock price of NVIDIA?")
    print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())