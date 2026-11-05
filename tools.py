import re
import requests

from functools import lru_cache
from typing import Type
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
from langsmith import traceable
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()


# --------------------------------------------------
# YOUTUBE URL VALIDATION
# --------------------------------------------------

@traceable(name="validate_youtube_url", run_type="tool")
def extract_video_id(video_url: str) -> str:

    if not video_url or not video_url.strip():
        raise ValueError("YouTube URL cannot be empty.")

    parsed = urlparse(video_url.strip())
    hostname = parsed.netloc.lower().split(":")[0]

    video_id = None

    if hostname in ("youtu.be", "www.youtu.be"):
        video_id = parsed.path.strip("/").split("/")[0]

    elif hostname in (
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com"
    ):
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]

        else:
            match = re.match(
                r"^/(?:shorts|embed|live|v)/([^/?]+)",
                parsed.path
            )

            if match:
                video_id = match.group(1)

    if not video_id or not re.fullmatch(
        r"[A-Za-z0-9_-]{11}", video_id
    ):
        raise ValueError("Invalid or unsupported YouTube URL.")

    return video_id


# --------------------------------------------------
# VIDEO TITLE
# --------------------------------------------------

@traceable(name="fetch_youtube_video_title", run_type="tool")
@lru_cache(maxsize=32)
def fetch_video_title(video_id: str) -> str:

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        response = requests.get(
            "https://www.youtube.com/oembed",
            params={
                "url": video_url,
                "format": "json"
            },
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        return data.get("title", "YouTube Video")

    except requests.RequestException:
        return f"YouTube Video ({video_id})"


# --------------------------------------------------
# TRANSCRIPT EXTRACTION
# --------------------------------------------------

@traceable(
    name="youtube_transcript_extraction",
    run_type="tool",
    process_outputs=lambda output: {
        "language": output[1],
        "character_count": len(output[0])
    }
)
@lru_cache(maxsize=16)
def _fetch_transcript_data(video_id: str):

    try:
        api = YouTubeTranscriptApi()

        transcript_data = api.fetch(
            video_id,
            languages=["en"]
        )

        transcript = "\n".join(
            segment.text
            for segment in transcript_data
        )

        language = transcript_data.language

        if not transcript.strip():
            raise ValueError(
                "The video returned an empty transcript."
            )

        return transcript, language

    except Exception as error:
        raise RuntimeError(
            f"Unable to retrieve YouTube transcript: {error}"
        ) from error


@traceable(name="fetch_video_transcript", run_type="tool")
def fetch_video_transcript(video_id: str):

    return _fetch_transcript_data(video_id)


# --------------------------------------------------
# CREWAI TOOL
# --------------------------------------------------

class YouTubeTranscriptInput(BaseModel):

    video_url: str = Field(
        description="Public YouTube video URL."
    )


class YouTubeTranscriptTool(BaseTool):

    name: str = "YouTube Transcript Extractor"

    description: str = (
        "Retrieves available English captions directly from "
        "YouTube using the youtube-transcript-api package. "
        "Does not require an API key or local transcription model."
    )

    args_schema: Type[BaseModel] = YouTubeTranscriptInput

    def _run(self, video_url: str) -> str:

        try:
            video_id = extract_video_id(video_url)
            title = fetch_video_title(video_id)

            transcript, language = fetch_video_transcript(video_id)

            return (
                f"VIDEO TITLE: {title}\n"
                f"LANGUAGE: {language}\n"
                f"COMPLETE TRANSCRIPT:\n\n"
                f"{transcript}"
            )

        except Exception as error:
            return f"Transcript extraction error: {error}"


youtube_transcript_tool = YouTubeTranscriptTool()

# Compatibility with existing agents.py imports
yt_tool = youtube_transcript_tool
