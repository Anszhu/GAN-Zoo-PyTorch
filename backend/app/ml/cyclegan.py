from pathlib import Path

import torch
from torch import nn


class ResidualBlock(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.ReflectionPad2d(1),
            nn.Conv2d(channels, channels, kernel_size=3),
            nn.InstanceNorm2d(channels),
            nn.ReLU(inplace=True),
            nn.ReflectionPad2d(1),
            nn.Conv2d(channels, channels, kernel_size=3),
            nn.InstanceNorm2d(channels),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.block(x)


class CycleGenerator(nn.Module):
    def __init__(self, channels: int = 3, residual_blocks: int = 6):
        super().__init__()
        layers: list[nn.Module] = [
            nn.ReflectionPad2d(3),
            nn.Conv2d(channels, 64, kernel_size=7),
            nn.InstanceNorm2d(64),
            nn.ReLU(inplace=True),
        ]
        in_features = 64
        out_features = 128
        for _ in range(2):
            layers.extend(
                [
                    nn.Conv2d(in_features, out_features, kernel_size=3, stride=2, padding=1),
                    nn.InstanceNorm2d(out_features),
                    nn.ReLU(inplace=True),
                ]
            )
            in_features = out_features
            out_features *= 2
        for _ in range(residual_blocks):
            layers.append(ResidualBlock(in_features))
        out_features = in_features // 2
        for _ in range(2):
            layers.extend(
                [
                    nn.ConvTranspose2d(in_features, out_features, kernel_size=3, stride=2, padding=1, output_padding=1),
                    nn.InstanceNorm2d(out_features),
                    nn.ReLU(inplace=True),
                ]
            )
            in_features = out_features
            out_features //= 2
        layers.extend([nn.ReflectionPad2d(3), nn.Conv2d(64, channels, kernel_size=7), nn.Tanh()])
        self.model = nn.Sequential(*layers)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.model(inputs)


def load_cyclegan_generator(checkpoint_path: Path | None, device: str) -> CycleGenerator:
    generator = CycleGenerator()
    if checkpoint_path and checkpoint_path.exists():
        state = torch.load(checkpoint_path, map_location=device)
        generator.load_state_dict(state["generator"])
    generator.to(device)
    generator.eval()
    return generator

