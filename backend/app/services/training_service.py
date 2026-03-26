import json
from pathlib import Path

import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from backend.app.core.config import get_settings
from backend.app.core.logging import get_logger
from backend.app.ml.dcgan import Discriminator, Generator, weights_init

settings = get_settings()
logger = get_logger(__name__)


class TrainingService:
    def __init__(self) -> None:
        self.device = settings.default_device

    def _get_dataset(self, dataset_name: str, image_size: int):
        base_transforms = [transforms.Resize(image_size), transforms.CenterCrop(image_size), transforms.ToTensor()]
        if dataset_name == "mnist":
            transform = transforms.Compose(
                [transforms.Resize(image_size), transforms.CenterCrop(image_size), transforms.Grayscale(num_output_channels=3), transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
            )
            return datasets.MNIST(settings.dataset_dir, download=True, transform=transform)
        if dataset_name == "celeba":
            transform = transforms.Compose([*base_transforms, transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
            return datasets.CelebA(settings.dataset_dir, split="train", download=True, transform=transform)
        if dataset_name == "custom":
            transform = transforms.Compose([*base_transforms, transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
            return datasets.ImageFolder(settings.dataset_dir / "custom", transform=transform)
        raise ValueError(f"unsupported dataset {dataset_name}")

    def train_dcgan(
        self,
        dataset_name: str,
        epochs: int,
        batch_size: int,
        latent_dim: int,
        learning_rate: float,
        beta1: float,
        image_size: int,
    ) -> tuple[str, str]:
        dataset = self._get_dataset(dataset_name, image_size)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)
        generator = Generator(latent_dim=latent_dim).to(self.device)
        discriminator = Discriminator().to(self.device)
        generator.apply(weights_init)
        discriminator.apply(weights_init)

        criterion = nn.BCELoss()
        optimizer_g = optim.Adam(generator.parameters(), lr=learning_rate, betas=(beta1, 0.999))
        optimizer_d = optim.Adam(discriminator.parameters(), lr=learning_rate, betas=(beta1, 0.999))
        metrics: list[dict[str, float | int]] = []
        real_label = 1.0
        fake_label = 0.0

        for epoch in range(epochs):
            g_loss_epoch = 0.0
            d_loss_epoch = 0.0
            for batch_idx, (real_images, _) in enumerate(dataloader):
                real_images = real_images.to(self.device)
                batch_size_now = real_images.size(0)

                discriminator.zero_grad(set_to_none=True)
                labels = torch.full((batch_size_now,), real_label, dtype=torch.float, device=self.device)
                real_output = discriminator(real_images)
                loss_real = criterion(real_output, labels)
                loss_real.backward()

                noise = torch.randn(batch_size_now, latent_dim, 1, 1, device=self.device)
                fake_images = generator(noise)
                labels.fill_(fake_label)
                fake_output = discriminator(fake_images.detach())
                loss_fake = criterion(fake_output, labels)
                loss_fake.backward()
                optimizer_d.step()

                generator.zero_grad(set_to_none=True)
                labels.fill_(real_label)
                generated_output = discriminator(fake_images)
                loss_g = criterion(generated_output, labels)
                loss_g.backward()
                optimizer_g.step()

                d_loss = (loss_real + loss_fake).item()
                g_loss = loss_g.item()
                d_loss_epoch += d_loss
                g_loss_epoch += g_loss

                if batch_idx % 100 == 0:
                    logger.info("epoch=%s batch=%s d_loss=%.4f g_loss=%.4f", epoch + 1, batch_idx, d_loss, g_loss)

            metrics.append(
                {
                    "epoch": epoch + 1,
                    "d_loss": d_loss_epoch / max(1, len(dataloader)),
                    "g_loss": g_loss_epoch / max(1, len(dataloader)),
                }
            )

        checkpoint_path = Path(settings.model_registry_dir / f"dcgan-{dataset_name}-{epochs}e.pt")
        torch.save(
            {
                "generator": generator.state_dict(),
                "discriminator": discriminator.state_dict(),
                "config": {
                    "dataset_name": dataset_name,
                    "epochs": epochs,
                    "batch_size": batch_size,
                    "latent_dim": latent_dim,
                    "learning_rate": learning_rate,
                    "beta1": beta1,
                    "image_size": image_size,
                },
            },
            checkpoint_path,
        )
        return str(checkpoint_path), json.dumps(metrics)


training_service = TrainingService()
