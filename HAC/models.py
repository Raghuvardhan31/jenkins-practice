from django.db import models
from django.utils import timezone

STAY_TYPE_CHOICES = [
    ('hostel', 'Hostel'),
    ('apartment', 'Apartment'),
    ('commercial', 'Commercial'),
]


# ------------------ OWNERS ------------------
class Owners(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    owner_img_field = models.FileField(
        upload_to="identity_proofs/",
        blank=True,
        null=True
    )
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('suspend', 'Suspend'),
    ]
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='pending')

     # ✅ ADD THIS LINE
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ------------------ HOSTEL ------------------
class StayHostelDetails(models.Model):
    HOSTEL_TYPE_CHOICES = [
        ('boys', 'Boys'),
        ('girls', 'Girls'),
        ('coliving', 'Co-Living'),
    ]

    owner = models.ForeignKey(
        Owners,
        on_delete=models.CASCADE,
        related_name="stay_details"
    )

    stayType = models.CharField(max_length=20, choices=STAY_TYPE_CHOICES)
    hostelName = models.CharField(max_length=150, null=True, blank=True)
    location = models.CharField(max_length=255)
    hostelType = models.CharField(max_length=20, choices=HOSTEL_TYPE_CHOICES, blank=True, null=True)
    facilities = models.JSONField(blank=True, null=True)
    owner_ship_proof = models.FileField(upload_to='identity_proofs/', blank=True, null=True)
    gallery_images = models.JSONField(blank=True, null=True) #New

    def __str__(self):
        return self.hostelName or "Hostel"


# ------------------ APARTMENT ------------------
class ApartmentStayDetails(models.Model):
    BHK_CHOICES = [
        ('1', '1 BHK'),
        ('2', '2 BHK'),
        ('3', '3 BHK'),
    ]

    TENANT_TYPE_CHOICES = [
        ('family', 'Family'),
        ('bachelors', 'Bachelors'),
    ]

    owner = models.ForeignKey(
        Owners,
        on_delete=models.CASCADE,
        related_name='apartments'
    )

    stayType = models.CharField(max_length=20, choices=STAY_TYPE_CHOICES)
    apartmentName = models.CharField(max_length=150, null=True, blank=True)
    location = models.CharField(max_length=255)
    # bhk = models.CharField(max_length=10, choices=BHK_CHOICES)
    tenantType = models.CharField(max_length=20, choices=TENANT_TYPE_CHOICES, null=True, blank=True)
    facilities = models.JSONField(blank=True, null=True)
    owner_ship_proof = models.FileField(upload_to='identity_proofs/', blank=True, null=True)
    gallery_images = models.JSONField(blank=True, null=True) #New

    def __str__(self):
        return self.apartmentName or "Apartment"

# ------------------ COMMERCIAL ------------------
class CommericialDetails(models.Model):
    USAGE_CHOICES = [
        ('lease', 'Lease'),
        ('rent', 'Rent'),
    ]

    owner = models.ForeignKey(
        Owners,
        on_delete=models.CASCADE,
        related_name='commercial'
    )

    stayType = models.CharField(max_length=20, choices=STAY_TYPE_CHOICES)
    commercialName = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255)
    usage = models.CharField(max_length=20, choices=USAGE_CHOICES, blank=True, null=True)
    facilities = models.JSONField(blank=True, null=True)
    owner_ship_proof = models.FileField(upload_to='identity_proofs/', blank=True, null=True)
    gallery_images = models.JSONField(blank=True, null=True) #New

    def __str__(self):
        return self.commercialName or "Commercial Property"


# ------------------ BANK ------------------
class BankDetails(models.Model):
    owner = models.ForeignKey(
        Owners,
        on_delete=models.CASCADE,
        related_name="bank_details"
    )

    bankName = models.CharField(max_length=150, null=True, blank=True)
    ifsc = models.CharField(max_length=20, null=True, blank=True)
    accountNo = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f"{self.bankName} - {self.accountNo}"


# ------------------ HOSTEL FLOORS ------------------
class HostelFloorRoom(models.Model):
    owner = models.ForeignKey(
        Owners,
        on_delete=models.CASCADE,
        related_name='hostel_floors'
    )

    hostel = models.ForeignKey(
        StayHostelDetails,
        on_delete=models.CASCADE,
        related_name='floors'
    )

    floor = models.IntegerField()
    roomNo = models.PositiveIntegerField()
    sharing = models.PositiveIntegerField()

    class Meta:
        ordering = ['roomNo']
        unique_together = ('hostel', 'floor', 'roomNo')

    def __str__(self):
        return f"{self.hostel.hostelName} - Floor {self.floor} Room {self.roomNo} ({self.sharing} beds)"
    # floorNo = models.IntegerField()
    # roomNo = models.PositiveIntegerField()
    # beds = models.PositiveIntegerField()

    # class Meta:
    #     ordering = ['roomNo']
    #     unique_together = ('hostel', 'floorNo', 'roomNo')

    # def __str__(self):
    #     return f"{self.hostel.hostelName} - Floor {self.floorNo} Room {self.roomNo} ({self.beds} beds)"


# ------------------ APARTMENT FLOORS ------------------
class ApartmentFloorUnit(models.Model):
    owner = models.ForeignKey(
        Owners,
        on_delete=models.CASCADE,
        related_name='apartment_floors'
    )

    apartment = models.ForeignKey(
        ApartmentStayDetails,
        on_delete=models.CASCADE,
        related_name='floors'
    )

    floor = models.IntegerField()
    flatNo = models.PositiveIntegerField()
    bhk = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.apartment.apartmentName} - Floor {self.floor} Flat {self.flatNo} ({self.bhk} BHK)"


# ------------------ COMMERCIAL FLOORS ------------------
class CommercialFloor(models.Model):

    owner = models.ForeignKey(
        Owners,
        on_delete=models.CASCADE,
        related_name='commercial_floors'
    )

    commercial_property = models.ForeignKey(
        CommericialDetails,
        on_delete=models.CASCADE,
        related_name='floors'
    )

    floorNo = models.PositiveIntegerField()

    sectionNo = models.PositiveIntegerField(null=True, blank=True)

    area_sqft = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["floorNo", "sectionNo"]

    def __str__(self):
        return f"{self.commercial_property.commercialName} - Floor {self.floorNo} Section {self.sectionNo}"


class Tenent(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    IDENTITY_CHOICES = [
        ('Aadhar', 'Aadhar'),
        ('PAN', 'PAN'),
        ('Other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES)
    identityType = models.CharField(max_length=30,choices=IDENTITY_CHOICES)
    identityImage = models.ImageField(upload_to='identity_proofs/')
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.name
    

class TenantBeds(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    bed = models.IntegerField()
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    checkIn = models.DateField()
    checkOut = models.DateField()
    idUri = models.ImageField(upload_to='identity_proofs/', null=True, blank=True)

    def __str__(self):
        return self.name