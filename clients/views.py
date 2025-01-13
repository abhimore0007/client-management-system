from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Client, Project
from .serializers import ClientSerializer, ProjectSerializer, UserSerializer
# Create your views here.

@api_view(['GET', 'POST'])
def list_or_create_clients(request):
    if request.method == 'GET':
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def client_detail_or_update_or_delete(request, id):
    try:
        client = Client.objects.get(id=id)
    except Client.DoesNotExist:
        return Response({'detail': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        projects = client.projects.all()
        project_serializer = ProjectSerializer(projects, many=True)
        client_serializer = ClientSerializer(client)
        data = client_serializer.data
        data['projects'] = project_serializer.data
        return Response(data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = ClientSerializer(client, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save(updated_at=True)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

@api_view(['POST'])
def create_project(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return Response({'detail': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    user_ids = [user_data['id'] for user_data in request.data.get('users', [])]
    users = User.objects.filter(id__in=user_ids)

    if len(users) != len(user_ids):
        return Response({'detail': 'Some users not found'}, status=status.HTTP_400_BAD_REQUEST)

    data = {
        'project_name': request.data.get('project_name'),
        'client': client.id, 
        'created_by': request.user.id,  
        'users': user_ids, 
    }

    serializer = ProjectSerializer(data=data)

    if serializer.is_valid():
        project = serializer.save() 


        response_data = {
            'id': project.id,
            'project_name': project.project_name,
            'client': client.client_name, 
            'users': [{'id': user.id, 'name': user.username} for user in project.users.all()],
            'created_at': project.created_at.isoformat(),
            'created_by': project.created_by.username,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_projects(request):
    projects = request.user.projects.all()
    serialized_projects = ProjectSerializer(projects, many=True)

    response_data = []
    for project in serialized_projects.data:
        project_data = {
            'id': project['id'],
            'project_name': project['project_name'],
            'created_at': project['created_at'],
            'created_by': project['created_by'],
        }
        response_data.append(project_data)

    return Response(response_data)
