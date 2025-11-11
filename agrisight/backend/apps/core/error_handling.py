"""
Error handling utilities for AgriSight backend.

Provides:
- Standardized error response format
- Error codes and types
- Custom exception classes
- Error middleware
- Error logging and tracking
"""

from enum import Enum
from typing import Optional, Dict, Any
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# Error Types and Codes
# =============================================================================

class ErrorType(str, Enum):
    """Standard error types for the API."""
    
    # Client errors
    VALIDATION = "VALIDATION_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    
    # Server errors
    SERVER_ERROR = "SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    
    # Application-specific errors
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    INVALID_TOKEN = "INVALID_TOKEN"
    EXPIRED_TOKEN = "EXPIRED_TOKEN"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RESOURCE_LOCKED = "RESOURCE_LOCKED"
    INTEGRATION_ERROR = "INTEGRATION_ERROR"
    DATA_PROCESSING_ERROR = "DATA_PROCESSING_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


class ErrorCode(str, Enum):
    """Specific error codes for different scenarios."""
    
    # Authentication (1xxx)
    AUTH_INVALID_CREDENTIALS = "1001"
    AUTH_USER_INACTIVE = "1002"
    AUTH_USER_NOT_FOUND = "1003"
    AUTH_INVALID_TOKEN = "1004"
    AUTH_TOKEN_EXPIRED = "1005"
    AUTH_PERMISSION_DENIED = "1006"
    AUTH_EMAIL_NOT_VERIFIED = "1007"
    AUTH_MFA_REQUIRED = "1008"
    
    # User Management (2xxx)
    USER_ALREADY_EXISTS = "2001"
    USER_NOT_FOUND = "2002"
    USER_PROFILE_INCOMPLETE = "2003"
    USER_EMAIL_NOT_VERIFIED = "2004"
    USER_SUSPENDED = "2005"
    
    # Validation (3xxx)
    INVALID_INPUT = "3001"
    INVALID_EMAIL = "3002"
    INVALID_PASSWORD = "3003"
    INVALID_DATE_FORMAT = "3004"
    MISSING_REQUIRED_FIELD = "3005"
    FILE_TOO_LARGE = "3006"
    UNSUPPORTED_FILE_TYPE = "3007"
    
    # Data Operations (4xxx)
    RESOURCE_NOT_FOUND = "4001"
    RESOURCE_ALREADY_EXISTS = "4002"
    RESOURCE_LOCKED = "4003"
    INVALID_STATE_TRANSITION = "4004"
    OPERATION_NOT_ALLOWED = "4005"
    DATA_CONSISTENCY_ERROR = "4006"
    
    # Geospatial Operations (5xxx)
    INVALID_GEOMETRY = "5001"
    INVALID_COORDINATES = "5002"
    AREA_OUT_OF_BOUNDS = "5003"
    GEOSPATIAL_PROCESSING_ERROR = "5004"
    
    # Satellite Data (6xxx)
    SATELLITE_DATA_NOT_AVAILABLE = "6001"
    INVALID_DATE_RANGE = "6002"
    INSUFFICIENT_CLOUD_COVERAGE = "6003"
    SENTINEL_HUB_ERROR = "6004"
    EARTH_ENGINE_ERROR = "6005"
    DATA_RETRIEVAL_ERROR = "6006"
    
    # ML Models (7xxx)
    MODEL_NOT_FOUND = "7001"
    MODEL_PREDICTION_ERROR = "7002"
    INVALID_MODEL_INPUT = "7003"
    MODEL_TIMEOUT = "7004"
    
    # External Services (8xxx)
    EXTERNAL_SERVICE_UNAVAILABLE = "8001"
    EXTERNAL_SERVICE_ERROR = "8002"
    RATE_LIMIT_EXCEEDED = "8003"
    TIMEOUT = "8004"
    
    # Database (9xxx)
    DATABASE_ERROR = "9001"
    DATABASE_INTEGRITY_ERROR = "9002"
    DATABASE_TIMEOUT = "9003"
    
    # System (10xxx)
    SYSTEM_ERROR = "10001"
    CONFIGURATION_ERROR = "10002"
    FEATURE_NOT_IMPLEMENTED = "10003"
    FEATURE_DISABLED = "10004"


# =============================================================================
# Custom Exception Classes
# =============================================================================

class APIErrorException(APIException):
    """Base exception class for API errors."""
    
    default_detail = "An error occurred"
    default_code = ErrorCode.SYSTEM_ERROR
    default_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_type = ErrorType.SERVER_ERROR
    
    def __init__(
        self,
        message: str = None,
        code: str = None,
        error_type: str = None,
        status_code: int = None,
        detail: str = None,
        field_errors: Dict[str, Any] = None,
        retry_after: int = None,
        **kwargs
    ):
        """
        Initialize API error.
        
        Args:
            message: Human-readable error message
            code: Error code (from ErrorCode enum)
            error_type: Error type (from ErrorType enum)
            status_code: HTTP status code
            detail: Additional details
            field_errors: Field-specific validation errors
            retry_after: Seconds to wait before retry (for rate limits)
        """
        self.message = message or self.default_detail
        self.code = code or self.default_code
        self.error_type = error_type or self.default_type
        self.status_code = status_code or self.default_status_code
        self.detail = detail
        self.field_errors = field_errors or {}
        self.retry_after = retry_after
        self.metadata = kwargs
        self.timestamp = datetime.utcnow().isoformat()
        
        super().__init__(detail=self.message)


class ValidationErrorException(APIErrorException):
    """Raised when input validation fails."""
    
    default_status_code = status.HTTP_400_BAD_REQUEST
    default_type = ErrorType.VALIDATION


class AuthenticationException(APIErrorException):
    """Raised when authentication fails."""
    
    default_status_code = status.HTTP_401_UNAUTHORIZED
    default_type = ErrorType.AUTHENTICATION_FAILED


class AuthorizationException(APIErrorException):
    """Raised when user lacks permission."""
    
    default_status_code = status.HTTP_403_FORBIDDEN
    default_type = ErrorType.FORBIDDEN


class ResourceNotFoundException(APIErrorException):
    """Raised when requested resource is not found."""
    
    default_status_code = status.HTTP_404_NOT_FOUND
    default_type = ErrorType.NOT_FOUND


class ConflictException(APIErrorException):
    """Raised when request conflicts with existing data."""
    
    default_status_code = status.HTTP_409_CONFLICT
    default_type = ErrorType.CONFLICT


class RateLimitException(APIErrorException):
    """Raised when rate limit is exceeded."""
    
    default_status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_type = ErrorType.RATE_LIMITED


class ExternalServiceException(APIErrorException):
    """Raised when external service fails."""
    
    default_status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_type = ErrorType.EXTERNAL_SERVICE_ERROR


class TimeoutException(APIErrorException):
    """Raised when operation times out."""
    
    default_status_code = status.HTTP_504_GATEWAY_TIMEOUT
    default_type = ErrorType.SERVER_ERROR


# =============================================================================
# Error Response Format
# =============================================================================

class ErrorResponse:
    """Standardized error response."""
    
    def __init__(
        self,
        message: str,
        code: str = ErrorCode.SYSTEM_ERROR,
        error_type: str = ErrorType.SERVER_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        field_errors: Dict[str, Any] = None,
        detail: str = None,
        trace_id: str = None,
        retry_after: int = None,
        **metadata
    ):
        """
        Initialize error response.
        
        Args:
            message: User-friendly error message
            code: Error code for client handling
            error_type: Type of error for categorization
            status_code: HTTP status code
            field_errors: Field-level validation errors
            detail: Additional details
            trace_id: Unique identifier for error tracking
            retry_after: Seconds before retry (for rate limits)
            **metadata: Additional metadata
        """
        self.message = message
        self.code = code
        self.error_type = error_type
        self.status_code = status_code
        self.field_errors = field_errors or {}
        self.detail = detail
        self.trace_id = trace_id
        self.retry_after = retry_after
        self.timestamp = datetime.utcnow().isoformat()
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        response = {
            "success": False,
            "error": {
                "message": self.message,
                "code": self.code,
                "type": self.error_type,
                "timestamp": self.timestamp,
            }
        }
        
        # Add optional fields
        if self.field_errors:
            response["error"]["field_errors"] = self.field_errors
        
        if self.detail:
            response["error"]["detail"] = self.detail
        
        if self.trace_id:
            response["error"]["trace_id"] = self.trace_id
        
        if self.retry_after:
            response["error"]["retry_after"] = self.retry_after
        
        # Add metadata if in development mode
        if settings.DEBUG and self.metadata:
            response["error"]["metadata"] = self.metadata
        
        return response
    
    def to_response(self) -> Response:
        """Convert to DRF Response."""
        return Response(
            self.to_dict(),
            status=self.status_code
        )


# =============================================================================
# Exception Handler
# =============================================================================

def api_exception_handler(exc, context):
    """
    Custom exception handler for DRF.
    
    Converts all exceptions to standardized error responses.
    """
    trace_id = context.get('request').META.get('HTTP_X_TRACE_ID', '')
    
    # Handle our custom API exceptions
    if isinstance(exc, APIErrorException):
        error_response = ErrorResponse(
            message=exc.message,
            code=exc.code,
            error_type=exc.error_type,
            status_code=exc.status_code,
            field_errors=exc.field_errors,
            detail=exc.detail,
            trace_id=trace_id,
            retry_after=exc.retry_after
        )
        
        # Log the error
        log_error(exc, context, error_response)
        
        return error_response.to_response()
    
    # Handle Django validation errors
    if isinstance(exc, DjangoValidationError):
        error_response = ErrorResponse(
            message="Validation error",
            code=ErrorCode.INVALID_INPUT,
            error_type=ErrorType.VALIDATION,
            status_code=status.HTTP_400_BAD_REQUEST,
            trace_id=trace_id
        )
        
        logger.warning(f"Validation error: {exc}")
        return error_response.to_response()
    
    # Handle DRF validation errors
    if isinstance(exc, Exception) and hasattr(exc, 'detail'):
        error_response = ErrorResponse(
            message=str(exc.detail),
            code=ErrorCode.INVALID_INPUT,
            error_type=ErrorType.VALIDATION,
            status_code=status.HTTP_400_BAD_REQUEST,
            trace_id=trace_id
        )
        
        logger.warning(f"DRF error: {exc}")
        return error_response.to_response()
    
    # Handle unexpected exceptions
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
        extra={
            'trace_id': trace_id,
            'path': context.get('request').path if context.get('request') else '',
            'method': context.get('request').method if context.get('request') else '',
        }
    )
    
    error_response = ErrorResponse(
        message="An internal server error occurred",
        code=ErrorCode.SYSTEM_ERROR,
        error_type=ErrorType.SERVER_ERROR,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        trace_id=trace_id
    )
    
    return error_response.to_response()


def log_error(exc: APIErrorException, context: Dict, error_response: ErrorResponse):
    """Log error with appropriate severity level."""
    
    # Extract request info
    request = context.get('request')
    path = request.path if request else 'unknown'
    method = request.method if request else 'unknown'
    user_id = request.user.id if request and request.user and request.user.is_authenticated else None
    
    # Determine log level based on status code
    if error_response.status_code >= 500:
        log_level = logger.error
        severity = "ERROR"
    elif error_response.status_code >= 400:
        log_level = logger.warning
        severity = "WARNING"
    else:
        log_level = logger.info
        severity = "INFO"
    
    # Build log message
    log_message = f"{severity}: {error_response.message} ({error_response.code})"
    
    log_level(
        log_message,
        extra={
            'trace_id': error_response.trace_id,
            'error_code': error_response.code,
            'error_type': error_response.error_type,
            'status_code': error_response.status_code,
            'path': path,
            'method': method,
            'user_id': user_id,
        }
    )


# =============================================================================
# Success Response Format
# =============================================================================

class SuccessResponse:
    """Standardized success response."""
    
    def __init__(
        self,
        data: Any = None,
        message: str = None,
        status_code: int = status.HTTP_200_OK,
        **metadata
    ):
        """
        Initialize success response.
        
        Args:
            data: Response data
            message: Optional message
            status_code: HTTP status code
            **metadata: Additional metadata
        """
        self.data = data
        self.message = message
        self.status_code = status_code
        self.timestamp = datetime.utcnow().isoformat()
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        response = {
            "success": True,
            "data": self.data,
            "timestamp": self.timestamp,
        }
        
        if self.message:
            response["message"] = self.message
        
        if self.metadata:
            response.update(self.metadata)
        
        return response
    
    def to_response(self) -> Response:
        """Convert to DRF Response."""
        return Response(
            self.to_dict(),
            status=self.status_code
        )


# =============================================================================
# Utility Functions
# =============================================================================

def create_validation_error(
    message: str = "Validation error",
    field_errors: Dict[str, Any] = None,
    code: str = ErrorCode.INVALID_INPUT,
    **kwargs
) -> ValidationErrorException:
    """Create a validation error exception."""
    return ValidationErrorException(
        message=message,
        code=code,
        field_errors=field_errors or {},
        **kwargs
    )


def create_auth_error(
    message: str = "Authentication failed",
    code: str = ErrorCode.AUTH_INVALID_CREDENTIALS,
    **kwargs
) -> AuthenticationException:
    """Create an authentication error exception."""
    return AuthenticationException(
        message=message,
        code=code,
        **kwargs
    )


def create_permission_error(
    message: str = "Permission denied",
    code: str = ErrorCode.AUTH_PERMISSION_DENIED,
    **kwargs
) -> AuthorizationException:
    """Create an authorization error exception."""
    return AuthorizationException(
        message=message,
        code=code,
        **kwargs
    )


def create_not_found_error(
    resource: str = "Resource",
    code: str = ErrorCode.RESOURCE_NOT_FOUND,
    **kwargs
) -> ResourceNotFoundException:
    """Create a not found error exception."""
    return ResourceNotFoundException(
        message=f"{resource} not found",
        code=code,
        **kwargs
    )


def create_conflict_error(
    message: str = "Resource conflict",
    code: str = ErrorCode.RESOURCE_ALREADY_EXISTS,
    **kwargs
) -> ConflictException:
    """Create a conflict error exception."""
    return ConflictException(
        message=message,
        code=code,
        **kwargs
    )


def create_rate_limit_error(
    retry_after: int = 60,
    message: str = "Rate limit exceeded",
    **kwargs
) -> RateLimitException:
    """Create a rate limit error exception."""
    return RateLimitException(
        message=message,
        code=ErrorCode.RATE_LIMIT_EXCEEDED,
        retry_after=retry_after,
        **kwargs
    )


def create_external_service_error(
    service: str = "External service",
    message: str = None,
    code: str = ErrorCode.EXTERNAL_SERVICE_ERROR,
    **kwargs
) -> ExternalServiceException:
    """Create an external service error exception."""
    if not message:
        message = f"{service} is temporarily unavailable"
    
    return ExternalServiceException(
        message=message,
        code=code,
        **kwargs
    )


def create_timeout_error(
    operation: str = "Operation",
    timeout_seconds: int = None,
    **kwargs
) -> TimeoutException:
    """Create a timeout error exception."""
    message = f"{operation} timed out"
    if timeout_seconds:
        message += f" (after {timeout_seconds}s)"
    
    return TimeoutException(
        message=message,
        code=ErrorCode.TIMEOUT,
        **kwargs
    )
