# Use the Coqui TTS base image with GPU support
FROM ghcr.io/coqui-ai/tts:latest

# Install ffmpeg
RUN apt-get update && apt-get install -y \
ffmpeg \
git \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install fastapi uvicorn pydub

# Expose the port for FastAPI
EXPOSE 9000

RUN git clone https://github.com/AmrAlaaa/pod_tts.git /app/tts

# Set the working directory
WORKDIR /app/tts

# Command to run the FastAPI application with Uvicorn
CMD ["uvicorn", "tts_api:app", "--host", "0.0.0.0", "--port", "9000"]

# docker run --rm -v C:\Users\Amr_Alaa\AppData\Local\tts:/root/.local/share/tts -v C:\Users\Amr_Alaa\tts-output:/out coquiapi
# docker run --rm -v C:\Users\Amr_Alaa\AppData\Local\tts:/root/.local/share/tts -v C:\Users\Amr_Alaa\tts-output:/out -it --entrypoint /bin/bash coquiapi
# docker run --rm --gpus all -v C:\Users\Amr_Alaa\AppData\Local\tts:/root/.local/share/tts -v C:\Users\Amr_Alaa\tts-output:/out -it --entrypoint /bin/bash coquiapi