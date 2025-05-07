from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.deepseek import DeepSeek
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler, CBEventType

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

llm = DeepSeek(model="deepseek-chat", api_key="sk-7f51479796714853b8c40fd52dc41ff5")
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

llama_debug = LlamaDebugHandler(print_trace_on_end=False)
Settings.callback_manager = CallbackManager([LlamaDebugHandler(print_trace_on_end=True)])


documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(llm=llm)
response = query_engine.query("what is the name of the candidate in the resume document?")
print(response)

llm_io_pairs = llama_debug.get_llm_inputs_outputs()
print(llm_io_pairs)
# for i, pair in enumerate(llm_io_pairs):
#     print(f"--- LLM Call #{i+1} ---")
#     print("Prompt sent to LLM:")
#     print(pair.payload["prompt"])  # The actual prompt text sent
#     print("\nLLM response:")
#     print(pair.payload["response"])  # The response text from LLM
#     print("\n")

