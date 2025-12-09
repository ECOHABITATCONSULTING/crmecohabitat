#!/usr/bin/env python3
"""
Script de test de connexion SSH au VPS crm-ehc.fr
"""

import paramiko
import socket
import sys

# Configuration
HOSTS = ["217.182.171.179", "213.186.33.5"]  # Les 2 IPs du domaine
USERNAMES = ["root", "ubuntu"]  # Utilisateurs courants pour VPS
PASSWORD = "Pirouli2652148"
PORT = 22
TIMEOUT = 10

def test_ssh_connection(host, username, password, port=22):
    """Test une connexion SSH avec les credentials fournis"""
    print(f"\n🔍 Test de connexion: {username}@{host}:{port}")
    print("-" * 50)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Tentative de connexion
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=TIMEOUT,
            banner_timeout=TIMEOUT,
            auth_timeout=TIMEOUT
        )

        print(f"✅ CONNEXION RÉUSSIE!")

        # Exécuter une commande de test
        stdin, stdout, stderr = client.exec_command('whoami && hostname && pwd')
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        print(f"\n📋 Informations du serveur:")
        print(output)
        if error:
            print(f"⚠️  Erreurs: {error}")

        # Vérifier la version du système
        stdin, stdout, stderr = client.exec_command('cat /etc/os-release | head -n 2')
        os_info = stdout.read().decode().strip()
        print(f"\n🐧 OS: {os_info}")

        # Vérifier le projet CRM
        stdin, stdout, stderr = client.exec_command('ls -la /var/www/crmecohabitat 2>&1')
        crm_check = stdout.read().decode().strip()
        if "crmecohabitat" in crm_check or "cannot access" not in crm_check:
            print(f"\n📂 Projet CRM trouvé:")
            print(crm_check[:500])  # Afficher les premiers caractères

        client.close()
        return True

    except paramiko.AuthenticationException:
        print(f"❌ Échec d'authentification (mauvais mot de passe)")
        return False
    except paramiko.SSHException as e:
        print(f"❌ Erreur SSH: {e}")
        return False
    except socket.timeout:
        print(f"❌ Timeout - Le serveur ne répond pas")
        return False
    except socket.error as e:
        print(f"❌ Erreur réseau: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {type(e).__name__}: {e}")
        return False
    finally:
        client.close()

def main():
    print("=" * 60)
    print("🚀 TEST DE CONNEXION SSH AU VPS CRM-EHC.FR")
    print("=" * 60)

    success = False

    # Tester toutes les combinaisons
    for host in HOSTS:
        for username in USERNAMES:
            result = test_ssh_connection(host, username, PASSWORD, PORT)
            if result:
                success = True
                print(f"\n✨ CONNEXION ÉTABLIE AVEC SUCCÈS!")
                print(f"📌 Credentials validés:")
                print(f"   Host: {host}")
                print(f"   User: {username}")
                print(f"   Port: {PORT}")
                print("\n💡 Utilisez ces credentials pour vous connecter:")
                print(f"   ssh {username}@{host}")
                return 0

    if not success:
        print("\n" + "=" * 60)
        print("❌ ÉCHEC: Aucune connexion réussie")
        print("=" * 60)
        print("\n💡 Suggestions:")
        print("   - Vérifiez le mot de passe")
        print("   - Essayez d'autres usernames (admin, debian, etc.)")
        print("   - Vérifiez que le firewall autorise les connexions SSH")
        print("   - Contactez votre hébergeur pour récupérer les credentials")
        return 1

if __name__ == "__main__":
    sys.exit(main())
