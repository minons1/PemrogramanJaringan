import os

filename="Soal.png"
try:
    with open("dataset/"+filename, "rb") as file:
        print(str(os.path.getsize("dataset/"+filename)))
    
except:
    print("error")  