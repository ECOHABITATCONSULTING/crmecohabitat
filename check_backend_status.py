#!/usr/bin/env python3
"""
CHECK BACKEND STATUS ET LOGS
"""

import paramiko

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'

print("🔍 DIAGNOSTIC BACKEND\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    # Check PM2 status
    print("📊 PM2 Status:")
    stdin, stdout, stderr = ssh.exec_command("pm2 list")
    print(stdout.read().decode())

    # Check last 100 lines of error log
    print("\n📋 Backend Error Logs (dernières 100 lignes):")
    stdin, stdout, stderr = ssh.exec_command("tail -100 /home/ubuntu/.pm2/logs/crm-backend-error.log")
    print(stdout.read().decode())

    # Check database file exists
    print("\n📁 Database:")
    stdin, stdout, stderr = ssh.exec_command("ls -lh /var/www/crm-ehc/backend/crm.db")
    print(stdout.read().decode())

    # Check database schema
    print("\n📊 Database Schema (tables):")
    stdin, stdout, stderr = ssh.exec_command("cd /var/www/crm-ehc/backend && sqlite3 crm.db '.tables'")
    print(stdout.read().decode())

    # Check commerciaux table structure
    print("\n📊 Table 'commerciaux' structure:")
    stdin, stdout, stderr = ssh.exec_command("cd /var/www/crm-ehc/backend && sqlite3 crm.db 'PRAGMA table_info(commerciaux);'")
    print(stdout.read().decode())

    # Check clients table for rdv_pris column
    print("\n📊 Table 'clients' columns:")
    stdin, stdout, stderr = ssh.exec_command("cd /var/www/crm-ehc/backend && sqlite3 crm.db 'PRAGMA table_info(clients);'")
    print(stdout.read().decode())

    # Check appointments table for commercial_id column
    print("\n📊 Table 'appointments' columns:")
    stdin, stdout, stderr = ssh.exec_command("cd /var/www/crm-ehc/backend && sqlite3 crm.db 'PRAGMA table_info(appointments);'")
    print(stdout.read().decode())

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
