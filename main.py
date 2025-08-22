import requests

model_id = "bananas-para-consumo-humano/2"
api_key = "iXJNcsFQHuw4Vtfk6MZ8"
image_path = "test.png"

with open(image_path, "rb") as image_file:
    response = requests.post(
        url=f"https://classify.roboflow.com/{model_id}?api_key={api_key}",
        files={"file": image_file}
    )

print(response.status_code)
print(response.json())
