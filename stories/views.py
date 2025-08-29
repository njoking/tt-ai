import json
import os
import uuid

import replicate
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from together import Together

from .models import Story
ELEVENLABS_API_KEY = 'sk_266ba8895079bf8eebaa6e347c40680b8698726ab4da23e8'

client = ElevenLabs(
    api_key=None,
)
os.environ["REPLICATE_API_TOKEN"] = "r8_070aO4rwYhGO7AR8sCJw2Ybt7at7YCo48lPxZ"
together_client = Together(api_key="a356f3a9aff6efcb0b64bdfa6801d28ea6e9988db52fdef8903770e34ea4d8b1")


# View for the home page
def home(request):
    return render(request, 'home.html')


# View to generate stories
def stories(request):
    return render(request, "stories.html")


def generate_story(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        word = data.get('word')
        if not word:
            return JsonResponse({"error": "Word is required"}, status=400)
        try:
            response = together_client.chat.completions.create(
                model="meta-llama/Llama-3-70b-chat-hf",
                messages=[
                    {"role": "system",
                     "content": """You are a seasoned Story teller who makes a captivating shortstory based on a given word."""},
                    {"role": "user",
                     "content": f"Please generate a captivating and creative short story based on the following word or phrase: {word}"}
                ]
            )
            story = response.choices[0].message.content
        except Exception as e:
            print(e)
            story = "Not Available"

        try:
            # Generate image
            image_filename = generate_image(story)
        except Exception as e:
            print(e)
            image_filename = "Not Available"

        try:
            # Generate audio
            audio_filename = text_to_speech_file(story)
        except Exception as e:
            print(e)
            audio_filename = "Not available"

        # Save story to the database
        saved_story = Story(
            story_text=story,
            audio_file=f'audio/{audio_filename}' if audio_filename else None,
            image_file=image_filename if image_filename else None
        )
        saved_story.save()

        return JsonResponse({
            "story": story if story else "Not Available",
            "image_url": saved_story.image_file if saved_story.image_file else "Not Available",
            "audio_url": saved_story.audio_file.url if saved_story.audio_file else "Not Available"
        })


def text_to_speech_file(text: str) -> str:
    text =text[:500]
    # Calling the text_to_speech conversion API with detailed parameters
    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam pre-made voice
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # Generating a unique file name for the output MP3 file
    audio_filename = f"{uuid.uuid4()}.mp3"
    save_file_path = os.path.join(settings.MEDIA_ROOT, 'audio', audio_filename)

    # Ensuring the directory exists
    os.makedirs(os.path.dirname(save_file_path), exist_ok=True)

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")

    # Return the filename of the saved audio file
    return audio_filename


def generate_image(story_text):
    output = replicate.run(
        "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
        input={
            "width": 768,
            "height": 768,
            "prompt": story_text,
            "scheduler": "K_EULER",
            "num_outputs": 1,
            "guidance_scale": 7.5,
            "num_inference_steps": 50
        }
    )
    print(output)
    return output[0]
