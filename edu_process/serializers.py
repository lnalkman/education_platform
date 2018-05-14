from rest_framework import serializers

from teacher.models import Course, Category
from .models import Profile


class CourseAuthorSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'url')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    author = CourseAuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True)
    students_count = serializers.IntegerField()
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Course
        exclude = ('students',)
