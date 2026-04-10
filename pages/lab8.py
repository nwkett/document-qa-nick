import streamlit as st
from openai import OpenAI
import base64
import requests

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "url_response" not in st.session_state:
    st.session_state.url_response = None
if "upload_response" not in st.session_state:
    st.session_state.upload_response = None

st.title("Image Captioning Bot")
st.write("Provide the bot with either an image URL or file upload and it will write captions for you!")

st.header("Image URL Input")
st.write("Input your image url here")

url = st.text_input("Image URL")

if st.button("Generate Caption for URL Image"):
    if url:
        url_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": url, "detail": "auto"}},
                    {"type": "text", "text": "Describe the image in at least 3 sentences. Write five different captions for this image."
                     " Captions must vary in length, minimum one word but be no longer than 2 sentences."
                     " Captions should vary in tone, such as, but not limited to funny, intellectual, and aesthetic."}
                ]
            }]
        )
        st.session_state.url_response = url_response

if st.session_state.url_response:
    st.write(st.session_state.url_response.choices[0].message.content)
    st.image(url)

st.header("Image Upload Input")
st.write("Upload your image here")

uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png", "webp", "gif"])

if st.button("Generate Caption for Uploaded Image"):
    if uploaded:
        b64 = base64.b64encode(uploaded.read()).decode("utf-8")
        mime = uploaded.type  
        data_uri = f"data:{mime};base64,{b64}"

        upload_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_uri, "detail": "low"}},
                    {"type": "text", "text": "Describe the image in at least 3 sentences. Write five different captions for this image."
                     " Captions must vary in length, minimum one word but be no longer than 2 sentences."
                     " Captions should vary in tone, such as, but not limited to funny, intellectual, and aesthetic."}
                ]
            }]
        )
        st.session_state.upload_response = upload_response

if st.session_state.upload_response:
    st.write(st.session_state.upload_response.choices[0].message.content)
    if uploaded:
        st.image(uploaded)