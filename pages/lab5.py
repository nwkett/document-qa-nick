import requests
import streamlit as st
import json
from openai import OpenAI

# location in form City, State, Country
# e.g., Syracuse, NY, US
# default units is degrees Fahrenheit
def get_current_weather(location, api_key, units='imperial'):
    url = (
    f'https://api.openweathermap.org/data/2.5/weather'
    f'?q={location}&appid={api_key}&units={units}'
    )

    response = requests.get(url)
    if response.status_code == 401:
        raise Exception('Authentication failed: Invalid API key (401 Unauthorized)')
    if response.status_code == 404:
        error_message = response.json().get('message')
        raise Exception(f'404 error: {error_message}')
    
    data = response.json()
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    temp_min = data['main']['temp_min']
    temp_max = data['main']['temp_max']
    humidity = data['main']['humidity']

    return {'location': location,
    'temperature': round(temp, 2),
    'feels_like': round(feels_like, 2),
    'temp_min': round(temp_min, 2),
    'temp_max': round(temp_max, 2),
    'humidity': round(humidity, 2)
    }


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": (
                "Get the current weather for a given city. "
                "Use 'Syracuse, NY, US' if no location is provided."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g. 'Syracuse, NY, US' or 'Lima, Peru'",
                    }
                },
                "required": ["location"],
            },
        },
    }
]

openai_api_key = st.secrets.get("OPENAI_API_KEY")
weather_api_key = st.secrets.get("WEATHER_KEY")

if not openai_api_key or not weather_api_key:
    st.error("Missing API keys.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# Sidebar

st.sidebar.title("Weather bot")
city_input = st.sidebar.text_input(
    "Enter a city:",
    placeholder = "Syracuse, NY, US"
)

get_advice_btn = st.sidebar.button("Get Clothes Advice")

# Main

st.title ("Nick's Weather Bot for Lab 5")


if get_advice_btn:
    model_name   = "gpt-4o"
    user_location = city_input.strip() if city_input.strip() else "Syracuse, NY, US"
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful advisor that makes suggestions based on weather "
                "When given weather data, suggest appropriate clothing and "
                "outdoor activities for that day."
            ),
        },
        {
            "role": "user",
            "content": f"What should I wear today in {user_location}? Also suggest some outdoor activities.",
        },
    ]

    response = client.chat.completions.create(
        model = model_name,
        messages = messages,
        tools=tools,
        tool_choice = "auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(response_message)

        for tool_call in tool_calls:
            args= json.loads(tool_call.function.arguments)
            location = args.get("location", "Syracuse, NY, US")

            try:
                weather_data = get_current_weather(location, weather_api_key)
            except Exception as e:
                st.error(f"Weather lookup failed: {e}")
                st.stop()

            st.subheader(f"Current Weather in {weather_data['location']}")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Temperature (F)", f"{weather_data['temperature']}°")
            col2.metric("Feels Like", f"{weather_data['feels_like']}°")
            col3.metric("Humidity", f"{weather_data['humidity']}%")
            col4.metric("Low", f"{weather_data['temp_min']}°")
            col5.metric("High", f"{weather_data['temp_max']}°")
            

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(weather_data),
            })

        st.subheader("Today's Clothing Advice")
        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True,
        )
        st.write_stream(stream)

    else:
        st.write(response_message.content)