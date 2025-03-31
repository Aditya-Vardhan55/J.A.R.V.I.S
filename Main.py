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

def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json', "r", encoding='utf-8')
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
            
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)
            
def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

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

def ChooseChromeProfile():
    chrome_user_data_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    
    if not os.path.exists(chrome_user_data_path):
        ErrorMessage = "Chrome user data directory not found. Please ensure Chrome is installed."
        ShowTextToScreen(f"{Assistantname} : {ErrorMessage}")
        TextToSpeech(ErrorMessage)
        return None
    
    profiles = [profile for profile in os.listdir(chrome_user_data_path) if os.path.isdir(os.path.join(chrome_user_data_path, profile))]
    
    if not profiles:
        ErrorMessage = "No Chrome profiles found."
        ShowTextToScreen(f"{Assistantname} : {ErrorMessage}")
        TextToSpeech(ErrorMessage)
        return None
    
    profile_message = "I found the following Chrome profiles: " + ", ".join(profiles) + ". Please choose one."
    ShowTextToScreen(f"{Assistantname} : {profile_message}")
    TextToSpeech(profile_message)
    
    for index, profile in enumerate(profiles, start=1):
        print(f"{index}. {profile}")
        
    try:
        choice = int(input("Enter the number corresponding to your choice: "))
        if 1 <= choice <= len(profiles):
            selected_profile = profiles[choice - 1]
            return selected_profile
        else:
            ErrorMessage = "Invalid choice. Please try again."
            ShowTextToScreen(f"{Assistantname} : {ErrorMessage}")
            TextToSpeech(ErrorMessage)
            return None
    
    except ValueError:
        ErrorMessage = "Invalid input. Please enter a number."
        ShowTextToScreen(f"{Assistantname} : {ErrorMessage}")
        TextToSpeech(ErrorMessage)
        return None
                
def MainExecution():
    
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)
    
    print("")
    print(f"Decision : {Decision}")
    print("")
    
    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    
    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )
    
    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True
            
    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                if "open chrome" in queries:
                    selected_profile = ChooseChromeProfile()
                    if selected_profile:
                        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                        profile_path = os.path.join(os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"), selected_profile)
                        try:
                            subprocess.Popen([chrome_path, f"--profile-directory={selected_profile}"])
                            TaskExecution = True
                        except Exception as e:
                            print(f"Error opening Chrome with profile {selected_profile}: {e}")
                            ErrorMessage = "Sorry, I couldn't open Chrome with the selected profile."
                            ShowTextToScreen(f"{Assistantname} : {ErrorMessage}")
                            TextToSpeech(ErrorMessage)
                            return False
                
                else:
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
        
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
            
        try:
            p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE, shell=False)
            subprocess.append(p1)
            
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")
            
    if G and R or R:
        
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
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
                return True
            
            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime ","")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
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
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
    