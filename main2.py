import logging
import time
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def escribir_log(filename: str):
    logs_dir = "/app/logs"
    path = os.path.join(logs_dir, filename)
    with open(path, "a", encoding="utf-8") as f:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ahora}]\n")

def main():
    i = 0
    while True:
        logging.info("🚀 UTEA Notificaciones ejecutándose...")
        filename = f"log_{i}.txt"
        escribir_log(filename)
        i += 1
        time.sleep(5)

if __name__ == "__main__":
    main()