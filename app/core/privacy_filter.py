import re
from loguru import logger
  
SENSITIVE_PATTERNS = [ 
    (r'\b(?:\d{1,3}\.){3}\d{1,3}\b',          '[IP_REDACTED]'), 
    (r'([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}', '[MAC_REDACTED]'), 
    (r'(?i)password[\s=:]+\S+',                  '[CRED_REDACTED]'), 
    (r'(?i)api[_-]?key[\s=:]+\S+',              '[KEY_REDACTED]'), 
    (r'(?i)ssid[\s=:]+\S+',                     '[SSID_REDACTED]'), 
    (r'(?i)secret[\s=:]+\S+',                   '[SECRET_REDACTED]'), 
] 
  
def sanitize(text: str) -> str: 
    """Strip all sensitive identifiers before sending to cloud LLM.""" 
    result = text 
    for pattern, replacement in SENSITIVE_PATTERNS: 
        result = re.sub(pattern, replacement, result) 
    if result != text: 
        logger.debug('Privacy filter: sensitive data redacted before cloud send') 
    return result
