from django.db import models
from django.contrib.auth.models import User

SECTION_CHOICES = [
    ('BME', 'Biomedical Engineering'),
    ('ZAD', 'Zain ul Abadin'),
    ('FAH', 'Faizan Hairder'),
    ('KHI', 'Khansa Ibrahim'),
    ('STANDARD', 'Standard Lab'),
    ('MICROBIOLOGY', 'Microbiology Lab'),
    ('HPLC', 'HPLC Lab'),
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