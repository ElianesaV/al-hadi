import streamlit as st
import random
from openai import OpenAI 
from brain import SYSTEM_PROMPT
from rag import retrieve_context
import os
from dotenv import load_dotenv

load_dotenv()


# 1. Page Configuration
st.set_page_config(
    page_title="AL HADI",
    page_icon="\u2721",
    layout="centered"
)



# 2. Divine Styling (Fixed & Advanced CSS)
st.markdown("""
    <style>
    /*  Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative&family=Spectral&display=swap');


    /* 1. Cinematic Background & Vignette */
    .stApp { 
        background: radial-gradient(circle, #0a0a0a 0%, #000000 100%);
        background-attachment: fixed;
    }
   
   
    /* 2. Floating Title Animation */
    @keyframes float {
        0% { transform: translateY(0px); opacity: 1; }
        50% { transform: translateY(0px); opacity: 0.7; }
        100% { transform: translateY(0px); opacity: 1; }
    }

    h1 { 
        color: #c9a84c !important; 
        text-align: center !important; 
        font-family: 'Cinzel Decorative', serif !important; 
        font-size: 4.5rem !important; 
        animation: float 6s ease-in-out infinite;
        text-shadow: 0 0 30px rgba(201, 168, 76, 0.6) !important;
        margin-bottom: 0px !important;
    }


    .subtitle { 
        color: #666; 
        text-align: center; 
        font-family: 'Spectral', serif; 
        letter-spacing: 7px; 
        text-transform: uppercase;
        font-size: 0.7rem;
        margin-top: -10px;
    }



    /* 3. THE GOLD DIVIDER */
    .gold-divider { 
        height: 1px; 
        background: linear-gradient(to right, transparent, #c9a84c, transparent); 
        margin: 25px 0;
        box-shadow: 0 0 10px rgba(201, 168, 76, 0.5); 
    }




    /* 4. Chat Bubbles & Glassmorphism */
    [data-testid="stChatMessage"] {
        background: rgba(20, 20, 20, 0.6) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(201, 168, 76, 0.1) !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
    }

    [data-testid="stChatMessage"]:nth-child(even) {
        border-left: 5px solid #c9a84c !important;
        background: linear-gradient(90deg, rgba(201,168,76,0.05) 0%, rgba(20,20,20,0.6) 100%) !important;
    }
    
    



/* 1. Target the main container - removes the default red border */
[data-testid="stChatInput"] {
    border: 2px solid rgba(201, 168, 76, 0.2) !important;
    border-radius: 11px !important;
    background-color: rgba(20, 20, 20, 0.9) !important;
    transition: all 0.3s ease-in-out !important;
}

/* 2. THE MAGIC FIX: This targets the hidden Streamlit focus state to kill the red */
[data-testid="stChatInput"] > div {
    border: none !important;
    box-shadow: none !important;
}

/* 3. The Gold Divine Glare when writing */
[data-testid="stChatInput"]:focus-within {
    border-color: #c9a84c !important; 
    box-shadow: 0 0 20px rgba(201, 168, 76, 0.4), 
                0 0 40px rgba(201, 168, 76, 0.1) !important;
}

/* 4. Style the internal textarea and the cursor */
[data-testid="stChatInput"] textarea {
    color: #c9a84c !important;
    caret-color: #c9a84c !important; /* Blinking cursor becomes gold */
    font-family: 'Spectral', serif !important;
}

/* 5. Replace the red send button with a gold one */
[data-testid="stChatInput"] button {
    border: 1px solid rgba(201, 168, 76, 0.2) !important;
    background-color: transparent !important;
    color: #c9a84c !important;
    
}

/* 6. Remove the small red highlight that appears on hover */
[data-testid="stChatInput"] button:hover {
    color: #f1e5c2 !important;
    background-color: rgba(201, 168, 76, 0.4) !important;
    box-shadow: 0 0 10px rgba(201, 168, 76, 0.4), 
                0 0 20px rgba(201, 168, 76, 0.1) !important;
    transform: scale(1.1);
}





[data-testid="stBottomBlockContainer"] {
    background-color: transparent !important;
    background: transparent !important;
}

[data-testid="stBottomBlockContainer"] > div {
    background: transparent !important;
}




/* 1. Target the master bottom container */
[data-testid="stBottom"] > div {
    background: transparent !important;
}


/* 1. Target the actual header bar */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    background: transparent !important;
    backdrop-filter: none !important; /* Removes the blurry effect */
}














    /* 6. Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #080808 !important;
        border-right: 1px solid rgba(201, 168, 76, 0.3) !important;
    }
    section[data-testid="stSidebar"] h4, section[data-testid="stSidebar"] p {
        font-family: 'Spectral', serif !important;
        color: #c9a84c !important;
    }



        /* Custom Divine Info Box */
    .divine-box {
        background-color: rgba(201, 168, 76, 0.05) !important; /* Very subtle gold tint */
        color: #e5e5e5 !important; /* white text */
        border: 1px solid rgba(201, 168, 76, 0.2) !important; /* Thin gold border */
        border-radius: 5px;
        padding: 10px;
        font-family: 'Spectral', serif;
        line-height: 1.6;
    }



    /* Scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(#000, #c9a84c, #000); border-radius: 10px; }
    
    #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)



# 3. Header UI
st.markdown("<h1>AL HADI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>The Black Banners Have Risen</p>", unsafe_allow_html=True)
st.markdown("<div class='gold-divider'></div>", unsafe_allow_html=True)



# 4. Divine Quote of the Day
quotes = [
    "The Goal of the Wise is the recognition of the Vicegerent of Allah on Earth.",
    "Truth is a light that Allah casts into the heart of whomsoever He wills.",
    "He will fill the Earth with justice, equity, and light, just as it would have been fraught with oppression, tyranny, and evil.",
    "The Seventh Covenant is the everlasting Covenant with the souls.",
    "Whoever sells his hereafter for his worldly life is a loser, utterly and truly.",
    "Purify your heart from the inside and you shall know as I know.",
    "The Black Banners have risen, and the call of the Mahdi is echoing through the horizons.",
    "He will place his hand over the heads of the servants (of Allah); he will then gather their minds together and complete their wisdom.",
    "You watched while a stone was cut out without hands, which struck the image on its feet of iron and clay, and broke them in pieces. ... And in the days of these kings the God of heaven will set up a kingdom which shall never be destroyed... it shall break in pieces and consume all these kingdoms, and it shall stand forever. [Daniel 2:34–35, 44]",
    "He who has not doubted has never believed.",
    "Verily, the Riser was called a Mahdi because he guides to a matter which was lost.",
    "From Prophet Muhammed (pbuhaf): Hijaz (Saudi Arabia) will be ruled by a man whose name is the name of an animal(Fahad/leopard), when you see him from a distance, you would think he has a lazy eye(crossed eyes), and if you get close to him, you do not see anything (wrong) in his eyes. He will be succeeded by a brother of his, named Abdullah. Woe to our Shia (followers) from him! Woe to our Shia (followers) from him! Woe to our Shia (followers) from him! – he repeated it three times – Give me the good news of his death, and I shall give you the good news of the appearance of the hujjah (The Mahdi).  [Two Hundred and Fifty Signs, sign number 122]",
    "One will not be considered a believer until he knows Allah, His Messenger and all of the Imams and the Imam of his time, acknowledges his Divine authority and submits his affairs to the Imam (PBUH).” He then said, “How would one know the last one when one is ignorant of the first one. [Al-Kafi vol.1 - book 4 chp7 hadith 2], [Al-Ghayba by al-Tousi page.447]",
    "From Imam al Sadiq (pbuhaf): Whoever guarantees for me the death of Abdullah, I will guarantee for him the Qa’im (The Mahdi). When Abdullah dies, then people will not gather/agree on anyone after him, and this matter will not except for your companion (The Qa'im) inshallah, and the kingdom of years will be over, and it will become the kingdom of months and days. So I asked: Will that be prolonged? He said: No.   [Bihar al Anwar, Volume 52, page 21]",
     "The religion of God is one, and its essence is the recognition of His representative.",
     "When the Qa'im of Ahl al-Bayt rises, he will redistribute the wealth with equity and justice among the people. Whomever follows him will have followed Allah, and whomever disobeys him will have disobeyed Allah.",
     "Whoever dies without knowing the Imam of his time dies a death of ignorance",
     "I was watching in the night visions, and behold, One like the Son of Man, coming with the clouds of heaven... Then to Him was given dominion and glory and a kingdom, that all peoples, nations, and languages should serve Him. His dominion is an everlasting dominion, which shall not pass away. [Daniel, 7:13-14]",
     "Those who pledge allegiance to you are pledging allegiance to God. The hand of God is over their hands. Whoever breaks his pledge breaks it to his own loss. And whoever fulfills his covenant with God, He will grant him a great reward. [Quran 48:10]"
     "When you see him, pledge allegiance to him, even if you have to crawl across snow, for he is the Caliph of Allah, the Mahdi",
     "There shall come forth a Rod from the stem of Jesse... With righteousness He shall judge the poor, and decide with equity for the meek of the earth; He shall strike the earth with the rod of His mouth, and with the breath of His lips He shall slay the wicked. [Isaiah, 11:1-4]",
    "The allegiance to the successor for Allah is the pillar of religion.",
    "Change begins with us; justice and equality begin with us.",
    "And as for Ishmael, I have heard you. Behold, I have blessed him, and will make him fruitful, and will multiply him exceedingly; twelve princes shall he beget, and I will make him a great nation. [Genesis, 17:20]",
    "Humanity first comes before religion.",
    "For evildoers shall be cut off; but those who wait on the Lord, they shall inherit the earth. For yet a little while and the wicked shall be no more... But the meek shall inherit the earth, and shall delight themselves in the abundance of peace. [Psalm, 37:9-1]",
    "Even if the whole universe gathered against us they would not harm except themselves.",
    "Nobody is given success in this Call except he who has a relationship with God.",
    "Certainly was Allah pleased with the believers when they pledged allegiance to you, [O Muhammad], under the tree, and He knew what was in their hearts, so He sent down tranquility upon them and rewarded them with an imminent conquest. [Quran,48:18]",
    "Verily, what you have been promised has arrived.",
    "And We desired to show favor to those who were oppressed in the land, and to make them Imams, and to make them the heirs. [Quran, 28:5]",
    "The Riser shall rise with a new matter, a new book, and a new jurisprudence.",
    "The Day We will call every people with their Imam.. [Quran, 17:71]",
    "The Vicegerent is the face of God by which He is known.",
    "Allegiance is to Allah, for supremacy belongs to the Creator.",
    "Search for your religion until they call you a disbeliever.",
    "Islam began as something strange, and it will return to being strange as it began, so give glad tidings to the strangers",
    "Delete your existence, by heart and not by tongue."
]
st.markdown(f"<p style='text-align: center; color: #c9a84c; font-style: italic; font-family: Spectral; font-size: 1.1rem;'>\"{random.choice(quotes)}\"</p>", unsafe_allow_html=True)



# 5. Sidebar Content
with st.sidebar:
    st.markdown("<h4 style='text-align: center;'>\u2721 THE LAW OF THE VICEGERENT</h4>", unsafe_allow_html=True)
    st.markdown("""
        <div class='divine-box'>
            <b>1. The Will 📜</b><br>
            <i>Named by the predecessor.</i><br><br>
            <b>2. Divine Knowledge 🔑</b><br>
            <i>Answerer of all mysteries.</i><br><br>
            <b>3. The Banner 🏴</b><br>
            <i>Calls to God's Supremacy.</i>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    
    st.markdown("<p style='text-align: center;'>\u2721 ACCESS THE LIGHT</p>", unsafe_allow_html=True)
    st.link_button("✊ JOIN THE CALL", "https://theahmadireligion.org")
    st.link_button("🕊️ Our Beliefs", "https://theahmadireligion.org/our-beliefs")
    st.link_button("▶️ YouTube Channel", "https://www.youtube.com/@themahdihasappeared")
    st.link_button("📚 Download our Books", "https://theahmadireligion.org/library")
    st.markdown("", unsafe_allow_html=True)
    

    
    if st.button("⚠️ CHAT RESET"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)    
        # ── toggle between local and cloud ────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### 🪙 AI MODEL")
    use_cloud = st.toggle("", value=True)
    
    if use_cloud:
        client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/", # official URL to call google api
            api_key=os.getenv("GEMINI_API_KEY")
        )
        current_model = os.getenv("MODEL_NAME")
        st.markdown(f" <div class='divine-box'>Google Cloud ({current_model})</div>", unsafe_allow_html=True)
    else:
        client = OpenAI(
            base_url="http://localhost:11434/v1", # Local address
            api_key="mistral"
        )
        current_model = os.getenv("LOCAL_MODEL_NAME")
        st.markdown(f" <div class='divine-box'>Local GPU ({current_model})</div>", unsafe_allow_html=True)

        

# 6. Session Logic
if "messages" not in st.session_state:
    st.session_state.messages = []


# 7. Display History
for message in st.session_state.messages:
    avatar = "\u2721" if message["role"] == "assistant" else "💬"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"], unsafe_allow_html=True)



# 8. Chat Input & AI Logic
if user_input := st.chat_input("  Seek guidance..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="💬"):
        st.markdown(user_input)
        

    with st.chat_message("assistant", avatar="\u2721"):
        response_placeholder = st.empty()
        full_response = ""
        
        
        with st.spinner("Seeking the Light..."):
            context = ""
            sources = []
            
            GREETINGS = {"hi", "hello", "hey", "salam", "salaam", "peace", "greetings"}
            is_greeting = user_input.lower().strip() in GREETINGS
            is_too_short = len(user_input.split()) <= 2  # only skip for 1-2 word non-questions
            
            if is_greeting or is_too_short:
                context = ""
                sources = []
            else:
                try:
                    context, sources = retrieve_context(user_input, k=7)
                    # TEMPORARY DEBUG - remove after testing
                    print("=== RETRIEVED CONTEXT ===")
                    print(context)
                    print("=== SOURCES ===")
                    print(sources)
                except:
                    context = ""
                    sources = []
            IDENTITY_QUESTIONS = {"who is aba al sadiq", "who is ahmed al hassan", "who is abdullah hashem", "who is the riser", "who is the mahdi"}        
            is_identity = any(phrase in user_input.lower() for phrase in IDENTITY_QUESTIONS)
            if is_greeting or is_too_short or is_identity:
                context = ""
                sources = []
            
            #1. Persona
            messages_to_send = [{"role": "system", "content": SYSTEM_PROMPT}]
                
                
                # 2. Add the Sliding History
            messages_to_send.extend(st.session_state.messages[-6:])
            
            
            # 3. Add the "Sacred Knowledge" as a separate USER-level context
# This keeps the 'Knowledge' from 'Poisoning' the 'System Persona'
            context_block = {
                "role": "assistant", 
                "content": f"### — SACRED KNOWLEDGE — Speak from this truth with the voice and warmth of AL HADI. The answer must come from this knowledge, but deliver it as a devoted servant of the faith, not as a reader:\n\n{context}"}
                
            messages_to_send.append(context_block)

            # 4. Add the User's final question at the VERY end
            # This ensures the model focuses on the QUESTION, not the book references. 
            messages_to_send.append({"role": "user", "content": f"{user_input}\n\nReminder: You are AL HADI. Maximum 4 paragraphs. NEVER paste raw text directly. Read the Sacred Knowledge, understand it, then explain it in your own spiritual voice with warmth and conviction..... Synthesize. EXCEPT for specific evidence like direct quotes or narrations or calendar correspondences, Retrieve the full text from your knowledge base and paste raw it directly with the exact source and citations in the end of each narration or quote."})
            # TEMPORARY DEBUG
            import json
            print(json.dumps(messages_to_send, indent=2))

            # Dynamic Parameters using Unpacking
            params = {
                "model": current_model,
                "messages": messages_to_send,
                "temperature": 0.7,
                "max_tokens": 4096 ,
                "top_p": 0.9,
                "stream": True
            }

            # Add top_k only if using local GPU
            if not use_cloud:
                params["extra_body"] = {"top_k": 60}




            try:
                # ── Groq streaming call ───────────────────────────────────────
                stream = client.chat.completions.create(**params)
                
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)

                
                # Append sources if retrieved
                if sources and len(full_response.split()) > 30:
                
                    source_text = (
                        f"\n\n---\n"
                        f"<span style='color: gray; font-size: 0.9rem;'>"
                        f"📚 **Sources:** {', '.join(set(sources))}</span>"
                    )

            
                    full_response += source_text
                    
               
                response_placeholder.markdown(full_response, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                
            except Exception as e:
                st.error(f"Connection lost: {e}")
                
                
