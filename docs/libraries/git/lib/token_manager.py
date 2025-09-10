#!/usr/bin/env python3
"""Token management for review-based operations."""

import os
import time
import hashlib
import json
from pathlib import Path


class TokenManager:
    """Manage time-limited review tokens."""
    
    def __init__(self, namespace="git"):
        """Initialize with a namespace for tokens."""
        self.namespace = namespace
        self.token_dir = Path.home() / '.cache' / 'ry-next' / 'tokens'
        self.token_dir.mkdir(parents=True, exist_ok=True)
        self.token_file = self.token_dir / f'{namespace}_tokens.json'
        self.ttl = 300  # 5 minutes
    
    def generate_token(self, context: str) -> tuple[str, int]:
        """
        Generate a new token for given context.
        
        Args:
            context: String describing what's being reviewed
        
        Returns:
            (token, expires_in_seconds)
        """
        # Create token from context and time
        timestamp = int(time.time())
        token_data = f"{self.namespace}:{context}:{timestamp}"
        token = hashlib.sha256(token_data.encode()).hexdigest()[:12]
        
        # Store token with expiry
        tokens = self._load_tokens()
        tokens[token] = {
            'created': timestamp,
            'expires': timestamp + self.ttl,
            'context': context
        }
        self._save_tokens(tokens)
        
        return token, self.ttl
    
    def verify_token(self, token: str) -> bool:
        """
        Verify if token is valid and not expired.
        
        Args:
            token: Token to verify
        
        Returns:
            True if valid, False otherwise
        """
        if not token:
            return False
        
        tokens = self._load_tokens()
        
        if token not in tokens:
            return False
        
        token_data = tokens[token]
        now = int(time.time())
        
        if now > token_data['expires']:
            # Token expired, remove it
            del tokens[token]
            self._save_tokens(tokens)
            return False
        
        # Token is valid, remove it (one-time use)
        del tokens[token]
        self._save_tokens(tokens)
        return True
    
    def _load_tokens(self) -> dict:
        """Load tokens from file."""
        if not self.token_file.exists():
            return {}
        
        try:
            with open(self.token_file) as f:
                tokens = json.load(f)
            
            # Clean expired tokens
            now = int(time.time())
            tokens = {k: v for k, v in tokens.items() 
                     if v['expires'] > now}
            
            return tokens
        except:
            return {}
    
    def _save_tokens(self, tokens: dict):
        """Save tokens to file."""
        with open(self.token_file, 'w') as f:
            json.dump(tokens, f, indent=2)


# Convenience functions for command-line use
def generate_review_token(context: str = "staged changes") -> tuple[str, int]:
    """Generate a review token."""
    tm = TokenManager("git")
    return tm.generate_token(context)


def verify_review_token(token: str) -> bool:
    """Verify a review token."""
    tm = TokenManager("git")
    return tm.verify_token(token)


if __name__ == "__main__":
    # Test token generation and verification
    import sys
    token, ttl = generate_review_token("test context")
    print(f"Generated token: {token} (expires in {ttl}s)", file=sys.stderr)
    
    if verify_review_token(token):
        print("Token verified and consumed", file=sys.stderr)
    
    if not verify_review_token(token):
        print("Token invalid (already used)", file=sys.stderr)