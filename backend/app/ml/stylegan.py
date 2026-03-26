from pathlib import Path


def stylegan_stub(checkpoint_path: Path | None, device: str) -> dict[str, str]:
    available = checkpoint_path is not None and Path(checkpoint_path).exists()
    return {
        "status": "available" if available else "stub",
        "device": device,
        "note": "Integrate NVLabs StyleGAN weights or a hosted model for production usage.",
    }

