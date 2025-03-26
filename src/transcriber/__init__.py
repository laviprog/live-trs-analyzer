import logging
import whisperx

from src.config import settings

logger = logging.getLogger(__name__)

MODEL = whisperx.load_model(
    settings.MODEL,
    device=settings.DEVICE,
    compute_type=settings.COMPUTE_TYPE,
    download_root=settings.DOWNLOAD_ROOT
)