"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application
    app_name: str = Field(default="AI-Agent-Directus-FastMCP-FullStack", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # FastAPI
    fastapi_host: str = Field(default="0.0.0.0", alias="FASTAPI_HOST")
    fastapi_port: int = Field(default=8000, alias="FASTAPI_PORT")
    fastapi_workers: int = Field(default=1, alias="FASTAPI_WORKERS")
    fastapi_reload: bool = Field(default=True, alias="FASTAPI_RELOAD")
    metrics_endpoint: str = Field(default="/metrics", alias="METRICS_ENDPOINT")

    # FastMCP
    fastmcp_agent_endpoint: str = Field(default="/agent", alias="FASTMCP_AGENT_ENDPOINT")
    fastmcp_auto_register_tools: bool = Field(default=True, alias="FASTMCP_AUTO_REGISTER_TOOLS")

    # Directus
    directus_url: str = Field(default="http://localhost:8055", alias="DIRECTUS_URL")
    directus_token: Optional[str] = Field(default=None, alias="DIRECTUS_TOKEN")
    directus_database: str = Field(default="sqlite", alias="DIRECTUS_DATABASE")
    directus_database_path: str = Field(default="artifacts/data.db", alias="DIRECTUS_DATABASE_PATH")
    directus_bootstrap_models: str = Field(default="artifacts/models.json", alias="DIRECTUS_BOOTSTRAP_MODELS")
    directus_auth_source_of_truth: bool = Field(default=True, alias="DIRECTUS_AUTH_SOURCE_OF_TRUTH")

    # Cognee RAG
    cognee_embedding_model: str = Field(default="all-MiniLM-L6-v2", alias="COGNEE_EMBEDDING_MODEL")
    cognee_vector_store: str = Field(default="artifacts/embeddings.db", alias="COGNEE_VECTOR_STORE")
    cognee_auto_context_window: bool = Field(default=True, alias="COGNEE_AUTO_CONTEXT_WINDOW")
    cognee_similarity_threshold: float = Field(default=0.7, alias="COGNEE_SIMILARITY_THRESHOLD")
    cognee_max_results: int = Field(default=10, alias="COGNEE_MAX_RESULTS")

    # UI
    ui_default: str = Field(default="gradio", alias="UI_DEFAULT")
    gradio_server_name: str = Field(default="0.0.0.0", alias="GRADIO_SERVER_NAME")
    gradio_server_port: int = Field(default=7860, alias="GRADIO_SERVER_PORT")
    streamlit_server_port: int = Field(default=8501, alias="STREAMLIT_SERVER_PORT")
    streamlit_server_address: str = Field(default="0.0.0.0", alias="STREAMLIT_SERVER_ADDRESS")

    # External APIs
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    huggingface_token: Optional[str] = Field(default=None, alias="HUGGINGFACE_TOKEN")

    # Observability
    prometheus_enabled: bool = Field(default=True, alias="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, alias="PROMETHEUS_PORT")
    grafana_enabled: bool = Field(default=True, alias="GRAFANA_ENABLED")
    grafana_port: int = Field(default=3000, alias="GRAFANA_PORT")
    grafana_admin_user: str = Field(default="admin", alias="GRAFANA_ADMIN_USER")
    grafana_admin_password: str = Field(default="admin", alias="GRAFANA_ADMIN_PASSWORD")
    scrape_targets: str = Field(default="api.example.com/metrics", alias="SCRAPE_TARGETS")

    # Security
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    allowed_hosts: str = Field(default="localhost,127.0.0.1", alias="ALLOWED_HOSTS")
    cors_origins: str = Field(default="http://localhost", alias="CORS_ORIGINS")

    # Podman
    podman_use_secrets: bool = Field(default=True, alias="PODMAN_USE_SECRETS")
    podman_network_edge: str = Field(default="edge_net", alias="PODMAN_NETWORK_EDGE")
    podman_network_app: str = Field(default="app_net", alias="PODMAN_NETWORK_APP")
    podman_network_db: str = Field(default="db_net", alias="PODMAN_NETWORK_DB")

    # Database
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    database_pool_size: int = Field(default=10, alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, alias="DATABASE_MAX_OVERFLOW")

    # Cache
    cache_enabled: bool = Field(default=True, alias="CACHE_ENABLED")
    cache_ttl: int = Field(default=300, alias="CACHE_TTL")
    cache_max_size: int = Field(default=1000, alias="CACHE_MAX_SIZE")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()

    @field_validator("allowed_hosts", "cors_origins")
    @classmethod
    def parse_comma_separated(cls, v: str) -> str:
        """Parse comma-separated string."""
        if not v:
            return ""
        return ",".join([x.strip() for x in v.split(",")])

    @property
    def allowed_hosts_list(self) -> List[str]:
        """Get allowed hosts as list."""
        return [h.strip() for h in self.allowed_hosts.split(",") if h.strip()]

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env.lower() == "production"

    @property
    def artifacts_dir(self) -> Path:
        """Get artifacts directory path."""
        return Path("artifacts").resolve()

    @property
    def directus_db_path(self) -> Path:
        """Get Directus database path."""
        return Path(self.directus_database_path).resolve()

    @property
    def cognee_vector_store_path(self) -> Path:
        """Get Cognee vector store path."""
        return Path(self.cognee_vector_store).resolve()


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
