import streamlit as st
from openai import OpenAI, AuthenticationError

#initial empty messages
st.title('Nicks Lab3 Question answering chatbot')

openAI_model = st.sidebar.selectbox("Select Model", ('mini', 'regular'))

if openAI_model == 'mini':
    model_to_use = "gpt-4o-mini"
else:
    model_to_use = 'gpt-4o'

if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

if 'messages' not in st.session_state:
    st.session_state['messages'] = \
        [{"role": 'assistant','content': "How can I help you today?"}]
    
for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

        MAX_HISTORY = 4  # 2 user + 2 assistant messages

    if len(st.session_state.messages) > 1 + MAX_HISTORY:
        st.session_state.messages = (
            st.session_state.messages[:1] +   # keep initial assistant message
            st.session_state.messages[-MAX_HISTORY:]
        )

    client = st.session_state.client
    stream = client.chat.completions.create(
        model = model_to_use,
        messages = st.session_state.messages,
        stream=True
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
