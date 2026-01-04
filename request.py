import requests

url = 'http://localhost:5000/predict'
data = {
    'Age': 30,
    'BusinessTravel': 'Travel_Rarely',
    'DailyRate': 600,
    'DistanceFromHome': 15,
    'Education': 2,
    'EnvironmentSatisfaction': 3,
    'JobSatisfaction': 4,
    'WorkLifeBalance': 3
}

response = requests.post(url, data=data)
print(response.text)
