import re
import streamlit as st

from tools import (
    extract_video_id,
    fetch_video_title,
    fetch_video_transcript
)

from crew import generate_blog


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="YouTube to Blog Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.7rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #888888;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    .feature-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        text-align: center;
        min-height: 125px;
    }

    .stButton > button {
        width: 100%;
        border-radius: 9px;
        font-weight: 600;
        min-height: 45px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "generated_blog" not in st.session_state:
    st.session_state.generated_blog = None

if "video_title" not in st.session_state:
    st.session_state.video_title = None

if "video_url" not in st.session_state:
    st.session_state.video_url = None


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🎬 YouTube to Blog Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Transform YouTube videos into detailed, structured
        technical blog posts using CrewAI agents.
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# FEATURES
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="feature-card">
            <h2>🔗</h2>
            <b>Any Supported Video</b>
            <p>Submit an individual YouTube video URL.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
            <h2>🤖</h2>
            <b>CrewAI Agents</b>
            <p>Researcher and Writer collaborate to create blogs.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
            <h2>📄</h2>
            <b>Preview and Download</b>
            <p>Read your blog and download it as a TXT file.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# --------------------------------------------------
# VIDEO INPUT
# --------------------------------------------------

st.subheader("🔗 Enter YouTube Video")

video_url = st.text_input(
    "YouTube video URL",
    placeholder="https://www.youtube.com/watch?v=XXXXXXXXXXX",
    help="Supported formats include watch URLs, youtu.be, Shorts and embed URLs."
)

generate_button = st.button(
    "🚀 Generate Blog",
    type="primary"
)


# --------------------------------------------------
# GENERATION WORKFLOW
# --------------------------------------------------

if generate_button:

    if not video_url.strip():

        st.error("Please enter a YouTube video URL.")

    else:

        try:

            st.session_state.generated_blog = None

            with st.status(
                "Preparing your blog...",
                expanded=True
            ) as status:

                # STEP 1: VALIDATE URL

                st.write("🔍 Validating YouTube URL...")

                video_id = extract_video_id(video_url)

                # STEP 2: FETCH VIDEO TITLE

                st.write("📺 Fetching video information...")

                video_title = fetch_video_title(video_id)

                st.write(f"**Video:** {video_title}")

                # STEP 3: EXTRACT TRANSCRIPT

                st.write("📝 Extracting video transcript...")

                transcript, language = fetch_video_transcript(
                    video_id
                )

                transcript_length = len(transcript)

                st.write(
                    f"Transcript extracted successfully. "
                    f"Language: {language}"
                )

                # Limit extremely large transcripts

                max_transcript_chars = 60000

                if transcript_length > max_transcript_chars:

                    transcript = transcript[:max_transcript_chars]

                    st.warning(
                        "This transcript is very long. "
                        "The first 60,000 characters will be used "
                        "for this generation."
                    )

                st.write(
                    f"Transcript size: {len(transcript):,} characters"
                )

                # STEP 4: CREWAI BLOG GENERATION

                st.write("🤖 Starting CrewAI agents...")

                blog = generate_blog(
                    video_url=video_url,
                    video_title=video_title,
                    transcript=transcript
                )

                if not blog or not blog.strip():

                    raise ValueError(
                        "CrewAI returned an empty blog."
                    )

                st.session_state.generated_blog = blog
                st.session_state.video_title = video_title
                st.session_state.video_url = video_url

                status.update(
                    label="Blog generated successfully!",
                    state="complete",
                    expanded=False
                )

            st.success("Your YouTube blog is ready!")

        except Exception as error:

            st.error(
                f"Something went wrong: {str(error)}"
            )


# --------------------------------------------------
# BLOG PREVIEW
# --------------------------------------------------

if st.session_state.generated_blog:

    st.divider()

    st.subheader("📖 Generated Blog Preview")

    st.caption(
        f"Source video: {st.session_state.video_title}"
    )

    blog_content = st.session_state.generated_blog

    preview_tab, raw_tab = st.tabs(
        ["📖 Blog Preview", "📝 Markdown Source"]
    )

    with preview_tab:

        st.markdown(
            blog_content,
            unsafe_allow_html=False
        )

    with raw_tab:

        st.code(
            blog_content,
            language="markdown"
        )

    st.divider()

    # Create safe filename

    filename = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        st.session_state.video_title
    ).strip("_")

    filename = filename[:70] or "youtube_blog"

    st.download_button(
        label="⬇️ Download Complete Blog (.txt)",

        data=blog_content,

        file_name=f"{filename}.txt",

        mime="text/plain",

        type="primary"
    )

    st.caption(
        "Your generated blog is available for preview and download."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:gray;">
        Built with Streamlit, CrewAI and OpenRouter
    </div>
    """,
    unsafe_allow_html=True
)