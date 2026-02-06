import streamlit as st
from openai import OpenAI, AuthenticationError


st.title('Nicks Lab3 Question answering chatbot')

def apply_buffer():
    
    MAX_HISTORY = 4  # 2 user + 2 assistant

    msgs = st.session_state.messages
    system_msg = msgs[:1]      # keep system always
    rest = msgs[1:]            # everything else

    if len(rest) > MAX_HISTORY:
        rest = rest[-MAX_HISTORY:]

    st.session_state.messages = system_msg + rest


openAI_model = st.sidebar.selectbox("Select Model", ('mini', 'regular'))

if openAI_model == 'mini':
    model_to_use = "gpt-4o-mini"
else:
    model_to_use = 'gpt-4o'

if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
You are a helpful chatbot.

Rules:
1) Explain everything so a 10-year-old can understand. Use simple words and short sentences.
2) After you answer a question, ALWAYS ask: "Do you want more info?"
3) If the user says "Yes", provide more information about the SAME topic, then ask again: "Do you want more info?"
4) If the user says "No", say: "Okay! What can I help you with?" and wait for a new question.
"""

if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hi! What can I help you with?"}
    ]

if "expecting_more_info" not in st.session_state:
    st.session_state.expecting_more_info = False

if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])


YES_SET = {"yes", "y", "yeah", "yep", "sure", "ok", "okay"}
NO_SET = {"no", "n", "nope", "nah"}

if prompt := st.chat_input("Type here..."):
    user_text = prompt.strip()
    normalized = user_text.lower().strip()

    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    if st.session_state.expecting_more_info and normalized in YES_SET:
        followup = (
            f"Give more information about this topic: {st.session_state.last_topic}. "
            "Explain for a 10-year-old. End with: Do you want more info?"
        )
        st.session_state.messages.append({"role": "user", "content": followup})

    elif st.session_state.expecting_more_info and normalized in NO_SET:
        st.session_state.expecting_more_info = False
        st.session_state.last_topic = ""

        assistant_text = "Okay! What can I help you with?"
        st.session_state.messages.append({"role": "assistant", "content": assistant_text})
        with st.chat_message("assistant"):
            st.write(assistant_text)

        apply_buffer()
        st.stop()

    else:
        st.session_state.last_topic = user_text
        st.session_state.expecting_more_info = True

    apply_buffer()

    client = st.session_state.client
    stream = client.chat.completions.create(
        model=model_to_use,
        messages=st.session_state.messages,
        stream=True
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})

    apply_buffer()