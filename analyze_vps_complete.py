#!/usr/bin/env python3
"""
ANALYSE COMPLÈTE VPS - Diagnostic ERR_CONNECTION_RESET
Identifie la cause des déconnexions récurrentes
"""

import paramiko
import json
import time
from datetime import datetime

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'
PROJECT_DIR = '/var/www/crm-ehc'

class VPSAnalyzer:
    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'health_score': 100,
            'critical_issues': [],
            'medium_issues': [],
            'minor_issues': [],
            'stats': {},
            'recommendations': []
        }

    def connect(self):
        print("🔌 Connexion au VPS...")
        self.ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
        print("✅ Connecté\n")

    def exec_cmd(self, cmd, description=""):
        """Exécute une commande et retourne la sortie"""
        if description:
            print(f"  ▶ {description}")
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        return stdout.read().decode().strip()

    def analyze_system_resources(self):
        """PHASE 1: Ressources système"""
        print("═" * 60)
        print("PHASE 1: ANALYSE RESSOURCES SYSTÈME")
        print("═" * 60)

        # Mémoire
        mem = self.exec_cmd("free -m | grep Mem", "Mémoire")
        mem_parts = mem.split()
        total_mem = int(mem_parts[1])
        used_mem = int(mem_parts[2])
        mem_percent = (used_mem / total_mem) * 100

        print(f"💾 RAM: {used_mem}MB / {total_mem}MB ({mem_percent:.1f}%)")
        self.report['stats']['memory_percent'] = mem_percent

        if mem_percent > 90:
            self.report['critical_issues'].append(f"Mémoire critique: {mem_percent:.1f}% utilisée")
            self.report['health_score'] -= 30
        elif mem_percent > 75:
            self.report['medium_issues'].append(f"Mémoire élevée: {mem_percent:.1f}% utilisée")
            self.report['health_score'] -= 15

        # CPU Load
        load = self.exec_cmd("uptime | awk '{print $(NF-2), $(NF-1), $NF}'", "Load average")
        print(f"📊 Load average: {load}")
        self.report['stats']['load_average'] = load

        # Disque
        disk = self.exec_cmd("df -h / | tail -1 | awk '{print $5}'", "Espace disque")
        disk_percent = int(disk.replace('%', ''))
        print(f"💿 Disque: {disk} utilisé")
        self.report['stats']['disk_percent'] = disk_percent

        if disk_percent > 90:
            self.report['critical_issues'].append(f"Disque plein: {disk_percent}%")
            self.report['health_score'] -= 25

        # Uptime
        uptime = self.exec_cmd("uptime -p", "Uptime")
        print(f"⏱️  Uptime: {uptime}\n")
        self.report['stats']['uptime'] = uptime

    def analyze_pm2_backend(self):
        """PHASE 2: Backend PM2"""
        print("═" * 60)
        print("PHASE 2: ANALYSE BACKEND PM2")
        print("═" * 60)

        # PM2 status
        pm2_json = self.exec_cmd("pm2 jlist", "PM2 status")
        try:
            pm2_data = json.loads(pm2_json)
            if pm2_data:
                app = pm2_data[0]
                status = app['pm2_env']['status']
                restarts = app['pm2_env']['restart_time']
                memory = app['monit']['memory'] / 1024 / 1024  # MB
                cpu = app['monit']['cpu']

                print(f"📱 App: {app['name']}")
                print(f"   Status: {status}")
                print(f"   Restarts: {restarts}")
                print(f"   Memory: {memory:.1f}MB")
                print(f"   CPU: {cpu}%")

                self.report['stats']['pm2_restarts'] = restarts
                self.report['stats']['pm2_memory'] = memory
                self.report['stats']['pm2_status'] = status

                if status != 'online':
                    self.report['critical_issues'].append(f"Backend offline: {status}")
                    self.report['health_score'] -= 50

                if restarts > 10:
                    self.report['critical_issues'].append(f"Backend crashe souvent: {restarts} restarts")
                    self.report['health_score'] -= 40
                elif restarts > 5:
                    self.report['medium_issues'].append(f"Backend instable: {restarts} restarts")
                    self.report['health_score'] -= 20

                if memory > 200:
                    self.report['medium_issues'].append(f"Memory leak possible: {memory:.1f}MB")
                    self.report['health_score'] -= 15
        except:
            self.report['critical_issues'].append("PM2 ne répond pas")
            self.report['health_score'] -= 50

        # PM2 logs errors
        logs = self.exec_cmd("pm2 logs crm-backend --lines 50 --nostream --err 2>&1 | grep -i error | tail -10", "Erreurs récentes")
        if logs:
            error_count = len(logs.split('\n'))
            print(f"❌ Erreurs récentes: {error_count}")
            self.report['stats']['recent_errors'] = error_count
            if error_count > 5:
                self.report['medium_issues'].append(f"{error_count} erreurs récentes dans les logs")
                self.report['health_score'] -= 10
        print()

    def analyze_nginx(self):
        """PHASE 3: Nginx"""
        print("═" * 60)
        print("PHASE 3: ANALYSE NGINX")
        print("═" * 60)

        # Nginx status
        nginx_status = self.exec_cmd("systemctl is-active nginx", "Nginx status")
        print(f"🌐 Nginx: {nginx_status}")

        if nginx_status != 'active':
            self.report['critical_issues'].append(f"Nginx {nginx_status}")
            self.report['health_score'] -= 50

        # Test config
        nginx_test = self.exec_cmd("sudo nginx -t 2>&1", "Config Nginx")
        if 'successful' not in nginx_test:
            self.report['critical_issues'].append("Config Nginx invalide")
            self.report['health_score'] -= 30
            print(f"❌ Config: {nginx_test}")
        else:
            print("✅ Config OK")

        # Error logs
        nginx_errors = self.exec_cmd("sudo tail -100 /var/log/nginx/error.log | grep -i 'error\\|warn\\|502\\|503\\|504\\|upstream' | tail -10", "Erreurs Nginx")
        if nginx_errors:
            error_lines = nginx_errors.split('\n')
            print(f"⚠️  Erreurs Nginx: {len(error_lines)} récentes")

            # Analyser les types d'erreurs
            if 'upstream' in nginx_errors:
                self.report['critical_issues'].append("Connexions upstream échouent (backend inaccessible)")
                self.report['health_score'] -= 35
            if '502' in nginx_errors or '503' in nginx_errors or '504' in nginx_errors:
                self.report['critical_issues'].append("Erreurs 502/503/504 détectées (timeouts)")
                self.report['health_score'] -= 30

        print()

    def analyze_database(self):
        """PHASE 4: Base de données"""
        print("═" * 60)
        print("PHASE 4: ANALYSE BASE DE DONNÉES")
        print("═" * 60)

        # Taille DB
        db_size = self.exec_cmd(f"ls -lh {PROJECT_DIR}/backend/database.db | awk '{{print $5}}'", "Taille DB")
        print(f"🗄️  database.db: {db_size}")

        # Intégrité
        integrity = self.exec_cmd(f'cd {PROJECT_DIR}/backend && node -e "const db=require(\'better-sqlite3\')(\'./database.db\');const result=db.pragma(\'integrity_check\');console.log(result[0].integrity_check);db.close();" 2>&1', "Intégrité DB")
        print(f"   Intégrité: {integrity}")

        if 'ok' not in integrity.lower():
            self.report['critical_issues'].append("Base de données corrompue")
            self.report['health_score'] -= 50

        # WAL mode check
        wal_mode = self.exec_cmd(f'cd {PROJECT_DIR}/backend && node -e "const db=require(\'better-sqlite3\')(\'./database.db\');const mode=db.pragma(\'journal_mode\',{{simple:true}});console.log(mode);db.close();" 2>&1', "Journal mode")
        print(f"   Journal mode: {wal_mode}")

        if wal_mode != 'wal':
            self.report['medium_issues'].append(f"DB en mode {wal_mode} (recommandé: WAL)")
            self.report['health_score'] -= 10
            self.report['recommendations'].append("Passer la DB en mode WAL pour éviter les locks")

        print()

    def analyze_network(self):
        """PHASE 5: Réseau et connexions"""
        print("═" * 60)
        print("PHASE 5: ANALYSE RÉSEAU")
        print("═" * 60)

        # Port 3001 (backend)
        port_3001 = self.exec_cmd("ss -tlnp | grep :3001", "Port 3001")
        if port_3001:
            print("✅ Port 3001 (backend) en écoute")
        else:
            self.report['critical_issues'].append("Port 3001 non ouvert (backend down)")
            self.report['health_score'] -= 50

        # Connexions TIME_WAIT
        time_wait = self.exec_cmd("ss -tan | grep TIME_WAIT | wc -l", "Connexions TIME_WAIT")
        time_wait_count = int(time_wait) if time_wait else 0
        print(f"🔌 TIME_WAIT sockets: {time_wait_count}")

        if time_wait_count > 1000:
            self.report['medium_issues'].append(f"Trop de TIME_WAIT: {time_wait_count}")
            self.report['health_score'] -= 15

        # Test curl backend
        print("\n📡 Test connectivité backend...")
        curl_test = self.exec_cmd("curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://localhost:3001/api/health 2>&1", "Test curl backend")
        if '200' in curl_test:
            print("✅ Backend répond (200)")
        else:
            self.report['critical_issues'].append(f"Backend ne répond pas (code: {curl_test})")
            self.report['health_score'] -= 40

        print()

    def analyze_ssl(self):
        """PHASE 6: Certificat SSL"""
        print("═" * 60)
        print("PHASE 6: ANALYSE CERTIFICAT SSL")
        print("═" * 60)

        cert_exp = self.exec_cmd("sudo certbot certificates 2>&1 | grep 'Expiry Date' | head -1", "Expiration SSL")
        print(f"🔒 {cert_exp if cert_exp else 'Certificat non trouvé'}")

        if not cert_exp or 'INVALID' in cert_exp:
            self.report['critical_issues'].append("Certificat SSL invalide ou expiré")
            self.report['health_score'] -= 40

        print()

    def run_load_test(self):
        """PHASE 7: Test de charge"""
        print("═" * 60)
        print("PHASE 7: TEST DE CHARGE (10 requêtes)")
        print("═" * 60)

        successes = 0
        failures = 0
        total_time = 0

        for i in range(10):
            start = time.time()
            result = self.exec_cmd(f"curl -k -s -o /dev/null -w '%{{http_code}}' --max-time 10 https://crm-ehc.fr/ 2>&1", f"Requête {i+1}/10")
            elapsed = time.time() - start
            total_time += elapsed

            if '200' in result or '30' in result:  # 200 ou redirect
                successes += 1
                print(f"  ✅ {result} ({elapsed:.2f}s)")
            else:
                failures += 1
                print(f"  ❌ {result} ({elapsed:.2f}s)")
            time.sleep(0.5)

        avg_time = total_time / 10
        success_rate = (successes / 10) * 100

        print(f"\n📊 Résultats:")
        print(f"   Succès: {successes}/10 ({success_rate}%)")
        print(f"   Échecs: {failures}/10")
        print(f"   Temps moyen: {avg_time:.2f}s")

        self.report['stats']['load_test_success_rate'] = success_rate
        self.report['stats']['load_test_avg_time'] = avg_time

        if success_rate < 50:
            self.report['critical_issues'].append(f"Site très instable: {success_rate}% de succès")
            self.report['health_score'] -= 40
        elif success_rate < 80:
            self.report['medium_issues'].append(f"Site instable: {success_rate}% de succès")
            self.report['health_score'] -= 20

        if avg_time > 5:
            self.report['medium_issues'].append(f"Site lent: {avg_time:.2f}s en moyenne")
            self.report['health_score'] -= 15

        print()

    def generate_report(self):
        """Génère le rapport final"""
        print("\n")
        print("═" * 60)
        print("   RAPPORT D'ANALYSE VPS - CRM-EHC.FR")
        print("═" * 60)
        print(f"📅 Date: {self.report['timestamp']}")
        print(f"🏥 SCORE SANTÉ: {max(0, self.report['health_score'])}/100")
        print()

        if self.report['critical_issues']:
            print("❌ PROBLÈMES CRITIQUES:")
            for i, issue in enumerate(self.report['critical_issues'], 1):
                print(f"   {i}. {issue}")
            print()

        if self.report['medium_issues']:
            print("⚠️  PROBLÈMES MOYENS:")
            for i, issue in enumerate(self.report['medium_issues'], 1):
                print(f"   {i}. {issue}")
            print()

        if self.report['minor_issues']:
            print("ℹ️  PROBLÈMES MINEURS:")
            for i, issue in enumerate(self.report['minor_issues'], 1):
                print(f"   {i}. {issue}")
            print()

        print("📊 STATISTIQUES:")
        for key, value in self.report['stats'].items():
            print(f"   • {key}: {value}")
        print()

        if self.report['recommendations']:
            print("💡 RECOMMANDATIONS:")
            for i, rec in enumerate(self.report['recommendations'], 1):
                print(f"   {i}. {rec}")
            print()

        # Identifier la cause la plus probable
        print("🎯 CAUSE LA PLUS PROBABLE DU ERR_CONNECTION_RESET:")
        if any('Backend' in issue or 'PM2' in issue for issue in self.report['critical_issues']):
            print("   ➤ Le backend Node.js crashe ou redémarre fréquemment")
            print("   ➤ Solution: Investiguer les logs PM2 et fixer les crashes")
        elif any('upstream' in issue or '502' in issue or '503' in issue for issue in self.report['critical_issues']):
            print("   ➤ Nginx n'arrive pas à communiquer avec le backend")
            print("   ➤ Solution: Vérifier la connexion Nginx → Backend (port 3001)")
        elif any('instable' in issue.lower() for issue in self.report['critical_issues'] + self.report['medium_issues']):
            print("   ➤ Le site est globalement instable (timeouts, lenteurs)")
            print("   ➤ Solution: Optimiser les ressources et les requêtes")
        else:
            print("   ➤ Problème intermittent non identifié dans cette analyse")
            print("   ➤ Solution: Monitorer en continu avec un script de surveillance")

        print("\n" + "═" * 60)

    def close(self):
        self.ssh.close()

# Exécution
if __name__ == '__main__':
    analyzer = VPSAnalyzer()
    try:
        analyzer.connect()
        analyzer.analyze_system_resources()
        analyzer.analyze_pm2_backend()
        analyzer.analyze_nginx()
        analyzer.analyze_database()
        analyzer.analyze_network()
        analyzer.analyze_ssl()
        analyzer.run_load_test()
        analyzer.generate_report()
    except Exception as e:
        print(f"\n❌ ERREUR LORS DE L'ANALYSE: {e}")
        import traceback
        traceback.print_exc()
    finally:
        analyzer.close()
