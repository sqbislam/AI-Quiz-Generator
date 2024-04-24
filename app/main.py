import streamlit as st
import os
import sys

from app.collection_creator import ChromaCollectionCreator
from app.document_processor import DocumentProcessor
from app.embedding_client import EmbeddingClient
from app.manager import QuizManager
sys.path.append(os.path.abspath('../../'))
from app.generator import QuizGenerator
from constants import CONFIG
import asyncio

if __name__ == "__main__":    
    # Add Session State
    if 'question_bank' not in st.session_state or len(st.session_state['question_bank']) == 0:
    
        st.session_state['question_bank']=[]
        screen = st.empty()
        
        with screen.container():
            st.header("Quiz Builder")
            
            # Create a new st.form flow control for Data Ingestion
            with st.form("Load Data to Chroma"):
                st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")
                
                processor = DocumentProcessor()
                processor.ingest_documents()
                embed_client = EmbeddingClient(**CONFIG.EMBED_CONFIG.value) 
                chroma_creator = ChromaCollectionCreator(processor, embed_client)
                topic_input = st.text_input("Topic for Quiz", placeholder="Enter the topic for the quiz")
                questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)

                    
                submitted = st.form_submit_button("Submit")
                
                if submitted:
                    chroma_creator.create_chroma_collection()
                        
                    if len(processor.pages) > 0:
                        st.write(f"Generating {questions} questions for topic: {topic_input}")
                    

                    # Initialize a QuizGenerator with spinner
                    with st.spinner("Generating Quiz..."):
                        generator = QuizGenerator(topic_input, questions, chroma_creator)
                        question_bank = asyncio.run(generator.generate_quiz())

                        st.session_state["question_bank"] = question_bank
                        st.session_state["display_quiz"] = True
                        st.session_state["question_index"] = 0
                        st.session_state["score"] = 0
                        st.session_state["last_question"] = False

                    st.form_submit_button("Start Quiz")


    elif st.session_state['display_quiz']:
        st.empty()
        with st.container():
            st.header("Generated Quiz Question: ")
            quiz_manager = QuizManager(st.session_state['question_bank'])
            
            # Format the question and display it
            with st.form("MCQ"):
                index_question=quiz_manager.get_question_at_index(st.session_state['question_index'])
                
                # Unpack choices for radio button
                choices = []
                for choice in index_question['choices']:
                    key = choice['key']
                    value = choice['value']
                    choices.append(f"{key}) {value}")
                
                # Display the Question
                st.write(f"{st.session_state['question_index'] + 1}. {index_question['question']}")
                answer = st.radio(
                    "Choose an answer",
                    choices,
                    index = None
                )
                
                answer_choice = st.form_submit_button("Submit")
                

                # Navigate to the next and previous questions

                st.form_submit_button("Next Question", on_click= quiz_manager.next_question_index,kwargs={"direction":1})
                st.form_submit_button("Previous Question", on_click= quiz_manager.next_question_index,kwargs={"direction":-1})
                
                if answer_choice and answer is not None:
                    correct_answer_key = index_question['answer']
                    if answer.startswith(correct_answer_key):
                        st.success("Correct!")
                    else:
                        st.error("Incorrect!")
                    st.write(f"Explanation: {index_question['explanation']}")
                
                st.form_submit_button("Generate again 🔄", on_click=quiz_manager.reset_quiz_state)