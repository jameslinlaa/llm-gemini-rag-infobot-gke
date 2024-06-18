import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from backend.backend import run_g_llm
import os



st.set_page_config(page_title="infoBot")
with st.sidebar:
    st.title("Pokemon Go InfoBot")
    
    st.markdown(
    """
    ## Demo
    This is a demo for a infoBot to answer questions based on Pokemon Go activity web pages
    - web: [Pokemon Go 活動](https://pokemongolive.com/events?hl=zh_Hant)

    ## Referece
    - git: [github-assistant](https://github.com/g-emarco/github-assistant)
    """
    )

    
    add_vertical_space(10)

    st.write("Made by [James]")

if "generated" not in st.session_state:
    st.session_state["generated"] = ["Hi! 請問你想查詢什麼活動"]
if "past" not in st.session_state:
    st.session_state["past"] = ["Hi!"]
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


input_container = st.container()
colored_header(label="", description="", color_name="gray-30")
response_container = st.container()



if "my_text" not in st.session_state:
    st.session_state.my_text = ""


def submit():
    st.session_state.my_text = st.session_state.widget
    st.session_state.widget = ""


with input_container:
    st.text_input("請輸入問題吧：", key="widget", on_change=submit)
    user_input = st.session_state.my_text
    st.session_state.my_text = ""



## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if user_input and user_input != "":
        
        with st.spinner("Generating response..."):
            response = run_g_llm(
                query=user_input, chat_history=st.session_state["chat_history"]
            )
            st.session_state.past.append(user_input)
            st.session_state.generated.append(response["answer"])
            st.session_state["chat_history"].append((user_input, response["answer"]))

            
        

    if st.session_state["generated"]:
        for i in range(len(st.session_state["generated"])):
            # leverage streamlit_chat to display the conversation 
            message(st.session_state["past"][i], is_user=True, key=str(i) + "_user",avatar_style="adventurer-neutral")
            message(st.session_state["generated"][i], key=str(i),avatar_style="fun-emoji")
