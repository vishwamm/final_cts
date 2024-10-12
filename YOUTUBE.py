from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
from urllib.parse import urlparse, parse_qs
import os
from io import BytesIO
from reportlab.pdfgen import canvas


def extract_video_id(link):
    """
    Extract the video ID from a YouTube video link.
    """
    # Parse the link using urlparse
    parsed_url = urlparse(link)
    
    if parsed_url.netloc == "www.youtube.com":
        # Extract the video id from the query parameters for the www.youtube.com format
        query_params = parse_qs(parsed_url.query)
        if "v" in query_params:
            return query_params["v"][0]
        else:
            return None
    elif parsed_url.netloc == "youtu.be":
        # Extract the video id from the path for the youtu.be format
        path = parsed_url.path
        if path.startswith("/"):
            path = path[1:]
        return path
    else:
        # Return None for all other link formats
        return None


def GetSubtitles(video_id):
    try:
        # Get the transcript using the YouTubeTranscriptApi
        op = YouTubeTranscriptApi.get_transcript(video_id)

        # Use the TextFormatter to format the transcript as plain text
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(op)

        return formatted_transcript.splitlines()

    except TranscriptsDisabled:
        return ["Subtitles are disabled for this video."]
    except NoTranscriptFound:
        return ["No subtitles found for this video."]
    except Exception as e:
        return [f"An error occurred: {str(e)}"]


def transcript_to_pdf(lines, output_filename="transcript.pdf"):
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer)

    # Set font and font size
    pdf.setFont("Helvetica", 12)

    # Add title (optional)
    pdf.drawString(50, 750, "YouTube Transcript")

    # Write each line of the transcript with line spacing
    y_pos = 700  # Starting position for the text
    for line in lines:
        pdf.drawString(50, y_pos, line)
        y_pos -= 15  # Adjust Y position for each line (line spacing)

        # If we run out of space on the current page, start a new page
        if y_pos < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y_pos = 750  # Reset to the top of the new page

    # Save the PDF document
    pdf.save()

    # Write the PDF content to a file
    with open(output_filename, "wb") as output_file:
        output_file.write(pdf_buffer.getvalue())

    print(f"Transcript saved to {output_filename}")
