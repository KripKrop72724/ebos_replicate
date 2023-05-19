from rest_framework import serializers

from ebos2206.models.m06_hr_mas import (
    T06Alw10,
    T06Ded10,
    T06Doc10,
    T06Lon10,
    T06Lvr10,
    T06Tkr10,
)


class T06Alw10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Alw10
        fields = "__all__"


class T06Ded10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Ded10
        fields = "__all__"


class T06Doc10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Doc10
        fields = "__all__"


class T06Lvr10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Lvr10
        fields = "__all__"


class T06Lon10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Lon10
        fields = "__all__"


class T06Tkr10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Tkr10
        fields = "__all__"
