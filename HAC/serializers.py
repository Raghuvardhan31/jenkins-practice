from rest_framework import serializers
from .models import (
    Owners,
    StayHostelDetails,
    ApartmentStayDetails,
    CommericialDetails,
    BankDetails,
    HostelFloorRoom,
    ApartmentFloorUnit,
    CommercialFloor,
    Tenent,
    TenantBeds
)

# ----------------------------
# 1️⃣ Owner Registration
# ----------------------------
class OwnerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owners
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'password',
            'owner_img_field',
            'status'  # ✅ add this
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }


# ----------------------------
# 2️⃣ Bank Serializer
# ----------------------------
class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        fields = [
            'id',
            'owner',
            'bankName',
            'ifsc',
            'accountNo'
        ]


# ----------------------------
# 3️⃣ Hostel Serializer
# ----------------------------
class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StayHostelDetails
        fields = [
            'id',
            'owner',
            'stayType',
            'hostelName',
            'location',
            'hostelType',
            'facilities',
            'owner_ship_proof',
            #'owner_property_photos',
            'gallery_images'   # ⭐ ADDED
        ]


# ----------------------------
# 4️⃣ Hostel Floor/Room Serializer
# ----------------------------
class HostelRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelFloorRoom
        fields = [
            'id',
            'owner',
            'hostel',
            'floorNo',
            'roomNo',
            'beds'
        ]
        extra_kwargs = {
            'owner': {'write_only': True},
            'hostel': {'write_only': True}
        }


# ----------------------------
# 5️⃣ Apartment Serializer
# ----------------------------
class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentStayDetails
        fields = [
            'id',
            'owner',
            'stayType',
            'apartmentName',
            'location',
            # 'bhk',
            'tenantType',
            'facilities',
            'owner_ship_proof',
           # 'owner_property_photos',
            'gallery_images'   # ⭐ ADDED
        ]
        extra_kwargs = {
            'owner': {'write_only': True}
        }


# ----------------------------
# 6️⃣ Apartment Floor/Unit Serializer
# ----------------------------
class ApartmentRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentFloorUnit
        fields = [
            'id',
            'owner',
            'apartment',
            'floorNo',
            'roomNo',
            'bhkType'
        ]
        extra_kwargs = {
            'owner': {'write_only': True},
            'apartment': {'write_only': True}
        }


# ----------------------------
# 7️⃣ Commercial Serializer
# ----------------------------
class CommercialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommericialDetails
        fields = [
            'id',
            'owner',
            'stayType',
            'commercialName',    # ✅ Correct field name
            'location',
            'usage',
            'facilities',
            'owner_ship_proof',
            #'owner_property_photos',
            'gallery_images'   # ⭐ ADDED
            # add other fields as needed
        ]
        extra_kwargs = {'owner': {'write_only': True}}


# ----------------------------
# 8️⃣ Commercial Floor Serializer
# ----------------------------
class CommercialSqftSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommercialFloor
        fields = [
            'id',
            'owner',
            'commercial_property',
            'floorNo',
            'sectionNo',
            'area_sqft'
            # 'squareFeet'
        ]
        extra_kwargs = {
            'owner': {'write_only': True},
            'commercial_property': {'write_only': True}
        }


class TenentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenent
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'gender',
            'identityType',
            'identityImage',
            'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
class TenantLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class OwnerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()




class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantBeds
        fields = '__all__'