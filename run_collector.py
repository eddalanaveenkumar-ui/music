from app.collector import collect
from app.config import LANGUAGES

if __name__ == "__main__":
    for lang, queries in LANGUAGES.items():
        for q in queries:
            print(f"Collecting: {q}")
            collect(q)
