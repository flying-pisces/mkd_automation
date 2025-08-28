"""
Configuration Manager

Production configuration management with environment-specific settings,
secrets handling, and deployment configuration validation.
"""

import os
import json
import logging
import hashlib
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import base64
import getpass

try:
    import yaml
except ImportError:
    yaml = None

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

logger = logging.getLogger(__name__)


class DeploymentEnvironment(Enum):
    """Deployment environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    LOCAL = "local"


class ConfigFormat(Enum):
    """Configuration file formats"""
    JSON = "json"
    YAML = "yaml"
    INI = "ini"
    ENV = "env"
    TOML = "toml"


class SecretType(Enum):
    """Types of secrets"""
    PASSWORD = "password"
    API_KEY = "api_key"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    DATABASE_URL = "database_url"
    ENCRYPTION_KEY = "encryption_key"


@dataclass
class SecretConfig:
    """Secret configuration"""
    name: str
    secret_type: SecretType
    description: str
    required: bool = True
    environment_variable: Optional[str] = None
    default_value: Optional[str] = None
    validation_pattern: Optional[str] = None


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration"""
    environment: DeploymentEnvironment
    config_values: Dict[str, Any] = field(default_factory=dict)
    secrets: Dict[str, str] = field(default_factory=dict)
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    logging_config: Dict[str, Any] = field(default_factory=dict)


class ConfigurationManager:
    """Production configuration management system"""
    
    def __init__(self, config_directory: str = None, encryption_key: str = None):
        self.config_directory = Path(config_directory or Path.home() / ".mkd" / "config")
        self.config_directory.mkdir(parents=True, exist_ok=True)
        
        # Encryption for secrets
        self.encryption_key = encryption_key
        self.cipher_suite = self._setup_encryption(encryption_key)
        
        # Configuration registry
        self.environments: Dict[DeploymentEnvironment, EnvironmentConfig] = {}
        self.secret_definitions: Dict[str, SecretConfig] = {}
        self.current_environment = DeploymentEnvironment.LOCAL
        
        # Schema and validation
        self.config_schema = {}
        self.validation_rules = {}
        
        # Configuration cache
        self._config_cache = {}
        self._cache_timestamps = {}
        
        # Load existing configurations
        self._load_configurations()
        
        # Define default secret types
        self._define_default_secrets()
        
        logger.info(f"ConfigurationManager initialized with directory: {self.config_directory}")
    
    def _setup_encryption(self, key: str = None) -> Optional:
        """Setup encryption for secrets"""
        
        if not CRYPTO_AVAILABLE:
            logger.warning("Cryptography library not available - secrets will not be encrypted")
            return None
        
        try:
            if key:
                # Use provided key
                key_bytes = key.encode()
            else:
                # Generate key from system info or prompt
                key_material = self._get_key_material()
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b'mkd_config_salt',  # In production, use random salt
                    iterations=100000,
                )
                key_bytes = base64.urlsafe_b64encode(kdf.derive(key_material))
            
            return Fernet(key_bytes)
            
        except Exception as e:
            logger.warning(f"Failed to setup encryption: {e}")
            return None
    
    def _get_key_material(self) -> bytes:
        """Get key material for encryption"""
        
        # Try environment variable first
        env_key = os.environ.get('MKD_CONFIG_KEY')
        if env_key:
            return env_key.encode()
        
        # Use system-specific information
        import platform
        system_info = f"{platform.node()}-{getpass.getuser()}"
        return system_info.encode()
    
    def _define_default_secrets(self) -> None:
        """Define default secret configurations"""
        
        default_secrets = [
            SecretConfig(
                name="database_password",
                secret_type=SecretType.PASSWORD,
                description="Database connection password",
                environment_variable="DB_PASSWORD"
            ),
            SecretConfig(
                name="api_key",
                secret_type=SecretType.API_KEY,
                description="External API key",
                environment_variable="API_KEY"
            ),
            SecretConfig(
                name="jwt_secret",
                secret_type=SecretType.TOKEN,
                description="JWT signing secret",
                environment_variable="JWT_SECRET"
            ),
            SecretConfig(
                name="encryption_key",
                secret_type=SecretType.ENCRYPTION_KEY,
                description="Data encryption key",
                environment_variable="ENCRYPTION_KEY"
            )
        ]
        
        for secret in default_secrets:
            self.secret_definitions[secret.name] = secret
    
    def create_environment_config(self, environment: DeploymentEnvironment) -> EnvironmentConfig:
        """Create new environment configuration"""
        
        env_config = EnvironmentConfig(environment=environment)
        
        # Set default configurations based on environment
        if environment == DeploymentEnvironment.DEVELOPMENT:
            env_config.config_values = {
                "debug": True,
                "log_level": "DEBUG",
                "database_pool_size": 5,
                "cache_timeout": 60,
                "rate_limit_enabled": False
            }
            env_config.feature_flags = {
                "experimental_features": True,
                "debug_toolbar": True,
                "profiling": True
            }
            env_config.logging_config = {
                "level": "DEBUG",
                "format": "detailed",
                "handlers": ["console", "file"]
            }
        
        elif environment == DeploymentEnvironment.TESTING:
            env_config.config_values = {
                "debug": False,
                "log_level": "INFO",
                "database_pool_size": 3,
                "cache_timeout": 30,
                "rate_limit_enabled": True
            }
            env_config.feature_flags = {
                "experimental_features": True,
                "debug_toolbar": False,
                "profiling": False
            }
            
        elif environment == DeploymentEnvironment.STAGING:
            env_config.config_values = {
                "debug": False,
                "log_level": "INFO",
                "database_pool_size": 10,
                "cache_timeout": 300,
                "rate_limit_enabled": True
            }
            env_config.feature_flags = {
                "experimental_features": False,
                "debug_toolbar": False,
                "profiling": False
            }
            env_config.resource_limits = {
                "max_memory_mb": 1024,
                "max_cpu_percent": 80,
                "max_connections": 100
            }
        
        elif environment == DeploymentEnvironment.PRODUCTION:
            env_config.config_values = {
                "debug": False,
                "log_level": "WARNING",
                "database_pool_size": 20,
                "cache_timeout": 3600,
                "rate_limit_enabled": True
            }
            env_config.feature_flags = {
                "experimental_features": False,
                "debug_toolbar": False,
                "profiling": False
            }
            env_config.resource_limits = {
                "max_memory_mb": 2048,
                "max_cpu_percent": 90,
                "max_connections": 500
            }
            env_config.logging_config = {
                "level": "WARNING",
                "format": "json",
                "handlers": ["file", "syslog"]
            }
        
        self.environments[environment] = env_config
        return env_config
    
    def set_current_environment(self, environment: DeploymentEnvironment) -> None:
        """Set the current active environment"""
        
        if environment not in self.environments:
            self.create_environment_config(environment)
        
        self.current_environment = environment
        logger.info(f"Current environment set to: {environment.value}")
    
    def get_config_value(self, key: str, default: Any = None, 
                        environment: DeploymentEnvironment = None) -> Any:
        """Get configuration value"""
        
        env = environment or self.current_environment
        
        if env not in self.environments:
            logger.warning(f"Environment {env.value} not configured")
            return default
        
        env_config = self.environments[env]
        
        # Check environment variables first
        env_key = f"MKD_{key.upper()}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return self._parse_env_value(env_value)
        
        # Check configuration
        return env_config.config_values.get(key, default)
    
    def set_config_value(self, key: str, value: Any, 
                        environment: DeploymentEnvironment = None) -> None:
        """Set configuration value"""
        
        env = environment or self.current_environment
        
        if env not in self.environments:
            self.create_environment_config(env)
        
        self.environments[env].config_values[key] = value
        
        # Clear cache
        cache_key = f"{env.value}_{key}"
        if cache_key in self._config_cache:
            del self._config_cache[cache_key]
        
        logger.debug(f"Configuration set: {key} = {value} (env: {env.value})")
    
    def get_secret(self, secret_name: str, environment: DeploymentEnvironment = None) -> Optional[str]:
        """Get encrypted secret"""
        
        env = environment or self.current_environment
        
        if env not in self.environments:
            return None
        
        env_config = self.environments[env]
        
        # Check environment variable first
        secret_def = self.secret_definitions.get(secret_name)
        if secret_def and secret_def.environment_variable:
            env_value = os.environ.get(secret_def.environment_variable)
            if env_value:
                return env_value
        
        # Check encrypted secrets
        encrypted_secret = env_config.secrets.get(secret_name)
        if encrypted_secret and self.cipher_suite:
            try:
                return self.cipher_suite.decrypt(encrypted_secret.encode()).decode()
            except Exception as e:
                logger.error(f"Failed to decrypt secret {secret_name}: {e}")
                return None
        
        # Return default if available
        if secret_def and secret_def.default_value:
            return secret_def.default_value
        
        return None
    
    def set_secret(self, secret_name: str, value: str, 
                  environment: DeploymentEnvironment = None) -> bool:
        """Set encrypted secret"""
        
        env = environment or self.current_environment
        
        if env not in self.environments:
            self.create_environment_config(env)
        
        if not self.cipher_suite:
            logger.error("Encryption not available for secrets")
            return False
        
        try:
            encrypted_value = self.cipher_suite.encrypt(value.encode()).decode()
            self.environments[env].secrets[secret_name] = encrypted_value
            
            logger.debug(f"Secret set: {secret_name} (env: {env.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to encrypt secret {secret_name}: {e}")
            return False
    
    def get_feature_flag(self, flag_name: str, default: bool = False,
                        environment: DeploymentEnvironment = None) -> bool:
        """Get feature flag value"""
        
        env = environment or self.current_environment
        
        if env not in self.environments:
            return default
        
        # Check environment variable first
        env_key = f"MKD_FEATURE_{flag_name.upper()}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value.lower() in ('true', '1', 'yes', 'on')
        
        return self.environments[env].feature_flags.get(flag_name, default)
    
    def set_feature_flag(self, flag_name: str, enabled: bool,
                        environment: DeploymentEnvironment = None) -> None:
        """Set feature flag value"""
        
        env = environment or self.current_environment
        
        if env not in self.environments:
            self.create_environment_config(env)
        
        self.environments[env].feature_flags[flag_name] = enabled
        logger.debug(f"Feature flag set: {flag_name} = {enabled} (env: {env.value})")
    
    def save_configuration(self, environment: DeploymentEnvironment = None,
                          format: ConfigFormat = ConfigFormat.YAML) -> bool:
        """Save configuration to file"""
        
        env = environment or self.current_environment
        
        if env not in self.environments:
            logger.warning(f"No configuration to save for environment: {env.value}")
            return False
        
        env_config = self.environments[env]
        
        try:
            config_file = self.config_directory / f"{env.value}.{format.value}"
            
            # Prepare data for serialization
            config_data = {
                "environment": env.value,
                "config_values": env_config.config_values,
                "feature_flags": env_config.feature_flags,
                "resource_limits": env_config.resource_limits,
                "logging_config": env_config.logging_config,
                # Note: secrets are not saved in plain text files
                "secrets_available": list(env_config.secrets.keys())
            }
            
            # Save based on format
            if format == ConfigFormat.JSON:
                with open(config_file, 'w') as f:
                    json.dump(config_data, f, indent=2)
            
            elif format == ConfigFormat.YAML:
                if yaml is None:
                    raise ImportError("PyYAML is required for YAML format")
                with open(config_file, 'w') as f:
                    yaml.dump(config_data, f, default_flow_style=False)
            
            elif format == ConfigFormat.ENV:
                # Save as environment variables
                with open(config_file, 'w') as f:
                    for key, value in env_config.config_values.items():
                        f.write(f"MKD_{key.upper()}={value}\n")
                    
                    for flag, enabled in env_config.feature_flags.items():
                        f.write(f"MKD_FEATURE_{flag.upper()}={'true' if enabled else 'false'}\n")
            
            # Save encrypted secrets separately
            secrets_file = self.config_directory / f"{env.value}_secrets.enc"
            if env_config.secrets:
                with open(secrets_file, 'w') as f:
                    json.dump(env_config.secrets, f)
            
            logger.info(f"Configuration saved: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def load_configuration(self, environment: DeploymentEnvironment,
                          format: ConfigFormat = ConfigFormat.YAML) -> bool:
        """Load configuration from file"""
        
        try:
            config_file = self.config_directory / f"{environment.value}.{format.value}"
            
            if not config_file.exists():
                logger.warning(f"Configuration file not found: {config_file}")
                return False
            
            # Load configuration data
            config_data = {}
            
            if format == ConfigFormat.JSON:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
            
            elif format == ConfigFormat.YAML:
                if yaml is None:
                    raise ImportError("PyYAML is required for YAML format")
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
            
            elif format == ConfigFormat.ENV:
                # Load environment variables format
                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            if key.startswith('MKD_FEATURE_'):
                                flag_name = key[12:].lower()
                                config_data.setdefault('feature_flags', {})[flag_name] = value.lower() == 'true'
                            elif key.startswith('MKD_'):
                                config_key = key[4:].lower()
                                config_data.setdefault('config_values', {})[config_key] = self._parse_env_value(value)
            
            # Create or update environment config
            if environment not in self.environments:
                self.create_environment_config(environment)
            
            env_config = self.environments[environment]
            
            # Update configuration
            if 'config_values' in config_data:
                env_config.config_values.update(config_data['config_values'])
            
            if 'feature_flags' in config_data:
                env_config.feature_flags.update(config_data['feature_flags'])
            
            if 'resource_limits' in config_data:
                env_config.resource_limits.update(config_data['resource_limits'])
            
            if 'logging_config' in config_data:
                env_config.logging_config.update(config_data['logging_config'])
            
            # Load encrypted secrets
            secrets_file = self.config_directory / f"{environment.value}_secrets.enc"
            if secrets_file.exists():
                try:
                    with open(secrets_file, 'r') as f:
                        encrypted_secrets = json.load(f)
                        env_config.secrets.update(encrypted_secrets)
                except Exception as e:
                    logger.warning(f"Failed to load encrypted secrets: {e}")
            
            logger.info(f"Configuration loaded: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
    
    def _load_configurations(self) -> None:
        """Load all existing configurations"""
        
        for env in DeploymentEnvironment:
            yaml_file = self.config_directory / f"{env.value}.yaml"
            json_file = self.config_directory / f"{env.value}.json"
            
            if yaml_file.exists():
                self.load_configuration(env, ConfigFormat.YAML)
            elif json_file.exists():
                self.load_configuration(env, ConfigFormat.JSON)
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type"""
        
        # Boolean values
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer values
        if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
            return int(value)
        
        # Float values
        try:
            return float(value)
        except ValueError:
            pass
        
        # JSON values
        if value.startswith(('{', '[')):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # String value
        return value
    
    def validate_configuration(self, environment: DeploymentEnvironment = None) -> Dict[str, List[str]]:
        """Validate configuration for environment"""
        
        env = environment or self.current_environment
        
        if env not in self.environments:
            return {"error": ["Environment not configured"]}
        
        env_config = self.environments[env]
        validation_errors = {}
        
        # Validate required secrets
        for secret_name, secret_def in self.secret_definitions.items():
            if secret_def.required:
                secret_value = self.get_secret(secret_name, env)
                if not secret_value:
                    validation_errors.setdefault("missing_secrets", []).append(secret_name)
        
        # Validate configuration schema (if defined)
        for key, rules in self.validation_rules.items():
            value = env_config.config_values.get(key)
            
            if rules.get("required") and value is None:
                validation_errors.setdefault("missing_config", []).append(key)
            
            if value is not None:
                # Type validation
                expected_type = rules.get("type")
                if expected_type and not isinstance(value, expected_type):
                    validation_errors.setdefault("type_errors", []).append(f"{key}: expected {expected_type.__name__}")
                
                # Range validation
                min_val = rules.get("min")
                max_val = rules.get("max")
                if isinstance(value, (int, float)):
                    if min_val is not None and value < min_val:
                        validation_errors.setdefault("range_errors", []).append(f"{key}: value {value} < minimum {min_val}")
                    if max_val is not None and value > max_val:
                        validation_errors.setdefault("range_errors", []).append(f"{key}: value {value} > maximum {max_val}")
        
        return validation_errors
    
    def generate_deployment_config(self, environment: DeploymentEnvironment,
                                 template_path: str = None) -> str:
        """Generate deployment configuration file"""
        
        if environment not in self.environments:
            raise ValueError(f"Environment {environment.value} not configured")
        
        env_config = self.environments[environment]
        
        # Basic deployment configuration
        deployment_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"mkd-config-{environment.value}",
                "labels": {
                    "app": "mkd-automation",
                    "environment": environment.value
                }
            },
            "data": {}
        }
        
        # Add configuration values
        for key, value in env_config.config_values.items():
            deployment_config["data"][f"MKD_{key.upper()}"] = str(value)
        
        # Add feature flags
        for flag, enabled in env_config.feature_flags.items():
            deployment_config["data"][f"MKD_FEATURE_{flag.upper()}"] = str(enabled).lower()
        
        # Convert to YAML
        if yaml is None:
            return json.dumps(deployment_config, indent=2)
        return yaml.dump(deployment_config, default_flow_style=False)
    
    def get_configuration_summary(self, environment: DeploymentEnvironment = None) -> Dict[str, Any]:
        """Get comprehensive configuration summary"""
        
        env = environment or self.current_environment
        
        if env not in self.environments:
            return {"error": f"Environment {env.value} not configured"}
        
        env_config = self.environments[env]
        
        return {
            "environment": env.value,
            "config_values_count": len(env_config.config_values),
            "secrets_count": len(env_config.secrets),
            "feature_flags_count": len(env_config.feature_flags),
            "resource_limits_set": bool(env_config.resource_limits),
            "logging_configured": bool(env_config.logging_config),
            "validation_errors": self.validate_configuration(env),
            "encryption_enabled": self.cipher_suite is not None,
            "config_directory": str(self.config_directory)
        }