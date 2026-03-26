from io import BytesIO
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms

from backend.app.core.config import get_settings
from backend.app.ml.cyclegan import load_cyclegan_generator
from backend.app.ml.dcgan import load_generator

settings = get_settings()


def _tensor_to_png_bytes(tensor: torch.Tensor, size: int | None = None) -> bytes:
    tensor = (tensor.detach().cpu() + 1) / 2
    tensor = tensor.clamp(0, 1)
    image = transforms.ToPILImage()(tensor)
    if size:
        image = image.resize((size, size))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class GANService:
    def __init__(self) -> None:
        self.device = settings.default_device

    def generate_dcgan(self, latent_dim: int, num_images: int, checkpoint_name: str | None, image_size: int) -> list[bytes]:
        checkpoint_path = Path(settings.model_registry_dir / (checkpoint_name or "dcgan-latest.pt"))
        generator = load_generator(checkpoint_path if checkpoint_path.exists() else None, latent_dim, self.device)
        noise = torch.randn(num_images, latent_dim, 1, 1, device=self.device)
        with torch.inference_mode():
            fake_images = generator(noise)
        return [_tensor_to_png_bytes(image, size=image_size) for image in fake_images]

    def transform_cyclegan(self, image_bytes: bytes, checkpoint_name: str | None) -> bytes:
        checkpoint_path = Path(settings.model_registry_dir / (checkpoint_name or "cyclegan-latest.pt"))
        generator = load_cyclegan_generator(checkpoint_path if checkpoint_path.exists() else None, self.device)
        preprocess = transforms.Compose(
            [
                transforms.Resize((256, 256)),
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            ]
        )
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        tensor = preprocess(image).unsqueeze(0).to(self.device)
        with torch.inference_mode():
            generated = generator(tensor)[0]
        return _tensor_to_png_bytes(generated)


gan_service = GANService()
