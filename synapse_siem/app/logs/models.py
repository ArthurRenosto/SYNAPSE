from django.db import models
from django.utils import timezone


class LogFile(models.Model):
    """Representa um arquivo de log analisado"""
    filename = models.CharField(max_length=255)
    filepath = models.TextField()
    content = models.TextField(blank=True)  # Conteúdo do arquivo
    size_bytes = models.BigIntegerField()
    analyzed_at = models.DateTimeField(default=timezone.now)
    total_lines = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'log_files'
        
    def __str__(self):
        return self.filename


class LogAnalysis(models.Model):
    """Representa uma análise completa de logs"""
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_files = models.IntegerField(default=0)
    total_findings = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('running', 'Em execução'),
        ('completed', 'Concluída'),
        ('failed', 'Falhou')
    ], default='running')
    
    class Meta:
        db_table = 'log_analyses'
        
    def __str__(self):
        return f"Análise {self.id} - {self.started_at}"


class LogFinding(models.Model):
    """Representa um achado/alerta encontrado nos logs"""
    SEVERITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica')
    ]
    
    analysis = models.ForeignKey(LogAnalysis, on_delete=models.CASCADE, related_name='findings')
    log_file = models.ForeignKey(LogFile, on_delete=models.CASCADE)
    line_number = models.IntegerField()
    content = models.TextField()
    rule_name = models.CharField(max_length=100)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    description = models.TextField()
    recommendation = models.TextField(blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'log_findings'
        indexes = [
            models.Index(fields=['severity']),
            models.Index(fields=['rule_name']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"{self.rule_name} - {self.severity}"


class Rule(models.Model):
    """Representa uma regra de detecção"""
    name = models.CharField(max_length=100, unique=True)
    pattern = models.TextField()
    severity = models.CharField(max_length=10, choices=LogFinding.SEVERITY_CHOICES)
    description = models.TextField()
    recommendation = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rules'
        
    def __str__(self):
        return self.name
