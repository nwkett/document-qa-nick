import streamlit as st
from openai import OpenAI
import json
import os

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Chatbot with Long-Term Memory")


def load_memories():
    if os.path.exists("memories.json"):
        with open("memories.json", "r") as f:
            return json.load(f)
    return []
 
def save_memories(memories):
    with open("memories.json", "w") as f:
        json.dump(memories, f)
  
st.sidebar.title("Memories")
memories = load_memories()
 
if memories:
    for m in memories:
        st.sidebar.write(f"- {m}")
else:
    st.sidebar.write("No memories yet")
 
if st.sidebar.button("Clear All Memories"):
    save_memories([])
    st.rerun()
  
if "messages" not in st.session_state:
    st.session_state.messages = []
 
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
 
prompt = st.chat_input("Say something...")
 
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
 
    memories = load_memories()
    if memories:
        system_prompt = "Here are things you remember about this user from past conversations:\n" + "\n".join(memories) + "\nUse these memories to personalize your responses."
    else:
        system_prompt = "You are a helpful assistant."
 
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": system_prompt}
        ] + st.session_state.messages
    )
 
    assistant_message = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
 
    with st.chat_message("assistant"):
        st.write(assistant_message)
 
    existing = json.dumps(memories)
    try:
        extraction = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": f"Extract any new facts about the user worth remembering (name, preferences, interests, location, etc.) from the conversation below. Already saved memories: {existing}. Do not duplicate existing memories. Return ONLY a JSON list of new fact strings. If there are no new facts, return an empty list []."},
                {"role": "user", "content": f"User said: {prompt}\nAssistant said: {assistant_message}"}
            ]
        )
        new_facts = json.loads(extraction.choices[0].message.content)
        if new_facts:
            memories.extend(new_facts)
            save_memories(memories)
            st.rerun()
    except Exception:
        pass
