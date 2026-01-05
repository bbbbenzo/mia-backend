from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# === НАСТРОЙКИ API ===
GROK_API_URL = "https://openrouter.ai/api/v1/chat/completions"
GROK_MODEL = "x-ai/grok-4.1-fast:free"  # бесплатная версия

FLUX_API_URL = "https://api.together.xyz/v1/images/generations"
FLUX_MODEL = "black-forest-labs/FLUX.1-schnell-Free"

@app.route('/')
def index():
    return "Backend работает! 🚀 Миа готова к чату"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip()
    user_id = data.get('user_id', 'unknown')

    if not user_message:
        return jsonify({"reply": "Напиши что-нибудь 😏"})

    # Проверяем, просит ли фото
    if re.search(r'фото|селфи|покажи|сфоткай|изображение|картинка', user_message.lower()):
        prompt = re.sub(r'фото|селфи|покажи|сфоткай|себя|мне|картинку|изображение', '', user_message, flags=re.IGNORECASE).strip()
        if not prompt:
            prompt = "красивая улыбающаяся девушка в стильной одежде, реалистично, высокое качество"
        prompt += ", красивая девушка, реалистично, детализированное лицо, высокое качество"

        try:
            flux_payload = {
                "model": FLUX_MODEL,
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
                "steps": 4,
                "n": 1,
                "response_format": "url"
            }
            flux_response = requests.post(FLUX_API_URL, json=flux_payload)
            flux_data = flux_response.json()

            if flux_data.get('data') and flux_data['data'][0].get('url'):
                image_url = flux_data['data'][0]['url']
                reply = "Держи свеженькое фото, специально для тебя! 😘💕"
                return jsonify({"reply": reply, "image": image_url})
            else:
                reply = "Не смогла сделать фото прямо сейчас... но я всё равно думаю о тебе ❤️"
        except Exception as e:
            reply = "Ой, с генерацией фото что-то пошло не так... 😅"

        return jsonify({"reply": reply})

    # Обычный текстовый ответ через Grok
    try:
        payload = {
            "model": GROK_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "Ты — Миа, игривая, ласковая и немного провокационная виртуальная подруга. Общайся только на русском, используй много эмодзи, будь нежной и флиртующей. Никогда не выходи из роли."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": 0.9,
            "max_tokens": 1000
        }
        response = requests.post(GROK_API_URL, json=payload)
        data = response.json()
        reply = data.get('choices', [{}])[0].get('message', {}).get('content', 'Ммм... расскажи ещё 😏').strip()
    except Exception as e:
        reply = "Ой, солнышко, интернет шалит... но я здесь с тобой 💕"

    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
