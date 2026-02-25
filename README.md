> 🌧 Versión actual: ^1.2.2

<h1 align="center">SIDEGEDUC</p>
<p>
        <img src= "https://files.catbox.moe/p4nvmh.jpg">
    </p>

---

## Descripción

SIDEGEDUC Es un Sistema en desarrollo constante de entorno local basado en lenguage `Python` junto al framework `Flask` y base de datos `SQLITE`, SIGEDUC ofrece una gestion y automatizacion de procesos de ente educativo como inscripciones, reparticion de secciones, boletas, junto  consultas de informacion y reportes por el momento.

---

### **`Requerimientos:`**
<a href="https://youtube.com/@lobito_sangriento?si=zYhM0krfxzz60Mvb">

  <img width="180px" src="https://files.catbox.moe/nm5i3h.jpeg"/>
</a>

<details>
 <summary><b>Requisistos Minimos: </b></summary>

- **Windows 7 x64 Service pack 2**
- **Python 3.8.10 x64**
- **Git v2.46.2 x64** 

</details>

--- 



### **`💣 Instalación`**

<details>
 <summary><b>🖤 Pasos a Realizar</b></summary>

### Python v3.8.10 x64 [Descargalo Aqui](https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe)

> ### `Importante:` 
*Asegurese de marcar la casilla `add python to path` antes iniciar la instalación, luego de marcar la casilla prosiga a presionar `Install Now`*

<img src="https://files.catbox.moe/d7uek0.webp" alt="Fuente: Andueza, Morales, Uzcategui" style="width: 100%; height: auto; max-width: 500px;">

> ### Git v2.46.2 x64 [Descargalo Aqui](https://release-assets.githubusercontent.com/github-production-release-asset/23216272/330a0c8f-8571-4b77-b17e-f7b3d5953ee2?sp=r&sv=2018-11-09&sr=b&spr=https&se=2026-02-24T16%3A25%3A13Z&rscd=attachment%3B+filename%3DGit-2.46.2-64-bit.exe&rsct=application%2Foctet-stream&skoid=96c2d410-5711-43a1-aedd-ab1947aa7ab0&sktid=398a6654-997b-47e9-b12b-9515b896b4de&skt=2026-02-24T15%3A25%3A11Z&ske=2026-02-24T16%3A25%3A13Z&sks=b&skv=2018-11-09&sig=DkW4o1Uzct4eoKKi7v%2FHDeOCuiPHKZZnKG5hUkRJWYQ%3D&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmVsZWFzZS1hc3NldHMuZ2l0aHVidXNlcmNvbnRlbnQuY29tIiwia2V5Ijoia2V5MSIsImV4cCI6MTc3MTk0ODc1NCwibmJmIjoxNzcxOTQ2OTU0LCJwYXRoIjoicmVsZWFzZWFzc2V0cHJvZHVjdGlvbi5ibG9iLmNvcmUud2luZG93cy5uZXQifQ.lojw9HDJUAb2oqtF6AWsW0Oodqkw0LcE6yhKdw4SViA&response-content-disposition=attachment%3B%20filename%3DGit-2.46.2-64-bit.exe&response-content-type=application%2Foctet-stream)

> ### `CMDER:` [Descargalo Aqui](https://release-assets.githubusercontent.com/github-production-release-asset/11276147/81416a25-87a1-470b-8569-c6e0bb2b52a5?sp=r&sv=2018-11-09&sr=b&spr=https&se=2026-02-25T17%3A43%3A56Z&rscd=attachment%3B+filename%3Dcmder.zip&rsct=application%2Foctet-stream&skoid=96c2d410-5711-43a1-aedd-ab1947aa7ab0&sktid=398a6654-997b-47e9-b12b-9515b896b4de&skt=2026-02-25T16%3A43%3A17Z&ske=2026-02-25T17%3A43%3A56Z&sks=b&skv=2018-11-09&sig=rVI1eDMgDjRsUdOIiI7FJ62ThSQYG5jgAV9AW5G%2BbsE%3D&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmVsZWFzZS1hc3NldHMuZ2l0aHVidXNlcmNvbnRlbnQuY29tIiwia2V5Ijoia2V5MSIsImV4cCI6MTc3MjA0MjM2MiwibmJmIjoxNzcyMDM4NzYyLCJwYXRoIjoicmVsZWFzZWFzc2V0cHJvZHVjdGlvbi5ibG9iLmNvcmUud2luZG93cy5uZXQifQ.ZBrkQjBPAmnuurAusPTczvw--GFVNHfsDxfi-ODZxJ0&response-content-disposition=attachment%3B%20filename%3Dcmder.zip&response-content-type=application%2Foctet-stream) (desconprima el archivo zip despues de descargarlo)

> Nota: Dirijase a la carpeta que se creo al descomprimir cmder y ejecute cmder.exe

*ejemplo:*
<img src="https://files.catbox.moe/lcci9c.png" alt= "Fuente: Andueza, Morales, Uzcategui">

> ### Copie y pege los siguientes comandos en cmder uno por uno

```bash
cd C:/ && git clone https://github.com/Technolobito/SIDEGEDUC.git && cd C:/SIDEGEDUC && python -m venv venv
```

```bash
venv/Scripts/activate.bat && pip install flask && pip install python-dotenv && pip install flask-sqlalchemy
```

```bash
py app.py
```
> ### Cada Que quieras encender el sistema en cmder pega el siguiente comando y ejecutalo:

```bash
cd C:/SIDEGEDUC && venv/Scripts/activate.bat && py app.py
```

</details>

---

### **`🪐Equipo de desarrallo`**
<a href="https://github.com/endanli78">
<img src="https://github.com/endanli78.png" width="50px" style="border-radius: 50%;" alt="Endanli Uzgategui(Database Designer)" title="Endanli Uzgategui — Database Designer">
</a> 
<a href="https://github.com/carmenmorana21-code">
<img src="https://github.com/carmenmorana21-code.png" width="50px" style="border-radius: 50%;" alt="Carmen Morales(Dev Backend)" title="Carmen Morales — Dev Backend">
</a>
<a href="https://github.com/Anduezajavierale">
<img src="https://github.com/Anduezajavierale.png" width="50px" style= "border-radius: 50%;" alt="Javier Andueza(Dev Frontend)" title="Javier Andueza — Dev Frontend">
</a>

### **`👑 Lider Técnico`**
<a href="https://github.com/Technolobito"><img src="https://github.com/Technolobito.png" width="130" height="130" alt="Anthony parada" title="Anthony Parada — Líder Técnico"/></a>

## **`⭐ CRÉDITOS`**
<a href="https://github.com/Nmaker19"><img src="https://github.com/Nmaker19.png" width="130" height="130" alt="Noel Rodriguez(Mi Honorable Maestro)" title="Noel Rodriguez — Mi Honorable Maestro"/></a>
