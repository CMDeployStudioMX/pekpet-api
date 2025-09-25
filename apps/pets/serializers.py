from rest_framework import serializers
from .models import *


class AnimalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalType
        fields = "__all__"


class AnimalTypeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalType
        fields = ("name", "slug", "id")


class AnimalTypeBulkCreateSerializer(serializers.Serializer):
    data = serializers.ListField(
        child=serializers.DictField(),
        help_text="Lista de objetos AnimalType a crear"
    )

    def validate_data(self, value):
        """Validar cada elemento del array"""
        for item in value:
            if 'slug' not in item or 'name' not in item:
                raise serializers.ValidationError(
                    "Cada item debe tener 'slug' y 'name'"
                )
            
            # Validar slug único
            if AnimalType.objects.filter(slug=item['slug']).exists():
                raise serializers.ValidationError(
                    f"El slug '{item['slug']}' ya existe"
                )
        return value


class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = "__all__"

class BreedReadSerializer(serializers.ModelSerializer):
    animal_type = AnimalTypeReadSerializer(read_only=True)    
    class Meta:
        model = Breed
        fields = ("name", "animal_type", "id")
        depth = 2

class BreedBulkCreateSerializer(serializers.Serializer):
    data = serializers.ListField(
        child=serializers.DictField(),
        help_text="Lista de objetos Breed a crear"
    )

    def validate_data(self, value):
        """Validar cada elemento del array"""
        required_fields = ['animal_type_slug', 'name']
        
        for index, item in enumerate(value):
            # Validar campos requeridos
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(
                        f"Item {index}: Campo requerido '{field}' faltante"
                    )
            
            # Validar que el animal_type_slug existe
            animal_type_slug = item['animal_type_slug']
            if not AnimalType.objects.filter(slug=animal_type_slug, is_active=True).exists():
                raise serializers.ValidationError(
                    f"Item {index}: AnimalType con slug '{animal_type_slug}' no existe o está inactivo"
                )
            
            # Validar nombre no vacío
            if not item['name'].strip():
                raise serializers.ValidationError(
                    f"Item {index}: El nombre no puede estar vacío"
                )
        
        return value

class PetSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    # photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = [
            "id", "owner", "name", "breed", "sex",
            "birth_date", "emergency_phone", "address",
            "tattoos", "microchip", "neutered",
            "notes", "curp", "weight_kg", "height_cm",
            # "photo", "photo_url",
            "is_active", "last_transferred_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at", "photo_url", "last_transferred_at"]

    # def get_photo_url(self, obj):
    #     request = self.context.get("request")
    #     return request.build_absolute_uri(obj.photo.url) if (request and obj.photo) else None

    # def validate(self, attrs):
    #     animal_type = attrs.get("animal_type") or getattr(self.instance, "animal_type", None)
    #     breed = attrs.get("breed") or getattr(self.instance, "breed", None)
    #     if breed and animal_type and breed.animal_type_id != animal_type.id:
    #         raise serializers.ValidationError("La raza no pertenece al tipo de animal indicado.")
    #     return attrs

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
