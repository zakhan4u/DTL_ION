from django.db import models
from django.contrib.auth.models import User

SECTION_CHOICES = [
    ('JK', 'Jamrod Khan'),
    ('STANDARD', 'Lab Standard'),
    ('SRA', 'Sample Receiving Area'),
    ('MTM', 'Tahir Mursleen'), 
    ('FAA', 'Fatima Akbar'), 
    ('ZA', 'Zainab Ali'),
    ('MF', 'Faizan Haider'), 
    ('SD', 'Sadaf Hafeez'),
    ('MKA', 'Mukarram Anees'), 
    ('ZAD', 'Zain ul Abadin'),
    ('ABB', 'Abbas Ahmed'),
    ('HRD', 'Hira Rashid'), 
    ('SKN', 'Sikandar Khan Niazi'), 
    ('AMT', 'Amat-ul-Mateen'),
    ('SS', 'Sidra Saghir'),
    ('TK', 'Tasneem Kausar'), 
    ('ZAS', 'Zahid Ashraf'), 
    ('WI', 'M. Waqas Ilyas'),
    ('SAH', 'Syed Arsalan Haider'), 
    ('UI', 'Umar Ismaeel'),
    ('HMJ', 'Hafiz M. Junaid'), 
    ('AAS', 'Aamer Sohail'),
    ('ZS', 'Zahid Sarfraz'), 
    ('SHK', 'Shaiza Kanwal'), 
    ('WA', 'Waqas Ahmad'), 
    ('ASA', 'Asim Ali'),
    ('MAM', 'Muhammad Ammad'),
    ('AZ', 'Anam Zehra'), 
    ('SFZ', 'Saira Fayyaz'), 
    ('AB', 'Afifa Bano'),
    ('SN', 'Sumeera Naz'), 
    ('KI', 'Khansa Ibrahim'), 
    ('HNA', 'Hina Naeem'), 
    ('SAB', 'Syeda Asma Batool'),
    ('SRS', 'Syeda Raeesa Shahid'),
    ('QK', 'Qurrat ul Ain Khan'), 
    ('MJ', 'Maria Jahangir'),
    ('ST', 'Sajida Tufail'),
    ('HKA', 'Hafiza Kanwal Azam'), 
    ('AFZ', 'Afshan Zaheer'), 
    ('MSF', 'Muhammad Asif'), 
    ('USM', 'Usman Ali'),
    ('SHM', 'Shahid Mahmood'), 
    ('BRR', 'Bareera Rana'), 
    ('NSS', 'Nasira Sarkar'), 
    ('USG', 'MUHAMMAD USMAN GHANI'),
    ('MTA', 'MUHAMMAD TAHIR'), 
    ('TS', 'Tahira Sultana'), 
    ('MHK', 'M. Haris Khalid'), 
    ('HZ', 'Hijab Zafar'),
    ('AJ', 'Alina Jamil'), 
    ('ABS', 'Abeera Shakeel'), 
    ('KHI', 'Khudeja Idrees'), 
    ('MSS', 'M. Sajjad Shoukat'),
    ('QMS', 'QMS Section'),
    ('STORES', 'Stores'),
    ('PROCUREMENT', 'Procurement'),
    ('DIRECTOR', 'Director'),
]

STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('REVIEWED', 'Reviewed'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    section = models.CharField(max_length=20, choices=SECTION_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.section}"

class Note(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_notes', on_delete=models.CASCADE)
    to_section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    unique_id = models.CharField(max_length=100, unique=True, editable=False)  # Increased length
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    receiver_comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.unique_id:
            sender_section = self.from_user.userprofile.section
            count = Note.objects.filter(unique_id__startswith=f"DTL-ION-{sender_section}-").count() + 1
            self.unique_id = f"DTL-ION-{sender_section}-{count:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.unique_id

class NoteForwardHistory(models.Model):
    note = models.ForeignKey(Note, related_name='forward_history', on_delete=models.CASCADE)
    from_section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    to_section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    forwarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    forwarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.note.unique_id}: {self.from_section} → {self.to_section}"
    

class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100, blank=True)
    purity = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, choices=[
        ('EQUIPMENT', 'Equipment'),
        ('SUPPLIES', 'Supplies'),
        ('CHEMICALS', 'Chemicals'),
        ('GLASSWARE', 'Glassware'),
        ('STANDARDS', 'Standards'),
        ('OTHER', 'Other'),
    ])
    location = models.CharField(max_length=100, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='inventory_items')
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} in {self.location})"
    

class ItemRequest(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='requests')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='item_requests')
    quantity = models.PositiveIntegerField()
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ], default='PENDING')

    def save(self, *args, **kwargs):
        if self.status == 'APPROVED' and self.pk is None:  # New approved request
            if self.item.quantity >= self.quantity:
                self.item.quantity -= self.quantity
                self.item.save()
            else:
                raise ValueError("Insufficient quantity in inventory.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Request for {self.quantity} {self.item.name} by {self.requested_by.username}"