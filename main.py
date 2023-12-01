from dotenv import load_dotenv
import threading
import queue
import os

import soundfile as sf
import speech_recognition as sr
import numpy as np
from io import BytesIO

from langchain import hub
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI

from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.tools.render import render_text_description
from langchain.agents import AgentType, AgentExecutor, Tool, initialize_agent, load_tools
from langchain.agents.format_scratchpad import format_log_to_messages
from langchain.agents.output_parsers import JSONAgentOutputParser

from langchain.prompts import PromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate

from langchain.utilities.dalle_image_generator import DallEAPIWrapper

from langchain.tools import Tool, tool
from tools.search_tools import search_general
from tools.geo_tools import get_ip, get_location
from tools.time_tools import get_time
from tools.lcd_tools import lcd_time
from tools.link_tools import get_links, get_website_content, parse_image
from tools.file_tools import parse_file
from tools.telegram_tools import parse_telegram_send
from tools.contact_tools import get_contacts
from tools.spotify_tools import play_song, play_album, spotify_controller, get_user_playlists, play_spotify_uri



from elevenlabs import generate, play, stream, voices, Voice, VoiceSettings

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
        description="Useful for when you need to answer general questions."
    ),
    Tool.from_function(
        name="Get Link",
        func=get_links,
        description="Useful for when you need to get links. Useful if you will need to open a link to open. The input to this tool should be a google search query."
    ),
    Tool.from_function(
        name="Open Link",
        func=get_website_content,
        description="Useful for when you need to get the content from a wesbite. Useful if more information is needed after a search. The input to this tool should be a valid URL."
    ),
    Tool.from_function(
        name="Current Location",
        func=get_location,
        description="Useful for when you need the current location or timezone for real time data such as weather."
    ),
    Tool.from_function(
        name="Current Time",
        func=get_time,
        description="Gets the current time if you know the timezone."
    ),
    Tool.from_function(
        name="Save Image",
        func=parse_image,
        description="Useful for when you need to save an image from a URL. The input to this tool should be a comma separated list of a URL and filename. For example, `www.website.com/img, apple.jpg` would be the input if you wanted to download an image of an apple from website.com."
    ),
    Tool.from_function(
        name="Create File",
        func=parse_file,
        description="Useful for when you need to write text or code to a file. The input to this tool should be a list of the content, and the filename separated by '@@@'. For example, `print(test) @@@ print.py` would be the input if you wanted to write a print statement to a file called print.py."
    ),
    Tool.from_function(
        name="Get Contact Info",
        func=get_contacts,
        description="Useful for when you need to get contact information of someone or when you need to know who your owner is. Do this before attempting to contact anyone."
    ),
    Tool.from_function(
        name="Send Telegram Message",
        func=parse_telegram_send,
        description="Useful for when you need to send a Telegram message. The input to this tool should be a list of the message content, and the telegram chat id separated by '@@@'. For example, `Hi there, John @@@ 87463624` would be the input if you wanted to greet John."
    ),
    Tool.from_function(
        name="Play Song on Spotify",
        func=play_song,
        description="Useful for when you need to play a song on Spotify. The input to this tool should be the search query to find this song. For example, `Lose Yourself by Eminem`."
    ),
    Tool.from_function(
        name="Play Album on Spotify",
        func=play_album,
        description="Useful for when you need to play an album on Spotify. The input to this tool should be the search query to find this album. For example, `The Car by Arctic Monkeys`."
    ),
    Tool.from_function(
        name="Spotify Controller",
        func=spotify_controller,
        description="Useful for when you need to control or start music playback on Spotify. The input to this tool must be one of the following based on the given request: 'start' | 'pause' | 'skip' | 'previous' | 'shuffle'"
    ),
    Tool.from_function(
        name="Get User Playlists",
        func=get_user_playlists,
        description="Useful for when you need to get user playlist URIs."
    ),
    Tool.from_function(
        name="Play URI on Spotify",
        func=play_spotify_uri,
        description="Useful for when you need to play a playlist, album, or song using its URI. The input to this tool must be a known URI, for example: 'spotify:playlist:6rqhFgbbKwnb9MLmUQDhG6'"
    ),
]

new_tools = load_tools(["dalle-image-generator"])
tools.extend(new_tools)


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

lcd_queue = queue.Queue(maxsize=1)

def live_chat(lcd_queue):
    try:
        while True:

            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Exiting live chat.")
                break

            lcd_queue.put(1)

            invocation_input = {"input": user_input}
            response = agent_executor.invoke(invocation_input)["output"]
            
            print("C-3DK:", response)

            lcd_queue.put(0)
            
            response_audio_bytes = generate(
                text=response,
                voice="Edgar - nerdy",
                model="eleven_monolingual_v1",
                stream=False 
            )

            response_audio_data, sample_rate = sf.read(BytesIO(response_audio_bytes))

            delay_samples = int(10 * sample_rate / 1000)
            echoed_audio_data = np.copy(response_audio_data)
            echoed_audio_data[delay_samples:] += 0.9 * response_audio_data[:-delay_samples]

            output_bytes_io = BytesIO()
            sf.write(output_bytes_io, echoed_audio_data, sample_rate, format='wav')

            output_audio_bytes = output_bytes_io.getvalue()
            play(output_audio_bytes)
            

    except KeyboardInterrupt:
        print("\nLive chat interrupted.")
    finally:
        lcd_queue.put(0)



if __name__ == "__main__":
    lcd_thread = threading.Thread(target=lcd_time, args=(lcd_queue,))
    chat_thread = threading.Thread(target=live_chat, args=(lcd_queue,)) 

    lcd_thread.start()
    chat_thread.start()

    lcd_thread.join()
    chat_thread.join()