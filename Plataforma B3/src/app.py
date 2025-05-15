from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import asyncio

from dotenv import load_dotenv
from flow_manager import FlowManager, Flow, FlowStep
from model_integration import ModelIntegration
from config import settings
from database import get_db

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa app FastAPI
app = FastAPI(title=settings.APP_NAME)

# Inicializa cliente de modelo
model_client = ModelIntegration(api_key=settings.UFPB_OPENAI_API_KEY)

# Schemas
class FlowStepSchema(BaseModel):
    step_name: str
    temperature: float = 0.7
    system_prompt: str
    max_tokens: int = 100
    step_order: int

class FlowSchema(BaseModel):
    name: str
    description: str
    steps: List[FlowStepSchema]
    is_active: bool = True

class FlowuserMessage(BaseModel):
    user_message: str = Field(..., example="Qual análise?")

# Rotas
@app.post("/createFlows/", response_model=Dict)
def create_flow(flow_id: str, flow: FlowSchema, db=Depends(get_db)):
    manager = FlowManager(db)
    try:
        new_flow = Flow(**flow.dict())
        manager.create_flow(flow_id, new_flow)
        return {"message": "Fluxo criado com sucesso", "flow_id": flow_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/getFlows/", response_model=List[Dict])
def list_flows(db=Depends(get_db)):
    manager = FlowManager(db)
    return manager.list_flows()

@app.get("/getFlowsById/{flow_id}", response_model=Dict)
def get_flow(flow_id: str, db=Depends(get_db)):
    manager = FlowManager(db)
    flow = manager.get_flow(flow_id)
    if flow is None:
        raise HTTPException(status_code=404, detail="Fluxo não encontrado")
    return flow.dict()

@app.put("/updateFlows/{flow_id}", response_model=Dict)
def update_flow(flow_id: str, flow: FlowSchema, db=Depends(get_db)):
    manager = FlowManager(db)
    try:
        updated_flow = Flow(**flow.dict())
        manager.update_flow(flow_id, updated_flow)
        return {"message": "Fluxo atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/deleteFlows/{flow_id}", response_model=Dict)
def delete_flow(flow_id: str, db=Depends(get_db)):
    manager = FlowManager(db)
    try:
        manager.delete_flow(flow_id)
        return {"message": "Fluxo deletado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/flows/{flow_id}/exec_flow", response_model=Dict)
def test_flow(flow_id: str, request: FlowuserMessage, db=Depends(get_db)):
    manager = FlowManager(db)
    flow = manager.get_flow(flow_id)
    if flow is None:
        raise HTTPException(status_code=404, detail="Fluxo não encontrado")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            model_client.process_flow(user_message=request.user_message, flow=flow)
        )
        loop.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
