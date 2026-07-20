# Guía de Integración - Aplicación Móvil con Backend Seguro

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Flujos de Pantalla](#flujos-de-pantalla)
3. [Implementación en Flutter](#implementación-en-flutter)
4. [Implementación en Android Nativo](#implementación-en-android-nativo)
5. [Manejo de Tokens](#manejo-de-tokens)
6. [Manejo de Errores](#manejo-de-errores)
7. [Testing](#testing)

---

## Descripción General

La aplicación móvil interactúa con el backend mediante:
- **Autenticación**: JWT con access token y refresh token
- **Almacenamiento seguro**: Tokens guardados en secure storage
- **Comunicación**: HTTPS en producción
- **Headers**: `Authorization: Bearer <TOKEN>` en todas las solicitudes protegidas

---

## Flujos de Pantalla

### Flujo de Autenticación

```
┌─────────────────┐
│  Splash Screen  │
│  (Verificar     │
│   token local)  │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Token   │
    │ válido? │
    └────┬────┘
    ┌────┴──────┬───────────┐
    │ SÍ        │ NO        │
    │           │           │
    ▼           ▼           ▼
┌────────┐ ┌──────────┐ ┌──────────┐
│ Inicio│ │  Login   │ │ Register │
│ Notas │ │  Screen  │ │ Screen   │
└────────┘ └──┬───────┘ └───┬──────┘
              │             │
              │             │
         ┌────▼─────────────▼───┐
         │  POST /api/auth/login│
         │  POST /api/auth/reg  │
         └────────┬─────────────┘
                  │
           ┌──────▼──────┐
           │ Éxito?      │
           └──┬───────┬──┘
          SÍ │       │ NO
             │       │
          ┌──▼──┐ ┌──▼────────────┐
          │Guardar│ │Mostrar error │
          │Token │ │y reintentar  │
          └──┬──┘ └─────────────┘
             │
             ▼
         ┌────────┐
         │ Inicio │
         │ Notas  │
         └────────┘
```

### Flujo de Notas

```
┌─────────────────────────────┐
│      Pantalla Inicial       │
│  (Listar Notas del Usuario) │
└────────────┬────────────────┘
             │
     ┌───────┼───────┐
     │       │       │
     ▼       ▼       ▼
  ┌──────┐┌──────┐┌──────┐
  │Crear ││ Ver  ││Editar│
  │ Nota ││ Nota ││ Nota │
  └──┬───┘└──┬───┘└──┬───┘
     │       │       │
     ▼       ▼       ▼
  POST   GET      PUT
  /api/  /api/    /api/
  notes  notes/:id notes/:id
```

---

## Implementación en Flutter

### 1. Dependencias (pubspec.yaml)

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  flutter_secure_storage: ^9.0.0
  shared_preferences: ^2.2.0
  dio: ^5.3.0  # Alternative to http
  jwt_decoder: ^2.0.1
```

### 2. Servicio de Autenticación

```dart
// lib/services/auth_service.dart

import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';

const String BASE_URL = 'http://localhost:5000/api';
const String ACCESS_TOKEN_KEY = 'access_token';
const String REFRESH_TOKEN_KEY = 'refresh_token';

class AuthService {
  final _secureStorage = const FlutterSecureStorage();
  
  // REGISTRO
  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$BASE_URL/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 201) {
        // Guardar tokens en secure storage
        await _secureStorage.write(
          key: ACCESS_TOKEN_KEY,
          value: data['data']['access_token'],
        );
        await _secureStorage.write(
          key: REFRESH_TOKEN_KEY,
          value: data['data']['refresh_token'],
        );
        
        return {'success': true, 'user_id': data['data']['user_id']};
      } else if (response.statusCode == 409) {
        return {
          'success': false,
          'error': 'El email ya está registrado'
        };
      } else if (response.statusCode == 400) {
        return {
          'success': false,
          'error': data['error']['message'] ?? 'Datos inválidos'
        };
      }
      
      return {'success': false, 'error': 'Error desconocido'};
    } catch (e) {
      return {'success': false, 'error': 'Error de conexión: $e'};
    }
  }

  // LOGIN
  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$BASE_URL/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        await _secureStorage.write(
          key: ACCESS_TOKEN_KEY,
          value: data['data']['access_token'],
        );
        await _secureStorage.write(
          key: REFRESH_TOKEN_KEY,
          value: data['data']['refresh_token'],
        );
        
        return {'success': true, 'user_id': data['data']['user_id']};
      } else if (response.statusCode == 401) {
        return {
          'success': false,
          'error': 'Email o contraseña incorrectos'
        };
      }
      
      return {'success': false, 'error': 'Error de login'};
    } catch (e) {
      return {'success': false, 'error': 'Error de conexión: $e'};
    }
  }

  // OBTENER TOKEN
  Future<String?> getAccessToken() async {
    return await _secureStorage.read(key: ACCESS_TOKEN_KEY);
  }

  // RENOVAR TOKEN
  Future<bool> refreshToken() async {
    try {
      final refreshToken = await _secureStorage.read(key: REFRESH_TOKEN_KEY);
      
      if (refreshToken == null) return false;

      final response = await http.post(
        Uri.parse('$BASE_URL/auth/refresh'),
        headers: {
          'Authorization': 'Bearer $refreshToken',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await _secureStorage.write(
          key: ACCESS_TOKEN_KEY,
          value: data['data']['access_token'],
        );
        return true;
      }
      
      return false;
    } catch (e) {
      return false;
    }
  }

  // LOGOUT
  Future<void> logout() async {
    try {
      final accessToken = await getAccessToken();
      if (accessToken != null) {
        await http.post(
          Uri.parse('$BASE_URL/auth/logout'),
          headers: {
            'Authorization': 'Bearer $accessToken',
          },
        );
      }
    } finally {
      await _secureStorage.delete(key: ACCESS_TOKEN_KEY);
      await _secureStorage.delete(key: REFRESH_TOKEN_KEY);
    }
  }
}
```

### 3. Servicio de Notas

```dart
// lib/services/notes_service.dart

class NotesService {
  final AuthService _authService = AuthService();

  // CREAR NOTA
  Future<Map<String, dynamic>> createNote({
    required String title,
    required String content,
  }) async {
    try {
      final token = await _authService.getAccessToken();
      
      if (token == null) {
        return {'success': false, 'error': 'No autenticado'};
      }

      final response = await http.post(
        Uri.parse('$BASE_URL/notes'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'title': title,
          'content': content,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 201) {
        return {'success': true, 'note': data['data']};
      } else if (response.statusCode == 401) {
        // Token expirado, renovar
        final refreshed = await _authService.refreshToken();
        if (refreshed) {
          return createNote(title: title, content: content);
        }
        return {'success': false, 'error': 'Sesión expirada'};
      } else if (response.statusCode == 409) {
        return {
          'success': false,
          'error': 'Ya existe una nota con ese título'
        };
      } else if (response.statusCode == 400) {
        return {
          'success': false,
          'error': data['error']['message'] ?? 'Datos inválidos'
        };
      }

      return {'success': false, 'error': 'Error desconocido'};
    } catch (e) {
      return {'success': false, 'error': 'Error: $e'};
    }
  }

  // LISTAR NOTAS
  Future<Map<String, dynamic>> listNotes({
    int page = 1,
    int limit = 10,
  }) async {
    try {
      final token = await _authService.getAccessToken();
      
      if (token == null) {
        return {'success': false, 'error': 'No autenticado'};
      }

      final response = await http.get(
        Uri.parse('$BASE_URL/notes?page=$page&limit=$limit'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'notes': data['data'],
          'pagination': data['pagination'],
        };
      } else if (response.statusCode == 401) {
        final refreshed = await _authService.refreshToken();
        if (refreshed) {
          return listNotes(page: page, limit: limit);
        }
        return {'success': false, 'error': 'Sesión expirada'};
      }

      return {'success': false, 'error': 'Error al listar notas'};
    } catch (e) {
      return {'success': false, 'error': 'Error: $e'};
    }
  }

  // ACTUALIZAR NOTA
  Future<Map<String, dynamic>> updateNote({
    required int noteId,
    required String title,
    required String content,
  }) async {
    try {
      final token = await _authService.getAccessToken();
      
      if (token == null) {
        return {'success': false, 'error': 'No autenticado'};
      }

      final response = await http.put(
        Uri.parse('$BASE_URL/notes/$noteId'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'title': title,
          'content': content,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return {'success': true, 'note': data['data']};
      } else if (response.statusCode == 403) {
        return {'success': false, 'error': 'No tienes permisos'};
      } else if (response.statusCode == 404) {
        return {'success': false, 'error': 'Nota no encontrada'};
      } else if (response.statusCode == 401) {
        final refreshed = await _authService.refreshToken();
        if (refreshed) {
          return updateNote(noteId: noteId, title: title, content: content);
        }
        return {'success': false, 'error': 'Sesión expirada'};
      }

      return {'success': false, 'error': 'Error al actualizar'};
    } catch (e) {
      return {'success': false, 'error': 'Error: $e'};
    }
  }

  // ELIMINAR NOTA
  Future<Map<String, dynamic>> deleteNote(int noteId) async {
    try {
      final token = await _authService.getAccessToken();
      
      if (token == null) {
        return {'success': false, 'error': 'No autenticado'};
      }

      final response = await http.delete(
        Uri.parse('$BASE_URL/notes/$noteId'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return {'success': true};
      } else if (response.statusCode == 403) {
        return {'success': false, 'error': 'No tienes permisos'};
      } else if (response.statusCode == 404) {
        return {'success': false, 'error': 'Nota no encontrada'};
      } else if (response.statusCode == 401) {
        final refreshed = await _authService.refreshToken();
        if (refreshed) {
          return deleteNote(noteId);
        }
        return {'success': false, 'error': 'Sesión expirada'};
      }

      return {'success': false, 'error': 'Error al eliminar'};
    } catch (e) {
      return {'success': false, 'error': 'Error: $e'};
    }
  }
}
```

### 4. Pantalla de Login

```dart
// lib/screens/login_screen.dart

class LoginScreen extends StatefulWidget {
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _authService = AuthService();
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Iniciar Sesión')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _emailController,
              decoration: InputDecoration(
                labelText: 'Email',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
            SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(
                labelText: 'Contraseña',
                border: OutlineInputBorder(),
              ),
              obscureText: true,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isLoading ? null : _handleLogin,
              child: _isLoading
                  ? CircularProgressIndicator()
                  : Text('Iniciar Sesión'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _handleLogin() async {
    setState(() => _isLoading = true);

    final result = await _authService.login(
      email: _emailController.text,
      password: _passwordController.text,
    );

    setState(() => _isLoading = false);

    if (result['success']) {
      Navigator.of(context).pushReplacementNamed('/notes');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['error'])),
      );
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
}
```

---

## Implementación en Android Nativo

### 1. Servicio de Autenticación

```kotlin
// AuthService.kt

package com.example.androidnativeapp

import android.content.Context
import android.content.SharedPreferences
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.URL
import java.nio.charset.StandardCharsets

const val BASE_URL = "http://localhost:5000/api"
const val PREFS_NAME = "secure_prefs"
const val ACCESS_TOKEN_KEY = "access_token"
const val REFRESH_TOKEN_KEY = "refresh_token"

class AuthService(private val context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences(
        PREFS_NAME,
        Context.MODE_PRIVATE
    )

    suspend fun register(email: String, password: String): AuthResult {
        return withContext(Dispatchers.IO) {
            try {
                val url = URL("$BASE_URL/auth/register")
                val connection = url.openConnection() as java.net.HttpURLConnection
                connection.requestMethod = "POST"
                connection.setRequestProperty("Content-Type", "application/json")
                connection.doOutput = true

                val body = JSONObject().apply {
                    put("email", email)
                    put("password", password)
                }

                connection.outputStream.write(body.toString().toByteArray(StandardCharsets.UTF_8))

                val responseCode = connection.responseCode
                val response = connection.inputStream.bufferedReader().readText()
                val data = JSONObject(response)

                when (responseCode) {
                    201 -> {
                        val tokens = data.getJSONObject("data")
                        saveTokens(
                            tokens.getString("access_token"),
                            tokens.getString("refresh_token")
                        )
                        AuthResult.Success(tokens.getInt("user_id"))
                    }
                    409 -> AuthResult.Error("Email ya registrado")
                    400 -> AuthResult.Error("Datos inválidos")
                    else -> AuthResult.Error("Error desconocido")
                }
            } catch (e: Exception) {
                AuthResult.Error("Error: ${e.message}")
            }
        }
    }

    suspend fun login(email: String, password: String): AuthResult {
        return withContext(Dispatchers.IO) {
            try {
                val url = URL("$BASE_URL/auth/login")
                val connection = url.openConnection() as java.net.HttpURLConnection
                connection.requestMethod = "POST"
                connection.setRequestProperty("Content-Type", "application/json")
                connection.doOutput = true

                val body = JSONObject().apply {
                    put("email", email)
                    put("password", password)
                }

                connection.outputStream.write(body.toString().toByteArray(StandardCharsets.UTF_8))

                val responseCode = connection.responseCode
                val response = connection.inputStream.bufferedReader().readText()
                val data = JSONObject(response)

                when (responseCode) {
                    200 -> {
                        val tokens = data.getJSONObject("data")
                        saveTokens(
                            tokens.getString("access_token"),
                            tokens.getString("refresh_token")
                        )
                        AuthResult.Success(tokens.getInt("user_id"))
                    }
                    401 -> AuthResult.Error("Credenciales incorrectas")
                    else -> AuthResult.Error("Error desconocido")
                }
            } catch (e: Exception) {
                AuthResult.Error("Error: ${e.message}")
            }
        }
    }

    fun getAccessToken(): String? = prefs.getString(ACCESS_TOKEN_KEY, null)

    private fun saveTokens(accessToken: String, refreshToken: String) {
        prefs.edit().apply {
            putString(ACCESS_TOKEN_KEY, accessToken)
            putString(REFRESH_TOKEN_KEY, refreshToken)
            apply()
        }
    }

    suspend fun logout() {
        val accessToken = getAccessToken()
        if (accessToken != null) {
            withContext(Dispatchers.IO) {
                try {
                    val url = URL("$BASE_URL/auth/logout")
                    val connection = url.openConnection() as java.net.HttpURLConnection
                    connection.requestMethod = "POST"
                    connection.setRequestProperty("Authorization", "Bearer $accessToken")
                    connection.connect()
                } catch (e: Exception) {
                    // Log error
                }
            }
        }
        
        prefs.edit().apply {
            remove(ACCESS_TOKEN_KEY)
            remove(REFRESH_TOKEN_KEY)
            apply()
        }
    }

    sealed class AuthResult {
        data class Success(val userId: Int) : AuthResult()
        data class Error(val message: String) : AuthResult()
    }
}
```

---

## Manejo de Tokens

### Almacenamiento Seguro

```dart
// Flutter: Utilizar flutter_secure_storage
final secureStorage = FlutterSecureStorage();
await secureStorage.write(key: 'token', value: token);

// Android Nativo: Utilizar SharedPreferences o EncryptedSharedPreferences
val encryptedSharedPreferences = EncryptedSharedPreferences.create(...)
encryptedSharedPreferences.edit().putString("token", token).apply()
```

### Renovación Automática de Token

```dart
// Interceptor automático para Dio
dio.interceptors.add(
  InterceptorsWrapper(
    onRequest: (options, handler) async {
      final token = await authService.getAccessToken();
      options.headers['Authorization'] = 'Bearer $token';
      return handler.next(options);
    },
    onError: (error, handler) async {
      if (error.response?.statusCode == 401) {
        final refreshed = await authService.refreshToken();
        if (refreshed) {
          return handler.resolve(await dio.request(
            error.requestOptions.path,
            options: RequestOptions(
              method: error.requestOptions.method,
            ),
          ));
        }
      }
      return handler.next(error);
    },
  ),
);
```

---

## Manejo de Errores

### Errores Comunes

| Código | Error | Solución |
|--------|-------|----------|
| 400 | Bad Request | Validar datos enviados |
| 401 | Unauthorized | Renovar token o re-autenticar |
| 403 | Forbidden | No tiene permisos para esta acción |
| 404 | Not Found | Recurso no existe |
| 409 | Conflict | Duplicado (ej: email o título) |
| 422 | Unprocessable Entity | Token inválido |
| 500 | Server Error | Error en servidor |

### Estrategia de Reintentos

```dart
Future<T> retryWithExponentialBackoff<T>(
  Future<T> Function() request, {
  int maxRetries = 3,
}) async {
  int retries = 0;
  
  while (retries < maxRetries) {
    try {
      return await request();
    } catch (e) {
      retries++;
      if (retries >= maxRetries) rethrow;
      
      // Esperar con backoff exponencial
      await Future.delayed(Duration(milliseconds: 100 * (2 ^ retries)));
    }
  }
  
  throw Exception('Max retries exceeded');
}
```

---

## Testing

### Tests de Autenticación

```dart
// test/auth_service_test.dart

void main() {
  group('AuthService', () {
    test('register should save tokens', () async {
      final authService = AuthService();
      
      final result = await authService.register(
        email: 'test@example.com',
        password: 'SecurePass123!',
      );
      
      expect(result['success'], true);
      
      final token = await authService.getAccessToken();
      expect(token, isNotNull);
    });

    test('login with invalid credentials should fail', () async {
      final authService = AuthService();
      
      final result = await authService.login(
        email: 'test@example.com',
        password: 'WrongPassword',
      );
      
      expect(result['success'], false);
      expect(result['error'], isNotNull);
    });
  });
}
```

---

## Resumen

1. **Registrar usuario**: POST /api/auth/register → Guardar tokens
2. **Login**: POST /api/auth/login → Guardar tokens
3. **Acceder a recursos**: Incluir `Authorization: Bearer <TOKEN>` en headers
4. **Token expirado**: POST /api/auth/refresh para renovar
5. **Logout**: POST /api/auth/logout → Eliminar tokens locales

Todos los tokens se guardan en **secure storage** y se incluyen automáticamente en las solicitudes.

