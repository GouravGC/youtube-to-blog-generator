from crewai import Task
from agents import blog_researcher, blog_writer


def create_tasks():

    research_task = Task(
        description=(
            "Analyze the supplied YouTube transcript carefully.\n\n"

            "VIDEO TITLE: {video_title}\n"
            "VIDEO URL: {video_url}\n\n"

            "TRANSCRIPT:\n"
            "{transcript}\n\n"

            "YOUR RESPONSIBILITY:\n"
            "Extract reliable research notes for a short technical blog.\n\n"

            "Identify:\n"
            "1. The central subject of the video.\n"
            "2. The most important concepts explained.\n"
            "3. Technical terminology and its meaning.\n"
            "4. Practical examples explicitly discussed.\n"
            "5. Important relationships between concepts.\n\n"

            "STRICT ACCURACY RULES:\n"
            "- Use only information supported by the transcript.\n"
            "- Never invent examples, statistics, applications or facts.\n"
            "- Do not add outside knowledge to fill missing information.\n"
            "- If an example is unclear or absent, leave it out.\n"
            "- Do not mistake speculation for something stated in the video.\n"
            "- Do not repeat the same concept in different words.\n\n"

            "OUTPUT RULES:\n"
            "- Do not write the blog yourself.\n"
            "- Produce structured, concise research notes.\n"
            "- Maximum 150 words.\n"
            "- Include only information useful for the final blog."
        ),
        expected_output=(
            "Accurate research notes of no more than 150 words, "
            "covering the video's central topic, key concepts, "
            "technical explanations and transcript-supported examples."
        ),
        agent=blog_researcher
    )

    write_task = Task(
        description=(
            "Write a concise and technically accurate blog using "
            "ONLY the research notes produced by the researcher.\n\n"

            "VIDEO TITLE: {video_title}\n\n"

            "STRICT CONTENT REQUIREMENTS:\n"
            "1. Write approximately 300-400 tokens in total, "
            "including the title.\n"
            "2. Start with one meaningful Markdown heading.\n"
            "3. Introduce the central topic briefly.\n"
            "4. Explain the most important concepts clearly.\n"
            "5. Include one transcript-supported example if available.\n"
            "6. End with a short conclusion.\n"
            "7. Use clear, professional and technically accurate language.\n\n"

            "STRICT ACCURACY REQUIREMENTS:\n"
            "- Use only facts present in the research notes.\n"
            "- Do not introduce external information.\n"
            "- Do not invent industry applications or use cases.\n"
            "- Do not add unsupported company or product examples.\n"
            "- If the research notes do not contain an example, "
            "do not manufacture one.\n"
            "- Do not exaggerate claims made in the video.\n\n"

            "STRICT FORMATTING REQUIREMENTS:\n"
            "- Return only the blog in Markdown.\n"
            "- Use short paragraphs.\n"
            "- Avoid unnecessary headings and bullet lists.\n"
            "- Do not include a separate key takeaways section.\n"
            "- Do not include a preface or explanation about the blog.\n"
            "- Avoid repetition and filler sentences.\n\n"

            "IMPORTANT:\n"
            "This is a concise blog, not a comprehensive article. "
            "Prioritize the most valuable information and stay "
            "within the requested 300-400-token target."
        ),
        expected_output=(
            "A concise Markdown technical blog of approximately "
            "300-400 tokens, including its title, based exclusively "
            "on the researcher's notes."
        ),
        agent=blog_writer,
        context=[research_task],
        async_execution=False
    )

    return research_task, write_task