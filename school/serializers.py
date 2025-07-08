from rest_framework import serializers
from .models import School, Home, AccreditedReferral

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class HomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Home
        fields = '__all__'

class AccreditedReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccreditedReferral
        fields = '__all__'

# Adding specific fields for Sign-Up process
class SignUpSerializer(serializers.Serializer):
    account_type = serializers.ChoiceField(choices=["home", "school", "accredited_referral"])
    state = serializers.CharField()
    num_slots = serializers.IntegerField()
    payment_proof = serializers.FileField()
    account_details = serializers.CharField(allow_blank=True, required=False)  # Only for accredited_referral

    def validate(self, data):
        account_type = data.get('account_type')
        if account_type == "accredited_referral" and not data.get("account_details"):
            raise serializers.ValidationError("Account details are required for Accredited Referral.")
        return data
