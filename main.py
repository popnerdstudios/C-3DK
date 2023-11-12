import os
from langchain.llms import OpenAI
from langchain.utilities import SerpAPIWrapper
from langchain.agents import Tool, AgentExecutor, initialize_agent, AgentType
from langchain.prompts import ChatPromptTemplate
from langchain.agents.output_parsers import SelfAskOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain import hub

# Assuming the SerpAPI key is set as an environment variable
os.environ["SERPAPI_KEY"] = "your-serpapi-key"

# Initialize the language model and SerpAPI wrapper
llm = OpenAI(temperature=0)
search = SerpAPIWrapper()

# Define the search tool with SerpAPI
tools = [
    Tool(
        name="Intermediate Answer",
        func=search.run,
        description="useful for when you need to ask with search",
    )
]

# Pull the prompt from the LangChain hub
prompt = hub.pull("hwchase17/self-ask-with-search")

# Bind stopping conditions to the LLM if necessary
llm_with_stop = llm.bind(stop=["\nIntermediate answer:"])

# Define the agent using LCEL
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_str(
            x["intermediate_steps"],
            observation_prefix="\nIntermediate answer: ",
            llm_prefix="",
        ),
    }
    | prompt
    | llm_with_stop
    | SelfAskOutputParser()
)

# Create an AgentExecutor to manage the agent's execution
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Invoke the agent with a question
agent_executor.invoke(
    {"input": "What is the hometown of the reigning men's U.S. Open champion?"}
)
