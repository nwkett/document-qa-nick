import streamlit as st
from openai import OpenAI, AuthenticationError

#initial empty messages
if messages is not initialized:
    messages = []
#add user prompt to messages
prompt = get_chat_input()

if prompt:
    messages.add('user', prompt)
#get LLM response
    response = call_llm('gpt-5-chat', messages, temperature = 0)
    messages.add('assistant', response.text)
    show_chat_output(response.text)