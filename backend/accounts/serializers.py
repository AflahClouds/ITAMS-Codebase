from django.contrib.auth.models import User as AuthUser
from rest_framework import serializers

from .models import Department, Location, Permission, Role, User


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'description')


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'address')


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'code', 'name')


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_codes = serializers.SlugRelatedField(
        source='permissions', slug_field='code',
        queryset=Permission.objects.all(), many=True, write_only=True, required=False)
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ('id', 'name', 'description', 'permissions', 'permission_codes', 'user_count')

    def get_user_count(self, obj):
        return obj.user_set.count()


class UserSerializer(serializers.ModelSerializer):
    department_details = DepartmentSerializer(source='department', read_only=True)
    role_details = RoleSerializer(source='role', read_only=True)
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    login_username = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'user_name', 'emp_id', 'email_id', 'mob_no', 'department',
                  'department_details', 'designation', 'role', 'role_details',
                  'status', 'username', 'password', 'login_username', 'created', 'modified')

    def get_login_username(self, obj):
        return obj.account.username if obj.account else None

    def _sync_account(self, profile, username, password):
        if not username and not password:
            return
        if profile.account is None:
            if not username or not password:
                raise serializers.ValidationError(
                    "Both username and password are required to create a login account.")
            if AuthUser.objects.filter(username=username).exists():
                raise serializers.ValidationError("That login username is already taken.")
            account = AuthUser.objects.create_user(
                username=username, email=profile.email_id, password=password)
            profile.account = account
            profile.save(update_fields=["account"])
        else:
            if username and username != profile.account.username:
                if AuthUser.objects.filter(username=username).exclude(pk=profile.account.pk).exists():
                    raise serializers.ValidationError("That login username is already taken.")
                profile.account.username = username
            if password:
                profile.account.set_password(password)
            profile.account.email = profile.email_id
            profile.account.save()

    def create(self, validated_data):
        username = validated_data.pop('username', '')
        password = validated_data.pop('password', '')
        profile = super().create(validated_data)
        self._sync_account(profile, username, password)
        return profile

    def update(self, instance, validated_data):
        username = validated_data.pop('username', '')
        password = validated_data.pop('password', '')
        profile = super().update(instance, validated_data)
        self._sync_account(profile, username, password)
        if profile.account:
            profile.account.is_active = (profile.status == "Active")
            profile.account.save(update_fields=["is_active"])
        return profile


class UserLiteSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = User
        fields = ('id', 'user_name', 'emp_id', 'department_name')
