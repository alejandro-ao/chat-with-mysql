import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

def initialize_database(host, port, username, password, database):
  db_uri = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
  return SQLDatabase.from_uri(db_uri)

def get_sql_chain(db):
    template = """
    Based on the table schema below, write a SQL query that would answer the user's question.
    {schema}

    Write only the SQL query and nothing else. For example:
    Question: which 3 artists have the most tracks?
    SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
    Question: Name 10 artists
    SQL Query: SELECT Name FROM Artist LIMIT 10;
    Question: {question}
    SQL Query:
    """

    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatOpenAI()
    # llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")
    
    def get_schema(_):
      return db.get_table_info()

    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm.bind(stop="\nSQL Result:")
        | StrOutputParser()
    )
  
def get_response(user_query, chat_history, db):

  sql_chain = get_sql_chain(db)
  
  template = """
  Based on the table schema below, question, sql query, and sql response, write a natural language response:
  {schema}

  Conversation History: {chat_history}
  Question: {question}
  SQL Query: {query}
  SQL Response: {response}"""

  prompt = ChatPromptTemplate.from_template(template)
  
  # llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")
  llm = ChatOpenAI()
  
  def get_schema(_):
    return db.get_table_info()
  
  chain = (
    RunnablePassthrough.assign(query=sql_chain).assign(
    schema=get_schema,
    response= lambda vars: db.run(vars["query"])
  )
  | prompt
  | llm
  | StrOutputParser()
  )
  
  return chain.stream({
    "question": user_query,
    "chat_history": chat_history,
  })
  
load_dotenv()

st.set_page_config(initial_sidebar_state="expanded", page_title="Chat with a MySQL Database", page_icon=":speech_balloon:")

if 'chat_history' not in st.session_state:
  st.session_state.chat_history = [
    AIMessage(content="Hello! I'm a chatbot that can help you with your SQL queries. Ask me anything about your database!")
  ]
  
if 'db' not in st.session_state:
  st.session_state.db = None

with st.sidebar:
    st.title("Chat with a MySQL Database")
    st.write("This is a simple chat application allows you to chat with a MySQL database.")

    st.text_input("Host", key="name", value="localhost")
    st.text_input("Port", key="port", value="3306")
    st.text_input("Username", key="username", value="root")
    st.text_input("Password", key="password", type="password", value="admin")
    st.text_input("Database", key="database", value="Chinook")
    
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

# conversation
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)


if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        response = st.write_stream(get_response(
            user_query, 
            st.session_state.chat_history,
            st.session_state.db
          ))
        
    st.session_state.chat_history.append(AIMessage(content=response))

