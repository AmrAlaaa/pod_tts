from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from TTS.api import TTS
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import uvicorn
from fastapi.staticfiles import StaticFiles
import torch

#logging the IP and Port (Must be set as env variables on OS(inside docker image))
print("TTS_IP:", os.getenv("TTS_IP"))
print("TTS_PORT:", os.getenv("TTS_PORT"))

TTS_IP = os.environ["TTS_IP"]
TTS_PORT = int(os.environ["TTS_PORT"]) # Retrieve TTS_PORT and ensure it's an integer
os.environ["COQUI_TOS_AGREED"] = "1"

# Initialize FastAPI app
app = FastAPI()
app.mount("/static", StaticFiles(directory="/out"), name="static")

# Define input model for the request
class PodcastRequest(BaseModel):
    podcastScript: str
    numberOfSpeakers: int
    speaker1Gender: str
    speaker2Gender: str = None  # Optional if only 1 speaker

# Initialize Coqui TTS model (use GPU if available)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Check if GPU is available and set device accordingly
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tts.to(device)
print(f"> Using device: {device}")

# Define speaker WAV files (preloaded)
female_voices = ["voices/female_01.wav", "voices/female_02.wav"]
male_voices = ["voices/male_01.wav", "voices/male_02.wav"]

# Helper function to synthesize speech for a speaker
def synthesize_speech(text, speaker_wav, output_path):
    if not text.strip():  # Ensure the text is not empty
        raise ValueError("Text for synthesis is empty.")

    # Generate the audio file for the given text
    tts.tts_to_file(
        text=text,
        file_path=output_path,
        speaker_wav=speaker_wav,  # Pass speaker wav file directly
        language="en",
        split_sentences=True
    )
    return output_path

@app.get("/")
async def root():
    return {"message": "TTS Server is working"}

# API endpoint to generate the podcast
@app.post("/generate-podcast")
async def generate_podcast(request: PodcastRequest):
    # Validate number of speakers and required genders
    if request.numberOfSpeakers == 1 and request.speaker2Gender:
        raise HTTPException(status_code=400, detail="Speaker 2 gender not required for 1 speaker")
    if request.numberOfSpeakers == 2 and not request.speaker2Gender:
        raise HTTPException(status_code=400, detail="Speaker 2 gender is required for 2 speakers")

    # Choose voices for speakers
    if request.speaker1Gender == "female":
        speaker1_wav = female_voices[0]
    else:
        speaker1_wav = male_voices[0]

    if request.numberOfSpeakers == 2:
        if request.speaker2Gender == "female":
            speaker2_wav = female_voices[1] if request.speaker1Gender == "female" else female_voices[0]
        else:
            speaker2_wav = male_voices[1] if request.speaker1Gender == "male" else male_voices[0]
    else:
        speaker2_wav = None  # Not used in the case of one speaker

    # Initialize list to hold tuples of (text, speaker_wav)
    dialogues = []

    if request.numberOfSpeakers == 2:
        # Split the podcast script by '*' to separate the dialogues of each speaker
        script_lines = request.podcastScript.split("*")

        # Assign lines to the corresponding speakers based on their order
        for idx, line in enumerate(script_lines):
            line = line.strip()
            if not line:
                continue

            # Determine which speaker to use
            speaker_wav = speaker1_wav if idx % 2 == 0 else speaker2_wav
            dialogues.append((line, speaker_wav))  # Store the line and the corresponding speaker
    else:
        # If there's only one speaker, ignore asterisks and use the entire script for speaker 1
        dialogues.append((request.podcastScript, speaker1_wav))

    # Combine all audio segments
    combined_audio = AudioSegment.empty()

    # Generate audio for each dialogue segment
    for text, speaker_wav in dialogues:
        with NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            audio_path = synthesize_speech(text, speaker_wav, temp_audio.name)
            segment = AudioSegment.from_wav(audio_path)

            # Concatenate the audio segments
            combined_audio += segment

    # Save final combined audio file
    final_audio_path = "/out/final_output.wav"
    combined_audio.export(final_audio_path, format="wav")

    # Return the URL for the final audio file
    return {
    "status": "success",
    "output_file_url": f"http://{TTS_IP}:{TTS_PORT}/static/final_output.wav"
    }

    # return {"output_file_url": f"http://{TTS_IP}:{TTS_PORT}/static/final_output.wav"}

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=TTS_PORT)
