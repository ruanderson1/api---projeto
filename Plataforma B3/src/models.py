from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class Flow(Base):
    """Modelo para representar um fluxo de processamento"""
    __tablename__ = "flows"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    steps = relationship("FlowStep", back_populates="flow", cascade="all, delete-orphan")

class FlowStep(Base):
    """Modelo para representar um passo de um fluxo"""
    __tablename__ = "flow_steps"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(String, ForeignKey("flows.id"))
    step_name = Column(String)
    step_order = Column(Integer)
    system_prompt = Column(String)
    temperature = Column(Float, default=0.7)  
    max_tokens = Column(Integer, default=100)
    
    flow = relationship("Flow", back_populates="steps")