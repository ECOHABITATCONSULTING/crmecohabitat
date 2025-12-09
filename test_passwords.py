#!/usr/bin/env python3
"""
Script de test de mots de passe SSH pour le VPS crm-ehc.fr
"""

import paramiko
import sys

# Configuration
HOST = "217.182.171.179"
PORT = 22
USERNAMES = ["ubuntu", "root"]
PASSWORDS = [
    "pirouli2652148",
    "Pirouli2652148",
    "Lijadasa26",
    "lijadasa26",
    "Joker2652148",
    "joker2652148"
]
TIMEOUT = 10

def test_ssh_connection(host, username, password, port=22):
    """Test une connexion SSH avec les credentials fournis"""
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
            auth_timeout=TIMEOUT,
            look_for_keys=False,  # Ne pas chercher de clés SSH
            allow_agent=False     # Ne pas utiliser l'agent SSH
        )

        print(f"✅ CONNEXION RÉUSSIE!")
        print(f"   Host: {host}")
        print(f"   User: {username}")
        print(f"   Password: {password}")

        # Exécuter une commande de test
        stdin, stdout, stderr = client.exec_command('whoami && hostname && pwd')
        output = stdout.read().decode().strip()

        print(f"\n📋 Informations du serveur:")
        print(output)

        # Vérifier le projet CRM
        stdin, stdout, stderr = client.exec_command('ls -la /var/www/crmecohabitat 2>&1 | head -10')
        crm_check = stdout.read().decode().strip()
        print(f"\n📂 Projet CRM:")
        print(crm_check)

        client.close()
        return True

    except paramiko.AuthenticationException:
        return False
    except Exception as e:
        print(f"❌ Erreur pour {username}@{host} avec '{password}': {type(e).__name__}")
        return False
    finally:
        try:
            client.close()
        except:
            pass

def main():
    print("=" * 70)
    print("🔐 TEST DES MOTS DE PASSE SSH POUR crm-ehc.fr")
    print("=" * 70)
    print(f"\nHost: {HOST}")
    print(f"Users à tester: {', '.join(USERNAMES)}")
    print(f"Passwords à tester: {len(PASSWORDS)}")
    print("\n" + "-" * 70 + "\n")

    success = False
    tested = 0
    total = len(USERNAMES) * len(PASSWORDS)

    for username in USERNAMES:
        for password in PASSWORDS:
            tested += 1
            print(f"[{tested}/{total}] Test: {username} avec '{password}'...", end=" ")

            result = test_ssh_connection(HOST, username, password, PORT)

            if result:
                success = True
                print("\n" + "=" * 70)
                print("✨ ACCÈS VPS TROUVÉ !")
                print("=" * 70)
                print(f"\nPour vous connecter:")
                print(f"  ssh {username}@{HOST}")
                print(f"  Password: {password}")
                print("\n" + "=" * 70)
                return 0
            else:
                print("❌")

    if not success:
        print("\n" + "=" * 70)
        print("❌ AUCUN MOT DE PASSE VALIDE TROUVÉ")
        print("=" * 70)
        print("\n💡 Suggestions:")
        print("   - Vérifiez l'orthographe des mots de passe")
        print("   - Essayez d'autres variations")
        print("   - Contactez votre hébergeur OVH")
        return 1

if __name__ == "__main__":
    sys.exit(main())
