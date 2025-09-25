from django.contrib import admin
from .models import AnimalType, Breed, Pet, PetTransfer 

@admin.register(AnimalType)
class AnimalTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")

@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "animal_type", "is_active")
    list_filter = ("animal_type", "is_active")
    search_fields = ("name",)

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "breed", "owner", "is_active", "last_transferred_at", "created_at")
    list_filter  = ("breed", "is_active")
    search_fields = ("name", "owner__email", "owner__username")

@admin.register(PetTransfer)
class PetTransferAdmin(admin.ModelAdmin):
    list_display = ("id", "pet", "from_user", "to_user", "status", "created_at", "expires_at")
    list_filter  = ("status",)
    search_fields = ("code",)