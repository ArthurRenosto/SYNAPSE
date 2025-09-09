from rest_framework import serializers


class LogAnalysisResponseSerializer(serializers.Serializer):
    summary = serializers.DictField()
    total_findings = serializers.IntegerField()
    findings = serializers.ListField()


class ReportFileSerializer(serializers.Serializer):
    filename = serializers.CharField()
    created_at = serializers.FloatField()
    size = serializers.IntegerField()
