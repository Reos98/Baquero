# Secure Notes API - Backend

Backend seguro para aplicación de notas con autenticación JWT, autorización basada en roles y validaciones completas.

## Características

- ✅ **Autenticación JWT**: Access token + Refresh token
- ✅ **Roles y Permisos**: Sistema de control de acceso basado en roles
- ✅ **Validaciones**: Email, contraseña, entrada de datos
- ✅ **Hash seguro**: Contraseñas con bcrypt
- ✅ **Documentación Swagger**: OpenAPI automática
- ✅ **Tests completos**: 50+ casos de prueba
- ✅ **CORS**: Controlado y configurable

## Requisitos

- Python 3.8+
- pip

## Instalación

### 1. Clonar/Descargar el proyecto

```bash
cd backend
```

### 2. Crear ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con valores reales (especialmente JWT_SECRET_KEY)
```

### 5. Ejecutar la aplicación

```bash
python app.py
```

La API estará disponible en: `http://localhost:5000`

## Documentación Swagger

Accede a la documentación interactiva:
- **Swagger UI**: http://localhost:5000/apidocs
- **Swagger JSON**: http://localhost:5000/swagger.json

## Endpoints Rápidos

### Autenticación

```bash
# Registro
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'

# Renovar token
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"

# Logout
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Notas

```bash
# Crear nota
curl -X POST http://localhost:5000/api/notes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Mi nota",
    "content": "Contenido de la nota"
  }'

# Listar notas
curl -X GET "http://localhost:5000/api/notes?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Obtener nota específica
curl -X GET http://localhost:5000/api/notes/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Actualizar nota
curl -X PUT http://localhost:5000/api/notes/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Título actualizado",
    "content": "Contenido actualizado"
  }'

# Eliminar nota
curl -X DELETE http://localhost:5000/api/notes/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Ejecutar Tests

```bash
# Todos los tests
python -m pytest tests/

# Con detalles
python -m pytest tests/ -v

# Coverage
python -m pytest tests/ --cov=app
```

## Estructura del Proyecto

```
backend/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── .env.example          # Variables de entorno
├── notes.db              # Base de datos SQLite
├── SECURITY.md           # Documentación de seguridad
├── README.md             # Este archivo
└── tests/
    └── test_notes_api.py # Suite de tests
```

## Configuración de Seguridad

### Producción
```bash
# .env
FLASK_ENV=production
FLASK_DEBUG=False
JWT_SECRET_KEY=your-super-secure-random-key-here
CORS_ORIGINS=https://yourdomain.com
```

### Desarrollo
```bash
# .env
FLASK_ENV=development
FLASK_DEBUG=True
JWT_SECRET_KEY=dev-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Roles y Permisos

### Usuario (user)
- Ver sus propias notas
- Crear notas
- Editar sus propias notas
- Eliminar sus propias notas

### Administrador (admin)
- Ver todas las notas
- Crear notas
- Editar todas las notas
- Eliminar todas las notas
- Listar usuarios
- Cambiar rol de usuarios

## Códigos de Respuesta

```
200 OK              ✅ Exitoso
201 Created         ✅ Recurso creado
400 Bad Request     ❌ Validación fallida
401 Unauthorized    ❌ Sin autenticación
403 Forbidden       ❌ Sin permisos
404 Not Found       ❌ Recurso no existe
409 Conflict        ❌ Conflicto (ej: duplicado)
422 Unprocessable   ❌ Token inválido
500 Server Error    ❌ Error interno
```

## Variables de Entorno

| Variable | Valor Default | Descripción |
|----------|--------------|-------------|
| `FLASK_ENV` | development | Ambiente (development/production) |
| `FLASK_DEBUG` | True | Modo debug |
| `JWT_SECRET_KEY` | dev-secret-key-change-in-production | Clave para firmar JWT |
| `JWT_ACCESS_TOKEN_EXPIRES` | 3600 | Expiración access token (segundos) |
| `JWT_REFRESH_TOKEN_EXPIRES` | 2592000 | Expiración refresh token (segundos) |
| `DATABASE_URL` | sqlite:///notes.db | URL base de datos |
| `CORS_ORIGINS` | http://localhost:3000 | Orígenes CORS permitidos |

## Integración con App Móvil

### Flutter/Dart

```dart
// Registro
final response = await http.post(
  Uri.parse('http://localhost:5000/api/auth/register'),
  headers: {'Content-Type': 'application/json'},
  body: json.encode({
    'email': email,
    'password': password,
  }),
);

final data = json.decode(response.body);
String accessToken = data['data']['access_token'];
String refreshToken = data['data']['refresh_token'];

// Guardar tokens en secure storage
await FlutterSecureStorage().write(
  key: 'access_token',
  value: accessToken,
);
```

### Headers requeridos

Todos los endpoints protegidos requieren:
```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

## Troubleshooting

### "JWT_SECRET_KEY not found"
Solución: Copiar `.env.example` → `.env` y configurar clave

### "CORS error"
Solución: Actualizar `CORS_ORIGINS` en `.env` con URL del cliente

### "Token has expired"
Solución: Usar endpoint `/api/auth/refresh` para renovar token

### "Insufficient permissions"
Solución: Verificar que el usuario tenga el rol requerido

## Próximos Pasos

1. ✅ Implementar autenticación JWT
2. ✅ Agregar roles y permisos
3. ✅ Crear tests completos
4. ⏳ Integrar con base de datos PostgreSQL
5. ⏳ Agregar logging y monitoreo
6. ⏳ Rate limiting
7. ⏳ 2FA (Two-Factor Authentication)

## Documentación Completa

Ver [SECURITY.md](SECURITY.md) para:
- Arquitectura de seguridad detallada
- Análisis de riesgos
- Flujos de autenticación
- Matriz de control de acceso
- Casos de prueba

## Licencia

MIT
