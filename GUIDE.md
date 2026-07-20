# Guía de desarrollo Semana 6 - CRUD del módulo de notas

Como parte del práctico experimental de la Semana 6, se aplican los conceptos de operaciones CRUD, diseño de endpoints REST, validación de datos, reglas de negocio y manejo estructurado de errores sobre la base de datos actual del proyecto.

## Objetivo
Diseñar, implementar y probar las operaciones CRUD de la entidad principal del proyecto, usando como referencia la estructura actual de SQLite y la lógica de la aplicación móvil.

## Entidad principal seleccionada
La entidad principal seleccionada para esta guía es la tabla de notas, ya que representa el núcleo de la experiencia de uso de la aplicación: crear, listar, editar y eliminar contenido desde la pantalla principal.

### Estructura actual de la base de datos
El proyecto ya define las siguientes tablas en [lib/db_helper.dart](lib/db_helper.dart):

- users
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - name: TEXT NOT NULL
  - email: TEXT NOT NULL UNIQUE
  - password: TEXT NOT NULL
  - role: TEXT NOT NULL

- notes
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - title: TEXT NOT NULL
  - content: TEXT NOT NULL
  - createdAt: INTEGER NOT NULL

La clase [lib/note.dart](lib/note.dart) representa el modelo de la entidad notes, mientras que la pantalla principal en [lib/main.dart](lib/main.dart) consume esas operaciones desde la interfaz móvil.

## Diseño de endpoints RESTful
Para el backend, se propone la siguiente estructura de rutas:

| Método | Ruta | Descripción |
|---|---|---|
| POST | /api/notes | Crear una nueva nota |
| GET | /api/notes | Listar notas con paginación |
| GET | /api/notes/{id} | Consultar una nota específica |
| PUT | /api/notes/{id} | Actualizar completamente una nota |
| DELETE | /api/notes/{id} | Eliminar una nota |

### Justificación del uso de métodos
- Se utilizará POST para la creación.
- Se utilizará GET para listar y consultar.
- Se utilizará PUT para la actualización completa de una nota.
- Se utilizará DELETE para eliminar el registro.
- No se implementará PATCH en esta primera versión, porque la entidad es simple y la actualización completa cubre el flujo requerido por la app.

## Operación Create
### Endpoint
- POST /api/notes

### Datos esperados
```json
{
  "title": "Plan de marketing",
  "content": "Definir los objetivos y presupuesto para la próxima semana",
  "createdAt": 1710000000000
}
```

### Validaciones
- title: obligatorio, cadena de texto, longitud mínima 3 y máxima 100.
- content: obligatorio, cadena de texto, longitud mínima 1 y máxima 1000.
- createdAt: obligatorio, debe enviarse como timestamp en milisegundos.

### Regla de negocio
- No se permite crear una nota sin título ni sin contenido.
- La fecha de creación se asigna automáticamente al momento de guardar el registro y no debe modificarse desde la interfaz cliente.

### Código de respuesta esperado
- 201 Created si la nota se guarda correctamente.
- 400 Bad Request si los datos son inválidos.
- 500 Internal Server Error si ocurre un error inesperado.

## Operación Read
### Listar notas con paginación
- GET /api/notes?page=1&limit=10

### Respuesta esperada
```json
{
  "success": true,
  "message": "Notas consultadas correctamente",
  "data": [
    {
      "id": 1,
      "title": "Plan de marketing",
      "content": "Definir los objetivos y presupuesto",
      "createdAt": 1710000000000
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 1
  }
}
```

### Consultar una nota específica
- GET /api/notes/{id}

### Código de respuesta esperado
- 200 OK si existe la nota.
- 404 Not Found si no existe.

## Operación Update
### Endpoint
- PUT /api/notes/{id}

### Datos esperados
```json
{
  "title": "Plan de marketing actualizado",
  "content": "Se ajustaron los objetivos y se agregó el presupuesto",
  "createdAt": 1710000000000
}
```

### Validaciones
- Se deben validar nuevamente title y content.
- Si no existe la nota, debe responderse con 404.
- Si el cuerpo está incompleto o inválido, debe responderse con 400.

## Operación Delete
### Endpoint
- DELETE /api/notes/{id}

### Tipo de eliminación
Se recomienda aplicar una eliminación física, porque la tabla actual no incluye un campo como isDeleted, deletedAt o estado. Esto mantiene la implementación simple y coherente con la estructura actual de SQLite.

### Código de respuesta esperado
- 200 OK si se elimina correctamente.
- 404 Not Found si la nota no existe.

## Respuestas JSON estandarizadas
Se recomienda usar una estructura uniforme para éxito y error.

### Respuesta exitosa
```json
{
  "success": true,
  "message": "Nota creada correctamente",
  "data": {
    "id": 1,
    "title": "Plan de marketing",
    "content": "Definir los objetivos y presupuesto",
    "createdAt": 1710000000000
  }
}
```

### Respuesta de error
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "El título es obligatorio"
  }
}
```

## Casos de prueba recomendados
Se pueden probar con Postman o Insomnia:

1. Crear una nota con datos válidos.
2. Intentar crear una nota sin título.
3. Consultar el listado paginado.
4. Consultar una nota existente y otra inexistente.
5. Actualizar una nota con datos válidos.
6. Intentar actualizar una nota que no existe.
7. Eliminar una nota existente.
8. Intentar eliminar una nota inexistente.

## Pantallas o funcionalidades de la app móvil que consumirán estos endpoints
- Pantalla principal de notas: mostrará el listado de notas.
- Diálogo de creación y edición: enviará los datos para crear o actualizar una nota.
- Opción de eliminar: consumirá el endpoint DELETE al quitar una nota desde la lista.

## Riesgos de seguridad identificados
1. Inyección SQL o manipulación de datos.
   - Medida: usar consultas parametrizadas y validar todos los campos de entrada.
2. Acceso no autorizado a recursos.
   - Medida: implementar autenticación y autorización para que solo un usuario registrado pueda modificar sus propias notas.

## Oportunidades de optimización
- Implementar paginación real para evitar cargar demasiados registros en una sola respuesta.
- Agregar índices sobre campos de búsqueda y ordenación como createdAt.
- Reutilizar validaciones en un módulo común para evitar duplicación.
- En una versión posterior, asociar cada nota a un usuario mediante una relación user_id.

## Uso de inteligencia artificial
No se utilizó IA en esta guía. Si en una siguiente iteración se emplea una herramienta de IA, debe registrarse:
- herramienta usada,
- prompt realizado,
- resultado utilizado,
- modificaciones aplicadas,
- y verificación técnica realizada.

## Conclusión
La implementación propuesta mantiene coherencia con la base de datos actual del proyecto y prepara el camino para una futura integración backend con autenticación, seguridad y consumo desde la aplicación móvil.
