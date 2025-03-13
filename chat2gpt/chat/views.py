import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from dotenv import load_dotenv
from .models import AIResponse

load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Get API Key
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/gpt2"

HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

@csrf_exempt
def generate_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            input_text = data.get('input_text', '')

            if not input_text:
                return JsonResponse({'error': 'No input text provided'}, status=400)

            # Call Hugging Face API
            response = requests.post(HUGGINGFACE_API_URL, headers=HEADERS, json={"inputs": input_text})
            
            if response.status_code != 200:
                return JsonResponse({'error': 'Failed to fetch response from Hugging Face'}, status=500)

            generated_text = response.json()[0]["generated_text"]

            # Save response in database
            AIResponse.objects.create(prompt=input_text, response=generated_text)

            return JsonResponse({'generated_text': generated_text})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON input'}, status=400)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
