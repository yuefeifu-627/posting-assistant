import os
import streamlit as st
import streamlit.components.v1 as components
import requests
from typing import List, Dict

# 配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
st.set_page_config(
    page_title="用车总结生成器",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)


def check_backend_health():
    """检查后端服务状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.json()
    except Exception as e:
        return None


def get_themes():
    """获取所有主题"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/themes", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def create_theme(name: str, post_length: int = 500):
    """创建新主题"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/themes",
            json={"name": name, "post_length": post_length},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            st.error(response.json().get("detail", "创建失败"))
        return None
    except Exception as e:
        st.error(f"请求失败: {str(e)}")
        return None


def get_theme(theme_id: int):
    """获取单个主题详情"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/themes/{theme_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def update_theme(theme_id: int, name: str = None, post_length: int = None):
    """更新主题"""
    try:
        data = {}
        if name:
            data["name"] = name
        if post_length is not None:
            data["post_length"] = post_length
        response = requests.put(
            f"{API_BASE_URL}/api/themes/{theme_id}",
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"请求失败: {str(e)}")
        return None


def generate_post(theme_id: int, summary: str, requirements: str = None, post_length: int = None, use_api: bool = False):
    """生成帖子"""
    try:
        data = {
            "theme_id": theme_id,
            "summary": summary,
            "requirements": requirements,
            "use_api": use_api
        }
        if post_length:
            data["post_length"] = post_length

        response = requests.post(
            f"{API_BASE_URL}/api/posts/generate",
            json=data,
            timeout=300
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"生成失败: {response.json().get('detail', '未知错误')}")
            return None
    except Exception as e:
        st.error(f"请求失败: {str(e)}")
        return None


def get_posts(theme_id: int = None):
    """获取帖子列表"""
    try:
        params = {}
        if theme_id:
            params["theme_id"] = theme_id
        response = requests.get(
            f"{API_BASE_URL}/api/posts",
            params=params,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def get_post(post_id: int):
    """获取单个帖子"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/posts/{post_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def update_post(post_id: int, content: str):
    """更新帖子内容"""
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/posts/{post_id}",
            json={"content": content},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"请求失败: {str(e)}")
        return None


def delete_post(post_id: int):
    """删除帖子"""
    try:
        response = requests.delete(f"{API_BASE_URL}/api/posts/{post_id}", timeout=10)
        return response.status_code == 200
    except Exception:
        return False


# === 语料库相关 ===

def get_corpus():
    """获取语料库列表"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/corpus", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def add_to_corpus(title: str, content: str, tags: str = None, note: str = None):
    """添加帖子到语料库"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/corpus",
            json={"title": title, "content": content, "tags": tags, "note": note},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"请求失败: {str(e)}")
        return None


def delete_corpus(post_id: int):
    """删除语料库帖子"""
    try:
        response = requests.delete(f"{API_BASE_URL}/api/corpus/{post_id}", timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def analyze_style():
    """分析语料库生成风格特征"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/corpus/analyze-style", timeout=120)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"分析失败: {str(e)}")
        return None


def get_style_profile():
    """获取风格特征"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/corpus/style-profile", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def update_summary_count():
    """更新内容提要字数的回调函数"""
    st.session_state.summary_text = st.session_state.summary_input


def main():
    st.title("🚗 用车总结生成器")
    st.markdown("先创建主题，然后在主题下生成帖子")

    # 检查后端状态
    health = check_backend_health()
    if health is None:
        st.warning("⚠️ 后端服务未连接，请先启动FastAPI服务: `uvicorn app.main:app --reload`")
        st.stop()

    if not health.get("ai_connected"):
        st.warning("⚠️ Ollama服务未连接，请确保Ollama服务正在运行")
        st.info(f"当前配置模型: {health.get('config', {}).get('model')}")
        st.stop()

    # 初始化session state
    if "selected_theme_id" not in st.session_state:
        st.session_state.selected_theme_id = None
    if "editing_post_id" not in st.session_state:
        st.session_state.editing_post_id = None
    if "edit_content" not in st.session_state:
        st.session_state.edit_content = None
    if "clear_corpus_form" not in st.session_state:
        st.session_state.clear_corpus_form = False
    if "summary_text" not in st.session_state:
        st.session_state.summary_text = ""

    # 处理清空表单标志
    if st.session_state.clear_corpus_form:
        st.session_state.corpus_title = ""
        st.session_state.corpus_content = ""
        st.session_state.corpus_tags = ""
        st.session_state.corpus_note = ""
        st.session_state.clear_corpus_form = False

    # 侧边栏 - 标签页
    with st.sidebar:
        tab1, tab2 = st.tabs(["📂 主题", "📚 语料库"])

        # 标签页1 - 主题管理
        with tab1:
            # 创建新主题
            with st.expander("➕ 创建新主题", expanded=False):
                new_theme_name = st.text_input("主题名称", placeholder="例如：周末自驾游体验", key="new_theme_name")
                new_post_length = st.slider(
                    "发帖字数",
                    min_value=100,
                    max_value=2000,
                    value=500,
                    step=100,
                    help="生成帖子的目标字数",
                    key="new_post_length"
                )
                if st.button("创建主题", type="primary", key="create_theme_btn"):
                    if new_theme_name:
                        result = create_theme(new_theme_name, new_post_length)
                        if result:
                            st.success(f"主题 '{new_theme_name}' 创建成功！")
                            st.rerun()
                    else:
                        st.error("请输入主题名称")

            # 主题列表
            st.subheader("已有主题")
            themes_data = get_themes()
            if themes_data and themes_data.get("themes"):
                for theme in themes_data["themes"]:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        if st.button(
                            f"📌 {theme['name']} ({theme['post_count']}篇)",
                            key=f"theme_btn_{theme['id']}"
                        ):
                            st.session_state.selected_theme_id = theme['id']
                            st.session_state.editing_post_id = None
                            st.rerun()
                    with col3:
                        if st.button("🗑️", key=f"del_theme_{theme['id']}"):
                            requests.delete(f"{API_BASE_URL}/api/themes/{theme['id']}")
                            if st.session_state.selected_theme_id == theme['id']:
                                st.session_state.selected_theme_id = None
                            st.rerun()
            else:
                st.info("暂无主题，请先创建")

        # 标签页2 - 语料库管理
        with tab2:
            st.markdown("**添加你的历史帖子，AI会学习你的写作风格**")

            # 风格分析状态
            style_status = get_style_profile()
            if style_status:
                if style_status.get("has_profile"):
                    st.success(f"✅ 已分析风格（基于{style_status['post_count']}篇帖子）")
                    with st.expander("查看风格特征"):
                        st.text(style_status.get("profile", ""))
                        st.caption(f"更新时间: {style_status.get('updated_at', '')[:16]}")
                else:
                    st.info(f"📝 语料库中有 {style_status.get('corpus_count', 0)} 篇帖子，点击下方按钮分析风格")

            # 添加新帖子
            with st.expander("➕ 添加历史帖子", expanded=False):
                corpus_title = st.text_input("帖子标题/主题", placeholder="可选", key="corpus_title")
                corpus_content = st.text_area(
                    "帖子内容",
                    placeholder="粘贴你以前发过的帖子内容...",
                    height=200,
                    key="corpus_content"
                )
                corpus_tags = st.text_input("标签", placeholder="如：通勤、自驾游（逗号分隔）", key="corpus_tags")
                corpus_note = st.text_input("备注", placeholder="可选", key="corpus_note")

                if st.button("添加到语料库", type="primary", key="add_corpus_btn"):
                    if corpus_content:
                        result = add_to_corpus(
                            title=corpus_title if corpus_title else None,
                            content=corpus_content,
                            tags=corpus_tags if corpus_tags else None,
                            note=corpus_note if corpus_note else None
                        )
                        if result:
                            st.session_state.clear_corpus_form = True
                            st.success("✅ 已添加到语料库！")
                            st.rerun()
                    else:
                        st.error("请输入帖子内容")

            # 语料库列表
            st.subheader("已保存的帖子")
            corpus_data = get_corpus()
            if corpus_data and corpus_data.get("posts"):
                st.caption(f"共 {corpus_data['total']} 篇")
                for post in corpus_data["posts"]:
                    with st.expander(f"📝 {post['title'] if post['title'] else '无标题'}"):
                        st.text(post['content'][:300] + "..." if len(post['content']) > 300 else post['content'])
                        if post['tags']:
                            st.caption(f"标签: {post['tags']}")
                        if st.button("🗑️ 删除", key=f"del_corpus_{post['id']}"):
                            delete_corpus(post['id'])
                            st.rerun()

                # 分析风格按钮
                st.divider()
                if st.button("🧠 分析我的写作风格", type="primary"):
                    with st.spinner("正在分析..."):
                        result = analyze_style()
                        if result:
                            st.success(f"分析完成！基于 {result['post_count']} 篇帖子")
                            st.rerun()
            else:
                st.info("语料库为空，添加你以前发过的帖子来训练AI学习你的风格")

    # 主界面
    if st.session_state.selected_theme_id:
        theme = get_theme(st.session_state.selected_theme_id)
        if theme:
            st.header(f"主题: {theme['name']}")
            st.caption(f"目标字数: {theme['post_length']}字")

            # 生成新帖子
            st.subheader("生成新帖子")

            # 字数设置（可修改，默认使用主题设置）
            col_len1, col_len2 = st.columns([2, 1])
            with col_len1:
                post_length = st.slider(
                    "目标字数",
                    min_value=100,
                    max_value=2000,
                    value=theme['post_length'],
                    step=50,
                    help="生成帖子的目标字数，字数越少生成越快"
                )
            with col_len2:
                if st.button("重置为默认", key="reset_length"):
                    post_length = theme['post_length']
                    st.rerun()

            # 模型选择
            st.subheader("模型选择")
            col_model1, col_model2 = st.columns([3, 2])

            with col_model1:
                model_option = st.radio(
                    "选择生成模型",
                    options=["本地模型 (Ollama)", "云端API (GLM-4.7)", "云端API (通义千问)"],
                    index=0,
                    help="本地模型免费但较慢，云端API需要配置API Key但更快更稳定"
                )
                use_api = model_option != "本地模型 (Ollama)"
                api_type = "glm" if model_option == "云端API (GLM-4.7)" else "qwen"

            with col_model2:
                if use_api:
                    if health.get("api_configured"):
                        model_name = health.get('api_model', '未知')
                        st.success(f"✅ API已配置\n模型: {model_name}")
                    else:
                        if api_type == "glm":
                            st.warning("⚠️ 未配置API Key\n请在.env文件中设置GLM_API_KEY")
                        else:
                            st.warning("⚠️ 未配置API Key\n请在.env文件中设置QWEN_API_KEY")
                else:
                    if health.get("ai_connected"):
                        st.success(f"✅ 本地模型已连接\n模型: {health.get('config', {}).get('ollama_model')}")
                    else:
                        st.error("❌ 本地模型未连接")

            # 内容提要
            st.subheader("内容输入")

            summary = st.text_area(
                "📝 内容提要",
                placeholder="输入你想要表达的要点，例如：\n• 周末去了莫干山自驾，往返200公里\n• 能耗表现不错，大概15度/百公里\n• 用了NZP辅助驾驶，体验很好",
                height=150,
                help="简单列出你想说的要点，AI会帮你润色成完整帖子"
            )

            # 实时字数统计（JavaScript注入）
            components.html("""
            <div id="char-counter-container" style="font-size: 0.85rem; color: #888; margin-top: -10px; margin-bottom: 10px;">
                📊 已输入 <span id="live-char-count">0</span> 字
            </div>
            <script>
                // 等待页面加载完成
                setTimeout(function() {
                    // 找到所有textarea
                    var textareas = window.parent.document.querySelectorAll('textarea');
                    var targetTextarea = null;

                    // 找到内容提要的textarea（通过placeholder判断）
                    for (var i = 0; i < textareas.length; i++) {
                        var placeholder = textareas[i].getAttribute('placeholder');
                        if (placeholder && placeholder.includes('输入你想要表达的要点')) {
                            targetTextarea = textareas[i];
                            break;
                        }
                    }

                    if (targetTextarea) {
                        function updateCount() {
                            var text = targetTextarea.value.replace(/\\s/g, '');
                            var countEl = document.getElementById('live-char-count');
                            if (countEl) {
                                countEl.textContent = text.length;
                            }
                        }

                        targetTextarea.addEventListener('input', updateCount);
                        updateCount(); // 初始化
                    }
                }, 500);
            </script>
            """, height=30)

            # 主办方要求
            requirements = st.text_area(
                "📋 主办方任务要求（可选）",
                placeholder="例如：字数300-500字，需要提到续航和智能驾驶体验",
                height=80,
                help="发帖平台或主办方的具体要求"
            )

            # 生成按钮
            if st.button("✨ 润色生成", type="primary"):
                if not summary:
                    st.error("请输入内容提要")
                else:
                    model_name = "通义千问API" if use_api else "本地模型"
                    with st.spinner(f"正在使用{model_name}润色生成...（目标{post_length}字）"):
                        result = generate_post(
                            theme_id=st.session_state.selected_theme_id,
                            summary=summary,
                            requirements=requirements if requirements else None,
                            post_length=post_length,
                            use_api=use_api
                        )
                        if result:
                            st.success("帖子生成成功！")
                            st.session_state.editing_post_id = result['id']
                            st.session_state.edit_content = result['content']
                            st.rerun()

            # 显示该主题下的帖子历史
            st.subheader("该主题下的帖子")
            posts_data = get_posts(theme_id=st.session_state.selected_theme_id)
            if posts_data and posts_data.get("posts"):
                for post in posts_data["posts"]:
                    is_editing = st.session_state.editing_post_id == post['id']

                    with st.container():
                        st.caption(f"创建时间: {post['created_at'][:16]} | 更新: {post['updated_at'][:16]}")

                        if is_editing:
                            edited_content = st.text_area(
                                "帖子内容",
                                value=st.session_state.edit_content or post['content'],
                                height=400,
                                key=f"edit_content_{post['id']}"
                            )

                            col_save, col_cancel, col_del = st.columns([1, 1, 1])
                            with col_save:
                                if st.button("💾 保存修改", key=f"save_{post['id']}"):
                                    update_post(post['id'], edited_content)
                                    st.success("已保存")
                                    st.session_state.editing_post_id = None
                                    st.rerun()
                            with col_cancel:
                                if st.button("取消", key=f"cancel_{post['id']}"):
                                    st.session_state.editing_post_id = None
                                    st.rerun()
                            with col_del:
                                if st.button("🗑️ 删除", key=f"del_post_{post['id']}"):
                                    delete_post(post['id'])
                                    st.session_state.editing_post_id = None
                                    st.rerun()

                            st.download_button(
                                "📥 下载帖子",
                                edited_content,
                                file_name=f"{theme['name']}_post_{post['id']}.txt",
                                key=f"download_{post['id']}"
                            )
                        else:
                            st.text(post['content'][:300] + "..." if len(post['content']) > 300 else post['content'])

                            col_edit, col_view = st.columns([1, 1])
                            with col_edit:
                                if st.button("✏️ 编辑", key=f"edit_btn_{post['id']}"):
                                    st.session_state.editing_post_id = post['id']
                                    st.session_state.edit_content = post['content']
                                    st.rerun()
                            with col_view:
                                if st.button("查看全文", key=f"view_btn_{post['id']}"):
                                    st.session_state.editing_post_id = post['id']
                                    st.session_state.edit_content = post['content']
                                    st.rerun()

                        st.divider()
            else:
                st.info("该主题下暂无帖子，点击上方按钮生成")

    else:
        st.info("👈 请在左侧选择或创建一个主题")
        st.markdown("""
        ### 使用流程：
        1. **创建主题** - 在左侧点击"创建新主题"
        2. **添加语料** - 在"语料库"标签添加你的历史帖子，AI学习你的风格
        3. **生成帖子** - 选择主题，输入内容提要，点击润色生成
        4. **编辑修改** - 在生成的帖子基础上编辑完善
        """)


if __name__ == "__main__":
    main()