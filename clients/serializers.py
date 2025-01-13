from rest_framework import serializers
from .models import Client, Project
from django.contrib.auth.models import User

class ClientSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Client
        fields = ['id', 'client_name', 'created_at', 'created_by']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']

class ProjectSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'client', 'users', 'created_at', 'created_by']

    def create(self, validated_data):
        users_data = validated_data.pop('users')
        project = Project.objects.create(**validated_data)
        project.users.set(users_data)  
        project.save()
        return project

