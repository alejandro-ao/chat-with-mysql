import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

def initialize_database(host, port, username, password, database):
  db_uri = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
  return SQLDatabase.from_uri(db_uri)

def get_response(user_query, chat_history, db):

  from langchain_core.prompts import ChatPromptTemplate

  template = """
  Based on the table schema below, write a SQL query that would answer the user's question.
  {schema}

  Question: {question}
  SQL Query:
  """

  prompt = ChatPromptTemplate.from_template(template)
  
  llm = ChatOpenAI()
  
  def get_schema(_):
    return db.get_table_info()

  sql_chain = (
      RunnablePassthrough.assign(schema=get_schema)
      | prompt
      | llm.bind(stop="\nSQL Result:")
      | StrOutputParser()
  )
  
  return sql_chain.invoke({
    "question": user_query
  })
  
load_dotenv()

st.set_page_config(initial_sidebar_state="expanded", page_title="Chat with a MySQL Database", page_icon=":speech_balloon:")

if 'chat_history' not in st.session_state:
  st.session_state.chat_history = [
    AIMessage(content="")
  ]
  
if 'db' not in st.session_state:
  st.session_state.db = None

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
          st.session_state.db = initialize_database(
            username=st.session_state.username,
            password=st.session_state.password,
            host=st.session_state.name,
            port=st.session_state.port,
            database=st.session_state.database
          )
          if st.session_state.db is not None:
            st.success("Connected to the database!")
    
user_query = st.chat_input("Type a message...")

if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        response = get_response(
            user_query, 
            st.session_state.chat_history,
            st.session_state.db
          )
        print(f"Response generated: {response}")
        st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))

