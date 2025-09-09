import os
import json
import subprocess
import tempfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FileUploadParser
from django.conf import settings
from .models import LogFile, LogAnalysis, LogFinding


class LogAnalysisView(APIView):
    def get(self, request):
        """Lista arquivos importados disponíveis para análise"""
        try:
            log_files = LogFile.objects.all().order_by('-analyzed_at')
            files_data = []
            
            for log_file in log_files:
                files_data.append({
                    "id": log_file.id,
                    "filename": log_file.filename,
                    "size": log_file.size_bytes,
                    "uploaded_at": log_file.analyzed_at.isoformat(),
                    "total_lines": log_file.total_lines
                })
            
            return Response({
                "message": "Selecione arquivos e clique em 'Run Log Analysis'",
                "available_files": files_data,
                "total_files": len(files_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Erro: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Executa análise nos arquivos selecionados"""
        try:
            selected_ids = request.data.get('file_ids', [])
            
            if not selected_ids:
                # Se nenhum ID específico, analisa todos os arquivos
                log_files = LogFile.objects.all()
            else:
                log_files = LogFile.objects.filter(id__in=selected_ids)
            
            if not log_files.exists():
                return Response(
                    {"error": "Nenhum arquivo disponível para análise"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verifica se arquivos têm conteúdo
            empty_files = [f.filename for f in log_files if not f.content.strip()]
            if empty_files:
                return Response(
                    {"error": f"Arquivos sem conteúdo: {', '.join(empty_files)}. Faça novo upload."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cria nova análise
            analysis = LogAnalysis.objects.create(
                total_files=log_files.count(),
                status='running'
            )
            
            all_findings = []
            total_findings = 0
            errors = []
            
            # Para cada arquivo, analisa usando main.py real
            for log_file in log_files:
                try:
                    findings = self.analyze_file(log_file, analysis)
                    all_findings.extend(findings)
                    total_findings += len(findings)
                except Exception as e:
                    errors.append(f"Erro em {log_file.filename}: {str(e)}")
            
            # Atualiza análise
            analysis.total_findings = total_findings
            analysis.status = 'completed' if not errors else 'failed'
            analysis.save()
            
            # Prepara resposta
            summary = {
                "total_logs": log_files.count(),
                "total_findings": total_findings,
                "by_severity": {}
            }
            
            # Conta por severidade
            for finding in all_findings:
                severity = finding['severity']
                summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            response_data = {
                "analysis_id": analysis.id,
                "summary": summary,
                "total_findings": total_findings,
                "findings": all_findings,
                "scanned_files": [{"id": f.id, "filename": f.filename} for f in log_files]
            }
            
            if errors:
                response_data["warnings"] = errors
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Erro na análise: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def analyze_file(self, log_file, analysis):
        """Analisa um arquivo usando o main.py real"""
        try:
            # Cria arquivo temporário com o conteúdo salvo
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log', encoding='utf-8') as temp_file:
                temp_file.write(log_file.content)
                temp_path = temp_file.name
            
            try:
                backend_dir = os.path.join(settings.BASE_DIR, 'backend')
                main_py = os.path.join(backend_dir, 'main.py')
                
                cmd = [
                    'python', main_py,
                    temp_path,
                    '--formats', 'json',
                    '--output-dir', '/tmp'
                ]
                
                env = os.environ.copy()
                env['PYTHONPATH'] = '/app'
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=backend_dir, env=env)
                
                if result.returncode != 0:
                    raise Exception(f"Análise falhou: {result.stderr}")
                
                # Lê relatório gerado
                report_file = '/tmp/synapse_report.json'
                findings = []
                
                if os.path.exists(report_file):
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                        if isinstance(report_data, dict):
                            raw_findings = report_data.get('findings', [])
                        elif isinstance(report_data, list):
                            raw_findings = report_data
                        else:
                            raw_findings = []
                    
                    # Salva findings no banco
                    for finding_data in raw_findings:
                        finding = LogFinding.objects.create(
                            analysis=analysis,
                            log_file=log_file,
                            line_number=finding_data.get('line_number', 0),
                            content=finding_data.get('raw_line', ''),
                            rule_name=finding_data.get('rule_id', 'Unknown'),
                            severity=finding_data.get('severity', 'low'),
                            description=finding_data.get('description', ''),
                            recommendation=finding_data.get('recommendation', '')
                        )
                        
                        findings.append({
                            "id": finding.id,
                            "rule_name": finding.rule_name,
                            "severity": finding.severity,
                            "description": finding.description,
                            "recommendation": finding.recommendation,
                            "file": log_file.filename,
                            "line_number": finding.line_number
                        })
                
                return findings
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            
        except Exception as e:
            raise Exception(f"Erro analisando {log_file.filename}: {str(e)}")
        """Simula análise baseada no conteúdo do arquivo (mock)"""
        findings = []
        
        # Mock de findings baseado no nome do arquivo
        if 'security' in log_file.filename.lower():
            # Cria alguns findings de exemplo
            mock_findings = [
                {
                    "rule_name": "FAILED_LOGIN",
                    "severity": "medium",
                    "description": "Tentativa de login falhada detectada",
                    "recommendation": "Verificar origem do IP e implementar rate limiting"
                },
                {
                    "rule_name": "SUSPICIOUS_ACTIVITY", 
                    "severity": "high",
                    "description": "Atividade suspeita detectada nos logs",
                    "recommendation": "Investigar padrões de acesso anômalos"
                }
            ]
            
            for i, mock_finding in enumerate(mock_findings):
                finding = LogFinding.objects.create(
                    analysis=analysis,
                    log_file=log_file,
                    line_number=i + 1,
                    content=f"Mock log line {i + 1}",
                    rule_name=mock_finding["rule_name"],
                    severity=mock_finding["severity"],
                    description=mock_finding["description"],
                    recommendation=mock_finding["recommendation"]
                )
                
                findings.append({
                    "id": finding.id,
                    "rule_name": finding.rule_name,
                    "severity": finding.severity,
                    "description": finding.description,
                    "recommendation": finding.recommendation,
                    "file": log_file.filename,
                    "line_number": finding.line_number
                })
        
        return findings


class LogUploadView(APIView):
    parser_classes = [MultiPartParser, FileUploadParser]
    
    def post(self, request):
        """Upload de arquivo de log (salva metadados no banco)"""
        try:
            if 'file' not in request.FILES:
                return Response(
                    {"error": "Nenhum arquivo enviado"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['file']
            
            # Verifica se arquivo já existe
            if LogFile.objects.filter(filename=uploaded_file.name).exists():
                return Response(
                    {"error": f"Arquivo '{uploaded_file.name}' já foi importado anteriormente"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Lê e salva conteúdo do arquivo
            content = ""
            total_lines = 0
            try:
                content = uploaded_file.read().decode('utf-8', errors='ignore')
                if content.strip():  # Verifica se não está vazio
                    total_lines = len([line for line in content.splitlines() if line.strip()])
                else:
                    return Response(
                        {"error": f"Arquivo '{uploaded_file.name}' está vazio ou não contém texto válido"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                return Response(
                    {"error": f"Erro ao ler arquivo: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Salva metadados e conteúdo no banco
            log_file = LogFile.objects.create(
                filename=uploaded_file.name,
                filepath=f"/uploaded/{uploaded_file.name}",  # Path virtual
                content=content,  # Salva o conteúdo
                size_bytes=uploaded_file.size,
                total_lines=total_lines
            )
            
            return Response({
                "message": "Arquivo importado com sucesso",
                "file_id": log_file.id,
                "filename": log_file.filename,
                "size": log_file.size_bytes,
                "total_lines": log_file.total_lines,
                "uploaded_at": log_file.analyzed_at.isoformat()
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Erro no upload: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogFileDeleteView(APIView):
    def delete(self, request, file_id):
        """Exclui arquivo importado"""
        try:
            log_file = LogFile.objects.get(id=file_id)
            log_file.delete()
            
            return Response({
                "message": "Arquivo excluído com sucesso"
            }, status=status.HTTP_200_OK)
            
        except LogFile.DoesNotExist:
            return Response(
                {"error": "Arquivo não encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao excluir arquivo: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnalysisHistoryView(APIView):
    def get(self, request):
        """Lista histórico de análises realizadas"""
        try:
            analyses = LogAnalysis.objects.all().order_by('-started_at')[:10]
            history_data = []
            
            for analysis in analyses:
                history_data.append({
                    "id": analysis.id,
                    "started_at": analysis.started_at.isoformat(),
                    "total_files": analysis.total_files,
                    "total_findings": analysis.total_findings,
                    "status": analysis.status
                })
            
            return Response(history_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Erro ao listar histórico: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
