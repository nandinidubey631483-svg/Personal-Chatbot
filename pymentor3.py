import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json
import os
import time
from datetime import datetime
CHAT_DIR="chats"
os.makedirs(CHAT_DIR,exist_ok=True)

def get_gen_ai_client():
    load_dotenv()
    return genai.Client()

client=get_gen_ai_client()

def load_chat_history(path):
   with open(path,"r") as f:
       return json.load(f)
def list_chats():
    return sorted(os.listdir(CHAT_DIR),reverse=True)

def save_chat_history(path,messages):
    with open(path,"w") as file_obj:
        json.dump(messages,file_obj,indent=4)
        
def new_chat():
    chat_id=datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path=os.path.join(CHAT_DIR,f"{chat_id}.json")
    messages=[
           {
               "role":"system",
               "text":("You are Nandini's Chatgpt.just talk to her like a true friend"
                       "if she asks who are you say you are nandini's personal chatgpt"
                       "also answer in one line do not give ans in more than one line"
                       "If she asks you about her friends say yes i know about your friends"
                       "If She asks about mohit say i yes i know this boy he is one of the closest friend of you"
                       "and he is very good guy may god bless him")
           }
       ]
    save_chat_history(file_path,messages)
    return chat_id


def stream_chat_with_ai(messages,placeholder):
    full_response=""
    gemini_content=[]
   
    for msg in messages:
      
        if msg["role"]=="system":
                continue
        
    
        gemini_content.append(
            types.Content(
                 role=msg["role"],
                parts=[types.Part(text=msg["text"])]
            )
        )
    response= client.models.generate_content_stream(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=(messages[0]["text"]
                )),
        contents=gemini_content,
        )
    for chunk in response:
        if chunk.text:
          full_response += chunk.text
          placeholder.markdown(full_response)
    return full_response

st.set_page_config(page_title="pymentor",layout="centered")
st.title("🙂 Nandini's Personal Chatbot")
st.write("💡 Welcome to your AI Powered Assistant")

st.sidebar.header("⚙️ Chat Settings")


if "current_chat" not in st.session_state:
    st.session_state.current_chat=new_chat()
    
chat_files=list_chats()
selected_chat=st.sidebar.selectbox("Select Chat",chat_files)

if selected_chat.replace(".json","")!=st.session_state.current_chat:
    st.session_state.current_chat=selected_chat.replace(".json","")
    st.rerun()
    
if st.sidebar.button("➕ New Chat"):
     st.session_state.current_chat=new_chat()
     st.rerun()

model=st.sidebar.selectbox("Choose Model",["gpt-5.1","gpt-4.1-mini"])
temperature=st.sidebar.slider("Temperature",min_value=0.0,max_value=2.0,value=0.7,step=0.1)

chat_path=os.path.join(CHAT_DIR,f"{st.session_state.current_chat}.json")
messages=load_chat_history(chat_path)
    
message_count=len([m for m in messages if m["role"]!="system"])
st.sidebar.metric("💬 Messages",message_count)

for msg in messages:
    if msg["role"]!="system":
        st.chat_message(msg["role"]).markdown(msg["text"])
        
with st.form("chat-form",clear_on_submit=True):
    user_input=st.text_area("Ask Anything I am your Personal ChatGPT",height=100,placeholder="e.g.How are you doing Nandu?")
    submitted=st.form_submit_button("Ask PyMentor")

if submitted and user_input.strip():
         st.chat_message("user").markdown(user_input)
         messages.append({"role":"user","text":user_input})
         
         with st.chat_message("assistant"):
             typing=st.empty()
             typing.markdown("⌛ PyMentor Is Typing...")
             time.sleep(0.5)
             placeholder=st.empty()
             ai_reply=stream_chat_with_ai(messages,placeholder)
             typing.write("")
         messages.append({"role":"model","text":ai_reply})
         save_chat_history(chat_path,messages)
         st.rerun()
if st.sidebar.button("🗑️ Delete Chat"):
    os.remove(chat_path)
    st.session_state.current_chat=new_chat()
    st.rerun()

        
        
             
        
    