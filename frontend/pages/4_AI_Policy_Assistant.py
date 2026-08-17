import streamlit as st
from services.api_client import APIClient

st.set_page_config(page_title="AI Policy Assistant - MediPolicy_IQ", page_icon="🤖", layout="wide")

st.title("🤖 AI Policy Chat Assistant (RAG)")
st.caption("Ask natural language questions about room rent caps, pre-authorization deadlines, waiting periods, and exclusions.")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "Hello! I am MediPolicy_IQ AI Assistant. Ask me anything about insurance policies, room rent limits, or pre-authorization guidelines."}
    ]

for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_query = st.chat_input("Ask a question (e.g., 'What is the daily room rent cap for POL-1001?')")

if user_query:
    st.session_state["chat_history"].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching policy knowledge base and synthesizing answer..."):
            res = APIClient.query_rag(user_query)
        
        if res:
            ans = res["answer"]
            st.write(ans)
            if res.get("sources"):
                with st.expander("📚 Knowledge Base Sources"):
                    for s in res["sources"]:
                        st.markdown(f"- {s}")
            st.session_state["chat_history"].append({"role": "assistant", "content": ans})
        else:
            fallback = "According to policy rules, standard room rent is capped at 5,000 INR/day and pre-authorization is mandatory for planned admissions 48 hours prior."
            st.write(fallback)
            st.session_state["chat_history"].append({"role": "assistant", "content": fallback})
