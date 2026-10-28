"""
=============================================================================
VisualMind AI
=============================================================================
A beginner-friendly Streamlit web application powered by the Google Gemini API 
(google-genai SDK). It analyzes pasted text, automatically detects whether it 
represents an article, a process, or a comparison, and dynamically renders:
  - Article    -> Executive Summary & Key Points
  - Process    -> Interactive Mermaid Flowchart & Step-by-Step Breakdown
  - Comparison -> Markdown Comparison Table & Trade-off Insights
=============================================================================
"""

import os
import json
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from google import genai
from google.genai import types

# -----------------------------------------------------------------------------
# 1. Page Configuration & Environment Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="VisualMind AI - Text Categorizer & Visualizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables from .env file
load_dotenv()
env_api_key = os.getenv("GEMINI_API_KEY", "").strip()

# -----------------------------------------------------------------------------
# 2. Sample Datasets for 1-Click Testing
# -----------------------------------------------------------------------------
SAMPLES = {
    "article": {
        "label": "📰 Sample Article: Renewable Energy",
        "title": "The Global Transition to Renewable Energy",
        "text": (
            "Over the past decade, the global transition toward renewable energy has accelerated at an "
            "unprecedented pace. Driven by falling technology costs, supportive government policies, and "
            "urgent climate commitments, solar photovoltaics and onshore wind have become the cheapest "
            "sources of new electricity generation in most parts of the world. \n\n"
            "Modern power grids face the challenge of managing intermittent supply from renewables. "
            "To address this, utility-scale lithium-ion battery storage systems and long-duration storage "
            "technologies, such as pumped hydro and green hydrogen, are experiencing record investment. "
            "Furthermore, smart grids powered by artificial intelligence now forecast energy demand and "
            "reroute distribution in real-time, significantly reducing transmission losses.\n\n"
            "Despite this momentum, obstacles persist. Developing nations require significant capital "
            "investment to build modern transmission infrastructure, and regulatory hurdles frequently delay "
            "grid interconnection approvals. Nevertheless, experts agree that modernizing grid resilience and "
            "expanding decentralized solar installations will be decisive factors in achieving net-zero emissions by 2050."
        )
    },
    "process": {
        "label": "🔄 Sample Process: Web Browser Rendering",
        "title": "How a Web Browser Renders a Webpage",
        "text": (
            "When a user types a URL into a web browser and hits Enter, a multi-step sequence occurs to render "
            "the webpage. \n\n"
            "First, the browser performs a DNS Lookup to resolve the human-readable domain name into an IP address. "
            "Next, the browser establishes a TCP Connection with the destination server via a 3-way handshake, "
            "followed by a TLS handshake if the site uses HTTPS. Once the secure connection is ready, the browser "
            "sends an HTTP GET request to the server. \n\n"
            "The server processes the request and returns an HTTP response containing the HTML document. Upon receipt, "
            "the browser's rendering engine begins parsing the HTML bytes to construct the Document Object Model (DOM) tree. "
            "Concurrently, any linked CSS files are downloaded and parsed into the CSS Object Model (CSSOM) tree. \n\n"
            "The browser combines the DOM and CSSOM into a Render Tree, which calculates the visual layout and exact "
            "geometry of every visible element. Finally, in the Painting phase, pixels are rasterized onto the screen, "
            "displaying the fully loaded interactive webpage to the user."
        )
    },
    "comparison": {
        "label": "⚖️ Sample Comparison: SQL vs NoSQL",
        "title": "SQL vs NoSQL Databases: Architecture and Trade-offs",
        "text": (
            "Choosing the right database architecture is a pivotal decision in modern software engineering. "
            "Relational Databases (SQL) and Non-Relational Databases (NoSQL) offer fundamentally different approaches "
            "to data storage, consistency, and scalability.\n\n"
            "SQL databases (such as PostgreSQL, MySQL, and Oracle) store data in structured tables with predefined "
            "schemas, rows, and columns. They strictly adhere to ACID properties (Atomicity, Consistency, Isolation, "
            "Durability), guaranteeing transactional integrity. SQL databases scale vertically by upgrading hardware "
            "resources (CPU, RAM, SSD), which can become costly. They excel in applications requiring complex multi-table "
            "queries, financial transactions, and rigid data validation.\n\n"
            "In contrast, NoSQL databases (such as MongoDB, Cassandra, DynamoDB, and Redis) store unstructured or "
            "semi-structured data as documents, key-value pairs, wide-column stores, or graph nodes. They prioritize "
            "horizontal scaling by distributing data across clusters of commodity servers. Instead of strict ACID, "
            "many NoSQL systems adopt the BASE model (Basically Available, Soft-state, Eventual consistency) to maximize "
            "throughput and availability. NoSQL is ideal for real-time big data analytics, social networks, dynamic catalogs, "
            "and rapid prototyping where schemas evolve constantly."
        )
    }
}

# -----------------------------------------------------------------------------
# 3. Helper: Mermaid Diagram Visualizer Component
# -----------------------------------------------------------------------------
def render_mermaid_chart(mermaid_code: str, height: int = 420):
    """
    Renders a Mermaid flowchart using Mermaid.js inside an isolated Streamlit HTML component.
    """
    # Clean potential markdown fences from LLM output
    clean_code = mermaid_code.strip()
    if clean_code.startswith("```mermaid"):
        clean_code = clean_code[10:]
    elif clean_code.startswith("```"):
        clean_code = clean_code[3:]
    if clean_code.endswith("```"):
        clean_code = clean_code[:-3]
    clean_code = clean_code.strip()

    # Escape HTML special chars inside the mermaid code for safe inline embedding
    safe_code = (
        clean_code.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    html_payload = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'default',
                securityLevel: 'loose',
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                }}
            }});
        </script>
        <style>
            body {{
                margin: 0;
                padding: 12px;
                background-color: transparent;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }}
            .mermaid-card {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        <div class="mermaid-card">
            <div class="mermaid">
{safe_code}
            </div>
        </div>
    </body>
    </html>
    """
    components.html(html_payload, height=height, scrolling=True)

# -----------------------------------------------------------------------------
# 4. Helper: Gemini API Analyzer via google-genai SDK
# -----------------------------------------------------------------------------
def analyze_with_gemini(api_key: str, model_name: str, input_text: str, mode_override: str = "auto") -> dict:
    """
    Calls Google Gemini using the official `google-genai` SDK to classify
    the input text and generate structured visual data in JSON format.
    """
    # Initialize the client
    client = genai.Client(api_key=api_key)

    system_instruction = (
        "You are VisualMind AI, an expert text classification and visual-synthesis assistant. "
        "Analyze the provided text and determine whether it best fits one of three categories:\n"
        "1. 'article'    : Informational, narrative, conceptual, or expository prose describing a topic.\n"
        "2. 'process'    : Sequential workflow, pipeline, step-by-step instructions, or lifecycle.\n"
        "3. 'comparison' : Evaluation, comparison, pros/cons, or benchmarking between two or more concepts, tools, or items.\n\n"
        "You must return ONLY a valid JSON object matching the exact schema specified."
    )

    prompt = f"""
Input Text to Analyze:
\"\"\"
{input_text}
\"\"\"

Requested Classification Mode: {mode_override}
(Note: If Requested Mode is not 'auto', enforce that specific category).

Schema requirements:
Return a JSON object with:
{{
  "category": "article" | "process" | "comparison",
  "category_display": "Article / Overview" | "Step-by-Step Process" | "Comparison & Trade-offs",
  "title": "A concise and meaningful title for the content",
  "category_reason": "A 1-2 sentence explanation of why this category fits the text best",

  // Populate IF category == "article":
  "article_data": {{
    "summary": "A cohesive 2 to 4 sentence executive summary of the content.",
    "key_points": [
      "Crucial takeaway or highlighted fact 1",
      "Crucial takeaway or highlighted fact 2",
      "Crucial takeaway or highlighted fact 3"
    ]
  }},

  // Populate IF category == "process":
  "process_data": {{
    "overview": "A brief 1-2 sentence summary of what this workflow achieves.",
    "mermaid_code": "flowchart TD\\n  A[Start / Trigger] --> B[Step 1]\\n  B --> C[Step 2]\\n  C --> D[End / Result]",
    "steps": [
      {{"step_number": 1, "title": "Step 1 Title", "description": "Short explanation of step 1"}},
      {{"step_number": 2, "title": "Step 2 Title", "description": "Short explanation of step 2"}}
    ]
  }},

  // Populate IF category == "comparison":
  "comparison_data": {{
    "overview": "A 1-2 sentence overview of the items being compared and key findings.",
    "entities_compared": ["Entity A", "Entity B"],
    "table_markdown": "| Criteria | Entity A | Entity B |\\n|---|---|---|\\n| Feature 1 | Details A | Details B |",
    "key_takeaways": [
      "Key difference or trade-off point 1",
      "Key difference or trade-off point 2"
    ]
  }}
}}

Guidelines for Mermaid:
- Always use 'flowchart TD' (top-down) or 'flowchart LR' (left-to-right).
- Wrap node text containing special characters inside double quotes like `A["Step with (parentheses)"]`.
- Keep labels concise and visually readable.
"""

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.2,
        system_instruction=system_instruction
    )

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=config
    )

    raw_text = response.text.strip()

    # Strip markdown block quotes if returned
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    elif raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    raw_text = raw_text.strip()

    return json.loads(raw_text)

# -----------------------------------------------------------------------------
# 5. UI Layout - Sidebar Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ VisualMind AI Settings")
    st.caption("Configure your API connection and generation parameters.")

    # API Key Handling
    st.markdown("#### 🔑 Gemini API Key")
    if env_api_key:
        masked_key = env_api_key[:6] + "..." + env_api_key[-4:] if len(env_api_key) > 10 else "***"
        st.success(f"Loaded from `.env` (`{masked_key}`)")
        active_api_key = env_api_key
        with st.expander("Override API Key"):
            user_override = st.text_input("Enter alternative key", type="password", key="override_key")
            if user_override.strip():
                active_api_key = user_override.strip()
    else:
        st.warning("No API key detected in `.env`.")
        active_api_key = st.text_input(
            "Paste your Gemini API Key:",
            type="password",
            placeholder="AIzaSy...",
            help="Get your free key at https://aistudio.google.com/"
        ).strip()

    st.markdown(
        "[👉 Get a free Gemini API Key](https://aistudio.google.com/)",
        unsafe_allow_html=True
    )
    st.divider()

    # Model Selection
    model_choice = st.selectbox(
        "🧠 Gemini Model:",
        options=["gemini-3.8-flash", "gemini-3.8-pro"],
        index=0,
        help="gemini-3.8-flash is Google's recommended fast and capable model."
    )

    # Classification Mode
    mode_selection = st.selectbox(
        "🎯 Processing Mode:",
        options=[
            ("auto", "⚡ Auto-Detect (AI Decides)"),
            ("article", "📰 Force Article (Summary & Points)"),
            ("process", "🔄 Force Process (Mermaid Flowchart)"),
            ("comparison", "⚖️ Force Comparison (Comparison Table)")
        ],
        format_func=lambda x: x[1],
        index=0
    )[0]

    st.divider()

    # Quick Samples
    st.markdown("#### 💡 Quick Test Samples")
    st.caption("Click any button to populate the text area instantly:")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📰 Article", use_container_width=True):
            st.session_state["input_text"] = SAMPLES["article"]["text"]
    with col_btn2:
        if st.button("🔄 Process", use_container_width=True):
            st.session_state["input_text"] = SAMPLES["process"]["text"]

    if st.button("⚖️ Comparison", use_container_width=True):
        st.session_state["input_text"] = SAMPLES["comparison"]["text"]

    st.divider()
    st.markdown(
        "<small style='color: #64748b;'>Built with Streamlit & Google GenAI SDK</small>",
        unsafe_allow_html=True
    )

# -----------------------------------------------------------------------------
# 6. UI Layout - Main Application Canvas
# -----------------------------------------------------------------------------
st.title("🧠 VisualMind AI")
st.markdown(
    "**Turn unstructured text into structured insights.** VisualMind AI automatically classifies your input into an "
    "**Article**, a **Process**, or a **Comparison**, then produces a **Summary with Key Takeaways**, an "
    "**Interactive Mermaid Flowchart**, or a **Markdown Comparison Table**."
)

# Text Area for Input
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

user_text = st.text_area(
    label="Paste your text below:",
    value=st.session_state["input_text"],
    height=220,
    placeholder="Paste any article paragraph, workflow instructions, or comparison between technologies...",
    key="text_input_area"
)

# Metrics Bar
char_count = len(user_text)
word_count = len(user_text.split()) if user_text.strip() else 0

col_m1, col_m2, col_m3, col_m4 = st.columns([1, 1, 1, 2])
with col_m1:
    st.caption(f"📝 Words: **{word_count}**")
with col_m2:
    st.caption(f"🔤 Characters: **{char_count}**")
with col_m3:
    st.caption(f"⏱️ Read Time: **~{max(1, word_count // 150)} min**" if word_count > 0 else "⏱️ Read Time: 0 min")
with col_m4:
    pass

# Action Buttons
col_act1, col_act2, _ = st.columns([2, 1, 4])
with col_act1:
    analyze_clicked = st.button("🚀 Analyze & Visualize", type="primary", use_container_width=True)
with col_act2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state["input_text"] = ""
        st.rerun()

st.divider()

# -----------------------------------------------------------------------------
# 7. Processing & Results Presentation
# -----------------------------------------------------------------------------
if analyze_clicked:
    if not active_api_key:
        st.error("⚠️ Please provide a Gemini API Key in the `.env` file or enter one in the sidebar to proceed.")
    elif not user_text.strip():
        st.warning("⚠️ Please paste some text or select one of the Quick Test Samples from the sidebar.")
    else:
        with st.spinner("🧠 VisualMind AI is analyzing structure and synthesizing visualizations..."):
            try:
                result = analyze_with_gemini(
                    api_key=active_api_key,
                    model_name=model_choice,
                    input_text=user_text,
                    mode_override=mode_selection
                )
                st.session_state["last_result"] = result
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.info("Tip: Double-check your API key validity, internet connection, and model availability.")

# Render Results from Session State
if "last_result" in st.session_state and st.session_state["last_result"]:
    res = st.session_state["last_result"]
    category = res.get("category", "article").lower()
    category_display = res.get("category_display", category.capitalize())
    title = res.get("title", "Analysis Result")
    reason = res.get("category_reason", "")

    # Category Badges & Header
    badge_icons = {
        "article": "📰",
        "process": "🔄",
        "comparison": "⚖️"
    }
    icon = badge_icons.get(category, "📌")

    st.markdown(f"### {icon} {title}")

    # Classification Badge Callout
    col_b1, col_b2 = st.columns([1, 4])
    with col_b1:
        st.success(f"**Detected Type:**\n\n{icon} {category_display}")
    with col_b2:
        st.info(f"**Classification Context:**\n\n{reason}")

    st.write("")

    # -------------------------------------------------------------------------
    # Render Based on Category
    # -------------------------------------------------------------------------
    if category == "article":
        article_data = res.get("article_data", {})
        summary = article_data.get("summary", "No summary provided.")
        key_points = article_data.get("key_points", [])

        st.markdown("#### 📝 Executive Summary")
        st.info(summary)

        st.markdown("#### 🎯 Key Takeaways")
        for i, point in enumerate(key_points, 1):
            st.markdown(f"- **Point {i}:** {point}")

    elif category == "process":
        process_data = res.get("process_data", {})
        overview = process_data.get("overview", "")
        mermaid_code = process_data.get("mermaid_code", "")
        steps = process_data.get("steps", [])

        if overview:
            st.markdown("#### ℹ️ Process Overview")
            st.write(overview)

        st.markdown("#### 📊 Interactive Mermaid Flowchart")
        if mermaid_code:
            render_mermaid_chart(mermaid_code, height=450)
            
            with st.expander("🔍 View Mermaid Flowchart Code"):
                st.code(mermaid_code, language="mermaid")
        else:
            st.warning("No Mermaid code was generated.")

        if steps:
            st.markdown("#### 📋 Step-by-Step Breakdown")
            for step in steps:
                s_num = step.get("step_number", "•")
                s_title = step.get("title", "Step")
                s_desc = step.get("description", "")
                st.markdown(f"**Step {s_num}: {s_title}**  \n{s_desc}")

    elif category == "comparison":
        comparison_data = res.get("comparison_data", {})
        overview = comparison_data.get("overview", "")
        table_markdown = comparison_data.get("table_markdown", "")
        takeaways = comparison_data.get("key_takeaways", [])

        if overview:
            st.markdown("#### ℹ️ Comparison Overview")
            st.write(overview)

        st.markdown("#### 📊 Comparison Table")
        if table_markdown:
            st.markdown(table_markdown)
        else:
            st.warning("No comparison table was generated.")

        if takeaways:
            st.markdown("#### 💡 Trade-off Insights & Takeaways")
            for item in takeaways:
                st.markdown(f"- {item}")

    # Developer View
    with st.expander("🛠️ Developer View (Raw JSON Response)"):
        st.json(res)
