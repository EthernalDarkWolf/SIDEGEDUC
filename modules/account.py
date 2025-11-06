from conn import get_connection
from password import generate_password

def register(data):
  con = get_connection()

  c = con.cursor()
  c.execute("SELECT * from user WHERE email = %s", [data['email']])
  res = c.fetchone()

  print(res)

  if res: 
    print('Correo ya existe')
    return
  
  c = con.cursor()

  new_pass = generate_password(data['password'])

  c.execute('INSERT INTO user (email, password, name) VALUES (%s, %s, %s)', [
    data['email'],
    new_pass,
    data['name'],
  ])

  con.commit()

  con.close()
  
  

