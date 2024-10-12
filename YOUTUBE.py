from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from urllib.parse import urlparse, parse_qs
import os
from io import BytesIO
from reportlab.pdfgen import canvas



def extract_video_id(link):
    """
    Extract the video id from a YouTube video link.
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
    op = YouTubeTranscriptApi.get_transcript(video_id)
    op_use = TextFormatter.format_transcript(op,op)
    return op_use




def transcript_to_pdf(lines):
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer)

    # Set font and font size
    pdf.setFont("Helvetica", 12)

    # Add title (optional)
    pdf.drawString(50, 750, "YouTube Transcript")

    # Write each line of transcript with a line spacing
    y_pos = 700  # Starting position for the text
    for line in lines:
        pdf.drawString(50, y_pos, line)
        y_pos -= 15  # Adjust Y position for each line (line spacing)

    # Save the PDF document
    pdf.save()

    # Write the PDF content to a file (optional)
    with open("transcript.pdf", "wb") as output_file:
        output_file.write(pdf_buffer.getvalue())



        

