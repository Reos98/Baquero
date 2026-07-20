# Android Nativo con SQLite

Este ejemplo muestra cómo guardar notas usando SQLite en Android nativo con Kotlin.

## Estructura

- `android_native/settings.gradle`
- `android_native/build.gradle`
- `android_native/app/build.gradle`
- `android_native/app/src/main/java/com/example/androidnativeapp/MainActivity.kt`
- `android_native/app/src/main/java/com/example/androidnativeapp/DBHelper.kt`
- `android_native/app/src/main/java/com/example/androidnativeapp/Note.kt`
- `android_native/app/src/main/res/layout/activity_main.xml`
- `android_native/app/src/main/res/values/strings.xml`
- `android_native/app/src/main/AndroidManifest.xml`

## Cómo ejecutar

1. Abre `android_native` en Android Studio.
2. Sincroniza el proyecto.
3. Ejecuta la app en un emulador o dispositivo.

## Qué hace la app

- Crea una base de datos local SQLite llamada `app_db.db`.
- Inserta, actualiza y elimina notas.
- Muestra las notas en una lista.

> Si Android Studio te pide el `gradle-wrapper.jar`, puedes generar el wrapper desde Android Studio o usar Gradle instalado localmente.
