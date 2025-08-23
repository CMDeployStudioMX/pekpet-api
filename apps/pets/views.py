from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, mixins, decorators, response, status
from .models import AnimalType, Breed, Pet, PetTransfer
from .serializers import (
    AnimalTypeSerializer, BreedSerializer,
    PetSerializer, PetPhotoSerializer,
    PetTransferStartSerializer, PetTransferAcceptSerializer
)

User = get_user_model()


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "owner_id", None) == request.user.id


class AnimalTypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AnimalType.objects.filter(is_active=True)
    serializer_class = AnimalTypeSerializer
    permission_classes = [permissions.AllowAny]


class BreedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = BreedSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Breed.objects.filter(is_active=True)
        # filtro opcional por tipo: /api/breeds/?animal_type=dog  (slug) o id
        t = self.request.query_params.get("animal_type")
        if t:
            qs = qs.filter(animal_type__slug=t) | qs.filter(animal_type__id__iexact=t)
        return qs


class PetViewSet(viewsets.ModelViewSet):
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user, is_active=True).select_related("animal_type", "breed")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @decorators.action(detail=True, methods=["post"], serializer_class=PetPhotoSerializer)
    def upload_photo(self, request, pk=None):
        pet = self.get_object()
        ser = self.get_serializer(pet, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return response.Response(PetSerializer(pet, context={"request": request}).data)

    @decorators.action(detail=True, methods=["post"], serializer_class=PetTransferStartSerializer)
    def start_transfer(self, request, pk=None):
        pet = self.get_object()  # valida IsOwner
        data = self.get_serializer(data=request.data); data.is_valid(raise_exception=True)
        to_user = User.objects.get(id=data.validated_data["to_user_id"])
        # token simple; puedes reemplazarlo por algo firmado
        code = User.objects.make_random_password(length=12)
        tr = PetTransfer.objects.create(pet=pet, from_user=request.user, to_user=to_user, code=code)
        return response.Response({"transfer_code": tr.code, "status": tr.status}, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["post"], serializer_class=PetTransferAcceptSerializer,
                       permission_classes=[permissions.IsAuthenticated])
    def accept_transfer(self, request, pk=None):
        pet = self.get_object()  # si no eres owner, sigue permitiendo para aceptar
        data = self.get_serializer(data=request.data); data.is_valid(raise_exception=True)
        try:
            tr = PetTransfer.objects.get(pet=pet, to_user=request.user, status="pending", code=data.validated_data["code"])
        except PetTransfer.DoesNotExist:
            return response.Response({"detail": "Transferencia no encontrada"}, status=404)
        pet.owner = request.user
        pet.save(update_fields=["owner"])
        tr.status = "accepted"
        tr.accepted_at = timezone.now()
        tr.save(update_fields=["status", "accepted_at"])
        return response.Response({"detail": "Transferencia aceptada"})
