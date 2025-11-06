import bcrypt

def generate_password(password, rounds=8):
  password = password.encode('utf-8')  # Encode password to bytes
  salt = bcrypt.gensalt(rounds)
  hashed_password = bcrypt.hashpw(password, salt)
  return hashed_password

def compare_password(pass1, hashed_password):
  return bcrypt.checkpw(pass1.encode('utf-8'), hashed_password)
