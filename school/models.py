from django.db import models

# Adding fields for state, slots, and payment proof for Home, School, and AccreditedReferral

class School(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    established_year = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100, default=0)  # New field
    num_slots = models.PositiveIntegerField(default=0)  # New field
    payment_proof = models.FileField(upload_to='payment_proofs/', default=0)  # New field

    def __str__(self):
        return self.name
    

class Home(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100, default=0)  # New field
    num_slots = models.IntegerField(default=0) 
    payment_proof = models.FileField(upload_to='payment_proofs/', default=0)  # New field

    def __str__(self):
        return self.name


class AccreditedReferral(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    referral_code = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100, default=0)  # New field
    num_slots = models.PositiveIntegerField(default=0)  # New field
    payment_proof = models.FileField(upload_to='payment_proofs/', default=0)  # New field
    account_details = models.CharField(max_length=255, blank=True, null=True)  # Account details for commission

    def __str__(self):
        return self.name
