from rest_framework import serializers
from .models import AnimalType, Breed, Pet, PetTransfer

class AnimalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalType
        fields = ["id", "slug", "name", "is_active"]


class BreedSerializer(serializers.ModelSerializer):
    animal_type = AnimalTypeSerializer(read_only=True)
    animal_type_id = serializers.PrimaryKeyRelatedField(
        source="animal_type", queryset=AnimalType.objects.filter(is_active=True), write_only=True
    )

    class Meta:
        model = Breed
        fields = ["id", "name", "is_active", "animal_type", "animal_type_id"]


class PetSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = [
            "id", "owner", "name", "animal_type", "breed", "sex",
            "birth_date", "emergency_phone", "address",
            "tattoos", "microchip", "neutered",
            "notes", "curp", "weight_kg", "height_cm",
            "photo", "photo_url",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at", "photo_url"]

    def get_photo_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.photo.url) if obj.photo else None

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class PetPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ["photo"]


class PetTransferStartSerializer(serializers.Serializer):
    to_user_id = serializers.IntegerField()

class PetTransferAcceptSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=12)
