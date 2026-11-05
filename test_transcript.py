
from tools import youtube_transcript_tool

video_url = input("Paste YouTube video URL: ").strip()

print("\nExtracting transcript from cloud service...\n")

result = youtube_transcript_tool._run(video_url)

print("========== TRANSCRIPT RESULT ==========")
print(result[:3000])

print("\n========== EXTRACTION METRICS ==========")
print("Characters returned:", len(result))
print("Extraction successful:", "COMPLETE TRANSCRIPT:" in result)
