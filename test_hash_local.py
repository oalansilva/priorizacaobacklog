import hashlib
from passlib.context import CryptContext

# Test the exact configuration
PWD_CONTEXT = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",
    bcrypt__rounds=12,
)

def _pre_hash(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def get_password_hash(password):
    return PWD_CONTEXT.hash(_pre_hash(password))

# Test with short password
test_password = "abc"
print(f"Testing password: {test_password}")
print(f"Pre-hash: {_pre_hash(test_password)}")

try:
    hashed = get_password_hash(test_password)
    print(f"Success! Hashed: {hashed[:50]}...")
except Exception as e:
    print(f"Error: {e}")
