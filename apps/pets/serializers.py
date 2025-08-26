from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AnimalType, Breed, Pet, PetTransfer

User = get_user_model()


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
            "is_active", "last_transferred_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at", "photo_url", "last_transferred_at"]

    def get_photo_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.photo.url) if (request and obj.photo) else None

    def validate(self, attrs):
        animal_type = attrs.get("animal_type") or getattr(self.instance, "animal_type", None)
        breed = attrs.get("breed") or getattr(self.instance, "breed", None)
        if breed and animal_type and breed.animal_type_id != animal_type.id:
            raise serializers.ValidationError("La raza no pertenece al tipo de animal indicado.")
        return attrs

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class PetPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ["photo"]


class PetTransferStartSerializer(serializers.Serializer):
    to_user_id = serializers.IntegerField()

    def validate_to_user_id(self, value):
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario destino no existe.")
        request = self.context["request"]
        if request.user.id == user.id:
            raise serializers.ValidationError("El receptor no puede ser el mismo que el emisor.")
        return value


class PetTransferAcceptSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=16)
