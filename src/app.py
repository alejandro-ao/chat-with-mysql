import streamlit as st
from langchain_community.utilities import SQLDatabase

def initialize_database(host, port, username, password, database):
  db_uri = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
  return SQLDatabase.from_uri(db_uri)


st.set_page_config(initial_sidebar_state="expanded", page_title="Chat with a MySQL Database", page_icon=":speech_balloon:")

with st.sidebar:
    st.title("Chat with a MySQL Database")
    st.write("This is a simple chat application allows you to chat with a MySQL database.")

    st.text_input("Host", key="name")
    st.text_input("Port", key="port")
    st.text_input("Username", key="username")
    st.text_input("Password", key="password")
    st.text_input("Database", key="database")
    
    if st.button("Connect"):
        with st.spinner("Connecting to the database..."):
          db = initialize_database(
            username=st.session_state.username,
            password=st.session_state.password,
            host=st.session_state.name,
            port=st.session_state.port,
            database=st.session_state.database
          )
          st.success("Connected to the database!")
    
user_query = st.chat_input("Type a message...")

if user_query != "":
    pass