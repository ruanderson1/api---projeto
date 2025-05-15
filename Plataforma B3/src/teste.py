import requests

BASE_URL = "http://localhost:8000"

# Teste 1: Criar um novo fluxo
def test_create_flow():
    flow_id = "9"
    url = f"{BASE_URL}/createFlows/?flow_id={flow_id}"  # flow_id como query
    flow_payload = {
        "name": "Fluxo de Teste",
        "description": "Esse é um fluxo para testes.",
        "steps": [
            {
                "step_name": "inicio",
                "temperature": 0.5,
                "system_prompt": "Diga olá",
                "max_tokens": 100,
                "step_order": 1
            }
        ],
        # "is_active": True
    }
    response = requests.post(url, json=flow_payload)
    print("Criar fluxo:", response.status_code, response.json())


# Teste 4: Atualizar fluxo
def test_update_flow():
    url = f"{BASE_URL}/updateFlows/9"
    updated_flow = {
        "name": "Fluxo Atualizado",
        "description": "Descrição atualizada.",
        "steps": [
            {
                "step_name": "inicio",
                "temperature": 0.9,
                "system_prompt": "Atualize isso",
                "max_tokens": 150,
                "step_order": 1
            }
        ],
        # "is_active": False
    }
    response = requests.put(url, json=updated_flow)
    print("Atualizar fluxo:", response.status_code, response.json())



# Teste 2: Obter todos os fluxos
def test_get_all_flows():
    url = f"{BASE_URL}/getFlows/"
    response = requests.get(url)
    print("Obter todos os fluxos:", response.status_code, response.json())

# Teste 3: Obter fluxo específico
def test_get_flow_by_id():
    url = f"{BASE_URL}/getFlowsById/9"
    response = requests.get(url)
    print("Obter fluxo específico:", response.status_code, response.json())

def test_exec_flow():
    flow_id = "9"
    url = f"{BASE_URL}/flows/{flow_id}/exec_flow"
    payload = {
        "user_message": "Olá, tudo bem?"
    }
    response = requests.post(url, json=payload)
    print("Executar fluxo:", response.status_code, response.json())

# Teste 5: Deletar fluxo
def test_delete_flow():
    url = f"{BASE_URL}/deleteFlows/9"
    response = requests.delete(url)
    print("Deletar fluxo:", response.status_code, response.json())

if __name__ == "__main__":
    print("Criar fluxo\n\n")
    test_create_flow()
    print("\n\nObter todos os fluxos\n\n")
    test_get_all_flows()
    print("\n\nObter fluxo específico\n\n")
    test_get_flow_by_id()
    print("\n\nAtualizar fluxo\n\n")
    test_update_flow()
    test_get_flow_by_id()
    # print("\n\nDeletar fluxo\n\n")
    # test_delete_flow()
    # print("\n\nObter todos os fluxos após deleção\n\n")
    # test_get_all_flows()   # ver se foi deletado
    print("\n\nExecutar fluxo\n\n")
    test_exec_flow()