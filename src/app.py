from ollama import chat
from ollama import ChatResponse
import gradio as gr
import speech_recognition as sr
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

MODEL_AI = 'deepseek-r1:1.5b'


def preguntar(pregunta):
	response: ChatResponse = chat(model=MODEL_AI, messages=[
	  {
	    'role': 'user',
	    'content': pregunta,
	  },
	])

	return response.message.content

def to_text(audio_file):
	r = sr.Recognizer()
	with sr.AudioFile(audio_file) as source:
		audio = r.listen(source)
		transcription = r.recognize_google(audio, language="es-MX")
	return transcription

def to_speech(texto):
	client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
	audio = client.text_to_speech.convert(
		voice_id="pNInz6obpgDQGcFmaJgB",  # Adam pre-made voice
        optimize_streaming_latency="0",
        output_format="mp3_44100_32",
        text=texto,
        model_id="eleven_multilingual_v2",  # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
	)

	save_file_path = "audio/es.mp3"
	with open(save_file_path, "wb") as f:
		for chunk in audio:
			if chunk:
				f.write(chunk)

	return save_file_path

def answer(audio_file):
	question = to_text(audio_file)
	answer = preguntar(question)
	audio_file_path = to_speech(answer)
	return audio_file_path

web = gr.Interface(

	fn=answer,
	inputs=gr.Audio(
			label="You",
			sources=["microphone"],
			type="filepath"
		),
	outputs=gr.Audio(
			label="AI",
		),
	title="VoiceBot",
	# outputs=[gr.Textbox(label="AI", lines=3)],


)

web.launch(share=False)