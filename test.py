from youtube_transcript_api import YouTubeTranscriptApi

a = YouTubeTranscriptApi.get_transcript("_MWDpfg4Exg")
def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

# Function to display transcript
def display_transcript(transcript):
    for entry in transcript:
        start_time = format_time(entry['start'])
        end_time = format_time(entry['start'] + entry['duration'])
        print(f"[{start_time} - {end_time}] {entry['text']}")

# Display the transcript
display_transcript(a)
