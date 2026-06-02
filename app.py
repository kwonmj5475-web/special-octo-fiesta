import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💌", layout="centered")
st.title("💌 달콤살벌 연애상담소")
st.caption("연애 고민, 썸, 이별까지! 무엇이든 물어보세요. (gemini-2.5-flash-lite 탑재)")

# 2. Streamlit Secrets에서 API 키 가져오기 및 설정
try:
    # Streamlit Cloud 배포 환경 및 로컬 .streamlit/secrets.toml 대응
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("API 키를 찾을 수 없습니다. Streamlit Secrets 설정(GEMINI_API_KEY)을 확인해주세요.")
    st.stop()

# 3. 세션 상태(Session State)로 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요! 당신의 연애 고민을 들어드릴 연애 카운셀러입니다. 오늘 어떤 이야기가 궁금하신가요?"
        }
    ]

# 4. 기존 대화 내역 렌더링
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 5. 사용자 입력 처리
if user_input := st.chat_input("고민을 입력해보세요... (예: 썸남이 선톡을 안 해요)"):
    # 사용자 메시지 화면에 표시 및 세션 저장
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 6. Gemini API 호출 및 답변 생성
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            # 챗봇 페르소나 부여 (시스템 지침 설정)
            system_instruction = (
                "당신은 공감 능력이 뛰어나고 위트 있는 전문 연애 카운셀러입니다. "
                "사용자의 연애 고민에 대해 따뜻하게 공감해주면서도, 때로는 현실적이고 명확한 조언을 제공해야 합니다. "
                "이모지를 적절히 섞어서 친근한 어조로 답변해주세요."
            )
            
            # 모델 초기화
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-lite",
                system_instruction=system_instruction
            )
            
            # 대화 맥락 유지를 위해 기존 대화 기록을 Gemini 형식으로 변환
            # (Gemini API는 user와 model 역할을 사용합니다)
            chat_history = []
            for msg in st.session_state.messages[:-1]: # 마지막 입력 제외한 이전 기록
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [msg["content"]]})
            
            # 대화 시작 및 메시지 전송
            chat = model.start_chat(history=chat_history)
            
            with st.spinner("생각 중... 💬"):
                response = chat.send_message(user_input)
            
            # 답변 출력 및 세션 저장
            ai_response = response.text
            response_placeholder.write(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            error_msg = f"죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다. (오류 내용: {str(e)})"
            response_placeholder.error(error_msg)
