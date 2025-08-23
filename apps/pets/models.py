from django.db import models
from django.conf import settings

class AnimalType(models.Model):
    # p.ej. dog, cat, bird…
    slug = models.SlugField(unique=True, max_length=40)
    name = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Breed(models.Model):
    animal_type = models.ForeignKey(AnimalType, on_delete=models.CASCADE, related_name="breeds")
    name = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("animal_type", "name")]
        ordering = ["animal_type__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.animal_type.name})"


def pet_photo_path(instance, filename):
    # media/pets/<user_id>/<pet_id>/foto.ext
    return f"pets/{instance.owner_id}/{instance.id or 'new'}/{filename}"


class Pet(models.Model):
    SEX_CHOICES = [("M", "Macho"), ("F", "Hembra")]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pets")
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

    notes = models.TextField(blank=True)            # señas particulares
    curp = models.CharField(max_length=30, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    photo = models.ImageField(upload_to=pet_photo_path, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} – {self.animal_type.name}"


class PetTransfer(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("cancelled", "Cancelled"),
    ]
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="transfers")
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pet_transfers_out")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pet_transfers_in")
    code = models.CharField(max_length=12)  # p.ej. token simple que compartes
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["code", "status"])]

    def __str__(self):
        return f"{self.pet_id} {self.status}"
