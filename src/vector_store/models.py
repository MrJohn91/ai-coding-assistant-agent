"""Data models for vector store."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Product:
    """Product model representing a bike in the catalog."""

    id: int
    name: str
    type: str
    brand: str
    price_eur: int
    frame_material: str
    suspension: str
    wheel_size: int
    gears: int
    brakes: str
    weight_kg: float
    intended_use: List[str]
    color: str
    motor_power_w: Optional[int] = None
    battery_capacity_wh: Optional[int] = None
    range_km: Optional[int] = None
    max_load_kg: Optional[int] = None

    def to_text(self) -> str:
        """Convert product to text representation for embedding."""
        base_text = f"""{self.name} - {self.brand} {self.type}
Price: €{self.price_eur}
Features: {self.frame_material} frame, {self.suspension}, {self.gears} gears, {self.brakes}
Intended Use: {", ".join(self.intended_use)}
Specs: {self.wheel_size}" wheels, {self.weight_kg}kg
Color: {self.color}"""

        # Add electric bike specific details
        if self.motor_power_w:
            base_text += f"\nMotor: {self.motor_power_w}W"
        if self.battery_capacity_wh:
            base_text += f"\nBattery: {self.battery_capacity_wh}Wh"
        if self.range_km:
            base_text += f"\nRange: {self.range_km}km"
        if self.max_load_kg:
            base_text += f"\nMax Load: {self.max_load_kg}kg"

        return base_text


@dataclass
class FAQEntry:
    """FAQ entry model."""

    question: str
    answer: str
    id: Optional[int] = None

    def to_text(self) -> str:
        """Convert FAQ to text representation for embedding."""
        return f"Question: {self.question}\nAnswer: {self.answer}"
