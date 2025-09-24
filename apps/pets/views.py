from django.db import transaction
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from rest_framework import viewsets, permissions, decorators, response, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *


class AnimalTypeViewSet(viewsets.ModelViewSet):
    queryset = AnimalType.objects.filter(is_active=True)
    serializer_class = AnimalTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

class BreedViewSet(viewsets.ModelViewSet):
    queryset = Breed.objects.filter(is_active=True)
    serializer_class = BreedSerializer
    permission_classes = [permissions.IsAuthenticated]

class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.filter(is_active=True)
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['owner', 'animal_type', ]
    search_fields = ['name', ]

    # @decorators.action(detail=True, methods=["POST"], serializer_class=PetPhotoSerializer)
    # def upload_photo(self, request, pk=None):
    #     pet = self.get_object()
    #     ser = self.get_serializer(pet, data=request.data)
    #     ser.is_valid(raise_exception=True)
    #     ser.save()
    #     return response.Response(PetSerializer(pet, context={"request": request}).data)

    @decorators.action(detail=True, methods=["POST"], serializer_class=PetTransferStartSerializer)
    def start_transfer(self, request, pk=None):
        pet = self.get_object()  # IsOwner
        data = self.get_serializer(data=request.data, context={"request": request})
        data.is_valid(raise_exception=True)
        to_user = User.objects.get(id=data.validated_data["to_user_id"])

        # cooldown
        cooldown_days = int(getattr(settings, "PET_TRANSFER_COOLDOWN_DAYS", 7))
        if pet.last_transferred_at:
            next_allowed = pet.last_transferred_at + timedelta(days=cooldown_days)
            if timezone.now() < next_allowed:
                remaining = next_allowed - timezone.now()
                remaining_days = (remaining.days + (1 if remaining.seconds else 0))
                return response.Response(
                    {"detail": f"No puedes transferir esta mascota aún. Inténtalo en ~{remaining_days} día(s)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # única pending
        if PetTransfer.objects.filter(pet=pet, status="pending").exists():
            return response.Response(
                {"detail": "Ya existe una transferencia pendiente para esta mascota."},
                status=status.HTTP_400_BAD_REQUEST
            )

        tr = PetTransfer.start(pet=pet, from_user=request.user, to_user=to_user, ttl_hours=48)

        return response.Response(
            {"transfer_code": tr.code, "status": tr.status, "expires_at": tr.expires_at},
            status=status.HTTP_201_CREATED
        )

    @decorators.action(detail=True, methods=["POST"], serializer_class=PetTransferAcceptSerializer,
                       permission_classes=[permissions.IsAuthenticated])
    def accept_transfer(self, request, pk=None):
        with transaction.atomic():
            pet = Pet.objects.select_for_update().get(pk=pk)
            ser = self.get_serializer(data=request.data); ser.is_valid(raise_exception=True)
            code = ser.validated_data["code"]

            try:
                tr = PetTransfer.objects.select_for_update().get(
                    pet=pet, to_user=request.user, status="pending", code=code
                )
            except PetTransfer.DoesNotExist:
                return response.Response({"detail": "Transferencia no encontrada o no autorizada."}, status=404)

            if tr.is_expired():
                tr.mark_cancelled()
                return response.Response({"detail": "Transferencia expirada."}, status=400)

            pet.owner = request.user
            pet.save(update_fields=["owner"])
            tr.mark_accepted()
            return response.Response({"detail": "Transferencia aceptada"})

    @decorators.action(detail=True, methods=["POST"], permission_classes=[permissions.IsAuthenticated])
    def cancel_transfer(self, request, pk=None):
        pet = self.get_object()
        updated = PetTransfer.objects.filter(pet=pet, status="pending").update(
            status="cancelled", cancelled_at=timezone.now()
        )
        if updated == 0:
            return response.Response({"detail": "No hay transferencias pendientes"}, status=404)
        return response.Response({"detail": "Transferencia cancelada"})
