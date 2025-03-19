# Import the required libraries
import os
import streamlit as st
import google.generativeai as genai
from deep_translator import GoogleTranslator
from gtts import gTTS
from io import BytesIO
import base64
import requests
from PIL import Image
import speech_recognition as sr
from streamlit_option_menu import option_menu
from dotenv import load_dotenv  # Import the dotenv library

# Load environment variables from .env file
load_dotenv()

# Page icon
icon = Image.open(r"C:\Users\rishi\Desktop\Vijaya\Logo.png")

# Page configuration
st.set_page_config(
    page_title="🤖 AI-Powered Mental Health Therapist Chatbot",
    page_icon=icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("<h2 style='text-align: center; color: #000080;'>Ramachandra College of Engineering</h2>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #BDB76B;'>Department of Artificial Intelligence & Data Science</h2>", unsafe_allow_html=True)
st.text("")
st.text("")

# Page Styling
st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6;
    }
    .chat-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        max-width: 800px; /* Adjusted width */
        margin: auto;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .chat-bubble {
        max-width: 70%;
        padding: 12px 16px;
        border-radius: 15px;
        margin-bottom: 10px;
        position: relative;
        word-wrap: break-word;
    }
    .chat-bubble.user {
        background-color: #dcf8c6; /* Light green */
        margin-left: auto;
        margin-right: 0;
        border-bottom-right-radius: 5px;
    }
    .chat-bubble.bot {
        background-color: #f0f0f0; /* Light gray */
        margin-left: 0;
        margin-right: auto;
        border-bottom-left-radius: 5px;
    }
    .chat-input {
        display: flex;
        gap: 5px; /* Reduced gap between buttons */
        padding: 10px;
        background-color: #ffffff;
        border-radius: 15px;
        margin-top: 20px;
    }
    .chat-input input {
        flex: 1;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 15px;
        outline: none;
    }
    .chat-input button {
        background-color: #25d366; /* WhatsApp green */
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .chat-input button.mic {
        background-color: #f0f2f6;
        color: #333;
    }
    /* Adjust text area width */
    .stTextArea textarea {
        width: 90% !important; /* Adjusted width */
    }
    /* Reduce space between buttons */
    .stButton button {
        margin-right: 5px; /* Adjusted spacing */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.sidebar.image(icon, use_container_width=True)
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Project Details", "Contact", "Settings"],
        icons=["house", "book", "envelope", "gear"],  # optional
        menu_icon="cast",  # optional
        default_index=0,  # optional
    )

# Home Section
if selected == "Home":
    # Load API keys from .env file
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Gemini API key
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # YouTube API key

    # Configure Google Generative AI
    genai.configure(api_key=GOOGLE_API_KEY)

    # Function to autoplay audio in Streamlit
    def autoplay_audio(audio_data):
        b64 = base64.b64encode(audio_data).decode()
        md = f"""
            <audio controls autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

    # Function to translate text based on selected language
    def translate_text(text, target_lang):
        if target_lang == "English":
            return text
        elif target_lang == "Telugu":
            return GoogleTranslator(source='en', target='te').translate(text)
        elif target_lang == "Hindi":
            return GoogleTranslator(source='en', target='hi').translate(text)

    # Function to display chat messages in a modern chat interface
    def display_chat_message(role, message):
        if role == "bot":
            st.markdown(
                f'<div class="chat-bubble bot">'
                f'<b>🤖 Bot:</b> {message}'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-bubble user">'
                f'<b>👤 You:</b> {message}'
                '</div>',
                unsafe_allow_html=True
            )

    # Function to clean user input (remove empty lines and trim spaces)
    def clean_input(text):
        lines = text.splitlines()  # Split into lines
        non_empty_lines = [line.strip() for line in lines if line.strip()]  # Remove empty lines and trim spaces
        return "\n".join(non_empty_lines)  # Join non-empty lines

    # Function to generate YouTube video links using the API
    def generate_youtube_links(query):
        base_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 5,  # Number of videos to fetch
            "key": YOUTUBE_API_KEY
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            videos = response.json().get("items", [])
            video_links = []
            for video in videos:
                video_id = video["id"]["videoId"]
                video_title = video["snippet"]["title"]
                video_links.append((video_title, f"https://www.youtube.com/watch?v={video_id}"))
            return video_links
        else:
            return ["Failed to fetch videos. Please try again later."]

    # Function to generate images based on user's reason and feelings
    def generate_images(reason, feelings):
        search_query = f"{reason} {feelings}"
        try:
            response = requests.get(f"https://source.unsplash.com/400x300/?{search_query}")
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
            else:
                return None
        except Exception as e:
            st.error(f"Error fetching image: {e}")
            return None

    # Function to convert text to speech using gTTS
    def text_to_speech(text, language):
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            return audio_bytes.read()
        except Exception as e:
            st.error(f"Error generating audio: {e}")
            return None

    # Function to convert speech to text using speech_recognition
    def speech_to_text():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("🎤 Speak now...")
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                st.error("Sorry, I could not understand the audio.")
                return None
            except sr.RequestError:
                st.error("Sorry, there was an issue with the speech recognition service.")
                return None

    # Initialize session state for storing conversation and response parts
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'response_parts' not in st.session_state:
        st.session_state.response_parts = {}
    if 'step' not in st.session_state:
        st.session_state.step = 1

    # Input language selection moved to Settings page
    if 'input_language' not in st.session_state:
        st.session_state.input_language = "English"

    # Start the conversation
    if not st.session_state.conversation:
        # Translate initial bot message based on selected language
        initial_message = translate_text("Hi! How are you feeling today?", st.session_state.input_language)
        st.session_state.conversation.append({"role": "bot", "message": initial_message})
        st.session_state.step = 1

    # Display the conversation within a container box
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.conversation:
        display_chat_message(msg["role"], msg["message"])
    st.markdown('</div>', unsafe_allow_html=True)

    # Step 1: Ask how the user is feeling
    if st.session_state.step == 1:
        feelings_placeholder = {
            "English": "e.g., feeling anxious about my upcoming presentation",
            "Telugu": "e.g., నా రాబోయే ప్రెజెంటేషన్ గురించి ఆందోళన చెందుతున్నాను",
            "Hindi": "e.g., अपनी आगामी प्रस्तुति के बारे में चिंतित महसूस कर रहा हूँ"
        }
        
        # Translate the text area label based on selected language
        feelings_label = translate_text("How are you feeling right now?", st.session_state.input_language)
        
        # Create a container for the text area and submit button
        col1, col2 = st.columns([4, 1])  # Adjust column widths as needed
        
        with col1:
            feelings = st.text_area(
                f"{feelings_label} (in {st.session_state.input_language})",
                placeholder=feelings_placeholder[st.session_state.input_language],
                height=100
            )
        
        with col2:
            st.write("")  # Add some vertical space for alignment
            st.write("")  # Add some vertical space for alignment
            if st.button("Submit", key="submit_feelings"):
                if feelings.strip():
                    cleaned_feelings = clean_input(feelings)  # Clean user input
                    st.session_state.feelings = cleaned_feelings
                    st.session_state.conversation.append({"role": "user", "message": cleaned_feelings})
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("Please enter how you are feeling to proceed.")
        
        # Add the "Speak" button below the text area and submit button
        if st.button("🎤 Speak"):
            user_input = speech_to_text()
            if user_input:
                st.session_state.feelings = user_input
                st.session_state.conversation.append({"role": "user", "message": user_input})
                st.session_state.step = 2
                st.rerun()

    # Step 2: Ask for the reason behind the problem
    if st.session_state.step == 2:
        # Translate the question based on selected language
        reason_question = translate_text("Can you tell me more about why you're feeling this way?", st.session_state.input_language)
        display_chat_message("bot", reason_question)

        reason_placeholder = {
            "English": "e.g., I have a big presentation tomorrow, and I'm worried I'll mess up",
            "Telugu": "e.g., నాకు రేపు పెద్ద ప్రెజెంటేషన్ ఉంది, మరియు నేను దానిని పాడు చేస్తానని భయపడుతున్నాను",
            "Hindi": "e.g., मेरी कल एक बड़ी प्रस्तुति है, और मुझे डर है कि मैं इसे खराब कर दूंगा"
        }
        
        # Translate the text area label based on selected language
        reason_label = translate_text("Can you tell me more about why you're feeling this way?", st.session_state.input_language)
        
        # Create a container for the text area and submit button
        col1, col2 = st.columns([4, 1])  # Adjust column widths as needed
        
        with col1:
            reason = st.text_area(
                f"{reason_label} (in {st.session_state.input_language})",
                placeholder=reason_placeholder[st.session_state.input_language],
                height=100
            )
        
        with col2:
            st.write("")  # Add some vertical space for alignment
            st.write("")  # Add some vertical space for alignment
            if st.button("Submit", key="submit_reason"):
                if reason.strip():
                    cleaned_reason = clean_input(reason)  # Clean user input
                    st.session_state.reason = cleaned_reason
                    st.session_state.conversation.append({"role": "user", "message": cleaned_reason})
                    st.session_state.step = 3  # Move to step 3 for detailed situation
                    st.rerun()
                else:
                    st.error("Please provide more details to proceed.")
        
        # Add the "Speak" button below the text area and submit button
        if st.button("🎤 Speak", key="speak_reason"):
            user_input = speech_to_text()
            if user_input:
                st.session_state.reason = user_input
                st.session_state.conversation.append({"role": "user", "message": user_input})
                st.session_state.step = 3
                st.rerun()

    # Step 3: Ask for detailed situation
    if st.session_state.step == 3:
        # Translate the question based on selected language
        detailed_question = translate_text("Can you explain your situation in more detail? This will help me provide better suggestions.", st.session_state.input_language)
        display_chat_message("bot", detailed_question)

        detailed_placeholder = {
            "English": "e.g., I have a lot of work pressure, and I'm struggling to manage my time.",
            "Telugu": "e.g., నాకు చాలా వర్క్ ప్రెజర్ ఉంది, మరియు నేను నా టైమ్ ని మేనేజ్ చేయడంలో కష్టపడుతున్నాను.",
            "Hindi": "e.g., मुझे बहुत काम का दबाव है, और मैं अपने समय को प्रबंधित करने के लिए संघर्ष कर रहा हूँ।"
        }
        
        # Translate the text area label based on selected language
        detailed_label = translate_text("Can you explain your situation in more detail?", st.session_state.input_language)
        
        # Create a container for the text area and submit button
        col1, col2 = st.columns([4, 1])  # Adjust column widths as needed
        
        with col1:
            detailed_situation = st.text_area(
                f"{detailed_label} (in {st.session_state.input_language})",
                placeholder=detailed_placeholder[st.session_state.input_language],
                height=100
            )
        
        with col2:
            st.write("")  # Add some vertical space for alignment
            st.write("")  # Add some vertical space for alignment
            if st.button("Submit", key="submit_detailed"):
                if detailed_situation.strip():
                    cleaned_situation = clean_input(detailed_situation)  # Clean user input
                    st.session_state.detailed_situation = cleaned_situation
                    st.session_state.conversation.append({"role": "user", "message": cleaned_situation})
                    st.session_state.step = 4  # Move to step 4 for final response
                    st.rerun()
                else:
                    st.error("Please provide more details to proceed.")
        
        # Add the "Speak" button below the text area and submit button
        if st.button("🎤 Speak", key="speak_detailed"):
            user_input = speech_to_text()
            if user_input:
                st.session_state.detailed_situation = user_input
                st.session_state.conversation.append({"role": "user", "message": user_input})
                st.session_state.step = 4
                st.rerun()

    # Step 4: Provide detailed CBT and DBT-based solutions (Final Step)
    if st.session_state.step == 4 and 'response' not in st.session_state.response_parts:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Retrieve user input from session state
        feelings = st.session_state.get('feelings', '')
        reason = st.session_state.get('reason', '')
        detailed_situation = st.session_state.get('detailed_situation', '')

        # Translate input to English if not already in English
        if st.session_state.input_language == "Telugu":
            status_text.text("Translating from Telugu...")
            progress_bar.progress(20)
            translated_feelings = GoogleTranslator(source='te', target='en').translate(feelings)
            translated_reason = GoogleTranslator(source='te', target='en').translate(reason)
            translated_situation = GoogleTranslator(source='te', target='en').translate(detailed_situation)
        elif st.session_state.input_language == "Hindi":
            status_text.text("Translating from Hindi...")
            progress_bar.progress(20)
            translated_feelings = GoogleTranslator(source='hi', target='en').translate(feelings)
            translated_reason = GoogleTranslator(source='hi', target='en').translate(reason)
            translated_situation = GoogleTranslator(source='hi', target='en').translate(detailed_situation)
        else:
            translated_feelings = feelings
            translated_reason = reason
            translated_situation = detailed_situation
            progress_bar.progress(30)
        
        status_text.text("Analyzing your feelings and reason...")
        progress_bar.progress(40)
        
        prompt = f"""
        You are a highly intelligent and empathetic AI-powered mental health therapist.
        A user has described their feelings, the reason behind them, and their detailed situation as follows:
        Feelings: {translated_feelings}
        Reason: {translated_reason}
        Detailed Situation: {translated_situation}

        Please provide:
        1. A detailed step-by-step solution using CBT and DBT techniques to help the user overcome their problem.
        2. Specific exercises or activities the user can do to feel better (e.g., breathing exercises, journaling).
        3. Words of encouragement and reassurance.
        """

        try:
            model = genai.GenerativeModel('gemini-1.5-flash-002')
            response = model.generate_content(prompt)
            progress_bar.progress(70)
            
            full_response = response.text
            
            if st.session_state.input_language != "English":
                status_text.text(f"Translating response to {st.session_state.input_language}...")
                progress_bar.progress(90)
                target_lang = 'te' if st.session_state.input_language == "Telugu" else 'hi'
                translated_response = GoogleTranslator(source='en', target=target_lang).translate(full_response)
                st.session_state.response_parts['response'] = translated_response
            else:
                st.session_state.response_parts['response'] = full_response

            progress_bar.progress(100)
            status_text.empty()
            st.rerun()

        except Exception as e:
            st.error(f"Error generating response: {e}")

    # Display the response only once
    if st.session_state.step == 4 and 'response' in st.session_state.response_parts:
        st.write("### ✅ Suggested Solutions:")
        display_chat_message("bot", st.session_state.response_parts['response'])

        # Generate YouTube links and images based on user's reason and feelings
        feelings = st.session_state.get('feelings', '')
        reason = st.session_state.get('reason', '')
        
        if feelings and reason:
            # Generate YouTube link
            query = f"{reason} {feelings} mental health tips"
            video_links = generate_youtube_links(query)

            st.write("### 🎥 Recommended Videos:")
            for title, link in video_links:
                st.markdown(f"- [{title}]({link})")

            # Generate image
            image = generate_images(reason, feelings)
            if image:
                st.write("### 📸 Related Image:")
                st.image(image, caption="Related to your situation", use_container_width=True)

        # Automatically generate and play audio
        if 'response' in st.session_state.response_parts:
            response_text = st.session_state.response_parts['response']
            language_map = {"English": "en", "Telugu": "te", "Hindi": "hi"}
            
            # Generate audio
            audio_data = text_to_speech(response_text, language_map[st.session_state.input_language])
            if audio_data:
                st.write("### 🔊 Listen to the response:")
                autoplay_audio(audio_data)
            else:
                st.error("Failed to generate audio. Please try again.")

# Project Details Section
elif selected == "Project Details":
    # Header
    st.markdown("<h2 style='text-align: center; color: SlateGray;'>Project Details</h2>", unsafe_allow_html=True)
    st.write("")  # Add some space

    # Project Title
    st.markdown("<h3 style='color: #000080;'>Title:</h3>", unsafe_allow_html=True)
    st.write("🤖 AI-Powered Mental Health Therapist Chatbot")
    st.write("")  # Add some space

    # About the Project
    st.markdown("<h3 style='color: #000080;'>About the Project:</h3>", unsafe_allow_html=True)
    st.write("""
    The **AI-Powered Mental Health Therapist Chatbot** is an innovative application designed to provide mental health support and therapeutic guidance using advanced artificial intelligence (AI) technologies. 
    The chatbot leverages **Cognitive Behavioral Therapy (CBT)** and **Dialectical Behavior Therapy (DBT)** techniques to offer personalized, empathetic, and actionable solutions to users experiencing mental health challenges.
    """)
    st.write("")  # Add some space

    # Key Features
    st.markdown("<h3 style='color: #000080;'>Key Features:</h3>", unsafe_allow_html=True)
    st.write("""
    - **Multilingual Support**: Interact in English, Telugu, or Hindi.
    - **Voice and Text Input**: Speak or type to communicate with the chatbot.
    - **Personalized Mental Health Support**: Get tailored advice based on your feelings and situation.
    - **Therapeutic Exercises**: Learn breathing exercises, journaling, and mindfulness practices.
    - **Visual and Audio Support**: View related images and listen to audio responses.
    - **YouTube Video Recommendations**: Access additional resources like guided meditations and motivational talks.
    """)
    st.write("")  # Add some space

    # Technologies Used
    st.markdown("<h3 style='color: #000080;'>Technologies Used:</h3>", unsafe_allow_html=True)
    st.write("""
    - **Streamlit**: For building the web application interface.
    - **Google Generative AI (Gemini)**: For generating personalized responses.
    - **Deep Translator**: For multilingual support.
    - **gTTS (Google Text-to-Speech)**: For converting text responses to audio.
    - **SpeechRecognition Library**: For speech-to-text functionality.
    - **YouTube Data API**: For fetching relevant YouTube videos.
    - **Unsplash API**: For generating related images.
    - **PIL (Python Imaging Library)**: For image processing.
    - **Base64**: For encoding and decoding audio files.
    """)
    st.write("")  # Add some space

    # Display Logo
    st.markdown("<h3 style='color: #000080;'>Project Logo:</h3>", unsafe_allow_html=True)
    logo_path = r"C:\Users\rishi\Desktop\Vijaya\Logo.png" # Update the path to your logo
    try:
        logo = Image.open(logo_path)
        st.image(logo, caption="AI-Powered Mental Health Therapist Chatbot", width=300, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading logo: {e}")    
# Contact Section
elif selected == "Contact":
    # Header
    st.markdown("<h2 class='sider-title' style='color: SlateGray;'>Project Team</h2>", unsafe_allow_html=True)
    st.text("")
   
    # Team member details
    team_members = [
        {
            "name": "Mohammad Duldhana Farheen",
            "Roll_Number": "21ME1A5439",
            "Phone": "+919398911371",
            "Email": "ridhafarheen@gmail.com",
            "Dept": "Department of Artificial Intelligence & Data Science"
            
            
        },
        {
            "name": "B. Sudheer Kumar",
            "Roll_Number": "22ME5A5401",
            "Phone": "+916301371055",
            "Email": "bsudheerkumar2003@gmail.com",
            "Dept": "Department of Artificial Intelligence & Data Science"
    
            
        },
        {
            "name": "Bandaru Teja",
            "Roll_Number": "21ME1A5403",
            "Phone": "+916304155699",
            "Email": "bandaruteja86@gmail.com",
            "Dept": "Department of Artificial Intelligence & Data Science"
            
        },
        {
            "name": "Abdul Kausar",
            "Roll_Number": "21ME1A5401",
            "Phone": "+918919540598",
            "Email": "bdlkausar@gmail.com",
            "Dept": "Department of Artificial Intelligence & Data Science"
            
        }
    ]

    # Display team member details with images side by side
    col1, col2, col3, col4 = st.columns(4)

    for i, member in enumerate(team_members):
        with locals()[f"col{i+1}"]:
            st.write(f"Name: {member['name']}")
            st.write(f"Roll Number: {member['Roll_Number']}")  
            st.write(f"Phone: {member['Phone']}")
            st.write(f"Email: {member['Email']}")
            st.write(f"Department: {member['Dept']}")
            

# Settings Section
elif selected == "Settings":
    st.markdown("<h2 class='sider-title' style='color: SlateGray;'>Settings</h2>", unsafe_allow_html=True)
    st.text("")
    
    # Language selection
    st.session_state.input_language = st.selectbox(
        "🌍 Select your preferred language:",
        ["English", "Telugu", "Hindi"],
        index=["English", "Telugu", "Hindi"].index(st.session_state.input_language)
    )
    st.write(f"Selected Language: {st.session_state.input_language}")
