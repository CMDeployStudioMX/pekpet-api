from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
import secrets
import string


SEX_CHOICES = [
        ("M", "Macho"),
        ("F", "Hembra")
    ]

STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("cancelled", "Cancelled"),
    ]

class AnimalType(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    slug = models.SlugField(unique=True, max_length=40)
    name = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.name}"


class Breed(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    animal_type = models.ForeignKey(AnimalType, on_delete=models.CASCADE, related_name="breeds")
    name = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.name}"


class Pet(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pets")
    name = models.CharField(max_length=80)
    animal_type = models.ForeignKey(AnimalType, on_delete=models.PROTECT, related_name="pets")
    breed = models.ForeignKey(Breed, on_delete=models.SET_NULL, null=True, blank=True, related_name="pets")
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True)

    birth_date = models.DateField(null=True, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)

    tattoos = models.BooleanField(default=False)
    microchip = models.BooleanField(default=False)
    neutered = models.BooleanField(default=False)

    notes = models.TextField(blank=True)
    curp = models.CharField(max_length=30, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    photo = models.FileField(upload_to='pets/photos/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    last_transferred_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.id} - {self.name}"


class PetTransfer(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="transfers")
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pet_transfers_out")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pet_transfers_in")

    code = models.CharField(max_length=16, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        indexes = [models.Index(fields=["pet", "status"])]
        constraints = [
            models.UniqueConstraint(
                fields=["pet"],
                condition=models.Q(status="pending"),
                name="uniq_pending_transfer_per_pet"
            )
        ]

    @staticmethod
    def generate_code(length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @classmethod
    def start(cls, *, pet: Pet, from_user, to_user, ttl_hours: int = 48) -> "PetTransfer":
        if from_user.id == to_user.id:
            raise ValueError("El receptor no puede ser el mismo que el emisor.")
        code = cls.generate_code(12)
        expires = timezone.now() + timedelta(hours=ttl_hours)
        return cls.objects.create(
            pet=pet, from_user=from_user, to_user=to_user, code=code, expires_at=expires
        )

    def mark_accepted(self):
        self.status = "accepted"
        self.accepted_at = timezone.now()
        self.save(update_fields=["status", "accepted_at"])
        pet = self.pet
        pet.last_transferred_at = self.accepted_at
        pet.save(update_fields=["last_transferred_at"])

    def mark_cancelled(self):
        self.status = "cancelled"
        self.cancelled_at = timezone.now()
        self.save(update_fields=["status", "cancelled_at"])

    def is_expired(self) -> bool:
        return bool(self.expires_at and self.expires_at < timezone.now())

    def __str__(self):
        return f"Transfer {self.id} pet={self.pet_id} status={self.status}"
