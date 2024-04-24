import streamlit as st
import os
import sys
sys.path.append(os.path.abspath('../../'))

class QuizManager:
    def __init__(self, questions: list):
        """
        Initialize the QuizManager class with a list of quiz questions.

        """
        self.questions=questions
        self.num_of_questions=len(questions)


    def get_question_at_index(self, index: int):
        """
        Retrieves the quiz question object at the specified index. If the index is out of bounds,
        it restarts from the beginning index.

        :param index: The index of the question to retrieve.
        :return: The quiz question object at the specified index, with indexing wrapping around if out of bounds.
        """
        # Ensure index is always within bounds using modulo arithmetic
        valid_index = index % self.num_of_questions
        return self.questions[valid_index]

    def next_question_index(self, direction=1):
        """
        Adjust the current quiz question index based on the specified direction.
        """

        current_question_index=st.session_state["question_index"]
        valid_index = (current_question_index+direction) % self.num_of_questions # Ensure index is always within bounds using modulo arithmetic
        st.session_state.question_index=valid_index
     
    def reset_quiz_state(self):
        st.session_state['question_bank'] = []

