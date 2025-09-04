## Estructura
```
- main.py
- requirements.txt
- Dockerfile
- .dockerignore
```

**main()**

```python
def main():
    print("🚀 UTEA Notificaciones ejecutándose...")

if __name__ == "__main__":
    main()
```

**requiments.txt**
```bash
pip install -r requirements.txt
```

**Ejecutar en docker**
```bash
# Construir imagen
docker build -t utea-notificaciones-drones .

# Ejecutar contenedor (el ultimo elemento indica la imagen base)
docker run -d --name utea-notificaciones-drones utea-notificaciones-drones

# indicando volumenes
docker run -d --name utea-notificaciones-drones -v C:\Users\bismarksr\Desktop\logs:/app/logs utea-notificaciones-drones

```