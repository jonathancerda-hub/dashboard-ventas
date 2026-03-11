#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Auditoría de Seguridad - Dashboard de Ventas
======================================================

Ejecuta auditorías de seguridad automáticas usando pip-audit y safety check.
Genera reportes detallados de vulnerabilidades encontradas.

Uso:
    python security_audit.py [--fix]

Opciones:
    --fix    Intenta actualizar automáticamente los paquetes vulnerables

Recomendación: Ejecutar trimestralmente o antes de cada deployment.
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path


class SecurityAuditor:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.vulnerabilities_found = 0
        self.report_lines = []

    def log(self, message, level="INFO"):
        """Registra un mensaje en el reporte"""
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🔴"
        }.get(level, "•")
        
        line = f"{prefix} {message}"
        print(line)
        self.report_lines.append(line)

    def run_pip_audit(self):
        """Ejecuta pip-audit para detectar vulnerabilidades conocidas"""
        self.log("Ejecutando pip-audit...", "INFO")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip_audit", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.log("No se encontraron vulnerabilidades conocidas", "SUCCESS")
                return []
            
            # Parse JSON output
            try:
                vulnerabilities = json.loads(result.stdout)
                self.vulnerabilities_found += len(vulnerabilities.get("dependencies", []))
                
                self.log(f"Encontradas {len(vulnerabilities.get('dependencies', []))} vulnerabilidades", "WARNING")
                
                for dep in vulnerabilities.get("dependencies", []):
                    name = dep.get("name", "unknown")
                    version = dep.get("version", "unknown")
                    vulns = dep.get("vulns", [])
                    
                    self.log(f"  • {name} {version}:", "WARNING")
                    for vuln in vulns:
                        vuln_id = vuln.get("id", "unknown")
                        fix_versions = vuln.get("fix_versions", [])
                        self.log(f"    - {vuln_id} (fix: {', '.join(fix_versions)})", "CRITICAL")
                
                return vulnerabilities.get("dependencies", [])
                
            except json.JSONDecodeError:
                # Fallback to text parsing if JSON fails
                if "No known vulnerabilities found" in result.stdout:
                    self.log("No se encontraron vulnerabilidades conocidas", "SUCCESS")
                    return []
                else:
                    self.log("Error al parsear salida de pip-audit", "ERROR")
                    self.log(result.stdout, "INFO")
                    return []
            
        except subprocess.TimeoutExpired:
            self.log("Timeout ejecutando pip-audit", "ERROR")
            return []
        except FileNotFoundError:
            self.log("pip-audit no está instalado. Ejecuta: pip install pip-audit", "ERROR")
            return []
        except Exception as e:
            self.log(f"Error ejecutando pip-audit: {str(e)}", "ERROR")
            return []

    def run_safety_check(self):
        """Ejecuta safety check para verificar contra Safety DB"""
        self.log("\nEjecutando safety check...", "INFO")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            try:
                safety_results = json.loads(result.stdout)
                if not safety_results:
                    self.log("No se encontraron problemas de seguridad", "SUCCESS")
                    return []
                
                self.vulnerabilities_found += len(safety_results)
                self.log(f"Encontrados {len(safety_results)} problemas de seguridad", "WARNING")
                
                for issue in safety_results:
                    pkg = issue[0]
                    affected = issue[2]
                    advisory = issue[3]
                    self.log(f"  • {pkg}: {advisory}", "WARNING")
                
                return safety_results
                
            except json.JSONDecodeError:
                if result.returncode == 0:
                    self.log("No se encontraron problemas de seguridad", "SUCCESS")
                    return []
                else:
                    self.log("Error al parsear salida de safety check", "ERROR")
                    return []
            
        except subprocess.TimeoutExpired:
            self.log("Timeout ejecutando safety check", "ERROR")
            return []
        except FileNotFoundError:
            self.log("safety no está instalado. Ejecuta: pip install safety", "ERROR")
            return []
        except Exception as e:
            self.log(f"Error ejecutando safety check: {str(e)}", "ERROR")
            return []

    def check_outdated_packages(self):
        """Verifica paquetes desactualizados"""
        self.log("\nVerificando paquetes desactualizados...", "INFO")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            outdated = json.loads(result.stdout)
            
            if not outdated:
                self.log("Todos los paquetes están actualizados", "SUCCESS")
                return []
            
            self.log(f"Encontrados {len(outdated)} paquetes desactualizados", "INFO")
            
            for pkg in outdated:
                name = pkg.get("name", "unknown")
                current = pkg.get("version", "unknown")
                latest = pkg.get("latest_version", "unknown")
                self.log(f"  • {name}: {current} → {latest}", "INFO")
            
            return outdated
            
        except Exception as e:
            self.log(f"Error verificando paquetes desactualizados: {str(e)}", "ERROR")
            return []

    def save_report(self):
        """Guarda el reporte de auditoría"""
        report_dir = Path("security_reports")
        report_dir.mkdir(exist_ok=True)
        
        filename = report_dir / f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Reporte de Auditoría de Seguridad\n")
            f.write(f"Fecha: {self.timestamp}\n")
            f.write(f"{'='*60}\n\n")
            f.write("\n".join(self.report_lines))
            f.write(f"\n\n{'='*60}\n")
            f.write(f"Total vulnerabilidades encontradas: {self.vulnerabilities_found}\n")
        
        self.log(f"\nReporte guardado en: {filename}", "SUCCESS")

    def run_audit(self, auto_fix=False):
        """Ejecuta la auditoría completa"""
        self.log(f"Iniciando auditoría de seguridad - {self.timestamp}", "INFO")
        self.log("="*60, "INFO")
        
        # Ejecutar auditorías
        pip_audit_vulns = self.run_pip_audit()
        safety_issues = self.run_safety_check()
        outdated_pkgs = self.check_outdated_packages()
        
        # Resumen final
        self.log("\n" + "="*60, "INFO")
        self.log("RESUMEN DE AUDITORÍA", "INFO")
        self.log("="*60, "INFO")
        self.log(f"Total de vulnerabilidades: {self.vulnerabilities_found}", 
                 "CRITICAL" if self.vulnerabilities_found > 0 else "SUCCESS")
        self.log(f"Paquetes desactualizados: {len(outdated_pkgs)}", "INFO")
        
        if self.vulnerabilities_found == 0:
            self.log("\n🎉 Sistema seguro - No se encontraron vulnerabilidades", "SUCCESS")
        else:
            self.log(f"\n⚠️ ACCIÓN REQUERIDA: Se encontraron {self.vulnerabilities_found} vulnerabilidades", "CRITICAL")
            self.log("Actualiza los paquetes ejecutando: pip install -r requirements.txt --upgrade", "INFO")
        
        # Guardar reporte
        self.save_report()
        
        return self.vulnerabilities_found == 0


def main():
    """Función principal"""
    auto_fix = "--fix" in sys.argv
    
    auditor = SecurityAuditor()
    success = auditor.run_audit(auto_fix)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
