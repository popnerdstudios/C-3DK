from dotenv import load_dotenv
import os
import re

from langchain import hub
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.tools.render import render_text_description
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.agents import AgentExecutor
from langchain.agents import AgentType, Tool, initialize_agent

from langchain.memory import ConversationBufferMemory

from langchain.chat_models import ChatOpenAI

from langchain.agents.format_scratchpad import format_log_to_messages
from langchain.agents import AgentExecutor
from langchain.agents.output_parsers import JSONAgentOutputParser

from langchain.prompts import PromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate

from tools.search_tools import search_general
from tools.geo_tools import get_ip, get_location
from tools.search_tools import search_general
from tools.time_tools import get_time
from tools.lore_tools import get_lore
from tools.lcd_tools import get_lcd, safe_exit

import json


load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
serpapi_api_key = os.getenv("SERPAPI_API_KEY")
eleven_api_key = os.getenv('ELEVEN_API_KEY')

prompt = hub.pull("hwchase17/react-chat-json")

with open('system_message.txt', 'r') as file:
    system_message = file.read()
new_system_message_prompt = SystemMessagePromptTemplate(prompt=PromptTemplate(
    input_variables=[],  
    template=system_message
))

if isinstance(prompt.messages, list):
    prompt.messages[0] = new_system_message_prompt
else:
    prompt.messages = list(prompt.messages)
    prompt.messages[0] = new_system_message_prompt


chat_model = ChatOpenAI(temperature=0, model="gpt-4")

tools = [
    Tool.from_function(
        name="Search general",
        func=search_general,
        description="Useful for when you need to answer general questions"
    ),
    Tool.from_function(
        name="Current Location",
        func=get_location,
        description="Useful for when you need the current location or timezone for real time data."
    ),
    Tool.from_function(
        name="Current Time",
        func=get_time,
        description="Gets the current time if you know the timezone."
    ),
    Tool.from_function(
        name="Lore general",
        func=get_lore,
        description="Useful for when you need to get information about yourself or your past."
    ),
]

prompt = prompt.partial(
    tools=render_text_description(tools),
    tool_names=", ".join([t.name for t in tools]),
)


memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
llm = ChatOpenAI(temperature=0)
agent_chain = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
)

chat_model_with_stop = chat_model.bind(stop=["\nObservation"])

# We need some extra steering, or the chat model forgets how to respond sometimes
TEMPLATE_TOOL_RESPONSE = """TOOL RESPONSE: 
---------------------
{observation}

USER'S INPUT
--------------------

Okay, so what is the response to my last comment? If using information obtained from the tools you must mention it explicitly without mentioning the tool names - I have forgotten all TOOL RESPONSES! Remember to respond with a markdown code snippet of a json blob with a single action, and NOTHING else - even if you just want to respond to the user. Do NOT respond with anything except a JSON snippet no matter what!"""

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_messages(
            x["intermediate_steps"], template_tool_response=TEMPLATE_TOOL_RESPONSE
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | chat_model_with_stop
    | JSONAgentOutputParser()
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory)

# Main live chat loop
try:
    while True:
        # Get user input from the command prompt
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Exiting live chat.")
            break

        # Prepare the input for the agent
        invocation_input = {"input": user_input}
        
        # Invoke the agent and get the response
        response = agent_executor.invoke(invocation_input)["output"]
        
        # Print the agent's response
        print("Bot:", response)
except KeyboardInterrupt:
    print("\nLive chat interrupted.")