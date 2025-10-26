import streamlit as st


import random

# 模拟AI回复
class MockAI:
    def get_response(self, prompt):
        responses = [
            "根据你的需求，我推荐以下实习机会：\n\n1. **腾讯-前端开发实习生**\n   - 地点：深圳\n   - 薪资：8-10K\n   - 要求：JavaScript, Vue, React\n\n2. **字节跳动-后端开发实习生**\n   - 地点：北京\n   - 薪资：9-11K\n   - 要求：Python, MySQL, Linux",
            "我找到这些匹配的实习：\n\n1. **阿里巴巴-数据分析实习生**\n   - 地点：杭州\n   - 薪资：7-9K\n   - 要求：Python, SQL, 统计学\n\n2. **华为-软件测试实习生**\n   - 地点：深圳\n   - 薪资：6-8K\n   - 要求：测试理论, Python",
            "基于你的技能，推荐：\n\n1. **百度-机器学习实习生**\n   - 地点：北京\n   - 薪资：10-12K\n   - 要求：Python, TensorFlow, 深度学习\n\n2. **美团-产品经理实习生**\n   - 地点：上海\n   - 薪资：8-10K\n   - 要求：产品设计, 市场分析"
        ]
        return random.choice(responses)

ai = MockAI()




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

prompt = st.chat_input("请输入你的目标岗位、期望薪资、就业地点等信息...")  # 获取用户输入

if prompt:
    st.session_state['messages'].append({"role": "user", "content": prompt})  # 记录用户输入
    st.chat_message("user").markdown(prompt)  # 输出用户输入

    resp = ai.get_response(prompt)  # 调用AI接口获取回复
    # res = f"你刚才说了: {prompt}, 我们正在为你推荐实习岗位，请稍等片刻。"  # 生成回复
    
    st.session_state['messages'].append({"role": "assistant", "content": resp})  # 记录回复
    st.chat_message("assistant").markdown(resp)  # 输出回复
