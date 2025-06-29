# marin_life_generator
AI海洋生物图片生成器 (Demo版)

这是一个基于Web的应用，用户输入任意文本概念，应用会返回一张由AI创作的、符合该概念的、独特的海洋生物图片。

##核心技术栈

前端界面: Streamlit - 仅使用Python构建交互式Web界面。

文本到指令模型: Google Gemini API (gemini-1.5-flash) - 免费，用于将用户输入转化为高质量的AI绘画指令。

图像生成模型: Stability AI API (stable-image-core) - 免费套餐，用于根据指令生成最终图片。

开发语言: Python

##实现逻辑 (用户视角)

输入: 用户在Web界面看到一个文本框，输入一段描述，如“一只由星云和水晶构成的鲸鱼”，然后点击“生成”按钮。

处理: 界面显示加载动画和状态提示，后台开始工作。

输出: 几秒到几十秒后，加载动画消失，界面上会展示出一张全新的、符合用户描述的海洋生物图片。

##实现逻辑 (代码层面)

整个应用运行在一个名为 app.py 的Python脚本中，其执行流程如下：

初始化与配置:

脚本启动时，会加载所需的Python库（Streamlit, Google, Stability等）。

通过判断环境变量，智能地从本地 .env 文件（用于开发）或Streamlit Cloud的Secrets（用于部署）中读取并配置 Google 和 Stability AI 的API密钥。

界面渲染:

使用Streamlit的命令 (st.title, st.text_area, st.form) 渲染出一个包含标题、文本输入框和提交按钮的网页界面。所有界面元素均由Python代码直接生成，无HTML/CSS。

事件驱动执行:

脚本本身处于等待状态，直到用户点击“生成”按钮。该点击事件触发后续的核心逻辑。

第一阶段：文本处理 (调用Google Gemini):

构建元提示词 (Meta-Prompt): 将用户的原始输入（如“星云鲸鱼”）嵌入到一个预设的、更复杂的指令模板中。该模板会要求AI扮演一个专业的“AI绘画指令工程师”，并围绕“海洋生物”主题，生成一段充满视觉细节、符合AI绘画模型喜好的、详细的英文提示词（Image Prompt）。

API调用: 通过google-generativeai库，将构建好的元提示词以POST请求的方式发送给Google Gemini API。

获取结果: 接收API返回的文本，这就是为第二阶段准备好的、专业的图像生成指令。

第二阶段：图像生成 (调用Stability AI):

构建API请求: 使用requests库，构造一个对Stability AI API的POST请求。

Headers: 请求头中必须包含Authorization（值为Stability AI的API密钥）和accept（值为image/*，表示希望直接返回图片文件）。

Body: 请求主体是一个multipart/form-data表单，其中包含一个关键参数prompt，其值就是第一阶段从Google Gemini获取的专业绘画指令。

API调用: 发送请求到Stability AI的服务器。这是整个流程中最耗时的一步。

获取结果: 如果请求成功（HTTP状态码200），服务器会直接返回图片的二进制数据。

结果展示:

Streamlit的st.image()函数接收第二阶段获取的图片二进制数据，直接在前端Web界面上将其渲染成可见的图片，呈现给用户。

整个逻辑是一个线性的、由两步API调用串联而成的清晰流程，通过Streamlit巧妙地封装成一个无需编写前端代码的交互式Web应用。
