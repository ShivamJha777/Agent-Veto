import sqlite3
import os
import shutil
import requests
from Ai_text_api import model_chat
from youtube_transcript_api import YouTubeTranscriptApi
import time
from mtranslate import translate
import PyPDF2
import rename, getcwd
from webscout import YTdownloader
from webscout import weather as w
from webscout import PERPLEXITY
from rich import print
def web_search(query):
    """Searches the web for the given query."""
    result= ""
    perplexity = PERPLEXITY() 
    # Stream the response
    response = perplexity.chat(query)
    for chunk in response:
        result += chunk
    return result
def code_model(prompt):
    """Generates code using the given prompt."""
    return model_chat(prompt,model='o1-preview')
def weather(city):
    """Fetches the weather of a city."""
    return w.get_weather(city)
def download_audio(video_id):
    youtube_link = video_id 
    handler = YTdownloader.Handler(query=youtube_link)
    for third_query_data in handler.run(format='mp3', quality='128kbps', limit=1):
        audio_path = handler.save(third_query_data, dir=getcwd())  
        rename(audio_path, "audio.mp3")

def download_video(video_id):
    youtube_link = video_id 
    handler = YTdownloader.Handler(query=youtube_link)
    for third_query_data in handler.run(format='mp4', quality='auto', limit=1):
        video_path = handler.save(third_query_data, dir=getcwd())  
        rename(video_path, "video.mp4")
def make_files(file_name,extension,content=''):
    """Creates a file of the given name with the given extension and content(if provided)."""
    with open(f"{file_name}.{extension}", "w") as file:
        file.write(content)

def get_pdf_content(pdf_name,start_page,end_page):
    """Extracts the content of a PDF file."""
    reader = PyPDF2.PdfReader(pdf_name)
    a = ''
    for i in range(start_page, end_page):
        page = reader.pages[i]
        content = page.extract_text()
        a += str(content)
def translate_english(phrase):
    """Translates a phrase from English to Hindi."""
    english = translate(phrase,'en','hindi')
    return english

def get_transcript(video_id=''):
    """Fetches the transcript of a YouTube video."""
    video_id = video_id.replace('https://www.youtube.com/watch?v=','')
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        def format_time(seconds):
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        transcript = ''
# Function to display transcript
        def display_transcript(transcript=transcript_list):
            for entry in transcript:
                start_time = format_time(entry['start'])
                end_time = format_time(entry['start'] + entry['duration'])
                transcript += f"[{start_time} - {end_time}] {entry['text']}\n"
        return transcript
# Display the transcript
        display_transcript(transcript)
    except Exception as e:
        print("Error:", e)
        return None
def fetch_website_content(search_url: str) -> str:
    
    """Fetches the content of a webpage.

    Args:
        search_url: The URL of the webpage to fetch.

    Returns:
        The content of the webpage as a string.

    Raises:
        requests.exceptions.RequestException: If there is an error
            making the request.
    """

    jinna_url = "https://r.jina.ai"
    response = requests.get(f"{jinna_url}/{search_url}").text
    print("Fetched the Website content")
    return response
def get_latest_chrome_url() -> str:
    """
    Retrieves the URL of the most recent webpage visited in Google Chrome.

    Returns:
        str: The URL of the most recent webpage visited in Google Chrome.
    """
    chrome_history_path = os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data\Default\History"

    # Destination path for the copy of the history file
    history_db_path = os.path.join(os.getcwd(), "ChromeHistoryCopy.txt")

    # Copy the Chrome history database to a new location
    shutil.copy2(chrome_history_path, history_db_path)

    # Connect to the Chrome history database
    conn = sqlite3.connect(history_db_path)
    cursor = conn.cursor()

    # Execute a query to retrieve the latest URL from the history
    cursor.execute("SELECT url FROM urls ORDER BY last_visit_time DESC LIMIT 1")
    latest_url = cursor.fetchone()[0]

    # Close the connection
    conn.close()
    os.remove(history_db_path)

    print("Latest URL:", latest_url)
    return latest_url
