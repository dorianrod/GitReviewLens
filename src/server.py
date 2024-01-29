from src.app.create_app import create_app
from src.infra.monitoring.logger import logger

app = create_app(logger)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
