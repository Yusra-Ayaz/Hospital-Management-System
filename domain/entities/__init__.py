"""Domain entity namespace; persistence models are isolated in infrastructure."""
from domain.entities.hospital import Appointment, Doctor, Patient

__all__ = ["Appointment", "Doctor", "Patient"]
