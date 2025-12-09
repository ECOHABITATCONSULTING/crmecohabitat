#!/usr/bin/env python3
"""
TEST AUTOMATIQUE DES 11 MODIFICATIONS
Vérifie les endpoints backend et la structure de la base de données
"""

import requests
import json
from datetime import datetime

API_URL = 'https://crm-ehc.fr/api'
ADMIN_CREDENTIALS = {'username': 'admin', 'password': 'admin123'}

def print_test(name, status, details=""):
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name}")
    if details:
        print(f"   {details}")

def test_authentication():
    """Test 0: Authentification"""
    print("\n" + "="*60)
    print("TEST 0: AUTHENTIFICATION")
    print("="*60)

    try:
        response = requests.post(f"{API_URL}/auth/login", json=ADMIN_CREDENTIALS, timeout=10)
        if response.status_code == 200:
            token = response.json().get('token')
            print_test("Login admin", True, f"Token obtenu: {token[:20]}...")
            return token
        else:
            print_test("Login admin", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        print_test("Login admin", False, str(e))
        return None

def test_commerciaux(token):
    """Test 1: Système Commerciaux"""
    print("\n" + "="*60)
    print("TEST 1: SYSTÈME COMMERCIAUX")
    print("="*60)

    headers = {'Authorization': f'Bearer {token}'}

    # GET /commerciaux
    try:
        response = requests.get(f"{API_URL}/commerciaux", headers=headers, timeout=10)
        print_test("GET /commerciaux", response.status_code == 200, f"Status: {response.status_code}")
        if response.status_code == 200:
            commerciaux = response.json()
            print(f"   Nombre de commerciaux: {len(commerciaux)}")
    except Exception as e:
        print_test("GET /commerciaux", False, str(e))

    # POST /commerciaux
    try:
        new_commercial = {
            "name": "Test Commercial API",
            "color": "#ff5733"
        }
        response = requests.post(f"{API_URL}/commerciaux", headers=headers, json=new_commercial, timeout=10)
        print_test("POST /commerciaux", response.status_code == 201, f"Status: {response.status_code}")

        if response.status_code == 201:
            commercial_id = response.json().get('id')
            print(f"   Commercial créé avec ID: {commercial_id}")

            # PATCH /commerciaux/:id
            try:
                update = {"name": "Test Commercial Updated", "color": "#10b981"}
                response = requests.patch(f"{API_URL}/commerciaux/{commercial_id}", headers=headers, json=update, timeout=10)
                print_test("PATCH /commerciaux/:id", response.status_code == 200, f"Status: {response.status_code}")
            except Exception as e:
                print_test("PATCH /commerciaux/:id", False, str(e))

            # DELETE /commerciaux/:id
            try:
                response = requests.delete(f"{API_URL}/commerciaux/{commercial_id}", headers=headers, timeout=10)
                print_test("DELETE /commerciaux/:id", response.status_code == 200, f"Status: {response.status_code}")
            except Exception as e:
                print_test("DELETE /commerciaux/:id", False, str(e))
    except Exception as e:
        print_test("POST /commerciaux", False, str(e))

def test_extended_lead_fields(token):
    """Test 2: Champs étendus des leads"""
    print("\n" + "="*60)
    print("TEST 2: CHAMPS ÉTENDUS DES LEADS")
    print("="*60)

    headers = {'Authorization': f'Bearer {token}'}

    # POST /leads avec tous les nouveaux champs
    try:
        new_lead = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@test.fr",
            "phone": "0123456789",
            "mobile_phone": "0612345678",
            "address": "123 Rue de Test",
            "postal_code": "75001",
            "city": "Paris",
            "country": "France"
        }
        response = requests.post(f"{API_URL}/leads", headers=headers, json=new_lead, timeout=10)
        print_test("POST /leads avec 9 champs", response.status_code == 201, f"Status: {response.status_code}")

        if response.status_code == 201:
            lead_id = response.json().get('id')
            print(f"   Lead créé avec ID: {lead_id}")

            # GET /leads/:id pour vérifier les champs
            response = requests.get(f"{API_URL}/leads/${lead_id}", headers=headers, timeout=10)
            if response.status_code == 200:
                lead = response.json()
                fields_ok = all([
                    lead.get('mobile_phone') == "0612345678",
                    lead.get('address') == "123 Rue de Test",
                    lead.get('postal_code') == "75001",
                    lead.get('city') == "Paris",
                    lead.get('country') == "France"
                ])
                print_test("Nouveaux champs sauvegardés", fields_ok,
                          f"mobile_phone, address, postal_code, city, country")

            # Cleanup
            requests.delete(f"{API_URL}/leads/{lead_id}", headers=headers, timeout=10)
    except Exception as e:
        print_test("POST /leads avec 9 champs", False, str(e))

def test_appointments_with_commercial(token):
    """Test 3: Appointments avec commercial_id"""
    print("\n" + "="*60)
    print("TEST 3: APPOINTMENTS AVEC COMMERCIAL")
    print("="*60)

    headers = {'Authorization': f'Bearer {token}'}

    # Créer un commercial de test
    try:
        commercial = {"name": "Test Commercial RDV", "color": "#3b82f6"}
        response = requests.post(f"{API_URL}/commerciaux", headers=headers, json=commercial, timeout=10)
        if response.status_code == 201:
            commercial_id = response.json().get('id')
            print(f"   Commercial créé: ID {commercial_id}")

            # Créer un lead pour le RDV
            lead = {
                "first_name": "Test",
                "last_name": "Appointment",
                "email": "test@apt.fr",
                "phone": "0123456789"
            }
            response = requests.post(f"{API_URL}/leads", headers=headers, json=lead, timeout=10)
            if response.status_code == 201:
                lead_id = response.json().get('id')
                print(f"   Lead créé: ID {lead_id}")

                # Créer un RDV avec commercial_id
                appointment = {
                    "lead_id": lead_id,
                    "title": "RDV Test avec Commercial",
                    "date": "2025-12-15",
                    "time": "14:00",
                    "commercial_id": commercial_id
                }
                response = requests.post(f"{API_URL}/appointments", headers=headers, json=appointment, timeout=10)
                print_test("POST /appointments avec commercial_id", response.status_code == 201, f"Status: {response.status_code}")

                if response.status_code == 201:
                    apt_id = response.json().get('id')
                    print(f"   Appointment créé: ID {apt_id}")

                    # GET /appointments pour vérifier
                    response = requests.get(f"{API_URL}/appointments", headers=headers, timeout=10)
                    if response.status_code == 200:
                        appointments = response.json()
                        apt = next((a for a in appointments if a.get('id') == apt_id), None)
                        if apt:
                            has_commercial = apt.get('commercial_id') == commercial_id
                            has_color = 'commercial_color' in apt
                            print_test("Commercial_id sauvegardé", has_commercial, f"ID: {apt.get('commercial_id')}")
                            print_test("Couleur commercial dans response", has_color, f"Color: {apt.get('commercial_color')}")

                    # Cleanup
                    requests.delete(f"{API_URL}/appointments/{apt_id}", headers=headers, timeout=10)

                # Cleanup lead
                requests.delete(f"{API_URL}/leads/{lead_id}", headers=headers, timeout=10)

            # Cleanup commercial
            requests.delete(f"{API_URL}/commerciaux/{commercial_id}", headers=headers, timeout=10)
    except Exception as e:
        print_test("Test appointments avec commercial", False, str(e))

def test_rdv_pris_system(token):
    """Test 4: Système RDV Pris"""
    print("\n" + "="*60)
    print("TEST 4: SYSTÈME RDV PRIS")
    print("="*60)

    headers = {'Authorization': f'Bearer {token}'}

    # Créer un client pour tester rdv_pris
    try:
        client = {
            "first_name": "Test",
            "last_name": "RDV Pris",
            "email": "rdv@test.fr",
            "phone": "0123456789",
            "status": "contacted"
        }
        response = requests.post(f"{API_URL}/clients", headers=headers, json=client, timeout=10)
        if response.status_code == 201:
            client_id = response.json().get('id')
            print(f"   Client créé: ID {client_id}, status: contacted")

            # PATCH avec rdv_pris = true (devrait passer à rdv_pris)
            update = {"rdv_pris": True}
            response = requests.patch(f"{API_URL}/clients/{client_id}", headers=headers, json=update, timeout=10)
            print_test("PATCH rdv_pris = true", response.status_code == 200, f"Status: {response.status_code}")

            # GET client pour vérifier status
            response = requests.get(f"{API_URL}/clients/{client_id}", headers=headers, timeout=10)
            if response.status_code == 200:
                client = response.json()
                status_updated = client.get('status') == 'rdv_pris'
                rdv_field_set = client.get('rdv_pris') == 1
                print_test("Status auto-update → rdv_pris", status_updated, f"Status: {client.get('status')}")
                print_test("Champ rdv_pris = 1", rdv_field_set, f"rdv_pris: {client.get('rdv_pris')}")

            # PATCH avec rdv_pris = false (devrait rester rdv_pris)
            update = {"rdv_pris": False}
            response = requests.patch(f"{API_URL}/clients/{client_id}", headers=headers, json=update, timeout=10)

            response = requests.get(f"{API_URL}/clients/{client_id}", headers=headers, timeout=10)
            if response.status_code == 200:
                client = response.json()
                status_unchanged = client.get('status') == 'rdv_pris'
                rdv_field_unset = client.get('rdv_pris') == 0
                print_test("rdv_pris = false ne change pas status", status_unchanged, f"Status: {client.get('status')}")
                print_test("Champ rdv_pris = 0", rdv_field_unset, f"rdv_pris: {client.get('rdv_pris')}")

            # Cleanup
            requests.delete(f"{API_URL}/clients/{client_id}", headers=headers, timeout=10)
    except Exception as e:
        print_test("Test RDV Pris system", False, str(e))

def test_analytics_with_rdv_pris(token):
    """Test 5: Analytics avec rdv_pris"""
    print("\n" + "="*60)
    print("TEST 5: ANALYTICS AVEC RDV_PRIS")
    print("="*60)

    headers = {'Authorization': f'Bearer {token}'}

    # GET /analytics
    try:
        response = requests.get(f"{API_URL}/analytics", headers=headers, timeout=10)
        print_test("GET /analytics", response.status_code == 200, f"Status: {response.status_code}")

        if response.status_code == 200:
            analytics = response.json()
            has_rdv_pris = 'rdv_pris' in analytics
            has_funnel = 'conversionFunnel' in analytics
            print_test("Métrique rdv_pris présente", has_rdv_pris, f"Value: {analytics.get('rdv_pris')}")

            if has_funnel:
                funnel = analytics.get('conversionFunnel', [])
                rdv_stage = next((s for s in funnel if s.get('stage') == 'rdv_pris'), None)
                print_test("Étape rdv_pris dans funnel", rdv_stage is not None,
                          f"Count: {rdv_stage.get('count') if rdv_stage else 'N/A'}")
    except Exception as e:
        print_test("GET /analytics", False, str(e))

def test_agent_permissions(token):
    """Test 6: Permissions agents (nécessite création d'un agent)"""
    print("\n" + "="*60)
    print("TEST 6: PERMISSIONS AGENTS")
    print("="*60)

    print("⚠️  Test manuel requis:")
    print("   1. Créer un user avec role='agent'")
    print("   2. Se connecter comme agent")
    print("   3. Vérifier: voir tous les leads/clients mais modifier seulement les siens")
    print("   4. Vérifier: pas d'accès à /commerciaux ni /admin/users")

def test_database_structure():
    """Test 7: Structure de la base de données (via SSH)"""
    print("\n" + "="*60)
    print("TEST 7: STRUCTURE BASE DE DONNÉES")
    print("="*60)

    print("⚠️  Test SSH requis:")
    print("   1. Se connecter au VPS")
    print("   2. Vérifier table 'commerciaux' existe")
    print("   3. Vérifier colonnes dans 'leads': mobile_phone, address, postal_code, city, country")
    print("   4. Vérifier colonnes dans 'clients': rdv_pris")
    print("   5. Vérifier colonne dans 'appointments': commercial_id")

def main():
    print("\n" + "🔧 TEST AUTOMATIQUE DES 11 MODIFICATIONS")
    print("="*60)
    print(f"API: {API_URL}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Test 0: Auth
    token = test_authentication()
    if not token:
        print("\n❌ ÉCHEC: Impossible de s'authentifier. Tests interrompus.")
        return

    # Tests backend
    test_commerciaux(token)
    test_extended_lead_fields(token)
    test_appointments_with_commercial(token)
    test_rdv_pris_system(token)
    test_analytics_with_rdv_pris(token)
    test_agent_permissions(token)
    test_database_structure()

    print("\n" + "="*60)
    print("✅ TESTS AUTOMATIQUES TERMINÉS")
    print("="*60)
    print("\n📋 TESTS MANUELS REQUIS:")
    print("   - Test 6: Permissions agents (créer user agent)")
    print("   - Test 7: Structure BDD (SSH)")
    print("   - Tests UI complets (calendrier, import CSV, design)")
    print("\n🌐 Tests manuels UI sur: https://crm-ehc.fr")
    print("   Login: admin / admin123")

if __name__ == "__main__":
    main()
