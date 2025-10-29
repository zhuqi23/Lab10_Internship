# from rag.ai import rag
# from rag.rag import rag
from rag.test import rag
# from rag.final import rag
import streamlit as st


# 初始化
if "messages" not in st.session_state:
    st.session_state["messages"] = [{
        "role": "assistant", 
        "content": "你好！我是实习推荐助手，请告诉我你的目标岗位、期望薪资、就业地点等信息，我会为你推荐合适的实习机会。"
    }] 

st.title("RAG-实习推荐聊天机器人")
st.write("欢迎使用RAG-实习推荐聊天机器人！")
st.write("我们将从“深圳技术大学就业网”中获取实习信息，你可以向我咨询相关的实习推荐。")
st.divider()

for message in st.session_state['messages']:  # 输出历史记录
    st.chat_message(message["role"]).markdown(message["content"])

prompt = st.chat_input("请输入你的目标岗位、就业地点等信息...")  # 获取用户输入

if prompt:
    st.session_state['messages'].append({"role": "user", "content": prompt})  # 记录用户输入
    st.chat_message("user").markdown(prompt)  # 输出用户输入

    # resp = rag.get_response(prompt)  # 调用AI接口获取回复
    resp = rag.get_detailed_response(prompt)
    # res = f"你刚才说了: {prompt}, 我们正在为你推荐实习岗位，请稍等片刻。"  # 生成回复
    
    st.session_state['messages'].append({"role": "assistant", "content": resp})  # 记录回复
    st.chat_message("assistant").markdown(resp)  # 输出回复
