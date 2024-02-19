import streamlit as st

st.set_page_config(initial_sidebar_state="expanded", page_title="Chat with a MySQL Database", page_icon=":speech_balloon:")

with st.sidebar:
    st.title("Chat with a MySQL Database")
    st.write("This is a simple chat application allows you to chat with a MySQL database.")

    st.text_input("Host", key="name")
    st.text_input("Port", key="port")
    st.text_input("Username", key="username")
    st.text_input("Password", key="password")
    st.text_input("Database", key="database")
    
user_query = st.chat_input("Type a message...")

if user_query != "":
    pass