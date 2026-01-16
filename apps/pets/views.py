from django.db import transaction
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, datetime
from rest_framework import viewsets, permissions, response, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *


class AnimalTypeViewSet(viewsets.ModelViewSet):
    queryset = AnimalType.objects.filter(is_active=True)
    serializer_class = AnimalTypeReadSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'slug']

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return AnimalTypeReadSerializer
        return AnimalTypeSerializer


    @action(detail=False, methods=['POST'], permission_classes=[permissions.IsAuthenticated, permissions.IsAdminUser])
    def bulk_create(self, request):
        """
        Crea múltiples AnimalType desde un array JSON
        Ejemplo de payload:
        {
            "data": [
                {"slug": "perro", "name": "Perro", "is_active": true},
                {"slug": "gato", "name": "Gato", "is_active": true}
            ]
        }
        """
        serializer = AnimalTypeBulkCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data['data']
            created_objects = []
            errors = []
            
            for index, item_data in enumerate(data):
                try:
                    # Crear cada AnimalType individualmente
                    animal_type = AnimalType.objects.create(**item_data)
                    created_objects.append({
                        "index": index,
                        "id": animal_type.id,
                        "slug": animal_type.slug,
                        "name": animal_type.name
                    })
                except Exception as e:
                    errors.append({
                        "index": index,
                        "data": item_data,
                        "error": str(e)
                    })
            
            response_data = {
                "message": f"Procesados {len(data)} registros",
                "created": len(created_objects),
                "errors": len(errors),
                "created_objects": created_objects
            }
            
            if errors:
                response_data["errors_detail"] = errors
                return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BreedViewSet(viewsets.ModelViewSet):
    queryset = Breed.objects.filter(is_active=True)
    serializer_class = BreedReadSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['animal_type', ]
    search_fields = ['name', ]


    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return BreedReadSerializer
        return BreedSerializer


    @action(detail=False, methods=['POST'], permission_classes=[permissions.IsAuthenticated, permissions.IsAdminUser])
    def bulk_create(self, request):
        """
        Crea múltiples Breed desde un array JSON
        Relaciona cada raza con su AnimalType correspondiente
        
        Ejemplo de payload:
        {
            "data": [
                {
                    "animal_type_slug": "perro", 
                    "name": "Labrador Retriever", 
                    "is_active": true
                },
                {
                    "animal_type_slug": "perro",
                    "name": "Pastor Alemán", 
                    "is_active": true
                },
                {
                    "animal_type_slug": "gato",
                    "name": "Siamés",
                    "is_active": true
                }
            ]
        }
        """
        serializer = BreedBulkCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data['data']
            created_objects = []
            errors = []
            
            for index, item_data in enumerate(data):
                try:
                    # Obtener el AnimalType por slug
                    animal_type_slug = item_data.pop('animal_type_slug')
                    
                    try:
                        animal_type = AnimalType.objects.get(slug=animal_type_slug, is_active=True)
                    except AnimalType.DoesNotExist:
                        errors.append({
                            "index": index,
                            "data": item_data,
                            "error": f"AnimalType con slug '{animal_type_slug}' no existe o está inactivo"
                        })
                        continue
                    
                    # Verificar si la raza ya existe para este animal_type
                    if Breed.objects.filter(animal_type=animal_type, name=item_data['name']).exists():
                        errors.append({
                            "index": index,
                            "data": item_data,
                            "error": f"La raza '{item_data['name']}' ya existe para {animal_type.name}"
                        })
                        continue
                    
                    # Crear el Breed con la relación
                    breed = Breed.objects.create(animal_type=animal_type, **item_data)
                    created_objects.append({
                        "index": index,
                        "id": breed.id,
                        "animal_type": animal_type.name,
                        "animal_type_slug": animal_type.slug,
                        "name": breed.name,
                        "is_active": breed.is_active
                    })
                    
                except Exception as e:
                    errors.append({
                        "index": index,
                        "data": item_data,
                        "error": str(e)
                    })
            
            response_data = {
                "message": f"Procesados {len(data)} registros",
                "created": len(created_objects),
                "errors": len(errors),
                "created_objects": created_objects
            }
            
            if errors:
                response_data["errors_detail"] = errors
                return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.filter(is_active=True)
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['owner', 'breed', 'breed__animal_type' ]
    search_fields = ['name', ]


    def list(self, request, *args, **kwargs):
        """
        Lista todos los AnimalType activos
        """
        return super().list(request, *args, **kwargs)


    def create(self, request, *args, **kwargs):
        # Copiar los datos para poder modificarlos
        data = request.data.copy()
        
        # Extraer los campos auxiliares
        breed = data.pop('breed', None)[0]
        owner_email = data.pop('owner_email', None)

        # Extraer e instanciar la raza del animal
        # breed_instance = Breed.objects.filter(id=data.pop('breed')[0]).first() if 'breed' in data else None

        # Obtener Breed si se proporciona
        if breed:
            try:
                breed = Breed.objects.get(
                    id=breed, 
                    is_active=True
                )
                data['breed'] = breed.id  # Asignar el ID al campo del modelo
            except Breed.DoesNotExist:
                return Response(
                    {'breed': f"Raza '{breed}' no encontrada"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Obtener Owner por email si se proporciona
        if owner_email:
            try:
                owner = User.objects.get(email=owner_email)
                data['owner'] = owner.id  # Asignar el ID al campo del modelo
            except User.DoesNotExist:
                return Response(
                    {'owner_email': f"Usuario con email '{owner_email}' no encontrado"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Crear el serializer con los datos procesados
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # Crear la mascota
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @action(detail=False, methods=["POST"], serializer_class=PetTransferStartSerializer)
    def start_transfer(self, request, pk=None):
        pet = self.get_object()  # IsOwner
        data = self.get_serializer(data=request.data, context={"request": request})
        data.is_valid(raise_exception=True)
        to_user = User.objects.get(email=data.validated_data["to_user_email"])

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

    @action(detail=False, methods=["POST"], serializer_class=PetTransferAcceptSerializer, permission_classes=[permissions.IsAuthenticated])
    def accept_transfer(self, request, pk=None):
        with transaction.atomic():
            pet = Pet.objects.select_for_update().get(code=code)
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

    @action(detail=True, methods=["POST"], permission_classes=[permissions.IsAuthenticated])
    def cancel_transfer(self, request, pk=None):
        pet = self.get_object()
        updated = PetTransfer.objects.filter(pet=pet, status="pending").update(
            status="cancelled", cancelled_at=timezone.now()
        )
        if updated == 0:
            return response.Response({"detail": "No hay transferencias pendientes"}, status=404)
        return response.Response({"detail": "Transferencia cancelada"})
