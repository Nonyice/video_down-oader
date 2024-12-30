from flask import Flask, render_template, request, send_file, flash
import os
import yt_dlp
import random
import string

app = Flask(__name__)

app.config['SECRET_KEY'] = ''

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def generate_random_filename(extension):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + extension

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/extract', methods=['POST'])
def extract():
    video_url = request.form.get('video_url')

    if not video_url:
        return "No video URL provided.", 400

    try:
        # Create options for yt-dlp
        video_path = os.path.join(DOWNLOAD_FOLDER, generate_random_filename(".mp4"))
        audio_path = os.path.join(DOWNLOAD_FOLDER, generate_random_filename(".mp3"))

        ydl_opts_video = {
            'format': 'bestvideo',
            'outtmpl': video_path,
        }

        ydl_opts_audio = {
            'format': 'bestaudio',
            'outtmpl': audio_path,
        }

        # Download video stream
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            ydl.download([video_url])

        # Download audio stream
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            ydl.download([video_url])

        return f"""
            <h3>Download Links</h3>
            <ul>
                <li><a href="/download?file={os.path.basename(video_path)}" target="_blank">Download Video</a></li>
                <li><a href="/download?file={os.path.basename(audio_path)}" target="_blank">Download Audio</a></li>
            </ul>
        """

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger"), 500
        return render_template('base.html')

@app.route('/download')
def download():
    filename = request.args.get('file')
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return "File not found.", 404
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
