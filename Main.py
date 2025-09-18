from Frontend.GUI import (
GraphicalUserInterface,
SetAssistantStatus,
ShowTextToScreen,
TempDirectoryPath,
SetMicrophoneStatus,
AnswerModifier,
QueryModifier,
GetMicrophoneStatus,
GetAssistantStatus  )
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def request_memory_retrieval(query):
    """Writes a request to the memory manager to retrieve memories."""
    with open(r"Frontend\Files\memory_request.data", "w") as f:
        json.dump({"action": "retrieve", "payload": query}, f)
        
    sleep(1.5)
    
    with open(r"Frontend\Files\memory_response.data", "r") as f:
        try:
            memories = json.load(f)
            return memories
        except json.JSONDecodeError:
            return []
        
def request_memory_storage(text_to_store):
    """Writes a request to the memory manager to store a memory."""
    with open(r"Frontend\Files\memory_request.data", "w") as f:
        json.dump({"action": "store", "payload": text_to_store}, f)

def clean_image_prompt(query):
    query_lower = query.lower().strip()
    trigger_phrases = [
        "generate image of", "create picture of", "make photo of",
        "draw painting of", "show me picture of", "i want an image of",
        "generate image", "generate picture", "generate photo",
        "generate a", "image of", "picture of", "photo of", "generate "
    ]
    
    for phrase in trigger_phrases:
        if query_lower.startswith(phrase):
            return query[len(phrase):].strip()
    return None

def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json', "r", encoding='utf-8')
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
            
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)
            
def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")
    
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))
        
def ShowChatsOnGUI():
    File = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    Data = File.read()
    if len(str(Data))>0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8')
        File.write(result)
        File.close()
        
def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()
    
InitialExecution()
                
def MainExecution():
    
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    
    relevant_memories = request_memory_retrieval(Query)
    print(f"Retrieved memories: {relevant_memories}")
    
    augmented_query = Query
    if relevant_memories:
        context = "\n".join(relevant_memories)
        augmented_query = f"Here is some context from our past conversations:\n{context}\n\nNow, answer this question: {Query}"
        
    
    Decision = FirstLayerDMM(augmented_query)
    
    print("")
    print(f"Decision : {Decision}")
    print("")
    
    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    
    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )
    
    for queries in Decision:
        cleaned_prompt = clean_image_prompt(queries)
        if cleaned_prompt:
            ImageGenerationQuery = cleaned_prompt
            ImageExecution = True
            break
            
    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                    try:
                        run(Automation(list(Decision)))
                        TaskExecution = True
                    except Exception as e:
                        print(f"Error executing task: {e}")
                        SetAssistantStatus("Error...")
                        ErrorMessage = "Sorry, I couldn't execute the requested task. Please try again or check the task details."
                        ShowTextToScreen(f"{Assistantname} : {ErrorMessage}")
                        TextToSpeech(ErrorMessage)
                        return False
    
    if ImageExecution == True:
        prompt = ImageGenerationQuery
        
        feedback_message = f"Generating your image of {prompt}..."
        ShowTextToScreen(f"{Assistantname} : {feedback_message}")
        TextToSpeech(feedback_message)
        
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{prompt},True")
            
        try:
            p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'])
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")
            SetAssistantStatus("Error...")
            
        return 
            
    if G and R or R:
        
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        
        summary_of_turn = f"User asked about '{Query}' and I responded about '{Answer}'."
        request_memory_storage(summary_of_turn)
        return True
    
    else:
        for Queries in Decision:
            
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general ","")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                
                summary_of_turn = f"User asked about '{Query}' and I responded about '{Answer}'."
                request_memory_storage(summary_of_turn)
                return True
            
            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime ","")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
            
                summary_of_turn = f"User asked about '{Query}' and I responded about '{Answer}'."
                request_memory_storage(summary_of_turn)    
                return True
            
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering...")
                os._exit(1)
                
def FirstThread():
    
    while True:
        
        CurrentStatus = GetMicrophoneStatus()
        
        if CurrentStatus == "True":
            MainExecution()
        
        else:
            AIStatus = GetAssistantStatus()
            
            if "Available..." in AIStatus:
                sleep(0.1)
                
            else:
                SetAssistantStatus("Available...")
                
def SecondThread():
    
    GraphicalUserInterface()
    
if __name__ == "__main__":
    InitialExecution()
    
    subprocess.Popen(['python', r'Backend\MemoryManager.py'])
    
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    
    SecondThread()
    