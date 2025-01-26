import os
from termcolor import colored
import yaml
from PIL import Image
import chainlit as cl
from chainlit.input_widget import TextInput, Slider, Select, NumberInput
from agent_graph.graph import create_graph, compile_workflow

# Directory to save uploaded images
SAVE_DIR = "uploaded_images"
os.makedirs(SAVE_DIR, exist_ok=True)

def update_config(tavily_api_key,  groq_llm_api_key):
    config_path = "D:\Agent-Project\config\config.yaml"

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    config['TAVILY_API_KEY'] = tavily_api_key
    config['GROQ_API_KEY'] = groq_llm_api_key

    if tavily_api_key:
        os.environ['SERPER_API_KEY'] = tavily_api_key
    if groq_llm_api_key:
        os.environ['GROQ_API_KEY'] = groq_llm_api_key

    with open(config_path, 'w') as file:
        yaml.safe_dump(config, file)

    print("Configuration updated successfully.")

class ChatWorkflow:
    def __init__(self):
        self.workflow = None
        self.recursion_limit = 40

    def build_workflow(self, server, model,  temperature, recursion_limit=40, stop=None):
        graph = create_graph(
            server=server, 
            model=model,
            temperature=temperature,
            stop=stop
        )
        self.workflow = compile_workflow(graph)
        self.recursion_limit = recursion_limit

    def invoke_workflow(self, message):
        if not self.workflow:
            return "Workflow has not been built yet. Please update settings first."
        
        dict_inputs = {"query_question": message.content}
        limit = {"recursion_limit": self.recursion_limit}
        reporter_state = None

        for event in self.workflow.stream(dict_inputs, limit):
            if "end" in event:
                state = event["end"]
                reviewer_state = state["reviewer_response"]
                return reviewer_state[-1].content if reviewer_state else "No response available"



        return "Workflow did not reach any output"

# Use a single instance of ChatWorkflow
chat_workflow = ChatWorkflow()

@cl.on_chat_start
async def start():
    await cl.ChatSettings(
        [
            Select(
                id="server",
                label="Select the server you want to use:",
                values=[
                    "groq"
                ]
            ),
            NumberInput(
                id="recursion_limit",
                label="Enter the recursion limit:",
                description="The maximum number of agent actions the workflow will take before stopping. The default value is 40",
                initial=40
            ),
            TextInput(
                id="tavily_api_key",
                label="Enter your TAVILY API Key:",
                description="You can get your API key from https://tavily.com/",
                # initial="NO_KEY_GIVEN"
                
            ),
            TextInput(
                id='groq_llm_api_key',
                label='Enter your Groq API Key:',
                description="Only use this if you are using Groq, Get your key from groq cloud.",
                # initial="NO_KEY_GIVEN"
            ),
            TextInput(
                id='llm_model',
                label='Enter your Model Name:',
                description="The name of the model you want to use,You can use this for test (llama-3.3-70b-versatile)"
            ),
            TextInput(
                id='stop_token',
                label='Stop token:',
                description="The token that will be used to stop the model from generating more text. The default value is <|end_of_text|>",
                initial="<|end_of_text|>"
            ),
            Slider(
                id='temperature',
                label='Temperature:',
                initial=0,
                max=1,
                step=0.05,
                description="Lower values will generate more deterministic responses, while higher values will generate more random responses. The default value is 0"
            )
        ]
    ).send()

@cl.on_settings_update
async def update_settings(settings):
    global author
    TAVILY_API_KEY = settings["tavily_api_key"]
    GROQ_API_KEY = settings["groq_llm_api_key"]
    update_config(
        tavily_api_key=TAVILY_API_KEY,
        groq_llm_api_key=GROQ_API_KEY,
        )
    server = settings["server"]
    model = settings["llm_model"]
    temperature = settings["temperature"]
    recursion_limit = settings["recursion_limit"]
    stop = settings["stop_token"]
    author = settings["llm_model"]
    await cl.Message(content="✅ Settings updated successfully, building workflow...").send()
    chat_workflow.build_workflow(server, model, temperature, recursion_limit, stop)
    await cl.Message(content="😊 Workflow built successfully.").send()

@cl.on_message
async def main(message: cl.Message):
        if  message.elements :
            # Get the image file from the message
            print(colored(f"Reviewer : {message}", 'blue'))
            image = message.elements[-1]
            image_path = image.path
            # image_name = image.name
            image_name = "ocr.png"


            # # Open the image using PIL
            image = Image.open(image_path)
            # print(colored(f"Reviewer : {image}", 'blue'))

            image_path = os.path.join(SAVE_DIR, image_name)

            # Save the image
            image.save(image_path)

            # Respond with confirmation and details
            dimensions = image.size  # (width, height)
            response = await cl.make_async(chat_workflow.invoke_workflow)(message)
            await cl.Message(content=f"{response}", author=author).send()

        else:
            response = await cl.make_async(chat_workflow.invoke_workflow)(message)
            await cl.Message(content=f"{response}", author=author).send()
