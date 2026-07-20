package com.example.androidnativeapp

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

class DBHelper(context: Context) : SQLiteOpenHelper(context, DB_NAME, null, DB_VERSION) {

    companion object {
        private const val DB_NAME = "app_db.db"
        private const val DB_VERSION = 1
        private const val TABLE_NOTES = "notes"
        private const val COLUMN_ID = "id"
        private const val COLUMN_TITLE = "title"
        private const val COLUMN_CONTENT = "content"
        private const val COLUMN_CREATED_AT = "createdAt"
    }

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            """
            CREATE TABLE $TABLE_NOTES(
                $COLUMN_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                $COLUMN_TITLE TEXT NOT NULL,
                $COLUMN_CONTENT TEXT NOT NULL,
                $COLUMN_CREATED_AT INTEGER NOT NULL
            )
            """.trimIndent()
        )
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS $TABLE_NOTES")
        onCreate(db)
    }

    fun insertNote(note: Note): Long {
        val db = writableDatabase
        val values = ContentValues().apply {
            put(COLUMN_TITLE, note.title)
            put(COLUMN_CONTENT, note.content)
            put(COLUMN_CREATED_AT, note.createdAt)
        }
        return db.insert(TABLE_NOTES, null, values)
    }

    fun getNotes(): List<Note> {
        val db = readableDatabase
        val cursor = db.query(
            TABLE_NOTES,
            null,
            null,
            null,
            null,
            null,
            "$COLUMN_CREATED_AT DESC"
        )

        val notes = mutableListOf<Note>()
        with(cursor) {
            while (moveToNext()) {
                notes.add(
                    Note(
                        id = getInt(getColumnIndexOrThrow(COLUMN_ID)),
                        title = getString(getColumnIndexOrThrow(COLUMN_TITLE)),
                        content = getString(getColumnIndexOrThrow(COLUMN_CONTENT)),
                        createdAt = getLong(getColumnIndexOrThrow(COLUMN_CREATED_AT))
                    )
                )
            }
            close()
        }
        return notes
    }

    fun updateNote(note: Note): Int {
        val db = writableDatabase
        val values = ContentValues().apply {
            put(COLUMN_TITLE, note.title)
            put(COLUMN_CONTENT, note.content)
            put(COLUMN_CREATED_AT, note.createdAt)
        }
        return db.update(
            TABLE_NOTES,
            values,
            "$COLUMN_ID = ?",
            arrayOf(note.id.toString())
        )
    }

    fun deleteNote(id: Int): Int {
        val db = writableDatabase
        return db.delete(TABLE_NOTES, "$COLUMN_ID = ?", arrayOf(id.toString()))
    }
}
