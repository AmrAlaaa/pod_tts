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

# Add a build argument to control caching for the git clone step
ARG BUILD_DATE

RUN git clone https://github.com/AmrAlaaa/pod_tts.git /app/tts

# Set the working directory
WORKDIR /app/tts
ENTRYPOINT ["uvicorn"]
# ENTRYPOINT ["python3"]
# CMD ["tts_api.py"]
# Command to run the FastAPI application with Uvicorn
CMD ["tts_api:app", "--host", "0.0.0.0", "--port", "9000"]
# CMD [ "python3", "tts_api.py" ]

# docker build  -t pod_tts
# docker run --rm -v C:\Users\Amr_Alaa\AppData\Local\tts:/root/.local/share/tts -v C:\Users\Amr_Alaa\tts-output:/out coquiapi
# docker run --rm -v C:\Users\Amr_Alaa\AppData\Local\tts:/root/.local/share/tts -v C:\Users\Amr_Alaa\tts-output:/out -it --entrypoint /bin/bash coquiapi
# docker run --rm --gpus all -p 9000:9000 -v C:\Users\Amr_Alaa\AppData\Local\tts:/root/.local/share/tts -v C:\Users\Amr_Alaa\tts-output:/out -it --entrypoint /bin/bash coquiapi

# docker run --rm --gpus all -p 9000:9000 -v C:\Users\Amr\AppData\Local\tts:/root/.local/share/tts -v C:\Users\Amr\Music:/out -it --entrypoint /bin/bash pod_tts
# docker run --rm --gpus all -p 9000:9000 -v C:\Users\Amr\AppData\Local\tts:/root/.local/share/tts -v C:\Users\Amr\Music:/out -e TTS_IP="192.168.1.52" -e TTS_PORT="9000" --entrypoint "python3 tts_api.py" pod_tts

# docker run --rm --gpus all -p 9000:9000 -v C:\Users\Amr\AppData\Local\tts:/root/.local/share/tts -v C:\Users\Amr\Music:/out pod_tts