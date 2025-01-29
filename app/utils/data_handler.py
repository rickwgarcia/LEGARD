# utils/data_handler.py
import os
import pandas as pd
import datetime

class DataHandler:
    @staticmethod
    def load_user_info(username):
        info_file = os.path.join("Users", username, "info.txt")
        user = []
        df = pd.DataFrame(columns=['Day', 'Value'])
        if os.path.exists(info_file):
            with open(info_file, "r") as file:
                for i, f in enumerate(file):
                    if i == 0:
                        user.append(f.strip().split())
                    else:
                        line = f.strip().split()
                        if len(line) >= 4:
                            df = df.append({'Day': line[0], 'Value': [int(line[1]), int(line[2]), int(line[3])]}, ignore_index=True)
        day = len(df) + 1
        return user, df, day
    
    @staticmethod
    def save_performance(username, day, info, x, y, y2):
        user_path = os.path.join("Users", username)
        current_time = datetime.datetime.now()
        today = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        performance_file = os.path.join(user_path, f"{today}.txt")
        with open(performance_file, "w") as f:
            f.write("Repetition\tMax Angle\tAvg. Velocity(cm/s)\tTime\tDistance\n")
            for record in info:
                f.write("\t".join(map(str, record)) + "\n")
            f.write("X(Time)\tY(Sensor 1 Angle)\tY(Sensor 2 Angle)\n")
            for xs, ys, y2s in zip(x, y, y2):
                f.write(f"{xs}\t{ys}\t{y2s}\n")
        
        # Update user info
        info_txt = os.path.join(user_path, "info.txt")
        with open(info_txt, "a") as file:
            file.write(f"Day{day}\t{len(info)}\t{max(x) if x else 0}\t{y.count(0)}\n")

