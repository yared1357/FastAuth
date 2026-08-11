from fastauth.security.password import BcryptPasswordHasher


def test_bcrypt_password_hashing():
    hasher = BcryptPasswordHasher()
    password = "MySecurePassword123!"

    hashed = hasher.hash(password)
    assert hashed != password
    assert hasher.verify(password, hashed) is True
    assert hasher.verify("WrongPassword", hashed) is False
