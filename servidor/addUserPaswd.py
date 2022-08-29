import bcrypt
import pandas as pd
import os.path

if os.path.exists("userData.csv"):
    df = pd.read_csv("userData.csv")
else:
    df = pd.DataFrame(columns=['ID', 'HASHED_PASSWORD'])

user = input("User ID = ")
passwd = input("Password = ")

hashed_password = bcrypt.hashpw(passwd.encode(), bcrypt.gensalt(rounds=15))

newDfData = {'ID': user, 'HASHED_PASSWORD': hashed_password}
df = df.append(newDfData, ignore_index=True)

df.to_csv(path_or_buf="userData.csv", index=False)
