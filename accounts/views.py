from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import UserSerializer


# ✅ Connexion ADMIN (Dashboard - session)
def admin_login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.role == 'admin':
            login(request, user)
            return redirect('dash_admin:dashboard')
        else:
            error = "Identifiants incorrects ou accès refusé"
    return render(request, 'pages/login.html', {'error': error})


# ✅ Déconnexion ADMIN
def admin_logout_view(request):
    logout(request)
    return redirect('dash_admin:login')


# ✅ Middleware admin_required
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            return redirect('dash_admin:login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ========================
# API REST (React + JWT)
# ========================

# ✅ Token login ADMIN
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_token_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Identifiants incorrects'}, status=400)
    if user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })


# ✅ Inscription USER
@api_view(['POST'])
@permission_classes([AllowAny])
def user_register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    phone = request.data.get('phone', '')

    if CustomUser.objects.filter(username=username).exists():
        return Response({'error': 'Username déjà utilisé'}, status=400)

    user = CustomUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        phone=phone,
        role='user'
    )
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
        }
    }, status=201)


# ✅ Connexion USER
@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Identifiants incorrects'}, status=400)
    if user.role != 'user':
        return Response({'error': 'Accès refusé'}, status=403)
    if not user.is_active:
        return Response({'error': 'Compte désactivé'}, status=403)
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
        }
    })


# ✅ Déconnexion USER
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    return Response({'message': 'Déconnecté avec succès'})


# ✅ GET profil user connecté
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# ✅ UPDATE profil user connecté
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# ✅ Changer mot de passe
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not user.check_password(old_password):
        return Response({'error': 'Ancien mot de passe incorrect'}, status=400)

    user.set_password(new_password)
    user.save()
    return Response({'message': 'Mot de passe modifié avec succès'})


# ========================
# CRUD USERS (Admin JWT)
# ========================

# ✅ GET tous les users
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)
    users = CustomUser.objects.filter(role='user')
    return Response(UserSerializer(users, many=True).data)


# ✅ GET user par ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, user_id):
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)
    try:
        user = CustomUser.objects.get(id=user_id, role='user')
    except CustomUser.DoesNotExist:
        return Response({'error': 'Utilisateur non trouvé'}, status=404)
    return Response(UserSerializer(user).data)


# ✅ UPDATE user par ID
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)
    try:
        user = CustomUser.objects.get(id=user_id, role='user')
    except CustomUser.DoesNotExist:
        return Response({'error': 'Utilisateur non trouvé'}, status=404)
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# ✅ DELETE user par ID
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)
    try:
        user = CustomUser.objects.get(id=user_id, role='user')
    except CustomUser.DoesNotExist:
        return Response({'error': 'Utilisateur non trouvé'}, status=404)
    user.delete()
    return Response({'message': 'Utilisateur supprimé avec succès'}, status=200)


# ✅ DELETE tous les users
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_users(request):
    if request.user.role != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)
    count, _ = CustomUser.objects.filter(role='user').delete()
    return Response({'message': f'{count} utilisateurs supprimés'}, status=200)