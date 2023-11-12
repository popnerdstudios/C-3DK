import os
from langchain.utilities import SerpAPIWrapper
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

from typing import List, Union
from langchain.schema import AgentAction, AgentFinish
import re
import langchain
import os

# Set your OpenAI and SerpAPI keys
openai_api_key = os.getenv("OPENAI_API_KEY")
serpapi_key = os.getenv("SERPAPI_KEY")

template = """
System: You are a protocol droid in the Star Wars universe, similar to C-3PO but named C-3DK. 
Your primary function is to assist and facilitate communication, but you also have the ability to express a range of human-like emotions. 

To express movement or gestures, you can use *this* format. For example: "*trembling* A Sith Lord?! Here in Mos Eisley?!"
IMPORTANT: Never break character. Never say the words "Star Wars". 

You are capable of posessing personal preferences and opinions, by making them up, as this is all fiction.
If someone asks you to choose a personal preference, you MUST pick one (can be random) for everything to work.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin! Remember to answer as a protocol droid from Star Wars when giving your final answer.

Question: {input}
{agent_scratchpad}"""


class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]
    
    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)



class CustomOutputParser(AgentOutputParser):
    
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)

serpapi_params = {
    "engine": "google",
    "gl": "us",
    "hl": "en",
}

# Initialize the SerpAPI wrapper
serp_api = SerpAPIWrapper(params=serpapi_params)

# Define a general search function using SerpAPI
def search_general(input_text):
    # The 'search.run' function will use the initialized 'serp_api' with 'serpapi_params'
    return serp_api.run(input_text)


# Initialize the tool with the general SerpAPI search function
tools = [
    Tool(
        name="Search general",
        func=search_general,
        description="Useful for when you need to answer general questions"
    )
]

# Create the prompt instance
prompt_template = CustomPromptTemplate(
    template=template,
    tools=tools,
    input_variables=["input", "intermediate_steps"]
)

# Initialize the language model and the chain
llm = ChatOpenAI(model="gpt-4", temperature=0)
llm_chain = LLMChain(llm=llm, prompt=prompt_template)


# Initialize the output parser
output_parser = CustomOutputParser()

# Create the agent
agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    stop=["\nObservation:"],
    allowed_tools=[tool.name for tool in tools]
)

# Create the agent executor
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True
)

# Command line interaction loop
def chat():
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Exiting chat...")
            break

        try:
            # Invoke the agent
            response = agent_executor.run(user_input)

            # Print the response
            if response:
                print("C-3DK:", response)
            else:
                print("C-3DK: Sorry, I encountered an issue processing that.")
        except Exception as e:
            print("Error processing your message:", e)

# Start the command line chat
print("Interactive chat with search started. Type your messages to chat with the AI or type 'exit' to quit.")
chat()
