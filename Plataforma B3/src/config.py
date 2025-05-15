import os
from typing import Optional
from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Classe para gerenciar as configurações da aplicação
class Settings(BaseSettings):
    # Configurações do Azure OpenAI
    UFPB_OPENAI_API_KEY: str = Field(..., env="UFPB_OPENAI_API_KEY")  # Chave da API do OpenAI
    UFPB_OPENAI_API_BASE: str = Field(..., env="UFPB_OPENAI_API_BASE")  # URL base da API do OpenAI
    UFPB_LLM_DEPLOYMENT_NAME_4O: str = Field(..., env="UFPB_LLM_DEPLOYMENT_NAME_4O")  # Nome do deployment do modelo
    UFPB_OPENAI_API_VERSION: str = Field(..., env="UFPB_OPENAI_API_VERSION")  # Versão da API do OpenAI
    
    # Propriedade para construir a URL completa do endpoint do modelo
    @property
    def MODEL_URL(self) -> str:
        """Retorna a URL completa do endpoint"""
        return f"{self.UFPB_OPENAI_API_BASE}openai/deployments/{self.UFPB_LLM_DEPLOYMENT_NAME_4O}/chat/completions?api-version={self.UFPB_OPENAI_API_VERSION}"
    
    # Configurações do MongoDB
    MONGODB_URL: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")  # URL do MongoDB
    MONGODB_DB: str = Field(default="plataforma_b3", env="MONGODB_DB")  # Nome do banco de dados
    MONGODB_COLLECTION: str = Field(default="flows", env="MONGODB_COLLECTION")  # Nome da coleção no MongoDB
    
    # Configurações da aplicação
    APP_NAME: str = Field(default="Plataforma B3 - IA", env="APP_NAME")  # Nome da aplicação
    DEBUG: bool = Field(default=False, env="DEBUG")  # Modo de depuração
    
    # Configurações adicionais para o carregamento de variáveis de ambiente
    class Config:
        env_file = ".env"  # Nome do arquivo de variáveis de ambiente
        case_sensitive = True  # Sensibilidade a maiúsculas/minúsculas
        env_file_encoding = 'utf-8'  # Codificação do arquivo de variáveis de ambiente

# Instancia as configurações para uso na aplicação
settings = Settings() 