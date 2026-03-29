from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.files.storage import default_storage
from django.conf import settings
import json

from .models import (
    Owners,
    StayHostelDetails,
    ApartmentStayDetails,
    CommericialDetails,
    HostelFloorRoom,
    ApartmentFloorUnit,
    BankDetails,
    CommercialFloor,
    Tenent,
    TenantBeds
)

from .serializers import (
    OwnerRegistrationSerializer,
    HostelSerializer,
    ApartmentSerializer,
    CommercialSerializer,
    BankSerializer,
    TenentSerializer,
    TenantLoginSerializer,
    OwnerLoginSerializer,
    TenantSerializer
)


@api_view(['POST'])
@transaction.atomic
def register_owner(request):
    print("Request Data:", request.data)
    print("Request Files:", request.FILES)

    stay_type = request.data.get("stayType")

    if stay_type not in ["hostel", "apartment", "commercial"]:
        return Response({"error": "Invalid stayType"}, status=status.HTTP_400_BAD_REQUEST)

    # 1️⃣ OWNER
    owner_serializer = OwnerRegistrationSerializer(data=request.data)
    if not owner_serializer.is_valid():
        transaction.set_rollback(True)
        return Response(owner_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    owner = owner_serializer.save(status='pending')

    # 2️⃣ FACILITIES
    FACILITY_FIELDS = [
        "wifi",
        "parking",
        "food",
        "lift",
        "power_backup",
        "security",
        "play_area",
        "mess",
        "laundry",
        "water",
        "ac",
        "non_ac",
    ]

    facilities = [
        field for field in FACILITY_FIELDS
        if str(request.data.get(field)).lower() == "true"
    ]

    # 3️⃣ SAVE MULTIPLE GALLERY IMAGES
    uploaded_gallery_files = request.FILES.getlist("gallery_images")
    gallery_file_paths = []

    for file in uploaded_gallery_files:
        saved_path = default_storage.save(f"property_gallery/{file.name}", file)
        gallery_file_paths.append(saved_path)

    # 4️⃣ PROPERTY DATA
    property_data = request.data.dict()
    property_data.pop("facilities", None)
    property_data.pop("gallery_images", None)

    property_data["owner"] = owner.id
    property_data["facilities"] = facilities
    property_data["gallery_images"] = gallery_file_paths

    if stay_type == "hostel":
        serializer = HostelSerializer(data=property_data)
    elif stay_type == "apartment":
        serializer = ApartmentSerializer(data=property_data)
    else:
        serializer = CommercialSerializer(data=property_data)

    if not serializer.is_valid():
        transaction.set_rollback(True)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    property_obj = serializer.save()

    # 5️⃣ BANK
    bank_data = request.data.copy()
    bank_data["owner"] = owner.id

    bank_serializer = BankSerializer(data=bank_data)
    if not bank_serializer.is_valid():
        transaction.set_rollback(True)
        return Response(bank_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    bank_serializer.save()

    # 6️⃣ FLOORS
    building_layout = request.data.get("building_layout")

    if building_layout:
        try:
            layout = json.loads(building_layout)
        except json.JSONDecodeError:
            transaction.set_rollback(True)
            return Response(
                {"error": "Invalid building_layout JSON"},
                status=status.HTTP_400_BAD_REQUEST
            )

        for floor_data in layout:
            floor_no = floor_data.get("floorNo")

            if stay_type == "hostel":
                for room in floor_data.get("rooms", []):
                    HostelFloorRoom.objects.create(
                        owner=owner,
                        hostel=property_obj,
                        floor=floor_no,
                        roomNo=room.get("roomNo"),
                        sharing=room.get("beds")
                    )

            elif stay_type == "apartment":
                for flat in floor_data.get("flats", []):
                    ApartmentFloorUnit.objects.create(
                        owner=owner,
                        apartment=property_obj,
                        floor=floor_no,
                        flatNo=flat.get("flatNo"),
                        bhk=flat.get("bhk")
                    )

            elif stay_type == "commercial":
                for section in floor_data.get("sections", []):
                    CommercialFloor.objects.create(
                        owner=owner,
                        commercial_property=property_obj,
                        floorNo=floor_no,
                        sectionNo=section.get("sectionNo"),
                        area_sqft=section.get("area")
                    )

    return Response(
        {
            "message": "Registration successful. Wait for approval (2 days)",
            "status": owner.status,
            "created_at": owner.created_at,
            "email": owner.email
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
def register_tenent(request):
    print("Request Data:", request.data)
    print("Request Files:", request.FILES)

    serializer = TenentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Tenent registered successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        {
            "message": "Validation Error",
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def tenant_login(request):
    serializer = TenantLoginSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            tenant = Tenent.objects.get(email=email)

            if tenant.password == password:
                return Response(
                    {
                        "message": "Login Successful",
                        "tenant_id": tenant.id,
                        "name": tenant.name,
                        "email": tenant.email
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Invalid Password"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Tenent.DoesNotExist:
            return Response(
                {"error": "Email not registered"},
                status=status.HTTP_404_NOT_FOUND
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def owner_login(request):
    serializer = OwnerLoginSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            owner = Owners.objects.get(email=email)
            
            if owner.password != password:
                return Response(
                    {"error", "Invalid Password"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if owner.status == "pending":
                return Response(
                    {"error": "Your account is pending approval",
                     "status" : owner.status,
                     "message": "Please wait for the admin to approval"
                     },
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if owner.status == "suspend":
                return Response(
                    {
                        "error" : "Your account is Suspeded",
                        "status" : owner.status,
                        "message" : "Please contact admin"
                    },
                    status = status.HTTP_403_FORBIDDEN
                )
            if owner.status == "active" and owner.password == password:
                return Response(
                    {
                        "message": "Login Successful",
                    },
                    status = status.HTTP_200_OK
                )
            
    

            

            return Response(
                {"error": "Invalid Password"},
                status=status.HTTP_400_BAD_REQUEST
                )

        except Owners.DoesNotExist:
            return Response(
                {"error": "Owner not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_hostel_step3(request, email):
    try:
        owner = Owners.objects.get(email=email)
    except Owners.DoesNotExist:
        return Response({"error": "Owner not found"}, status=status.HTTP_404_NOT_FOUND)

    hostel = StayHostelDetails.objects.filter(owner=owner).first()
    apartment = ApartmentStayDetails.objects.filter(owner=owner).first()
    commercial = CommericialDetails.objects.filter(owner=owner).first()

    response_data = {}

    if hostel is not None:
        floors = HostelFloorRoom.objects.filter(hostel=hostel)

        layout = {}
        for room in floors:
            floor_no = room.floor
            if floor_no not in layout:
                layout[floor_no] = []

            layout[floor_no].append({
                "roomNo": room.roomNo,
                "beds": room.sharing
            })

        result = []
        for floor_no, rooms in layout.items():
            result.append({
                "floorNo": floor_no,
                "rooms": rooms
            })

        response_data = {
            "property_type": "hostel",
            "building_layout": result
        }

    elif apartment is not None:
        floors = ApartmentFloorUnit.objects.filter(apartment=apartment)

        layout = {}
        for flat in floors:
            floor_no = flat.floor
            if floor_no not in layout:
                layout[floor_no] = []

            layout[floor_no].append({
                "flatNo": flat.flatNo,
                "bhk": flat.bhk
            })

        result = []
        for floor_no, flats in layout.items():
            result.append({
                "floorNo": floor_no,
                "flats": flats
            })

        response_data = {
            "property_type": "apartment",
            "building_layout": result
        }

    elif commercial is not None:
        floors = CommercialFloor.objects.filter(commercial_property=commercial)

        layout = []
        for floor in floors:
            layout.append({
                "floorNo": floor.floorNo,
                "sectionNo": floor.sectionNo,
                "area_sqft": floor.area_sqft
            })

        response_data = {
            "property_type": "commercial",
            "building_layout": layout
        }

    else:
        return Response(
            {"error": "No property found for this owner"},
            status=status.HTTP_404_NOT_FOUND
        )

    response_data["owner"] = {
        "id": owner.id,
        "name": owner.name,
        "email": owner.email,
        "phone": owner.phone
    }

    print("API Response:", response_data)
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_properties_listing(request):
    property_list = []

    def build_gallery_urls(gallery_list):
        if not gallery_list:
            return []
        return [
            request.build_absolute_uri(settings.MEDIA_URL + path)
            for path in gallery_list
        ]

    hostels = StayHostelDetails.objects.select_related('owner').all()
    for hostel in hostels:
        property_list.append({
            "id": str(hostel.id),
            "type": "Hostel",
            "hostelType": hostel.hostelType.capitalize() if hostel.hostelType else None,
            "name": hostel.hostelName,
            "address": hostel.location,
            "contact": hostel.owner.phone if hostel.owner else None,
            "latitude": None,
            "longitude": None,
            "gallery": build_gallery_urls(hostel.gallery_images),
            "isAvailable": True,
            "rating": None,
            "facilities": hostel.facilities if hostel.facilities else [],
        })

    apartments = ApartmentStayDetails.objects.select_related('owner').all()
    for apartment in apartments:
        allowed_tenants = None
        if apartment.tenantType == "family":
            allowed_tenants = "FamilyOnly"
        elif apartment.tenantType == "bachelors":
            allowed_tenants = "BachelorsOnly"

        property_list.append({
            "id": str(apartment.id),
            "type": "Apartment",
            "name": apartment.apartmentName,
            "address": apartment.location,
            "contact": apartment.owner.phone if apartment.owner else None,
            "latitude": None,
            "longitude": None,
            "gallery": build_gallery_urls(apartment.gallery_images),
            "isAvailable": True,
            "rating": None,
            "facilities": apartment.facilities if apartment.facilities else [],
            "allowedTenants": allowed_tenants,
        })

    commercials = CommericialDetails.objects.select_related('owner').all()
    for commercial in commercials:
        property_list.append({
            "id": str(commercial.id),
            "type": "Commercial",
            "name": commercial.commercialName,
            "address": commercial.location,
            "contact": commercial.owner.phone if commercial.owner else None,
            "latitude": None,
            "longitude": None,
            "gallery": build_gallery_urls(commercial.gallery_images),
            "isAvailable": True,
            "rating": None,
            "facilities": commercial.facilities if commercial.facilities else [],
        })

    return Response(
        {
            "count": len(property_list),
            "data": property_list
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def registerbeds(request):
    serializer = TenantSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Tenant Added Successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_tenantsbeds(request):
    tenants = TenantBeds.objects.all()
    serializer = TenantSerializer(tenants, many=True)

    print("Tenant Data:", serializer.data)

    return Response(
        {
            "message": "Tenant list fetched successfully",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )
@api_view(['GET'])
def owner_admin_list(request):
    owners = Owners.objects.all().order_by('-id')

    data = []
    for owner in owners:
        data.append({
            "id": owner.id,
            "owner_name": owner.name,
            "phone": owner.phone,
            "email": owner.email,
            "properties": 1,
            "status": owner.status
        })

    return Response(
        {
            "count": len(data),
            "data": data
        },
        status=status.HTTP_200_OK
    )



@api_view(['GET'])
def get_owner_full_details(request, email):
    try:
        owner = Owners.objects.get(email=email)
    except Owners.DoesNotExist:
        return Response(
            {"error": "Owner not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    def build_file_url(file_field):
        if file_field:
            try:
                return request.build_absolute_uri(file_field.url)
            except Exception:
                return None
        return None

    def build_gallery_urls(gallery_list):
        if not gallery_list:
            return []
        return [
            request.build_absolute_uri(settings.MEDIA_URL + str(path))
            for path in gallery_list
        ]

    # ---------------- STEP 1 : OWNER DETAILS ----------------
    step1 = {
        "id": owner.id,
        "name": owner.name,
        "email": owner.email,
        "phone": owner.phone,
        "status": owner.status,
        "owner_img_field": build_file_url(owner.owner_img_field)
    }

    # ---------------- STEP 2 : PROPERTY + BANK DETAILS ----------------
    bank = BankDetails.objects.filter(owner=owner).first()

    bank_data = None
    if bank:
        bank_data = {
            "bankName": bank.bankName,
            "ifsc": bank.ifsc,
            "accountNo": bank.accountNo
        }

    property_data = None
    property_type = None

    hostel = StayHostelDetails.objects.filter(owner=owner).first()
    apartment = ApartmentStayDetails.objects.filter(owner=owner).first()
    commercial = CommericialDetails.objects.filter(owner=owner).first()

    # ---------------- STEP 3 : BUILDING LAYOUT ----------------
    building_layout = []

    if hostel:
        property_type = "hostel"
        property_data = {
            "id": hostel.id,
            "stayType": hostel.stayType,
            "hostelName": hostel.hostelName,
            "location": hostel.location,
            "hostelType": hostel.hostelType,
            "facilities": hostel.facilities if hostel.facilities else [],
            "owner_ship_proof": build_file_url(hostel.owner_ship_proof),
            "gallery_images": build_gallery_urls(hostel.gallery_images),
        }

        floors = HostelFloorRoom.objects.filter(hostel=hostel).order_by("floor", "roomNo")
        floor_map = {}

        for room in floors:
            if room.floor not in floor_map:
                floor_map[room.floor] = []

            floor_map[room.floor].append({
                "roomNo": room.roomNo,
                "beds": room.sharing
            })

        for floor_no, rooms in floor_map.items():
            building_layout.append({
                "floorNo": floor_no,
                "rooms": rooms
            })

    elif apartment:
        property_type = "apartment"
        property_data = {
            "id": apartment.id,
            "stayType": apartment.stayType,
            "apartmentName": apartment.apartmentName,
            "location": apartment.location,
            "tenantType": apartment.tenantType,
            "facilities": apartment.facilities if apartment.facilities else [],
            "owner_ship_proof": build_file_url(apartment.owner_ship_proof),
            "gallery_images": build_gallery_urls(apartment.gallery_images),
        }

        floors = ApartmentFloorUnit.objects.filter(apartment=apartment).order_by("floor", "flatNo")
        floor_map = {}

        for flat in floors:
            if flat.floor not in floor_map:
                floor_map[flat.floor] = []

            floor_map[flat.floor].append({
                "flatNo": flat.flatNo,
                "bhk": flat.bhk
            })

        for floor_no, flats in floor_map.items():
            building_layout.append({
                "floorNo": floor_no,
                "flats": flats
            })

    elif commercial:
        property_type = "commercial"
        property_data = {
            "id": commercial.id,
            "stayType": commercial.stayType,
            "commercialName": commercial.commercialName,
            "location": commercial.location,
            "usage": commercial.usage,
            "facilities": commercial.facilities if commercial.facilities else [],
            "owner_ship_proof": build_file_url(commercial.owner_ship_proof),
            "gallery_images": build_gallery_urls(commercial.gallery_images),
        }

        floors = CommercialFloor.objects.filter(
            commercial_property=commercial
        ).order_by("floorNo", "sectionNo")

        floor_map = {}

        for section in floors:
            if section.floorNo not in floor_map:
                floor_map[section.floorNo] = []

            floor_map[section.floorNo].append({
                "sectionNo": section.sectionNo,
                "area_sqft": section.area_sqft
            })

        for floor_no, sections in floor_map.items():
            building_layout.append({
                "floorNo": floor_no,
                "sections": sections
            })

    else:
        return Response(
            {"error": "No property found for this owner"},
            status=status.HTTP_404_NOT_FOUND
        )

    response_data = {
        "message": "Owner full details fetched successfully",
        "property_type": property_type,
        "step1": step1,
        "step2": {
            "property_details": property_data,
            "bank_details": bank_data
        },
        "step3": {
            "building_layout": building_layout
        }
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
def update_owner_status(request, email):
    try:
        owner = Owners.objects.get(email=email)
    except Owners.DoesNotExist:
        return Response({"error": "Owner not found"}, status=404)

    new_status = request.data.get("status")

    if not new_status:
        return Response({"error": "Status required"}, status=400)

    allowed_statuses = ["active", "pending", "suspend"]

    if new_status not in allowed_statuses:
        return Response({
            "error": "Invalid status",
            "allowed": allowed_statuses
        }, status=400)

    owner.status = new_status
    owner.save()

    return Response({
        "message": "Status updated",
        "email": owner.email,
        "status": owner.status
    })



from datetime import timedelta
from django.utils.timezone import now


@api_view(['GET'])
def check_owner_status(request, email):
    try:
        owner = Owners.objects.get(email=email)
    except Owners.DoesNotExist:
        return Response({"error": "Owner not found"}, status=404)

    remaining_time = (owner.created_at + timedelta(days=2)) - now()
    remaining_seconds = int(remaining_time.total_seconds())

    if remaining_seconds < 0:
        remaining_seconds = 0

    return Response({
        "status": owner.status,
        "time_left_seconds": remaining_seconds
    })


# @api_view(['GET'])
# def get_all_property_basic_details(request):
#     data = []

#     def build_file_url(file_field):
#         if not file_field:
#             return None
#         try:
#             if hasattr(file_field, "url") and file_field.url:
#                 return request.build_absolute_uri(file_field.url)
#         except Exception:
#             pass
#         return None

#     def build_first_gallery_image(gallery_list):
#         if not gallery_list or not isinstance(gallery_list, list):
#             return None

#         first_image = gallery_list[0]
#         if not first_image:
#             return None

#         first_image = str(first_image).replace("\\", "/").strip()

#         if not first_image:
#             return None

#         if first_image.startswith("http://") or first_image.startswith("https://"):
#             return first_image

#         first_image = first_image.lstrip("/")

#         if first_image.startswith("media/"):
#             return request.build_absolute_uri("/" + first_image)

#         return request.build_absolute_uri(f"{settings.MEDIA_URL}{first_image}")

#     # Hostels
#     for hostel in StayHostelDetails.objects.all():
#         data.append({
#             "email": hostel.owner.email,
#             "property_type": "hostel",
#             "image": build_first_gallery_image(hostel.gallery_images) or build_file_url(hostel.owner_ship_proof),# here this file has to be replaced
#             "name": hostel.hostelName,
#             "location": hostel.location,
#             "owner_name": hostel.owner.name,
#         })

#     # Apartments
#     for apartment in ApartmentStayDetails.objects.all():
#         data.append({
#             "email": apartment.owner.email,
#             "property_type": "apartment",
#             "image": build_first_gallery_image(apartment.gallery_images) or build_file_url(apartment.owner_ship_proof),
#             "name": apartment.apartmentName,
#             "location": apartment.location,
#             "owner_name": apartment.owner.name,
#         })

#     # Commercial
#     for commercial in CommericialDetails.objects.all():
#         data.append({
#             "email": commercial.owner.email,
#             "property_type": "commercial",
#             "image": build_first_gallery_image(commercial.gallery_images) or build_file_url(commercial.owner_ship_proof),
#             "name": commercial.commercialName,
#             "location": commercial.location,
#             "owner_name": commercial.owner.name,
#         })

#     return Response({
#         "message": "Property basic details fetched successfully",
#         "count": len(data),
#         "data": data
#     }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_all_property_basic_details(request):
    data = []

    def build_file_url(file_field):
        if not file_field:
            return None
        try:
            if hasattr(file_field, "url") and file_field.url:
                return request.build_absolute_uri(file_field.url)
        except Exception:
            pass
        return None

    def build_first_gallery_image(gallery_list):
        if not gallery_list or not isinstance(gallery_list, list):
            return None

        first_image = gallery_list[0]
        if not first_image:
            return None

        first_image = str(first_image).replace("\\", "/").strip()

        if not first_image:
            return None

        if first_image.startswith("http://") or first_image.startswith("https://"):
            return first_image

        first_image = first_image.lstrip("/")

        if first_image.startswith("media/"):
            return request.build_absolute_uri("/" + first_image)

        return request.build_absolute_uri(f"{settings.MEDIA_URL}{first_image}")

    # Hostels - only active owners
    for hostel in StayHostelDetails.objects.select_related("owner").filter(owner__status="active"):
        data.append({
            "email": hostel.owner.email,
            "property_type": "hostel",
            "image": build_first_gallery_image(hostel.gallery_images) or build_file_url(hostel.owner_ship_proof),
            "name": hostel.hostelName,
            "location": hostel.location,
            "owner_name": hostel.owner.name,
        })

    # Apartments - only active owners
    for apartment in ApartmentStayDetails.objects.select_related("owner").filter(owner__status="active"):
        data.append({
            "email": apartment.owner.email,
            "property_type": "apartment",
            "image": build_first_gallery_image(apartment.gallery_images) or build_file_url(apartment.owner_ship_proof),
            "name": apartment.apartmentName,
            "location": apartment.location,
            "owner_name": apartment.owner.name,
        })

    # Commercial - only active owners
    for commercial in CommericialDetails.objects.select_related("owner").filter(owner__status="active"):
        data.append({
            "email": commercial.owner.email,
            "property_type": "commercial",
            "image": build_first_gallery_image(commercial.gallery_images) or build_file_url(commercial.owner_ship_proof),
            "name": commercial.commercialName,
            "location": commercial.location,
            "owner_name": commercial.owner.name,
        })

    return Response({
        "message": "Active property basic details fetched successfully",
        "count": len(data),
        "data": data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def dashboard_counts(request):
    total_owners_count = Owners.objects.filter(status='active').values('phone').distinct().count()
    active_owners_count = Owners.objects.filter(status='active').count()
    pending_owners_count = Owners.objects.filter(status='pending').count()
    suspended_owners_count = Owners.objects.filter(status='suspend').count()

    total_tenants_count = Tenent.objects.count()


    return Response(
        {
            "message": "Dashboard counts fetched successfully",
            "data": {
                "total_owners": total_owners_count,
                "total_properties": active_owners_count,
                "pending_owners": pending_owners_count,
                "suspended_owners": suspended_owners_count,
                "total_tenants": total_tenants_count,
            }
        },
        status=status.HTTP_200_OK
    )