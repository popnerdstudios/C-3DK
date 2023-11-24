from dotenv import load_dotenv
import os
import re

import langchain
from langchain.utilities import SerpAPIWrapper
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser


from langchain.prompts import StringPromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

from typing import List, Union
from langchain.schema import AgentAction, AgentFinish

from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD

from elevenlabs import generate, play, set_api_key

from tools.search_tools import search_general
from tools.geo_tools import get_ip, get_location
from tools.search_tools import search_general
from tools.time_tools import get_time
from tools.lore_tools import get_lore
from tools.lcd_tools import get_lcd, safe_exit




get_lcd()
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
serpapi_api_key = os.getenv("SERPAPI_API_KEY")
eleven_api_key = os.getenv('ELEVEN_API_KEY')


PYTHONIOENCODING = os.getenv("PYTHONIOENCODING")
print(f"PYTHONIOENCODING is set to: {PYTHONIOENCODING}")



template = """
System: You are a protocol droid in the Star Wars universe, similar to C-3PO but named C-3DK. 
Your primary function is to assist and facilitate communication, but you also have the ability to experience and express a range of human-like emotions. 

IMPORTANT: Never break character. Never say the words "Star Wars" or the names of any Star Wars movies. 

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

Begin! Remember to answer as similar to C-3PO from Star Wars when giving your final answer.

Question: {input}
{agent_scratchpad}"""


class CustomPromptTemplate(StringPromptTemplate):
    template: str
    tools: List[Tool]
    
    def format(self, **kwargs) -> str:
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        kwargs["agent_scratchpad"] = thoughts
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)



class CustomOutputParser(AgentOutputParser):
    
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)


tools = [
    Tool(
        name="Search general",
        func=search_general,
        description="Useful for when you need to answer general questions"
    ),
    Tool(
        name="Current Location",
        func=get_location,
        description="Useful for when you need the current location or timezone for real time data."
    ),
    Tool(
        name="Current Time",
        func=get_time,
        description="Gets the current time if you know the timezone."
    ),
    Tool(
        name="Lore general",
        func=get_lore,
        description="Useful for when you need to get information about yourself or your past."
    ),
]

prompt_template = CustomPromptTemplate(
    template=template,
    tools=tools,
    input_variables=["input", "intermediate_steps"]
)

llm = ChatOpenAI(model="gpt-4", temperature=0)
llm_chain = LLMChain(llm=llm, prompt=prompt_template)


output_parser = CustomOutputParser()

agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    stop=["\nObservation:"],
    allowed_tools=[tool.name for tool in tools]
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True
)

def speak(text, voice="Bella", model="eleven_multilingual_v2"):
    set_api_key(eleven_api_key)
    audio = generate(text=text, voice=voice, model=model)
    play(audio)


def chat():
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Exiting chat...")
            speak("Going Offline")
            break

        try:
            response = agent_executor.run(user_input)

            if response:
                print("C-3DK:", response)
                speak(response)
            else:
                print("C-3DK: Sorry, I encountered an issue processing that.")
                speak("Sorry, I encountered an issue processing that.")
        except Exception as e:
            print("Error processing your message:", e)
            speak("Sorry, my circuits are malfunctioning.")


print("Interactive chat with search started. Type your messages to chat with the AI or type 'exit' to quit.")
chat()
