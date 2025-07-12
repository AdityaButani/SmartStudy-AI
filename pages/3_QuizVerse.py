import streamlit as st
import os
import time
from groq import Groq
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Validate API key
if not groq_api_key:
    st.error("GROQ_API_KEY environment variable is missing. Please set it.")
    st.stop()

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# CSS styles for the application
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
    }

    /* Header Styles */
    .quiz-header {
        text-align: center;
        margin: 2rem 0;
        padding: 2rem;
        background: linear-gradient(45deg, #2b5876 0%, #4e4376 100%);
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* Timer Styles */
    .timer-display {
        font-size: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .timer-warning {
        color: red;
    }

    /* Question Card Styles */
    .question-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .correct-answer {
        color: green;
    }
    .incorrect-answer {
        color: red;
    }

    /* Result Card Styles */
    .result-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .final-score {
        font-size: 1.5rem;
        text-align: center;
        margin-top: 2rem;
    }
    
    /* Description Card Styles */
    .description-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state variables
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "quiz_generated" not in st.session_state:
    st.session_state.quiz_generated = False
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "time_left" not in st.session_state:
    st.session_state.time_left = 0
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "quiz_type" not in st.session_state:
    st.session_state.quiz_type = "mixed"
if "auto_submitted" not in st.session_state:
    st.session_state.auto_submitted = False
if "timer_stop" not in st.session_state:
    st.session_state.timer_stop = False

def generate_question(subject, topic, question_type, difficulty, description, existing_questions, question_marks=None):
    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        prompt = ""

        # Include test description in the prompt for better context
        description_context = f"""
        Additional context about the test:
        {description}
        
        Use this information to generate a more relevant and targeted question.
        """

        if question_type == "mcq":
            prompt = f"""
            Generate a unique multiple-choice quiz question about {topic} in {subject} with {difficulty} difficulty.
            Ensure the question is different from the following list:
            {', '.join([q['question'] for q in existing_questions]) if existing_questions else 'None'}
            
            {description_context}

            Format the quiz exactly as follows:
            Question: [The question]
            A: [Option A]
            B: [Option B]
            C: [Option C]
            D: [Option D]
            Correct Answer: [Single letter A, B, C, or D indicating the correct option]
            """
        elif question_type == "true_false":
            prompt = f"""
            Generate a unique true/false question about {topic} in {subject} with {difficulty} difficulty.
            Ensure the question is different from the following list:
            {', '.join([q['question'] for q in existing_questions]) if existing_questions else 'None'}
            
            {description_context}

            Format the quiz exactly as follows:
            Question: [The statement that is either true or false]
            Correct Answer: [True or False]
            Explanation: [Brief explanation of why the statement is true or false]
            """
        elif question_type == "fill_blank":
            prompt = f"""
            Generate a unique fill-in-the-blank question about {topic} in {subject} with {difficulty} difficulty.
            Ensure the question is different from the following list:
            {', '.join([q['question'] for q in existing_questions]) if existing_questions else 'None'}
            
            {description_context}

            Format the quiz exactly as follows:
            Question: [The sentence with _____ indicating the blank to be filled]
            Correct Answer: [The word or phrase that correctly fills the blank]
            """
        else:  # subjective
            marks_text = f" worth {question_marks} marks" if question_marks else ""
            prompt = f"""
            Generate a unique subjective (open-ended) quiz question about {topic} in {subject} with {difficulty} difficulty{marks_text}.
            Ensure the question is different from the following list:
            {', '.join([q['question'] for q in existing_questions]) if existing_questions else 'None'}
            
            {description_context}

            Format the quiz exactly as follows:
            Question: [The question]
            Ideal Answer: [A comprehensive ideal answer that will be used for grading]
            Key Points: [List 3-5 key points that should be included in a good answer]
            """

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert educational quiz generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
            )

            quiz_text = completion.choices[0].message.content

            if question_type == "mcq":
                question, options, correct_answer = parse_mcq_question(quiz_text)

                if question and question not in [q["question"] for q in existing_questions]:
                    return {
                        "type": "mcq",
                        "question": question,
                        "options": options,
                        "correct_answer": correct_answer,
                        "difficulty": difficulty,
                        "marks": 1  # Each MCQ is worth 1 mark
                    }
            elif question_type == "true_false":
                question, correct_answer, explanation = parse_true_false_question(quiz_text)

                if question and question not in [q["question"] for q in existing_questions]:
                    return {
                        "type": "true_false",
                        "question": question,
                        "correct_answer": correct_answer,
                        "explanation": explanation,
                        "difficulty": difficulty,
                        "marks": 1  # Each True/False is worth 1 mark
                    }
            elif question_type == "fill_blank":
                question, correct_answer = parse_fill_blank_question(quiz_text)

                if question and question not in [q["question"] for q in existing_questions]:
                    return {
                        "type": "fill_blank",
                        "question": question,
                        "correct_answer": correct_answer,
                        "difficulty": difficulty,
                        "marks": 1  # Each Fill in the blank is worth 1 mark
                    }
            else:
                question, ideal_answer, key_points = parse_subjective_question(quiz_text)

                if question and question not in [q["question"] for q in existing_questions]:
                    return {
                        "type": "subjective",
                        "question": question,
                        "ideal_answer": ideal_answer,
                        "key_points": key_points,
                        "difficulty": difficulty,
                        "marks": question_marks or 5  # Default to 5 marks if not specified
                    }

        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None

        attempt += 1
        time.sleep(1)

    st.warning("Unable to generate unique questions. Try again.")
    return None

def parse_mcq_question(quiz_text):
    try:
        lines = quiz_text.strip().split("\n")
        question = None
        options = {}
        correct_answer = None

        for line in lines:
            line = line.strip()
            if line.startswith("Question:"):
                question = line[9:].strip()
            elif line.startswith("A:"):
                options["A"] = line[2:].strip()
            elif line.startswith("B:"):
                options["B"] = line[2:].strip()
            elif line.startswith("C:"):
                options["C"] = line[2:].strip()
            elif line.startswith("D:"):
                options["D"] = line[2:].strip()
            elif line.startswith("Correct Answer:"):
                correct_answer = line[15:].strip().upper()
                # Ensure we only use the first letter if it's more than one character
                if correct_answer and len(correct_answer) >= 1:
                    correct_answer = correct_answer[0]

                # Validate that the answer is one of A, B, C, or D
                if correct_answer not in ["A", "B", "C", "D"]:
                    # Default to A if we can't determine the answer
                    correct_answer = "A"

        return question, options, correct_answer
    except Exception as e:
        st.error(f"Error parsing MCQ question: {str(e)}")
        return None, None, None

def parse_true_false_question(quiz_text):
    try:
        lines = quiz_text.strip().split("\n")
        question = None
        correct_answer = None
        explanation = None

        for line in lines:
            line = line.strip()
            if line.startswith("Question:"):
                question = line[9:].strip()
            elif line.startswith("Correct Answer:"):
                answer_text = line[15:].strip().lower()
                if "true" in answer_text:
                    correct_answer = True
                elif "false" in answer_text:
                    correct_answer = False
                else:
                    # Default to True if we can't determine
                    correct_answer = True
            elif line.startswith("Explanation:"):
                explanation = line[12:].strip()

        return question, correct_answer, explanation
    except Exception as e:
        st.error(f"Error parsing True/False question: {str(e)}")
        return None, None, None

def parse_fill_blank_question(quiz_text):
    try:
        lines = quiz_text.strip().split("\n")
        question = None
        correct_answer = None

        for line in lines:
            line = line.strip()
            if line.startswith("Question:"):
                question = line[9:].strip()
            elif line.startswith("Correct Answer:"):
                correct_answer = line[15:].strip()

        return question, correct_answer
    except Exception as e:
        st.error(f"Error parsing Fill-in-the-blank question: {str(e)}")
        return None, None

def parse_subjective_question(quiz_text):
    try:
        parts = quiz_text.split("Question:")
        if len(parts) > 1:
            content = "Question:" + parts[1]
            lines = content.strip().split("\n")

            question = None
            ideal_answer = None
            key_points = []
            current_section = None

            for line in lines:
                line = line.strip()
                if line.startswith("Question:"):
                    question = line[9:].strip()
                    current_section = "question"
                elif line.startswith("Ideal Answer:"):
                    ideal_answer = line[13:].strip()
                    current_section = "ideal_answer"
                elif line.startswith("Key Points:"):
                    current_section = "key_points"
                elif current_section == "ideal_answer" and line and not line.startswith("Key Points:"):
                    if not ideal_answer:
                        ideal_answer = line
                    else:
                        ideal_answer += " " + line
                elif current_section == "key_points" and line and (line.startswith("-") or line.startswith("•") or any(str(i)+"." in line for i in range(1, 10))):
                    # Extract the key point without the bullet or number
                    for prefix in ["-", "•"] + [f"{i}." for i in range(1, 10)]:
                        if line.startswith(prefix):
                            key_points.append(line[len(prefix):].strip())
                            break
                    else:
                        key_points.append(line)

            # If no key points were extracted with bullets, try to split by commas or periods
            if not key_points and ideal_answer:
                # First try to see if there's a sentence that mentions key points
                for sentence in ideal_answer.split('.'):
                    if "key point" in sentence.lower():
                        potential_points = sentence.split(',')
                        if len(potential_points) > 1:
                            key_points = [pt.strip() for pt in potential_points]
                            break

                # If still no key points, generate some from the ideal answer
                if not key_points:
                    key_points = [pt.strip() for pt in ideal_answer.split('.') if pt.strip()][:3]

            return question, ideal_answer, key_points[:5]  # Limit to 5 key points
        return None, None, None
    except Exception as e:
        st.error(f"Error parsing subjective question: {str(e)}")
        return None, None, None

def grade_subjective_answer(user_answer, question_data):
    try:
        prompt = f"""
        Grade this subjective answer for a quiz question worth {question_data['marks']} marks.

        Question: {question_data['question']}
        Student's Answer: {user_answer if user_answer else "(No answer provided)"}

        For reference, an ideal answer would include:
        {question_data['ideal_answer']}

        The key points that should be covered are:
        {', '.join(question_data['key_points'])}

        Analyze how well the student's answer addresses the key points and provide:
        1. A score from 0-{question_data['marks']}
        2. A brief explanation of the score
        3. Which key points were addressed well or missed

        Format:
        Score: [0-{question_data['marks']}]
        Feedback: [Explanation]
        Key Points Addressed: [List of covered points]
        Key Points Missed: [List of missed points]
        """

        completion = client.chat.completions.create(
            model="mistral-saba-24b",
            messages=[
                {"role": "system", "content": "You are an expert educational grader. Be fair but thorough."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500,
        )

        response = completion.choices[0].message.content

        score = 0
        feedback = ""
        points_addressed = []
        points_missed = []

        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("Score:"):
                try:
                    score_text = line[6:].strip()
                    # Handle score ranges like "8/10" or "8 out of 10"
                    if "/" in score_text:
                        score = float(score_text.split("/")[0].strip())
                    elif "out of" in score_text:
                        score = float(score_text.split("out of")[0].strip())
                    else:
                        score = float(score_text)
                except:
                    score = 0
            elif line.startswith("Feedback:"):
                feedback = line[9:].strip()
            elif line.startswith("Key Points Addressed:"):
                points_text = line[21:].strip()
                if points_text and points_text.lower() != "none":
                    points_addressed = [pt.strip() for pt in points_text.split(",")]
            elif line.startswith("Key Points Missed:"):
                points_text = line[18:].strip()
                if points_text and points_text.lower() != "none":
                    points_missed = [pt.strip() for pt in points_text.split(",")]

        return {
            "score": min(max(score, 0), question_data['marks']),  # Ensure score is between 0 and max marks
            "feedback": feedback,
            "points_addressed": points_addressed,
            "points_missed": points_missed
        }

    except Exception as e:
        st.error(f"Error grading answer: {str(e)}")
        return {"score": 0, "feedback": "Error grading answer", "points_addressed": [], "points_missed": []}

def update_timer():
    while not st.session_state.timer_stop and st.session_state.timer_running and st.session_state.time_left > 0:
        time.sleep(1)
        st.session_state.time_left -= 1
        if st.session_state.time_left <= 0:
            st.session_state.quiz_submitted = True
            st.session_state.auto_submitted = True
            st.session_state.timer_running = False
            break

# Main UI
st.markdown("<div class='quiz-header'><h1>🎓QuizVerse - AI Quiz Generator</h1><p>Test your knowledge with AI-generated questions</p></div>", unsafe_allow_html=True)

# Input fields
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("📚 Subject:", placeholder="e.g., Physics")
        topic = st.text_input("📖 Topic:", placeholder="e.g., Gravitation")
        difficulty = st.select_slider("Difficulty:", options=["Easy", "Medium", "Hard"], value="Medium")
    with col2:
        num_questions = st.number_input("❓ Number of questions:", min_value=1, max_value=20, value=10)
        quiz_time = st.number_input("⏱️ Time limit (minutes):", min_value=1, max_value=120, value=15)

# Test description section - NEW ADDITION
st.markdown("### 📝 Test Description")
st.markdown("""
<div class='description-card'>
    <p>Enter a description of the test, including detailed syllabus information. This will help generate more relevant questions.</p>
</div>
""", unsafe_allow_html=True)

test_description = st.text_area(
    "Describe the test scope and syllabus:",
    placeholder="E.g., This test covers chapters 1-3 from the Physics textbook: Newton's Laws of Motion, Work & Energy, and Gravitation. It focuses on problem-solving and theoretical concepts with special emphasis on applications of Newton's Second Law and Conservation of Energy.",
    height=150
)

# Question format options
st.markdown("### Select Question Formats")
col1, col2 = st.columns(2)

with col1:
    include_mcq = st.checkbox("Multiple Choice Questions (1 mark each)", value=True)
    include_true_false = st.checkbox("True/False Questions (1 mark each)", value=False)
with col2:
    include_fill_blank = st.checkbox("Fill in the Blank (1 mark each)", value=False)
    include_subjective = st.checkbox("Subjective Questions", value=True)

# Only show subjective question options if subjective is selected
if include_subjective:
    subjective_marks = st.select_slider(
        "Marks per subjective question:",
        options=[5, 10, 15, 20],
        value=5
    )

# Generate quiz
if st.button("Generate Quiz", type="primary"):
    if subject and topic:
        # Check that at least one question type is selected
        if not any([include_mcq, include_true_false, include_fill_blank, include_subjective]):
            st.warning("Please select at least one question type.")
        else:
            st.session_state.quiz_data = []
            st.session_state.user_answers = {}
            st.session_state.quiz_generated = False
            st.session_state.quiz_submitted = False
            st.session_state.auto_submitted = False
            st.session_state.timer_stop = False

            # Create a list of question types to include
            question_types = []
            if include_mcq:
                question_types.append("mcq")
            if include_true_false:
                question_types.append("true_false")
            if include_fill_blank:
                question_types.append("fill_blank")
            if include_subjective:
                question_types.append("subjective")

            progress_bar = st.progress(0)
            with st.spinner("Generating your quiz..."):
                questions_per_type = num_questions // len(question_types)
                remaining = num_questions % len(question_types)

                question_count = 0
                for q_type in question_types:
                    type_count = questions_per_type + (1 if remaining > 0 else 0)
                    remaining -= 1 if remaining > 0 else 0

                    for i in range(type_count):
                        q_marks = subjective_marks if q_type == "subjective" else None
                        quiz_question = generate_question(subject, topic, q_type, difficulty, test_description, st.session_state.quiz_data, q_marks)
                        if quiz_question:
                            st.session_state.quiz_data.append(quiz_question)
                            question_count += 1
                            progress_bar.progress(question_count / num_questions)

                if st.session_state.quiz_data:
                    st.session_state.quiz_generated = True
                    st.session_state.time_left = quiz_time * 60
                    st.session_state.timer_running = True
                    # Start the timer in a separate thread
                    timer_thread = threading.Thread(target=update_timer)
                    timer_thread.daemon = True  # Thread will close when main program exits
                    timer_thread.start()
    else:
        st.warning("Please enter both subject and topic.")

# Show test description on quiz page if one was provided
if st.session_state.quiz_generated and not st.session_state.quiz_submitted and test_description:
    st.markdown(f"""
    <div class="description-card">
        <h4>📚 Test Information</h4>
        <p>{test_description}</p>
    </div>
    """, unsafe_allow_html=True)

# Display quiz
if st.session_state.quiz_generated and not st.session_state.quiz_submitted:
    # Timer display
    timer_placeholder = st.empty()

    mins, secs = divmod(st.session_state.time_left, 60)
    timer_class = "timer-warning" if st.session_state.time_left < 60 else ""
    timer_placeholder.markdown(f"""
    <div class="timer-display {timer_class}">
        Time Remaining: {mins:02d}:{secs:02d}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📝 Answer all questions below")

    with st.form(key="quiz_form"):
        for i, question in enumerate(st.session_state.quiz_data):
            st.markdown(f"""
            <div class="question-card">
                <h4>Question {i + 1} ({question['type'].capitalize()} - {question['difficulty']} - {question['marks']} mark{'s' if question['marks'] > 1 else ''})</h4>
                <p>{question["question"]}</p>
            </div>
            """, unsafe_allow_html=True)

            if question["type"] == "mcq":
                st.session_state.user_answers[i] = st.radio(
                    f"Select your answer for Question {i+1}:",
                    options=list(question['options'].keys()),
                    format_func=lambda x: f"{x}: {question['options'][x]}",
                    key=f"answer_{i}"
                )
            elif question["type"] == "true_false":
                st.session_state.user_answers[i] = st.radio(
                    f"Select your answer for Question {i+1}:",
                    options=["True", "False"],
                    key=f"answer_{i}"
                )
            elif question["type"] == "fill_blank":
                st.session_state.user_answers[i] = st.text_input(
                    f"Your answer for Question {i+1}:",
                    key=f"answer_{i}"
                )
            else:  # subjective
                st.session_state.user_answers[i] = st.text_area(
                    f"Your answer for Question {i+1} ({question['marks']} marks):",
                    key=f"answer_{i}",
                    height=150
                )

            st.markdown("<hr>", unsafe_allow_html=True)

        submit_button = st.form_submit_button(label="Submit Quiz", type="primary")
        if submit_button:
            st.session_state.quiz_submitted = True
            st.session_state.timer_running = False
            st.session_state.timer_stop = True

# Auto-submit notification
if st.session_state.auto_submitted and st.session_state.quiz_submitted:
    st.warning("⏱️ Time's up! Your quiz has been automatically submitted.")

# Show results
if st.session_state.quiz_submitted:
    st.markdown("<div class='result-card'><h2>📊 Quiz Results</h2>", unsafe_allow_html=True)

    # Show test description in results too
    if test_description:
        st.markdown(f"""
        <div class="description-card">
            <h4>📚 Test Information</h4>
            <p>{test_description}</p>
        </div>
        """, unsafe_allow_html=True)

    total_score = 0
    max_score = sum(q['marks'] for q in st.session_state.quiz_data)

    for i, question in enumerate(st.session_state.quiz_data):
        user_answer = st.session_state.user_answers.get(i, "")

        if question["type"] == "mcq":
            correct_answer = question["correct_answer"]
            question_score = question['marks'] if user_answer == correct_answer else 0
            total_score += question_score

            if user_answer == correct_answer:
                st.markdown(f"""
                <div class='question-card'>
                    <h4>Question {i+1} (MCQ - {question['difficulty']} - {question['marks']} mark)</h4>
                    <p>{question["question"]}</p>
                    <div class='correct-answer'>✨ Correct Answer: {correct_answer}: {question['options'][correct_answer]}</div>
                    <p>Score: {question_score}/{question['marks']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                selected_answer_text = question['options'].get(user_answer, 'Not answered')
                st.markdown(f"""
                <div class='question-card'>
                    <h4>Question {i+1} (MCQ - {question['difficulty']} - {question['marks']} mark)</h4>
                    <p>{question["question"]}</p>
                    <div class='incorrect-answer'>❌ Your Answer: {user_answer}: {selected_answer_text}</div>
                    <div class='correct-answer'>✅ Correct Answer: {correct_answer}: {question['options'][correct_answer]}</div>
                    <p>Score: 0/{question['marks']}</p>
                </div>
                """, unsafe_allow_html=True)

        elif question["type"] == "true_false":
            correct_answer = "True" if question["correct_answer"] else "False"
            question_score = question['marks'] if user_answer == correct_answer else 0
            total_score += question_score

            if user_answer == correct_answer:
                st.markdown(f"""
                <div class='question-card'>
                    <h4>Question {i+1} (True/False - {question['difficulty']} - {question['marks']} mark)</h4>
                    <p>{question["question"]}</p>
                    <div class='correct-answer'>✨ Correct Answer: {correct_answer}</div>
                    <p><strong>Explanation:</strong> {question['explanation']}</p>
                    <p>Score: {question_score}/{question['marks']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='question-card'>
                    <h4>Question {i+1} (True/False - {question['difficulty']} - {question['marks']} mark)</h4>
                    <p>{question["question"]}</p>
                    <div class='incorrect-answer'>❌ Your Answer: {user_answer}</div>
                    <div class='correct-answer'>✅ Correct Answer: {correct_answer}</div>
                    <p><strong>Explanation:</strong> {question['explanation']}</p>
                    <p>Score: 0/{question['marks']}</p>
                </div>
                """, unsafe_allow_html=True)

        elif question["type"] == "fill_blank":
            # Case-insensitive comparison for fill in the blank
            question_score = question['marks'] if user_answer.strip().lower() == question["correct_answer"].lower() else 0
            total_score += question_score

            if question_score > 0:
                st.markdown(f"""
                <div class='question-card'>
                    <h4>Question {i+1} (Fill in the Blank - {question['difficulty']} - {question['marks']} mark)</h4>
                    <p>{question["question"]}</p>
                    <div class='correct-answer'>✨ Your Answer: {user_answer} is correct!</div>
                    <p>Score: {question_score}/{question['marks']}</p>
                </div>
                """, unsafe_allow_html=True)