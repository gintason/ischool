from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import School, Home, AccreditedReferral
from .serializers import SignUpSerializer
from rest_framework import status
from .models import School, Home, AccreditedReferral
from django.contrib.auth.models import User
from django.core.mail import send_mail

class SignUpAPIView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            account_type = serializer.validated_data['account_type']
            state = serializer.validated_data['state']
            num_slots = serializer.validated_data['num_slots']
            payment_proof = serializer.validated_data['payment_proof']
            account_details = serializer.validated_data.get('account_details', None)

            # Handle creation based on account_type
            if account_type == "school":
                school = School.objects.create(
                    state=state,
                    num_slots=num_slots,
                    payment_proof=payment_proof
                )
                return Response({'message': 'School account created successfully'}, status=status.HTTP_201_CREATED)

            elif account_type == "home":
                home = Home.objects.create(
                    state=state,
                    num_slots=num_slots,
                    payment_proof=payment_proof
                )
                return Response({'message': 'Home account created successfully'}, status=status.HTTP_201_CREATED)

            elif account_type == "accredited_referral":
                if not account_details:
                    return Response({'error': 'Account details are required for Accredited Referral'}, status=status.HTTP_400_BAD_REQUEST)

                accredited_referral = AccreditedReferral.objects.create(
                    state=state,
                    num_slots=num_slots,
                    payment_proof=payment_proof,
                    account_details=account_details
                )
                return Response({'message': 'Accredited Referral account created successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PaymentConfirmationAPIView(APIView):
    def post(self, request):
        # Extract the necessary data from the request
        user_data = request.data
        account_type = user_data['account_type']
        state = user_data['state']
        num_slots = user_data['num_slots']
        payment_status = user_data['payment_status']  # From the payment gateway response

        if payment_status != 'success':
            return Response({'error': 'Payment not confirmed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle the account creation after payment is confirmed
        if account_type == "school":
            # Create the school instance
            school = School.objects.create(state=state, num_slots=num_slots)
            
            # Generate and assign the username for the school
            username = f"001/S001/{str(school.pk).zfill(3)}"
            school.user.username = username
            school.user.save()

        elif account_type == "home":
            # Create the home instance
            home = Home.objects.create(state=state, num_slots=num_slots)
            
            # Generate and assign the username for the home
            username = f"001/H001/{str(home.pk).zfill(3)}"
            home.user.username = username
            home.user.save()

        elif account_type == "accredited_referral":
            # Handle the accredited referral logic here
            referral = AccreditedReferral.objects.create(state=state, num_slots=num_slots)
            
            # Generate and assign the username for the referral
            username = f"001/AR/{str(referral.pk).zfill(3)}"
            referral.user.username = username
            referral.user.save()

        # Now, create student usernames and passwords
        assigned_usernames = []
        for i in range(num_slots):
            student_username = f"{username[:7]}{str(i+1).zfill(3)}"
            student_password = student_username  # Password is the same as username
            assigned_usernames.append(student_username)

            # Create students (we assume you have a student model related to the user)
            student_user = User.objects.create(username=student_username)
            student_user.set_password(student_password)
            student_user.save()

            # You can store the student details if you need, e.g., in a "Student" model.

        # Send username and password to user's email
        send_mail(
            'Your Username and Password',
            f'Your username is {username}, and your password is {student_password}.',
            'no-reply@schoolapp.com',
            [user_data['email']],
            fail_silently=False,
        )

        return Response({
            'message': 'Payment confirmed and users created successfully!',
            'assigned_usernames': assigned_usernames
        }, status=status.HTTP_201_CREATED)