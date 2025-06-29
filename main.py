# app.py
import os
import streamlit as st
import google.generativeai as genai
import requests
from dotenv import load_dotenv

# app.py

# --- 1. 配置 ---
# 加载本地.env文件 (仅用于本地开发)
load_dotenv()

# 检查应用是否运行在Streamlit Cloud上
# 这是更稳健的密钥加载方式
if 'STREAMLIT_SERVER_RUNNING_ON_CLOUD' in os.environ:
    # 在云端部署时，使用st.secrets
    st.info("☁️ 应用运行在Streamlit Cloud，正在从Secrets加载API密钥。")
    GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
    STABILITY_API_KEY = st.secrets.get("STABILITY_API_KEY")
else:
    # 在本地开发时，使用.env文件
    st.info("💻 应用在本地运行，正在从.env文件加载API密钥。")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# 配置Google Gemini API
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


# --- 2. 应用界面 ---
st.set_page_config(page_title="AI Sea Creature Generator", layout="wide")

st.title("🌊 AI 海洋生物图片生成器 (Google + Stability.ai 免费版)")
st.markdown("由 **Google Gemini** 负责构思，**Stability AI** 负责绘画。")

with st.form("generation_form"):
    user_text = st.text_area(
        "👇 在此输入你的想法 (例如: 一条身上长满发光蘑菇的深海巨龙)",
        height=100
    )
    submit_button = st.form_submit_button("✨ 免费生成图片")

# --- 3. 核心逻辑 ---
if submit_button:
    # 检查API密钥是否已配置
    if not GOOGLE_API_KEY or not STABILITY_API_KEY:
        st.error("错误：API密钥未配置。请在本地创建.env文件或在Streamlit Community Cloud中设置Secrets。")
    elif not user_text:
        st.warning("请输入一些文字来激发AI的灵感！")
    else:
        with st.spinner("AI正在连接深海网络... 请稍候..."):
            try:
                # 步骤一: 调用 Google Gemini 生成专业的绘画提示词
                st.info("第一步：请求Google Gemini将您的想法转化为艺术指令...")
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                meta_prompt = f"""
                You are a world-class AI art prompt engineer specializing in marine biology.
                Based on the user's idea: '{user_text}', generate a detailed, visually stunning English prompt for the Stable Diffusion model.
                Describe a unique sea creature, its form, texture, color, bioluminescence, and its environment (e.g., abyssal trench, vibrant coral reef).
                The final prompt should be a single, concise paragraph, rich with artistic keywords.
                Style should be: hyperrealistic, cinematic lighting, epic, breathtaking, ultra-detailed, 8k.
                Directly output the final English prompt without any introductory text.
                """
                
                response = model.generate_content(meta_prompt)
                image_prompt = response.text.strip()

                st.success("艺术指令生成完毕！")
                with st.expander("点击查看Gemini生成的英文提示词"):
                    st.write(image_prompt)

                # 步骤二: 调用 Stability AI (Stable Image Core) 生成图片
                st.info("第二步：请求Stability AI根据指令进行绘画创作...")
                
                engine_id = "stable-image-core"
                api_host = 'https://api.stability.ai'
                api_key = STABILITY_API_KEY

                response = requests.post(
                    f"{api_host}/v2beta/stable-image/generate/{engine_id}",
                    headers={
                        "authorization": f"Bearer {api_key}",
                        "accept": "image/*"
                    },
                    files={"none": ''},
                    data={
                        "prompt": image_prompt,
                        "output_format": "png",
                    },
                )

                if response.status_code == 200:
                    st.success("创作完成！一幅独一无二的海洋生物图诞生了！")
                    st.image(response.content, caption=f"“{user_text}”的AI艺术创作", use_column_width=True)
                    # st.markdown(f"🔗 [点击此处下载高清原图]({image_url})") # 下载功能需要额外处理，暂时简化
                else:
                    # 尝试解析错误信息
                    try:
                        error_data = response.json()
                        st.error(f"Stability AI 返回错误: {error_data.get('errors', [response.text])}")
                    except:
                        st.error(f"Stability AI 返回错误 (状态码 {response.status_code}): {response.text}")


            except Exception as e:
                st.error(f"糟糕，创作过程中遇到了意料之外的问题: {e}")

st.markdown("---")
st.markdown("文本模型: Google Gemini 1.5 Flash | 图像模型: Stability AI Stable Image Core")