from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from pymongo.collection import Collection
from bson import ObjectId
import re
from datetime import datetime
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Classe que representa um passo de um fluxo
class FlowStep(BaseModel):
    system_prompt: str = Field(..., min_length=1)  # Prompt do sistema para o passo
    step_name: str = Field(..., min_length=1)  # Nome do passo
    step_order: int = Field(..., ge=1)  # Ordem do passo no fluxo
    max_tokens: Optional[int] = Field(default=100, ge=1)  # Máximo de tokens permitidos
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)  # Temperatura do modelo

    # Validador para o nome do passo
    @validator('step_name')
    def validate_step_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\s\-]+$', v):
            raise ValueError('O nome do passo deve conter apenas letras, números, espaços, underscores e hífens')
        return v

# Classe que representa um fluxo
class Flow(BaseModel):
    name: str = Field(..., min_length=1)  # Nome do fluxo
    description: Optional[str] = None  # Descrição do fluxo
    steps: List[FlowStep] = Field(..., min_items=1)  # Lista de passos do fluxo
    is_active: bool = True  # Indica se o fluxo está ativo

    # Validador para o nome do fluxo
    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\s\-]+$', v):
            raise ValueError('O nome do fluxo deve conter apenas letras, números, espaços, underscores e hífens')
        return v

# Classe para gerenciar fluxos
class FlowManager:
    def __init__(self, collection: Collection):
        self.collection = collection  # Coleção do MongoDB onde os fluxos são armazenados

    # Valida a ordem dos passos para garantir que são únicas e sequenciais
    def validate_step_orders(self, steps: List[FlowStep]):
        step_orders = [step.step_order for step in steps]
        if len(set(step_orders)) != len(step_orders):
            raise ValueError("Ordens de passos devem ser únicas")
        if sorted(step_orders) != list(range(1, len(step_orders) + 1)):
            raise ValueError("Ordens de passos devem ser sequenciais começando de 1")

    # Cria um novo fluxo
    def create_flow(self, flow_id: str, flow: Flow) -> Flow:
        logger.info(f"Tentando criar fluxo com ID: {flow_id}")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', flow_id):
            raise ValueError('O ID do fluxo deve conter apenas letras, números e underscores')
        
        if self.collection.find_one({"_id": flow_id}):
            raise ValueError(f"Fluxo com ID {flow_id} já existe")
        
        self.validate_step_orders(flow.steps)
        
        flow_dict = {
            "_id": flow_id,
            "name": flow.name,
            "description": flow.description,
            "steps": [step.dict() for step in flow.steps],
            "is_active": flow.is_active,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        self.collection.insert_one(flow_dict)
        logger.info(f"Fluxo criado com sucesso: {flow_id}")
        return flow

    # Obtém um fluxo pelo ID
    def get_flow(self, flow_id: str) -> Flow:
        logger.info(f"Obtendo fluxo com ID: {flow_id}")
        flow_dict = self.collection.find_one({"_id": flow_id})
        if not flow_dict:
            raise ValueError(f"Fluxo com ID {flow_id} não encontrado")
        
        return Flow(
            name=flow_dict["name"],
            description=flow_dict["description"],
            steps=[FlowStep(**step) for step in flow_dict["steps"]],
            is_active=flow_dict["is_active"]
        )

    # Atualiza um fluxo existente
    def update_flow(self, flow_id: str, flow: Flow) -> Flow:
        logger.info(f"Tentando atualizar fluxo com ID: {flow_id}")
        
        if not self.collection.find_one({"_id": flow_id}):
            raise ValueError(f"Fluxo com ID {flow_id} não encontrado")
        
        self.validate_step_orders(flow.steps)
        
        flow_dict = {
            "name": flow.name,
            "description": flow.description,
            "steps": [step.dict() for step in flow.steps],
            "is_active": flow.is_active,
            "updated_at": datetime.utcnow()
        }
        
        self.collection.update_one(
            {"_id": flow_id},
            {"$set": flow_dict}
        )
        
        logger.info(f"Fluxo atualizado com sucesso: {flow_id}")
        return flow

    # Remove um fluxo
    def delete_flow(self, flow_id: str):
        logger.info(f"Tentando excluir fluxo com ID: {flow_id}")
        result = self.collection.delete_one({"_id": flow_id})
        if result.deleted_count == 0:
            raise ValueError(f"Fluxo com ID {flow_id} não encontrado")
        logger.info(f"Fluxo excluído com sucesso: {flow_id}")

    # Lista todos os fluxos
    def list_flows(self) -> List[Dict[str, Any]]:
        logger.info("Listando todos os fluxos")
        flows = self.collection.find()
        return [
            {
                "id": flow["_id"],
                "name": flow["name"],
                "description": flow["description"],
                "steps_count": len(flow["steps"]),
                "is_active": flow["is_active"]
            }
            for flow in flows
        ]