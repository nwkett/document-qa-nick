
import streamlit as st
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

class ResearchSummary(BaseModel):
    main_answer: str
    key_facts: list[str]
    source_hint: str

structured_mode = st.sidebar.checkbox("Return structured summary")
streaming_mode = st.sidebar.checkbox("Enable streaming")

st.title("Research Agent")
st.caption("Web Search")

user_input = st.text_input("Ask a question:")

if user_input:
    if structured_mode:
        response = client.responses.parse(
            model="gpt-4o",
            instructions="You are a helpful research assistant. Cite your sources.",
            input=user_input,
            tools=[{"type": "web_search_preview"}],
            previous_response_id=st.session_state.get("last_response_id"),
            text_format=ResearchSummary,
        )
        st.session_state.last_response_id = response.id
        summary = response.output_parsed
        st.write(summary.main_answer)
        st.write("Summary:")
        for fact in summary.key_facts:
            st.write(f"- {fact}")
        st.caption(f"Cite: {summary.source_hint}")

    elif streaming_mode:
        st.session_state.last_response_id = None  
        with client.responses.stream(
            model="gpt-4o",
            instructions="You are a helpful research assistant. Cite your sources.",
            input=user_input,
            tools=[{"type": "web_search_preview"}],
        ) as stream:
            st.write_stream(stream.text_stream)

    else:
        response = client.responses.create(
            model="gpt-4o",
            instructions="You are a helpful research assistant. Cite your sources.",
            input=user_input,
            tools=[{"type": "web_search_preview"}],
            previous_response_id=st.session_state.get("last_response_id"),
        )
        st.session_state.last_response_id = response.id
        st.write(response.output_text)

    follow_up = st.text_input("Ask a follow-up question:")

    if follow_up and st.session_state.get("last_response_id"):
        if structured_mode:
            follow_response = client.responses.parse(
                model="gpt-4o",
                instructions="You are a helpful research assistant. Cite your sources.",
                input=follow_up,
                tools=[{"type": "web_search_preview"}],
                previous_response_id=st.session_state.last_response_id,
                text_format=ResearchSummary,
            )
            st.session_state.last_response_id = follow_response.id
            summary = follow_response.output_parsed
            st.write(summary.main_answer)
            st.write("Summary")
            for fact in summary.key_facts:
                st.write(f"- {fact}")
            st.caption(f"Cite: {summary.source_hint}")

        elif streaming_mode:
            with client.responses.stream(
                model="gpt-4o",
                instructions="You are a helpful research assistant. Cite your sources.",
                input=follow_up,
                tools=[{"type": "web_search_preview"}],
                previous_response_id=st.session_state.get("last_response_id"),
            ) as stream:
                st.write_stream(stream.text_stream)

        else:
            follow_response = client.responses.create(
                model="gpt-4o",
                instructions="You are a helpful research assistant. Cite your sources.",
                input=follow_up,
                tools=[{"type": "web_search_preview"}],
                previous_response_id=st.session_state.last_response_id,
            )
            st.session_state.last_response_id = follow_response.id
            st.write(follow_response.output_text)