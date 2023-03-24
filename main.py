import os
import openai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from flask import Flask, jsonify, request

# ChatGPT API key and model name
OPENAI_API_KEY = 'key-xxxxxxxxxxxxxxx'

# Flask app initialization
app = Flask("api")

# ChatGPT initialization
openai.api_key = OPENAI_API_KEY

# Extracts the transcript of a YouTube video using YouTubeTranscriptApi
def get_video_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en', 'tr'])
        text = ""
        for line in transcript.fetch():
            text += line['text'] + " "
        return text
    except Exception as e:
        print(e)
        return None

# Summarizes the transcript using ChatGPT
def summarize_transcript(prompt):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt= f'Aşağıdaki metin hakkında notlar yazın. Tam cümleler içinde madde işaretleri kullanın: {prompt}',
            temperature=0.7,
            max_tokens=1400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0 
        )           
        return response.choices[0].text.strip()
    except openai.error.APIError as error:
        print('An error occurred: %s' % error)
        return None

# Flask app endpoint for summarizing a video transcript
@app.route('/summarize', methods=['POST'])
def index():
    data = request.json
    video_id = data.get('video_id', None)
    transcript = summarize_transcript(get_video_transcript(video_id))
    if transcript is not None:
        summary = transcript
        response = {'summary': summary}
    else:
        response = {'error': 'An error occurred while processing the transcript.'}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)