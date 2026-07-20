# Aplicación Flutter con SQLite

Esta es una aplicación Flutter de ejemplo que usa SQLite para almacenar notas localmente.

## Archivos creados

- `pubspec.yaml`
- `lib/main.dart`
- `lib/db_helper.dart`
- `lib/note.dart`
- `.gitignore`

## Cómo ejecutar Flutter

1. Instala Flutter desde: https://docs.flutter.dev/get-started/install
2. Abre esta carpeta en VS Code.
3. Ejecuta en la terminal:

```bash
flutter pub get
flutter create .
flutter run
```

Si `flutter create .` genera `android/` e `ios/`, el proyecto estará listo para correr.

## Qué hace la app Flutter

- Crea una base de datos local SQLite llamada `app_db.db`
- Crea una tabla `users` para login y roles
- Crea una tabla `notes` para realizar notas
- Permite:
  - registrar emprendedores y usuarios
  - iniciar sesión con correo y contraseña
  - ver el rol del usuario dentro de la app
  - agregar, editar y eliminar notas

## Backend de pruebas para CRUD

Se añadió una API básica en la carpeta `backend/` para probar operaciones CRUD sobre notas.

### Ejecutar el backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

La API quedará disponible en:

- http://127.0.0.1:5000/api/notes

### Probar los endpoints

- POST /api/notes
- GET /api/notes
- GET /api/notes/<id>
- PUT /api/notes/<id>
- DELETE /api/notes/<id>

### Ejecutar pruebas

```bash
cd backend
pytest -q
```

## Android nativo con SQLite

También agregué un ejemplo nativo en la carpeta `android_native/`.

Para abrirlo, usa Android Studio o un proyecto Gradle en esa carpeta.

### Archivos importantes

- `android_native/settings.gradle`
- `android_native/build.gradle`
- `android_native/app/build.gradle`
- `android_native/app/src/main/java/com/example/androidnativeapp/MainActivity.kt`
- `android_native/app/src/main/java/com/example/androidnativeapp/DBHelper.kt`
- `android_native/app/src/main/java/com/example/androidnativeapp/Note.kt`
- `android_native/app/src/main/res/layout/activity_main.xml`
- `android_native/app/src/main/res/values/strings.xml`
- `android_native/app/src/main/AndroidManifest.xml`

### Cómo ejecutar Android nativo

1. Abre la carpeta `android_native` en Android Studio.
2. Sincroniza el proyecto.
3. Ejecuta en un emulador o dispositivo.

> Si Android Studio necesita el `gradle-wrapper.jar`, puedes generar el wrapper o usar Gradle instalado localmente.

Para la guía de desarrollo de la Semana 6, consulta `GUIDE.md`.
