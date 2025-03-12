import logging
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("logs/trs.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
