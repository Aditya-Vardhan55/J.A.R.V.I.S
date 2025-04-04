from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import threading

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

def load_chat_history():
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            return load(f)
    except (FileNotFoundError, ValueError):
        return []
    
def save_chat_history(messages):
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages[-50:], f, indent=4)
        
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    
    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours:{minute} minutes:{second} seconds.\n"
    return data

def AnswerModifier(Answer):
    return '\n'.join([line for line in Answer.split('\n') if line.strip()])

def ChatBot(Query):
    """ This function sends the user's query to the chatbot and return the AI's response. """
    messages = load_chat_history()
    messages.append({"role": "user", "content": Query})
    
    try: 
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens= 1024,
            temperature= 0.7,
            top_p= 1,
            stream= True,
            stop= None
        )
        
        Answer = ""
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
                
        Answer = Answer.replace("</s>", "")
        
        messages.append({"role": "assistant", "content": Answer})
        save_chat_history(messages)
        return AnswerModifier(Answer=Answer)
    
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I encountered an error processing your request."
    
def async_chatbot(Query, callback):
    thread = threading.Thread(target=lambda: callback(ChatBot(Query)))
    thread.start()
    
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))