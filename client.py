import requests

url = "http://127.0.0.1:8000/check-audio/"

with open("sample.wav", "rb") as file:
    files = {"file": ("sample.wav", file, "audio/wav")}
    response = requests.post(url, files=files)

print(response.json())
