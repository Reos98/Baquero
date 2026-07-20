package com.example.androidnativeapp

import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var dbHelper: DBHelper
    private lateinit var listView: ListView
    private lateinit var adapter: ArrayAdapter<String>
    private var notes = listOf<Note>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        dbHelper = DBHelper(this)
        listView = findViewById(R.id.listNotes)
        adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, mutableListOf())
        listView.adapter = adapter

        findViewById<Button>(R.id.buttonAdd).setOnClickListener {
            showNoteDialog(null)
        }

        listView.setOnItemClickListener { _, _, position, _ ->
            showNoteDialog(notes[position])
        }

        listView.setOnItemLongClickListener { _, _, position, _ ->
            deleteNote(notes[position])
            true
        }

        refreshNotes()
    }

    private fun refreshNotes() {
        notes = dbHelper.getNotes()
        adapter.clear()
        adapter.addAll(notes.map { "${it.title}\n${it.content}" })
    }

    private fun showNoteDialog(note: Note?) {
        val titleInput = EditText(this).apply {
            hint = getString(R.string.title_label)
            setText(note?.title ?: "")
        }
        val contentInput = EditText(this).apply {
            hint = getString(R.string.content_label)
            setText(note?.content ?: "")
            minLines = 3
        }

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 32, 48, 0)
            addView(titleInput)
            addView(contentInput)
        }

        AlertDialog.Builder(this)
            .setTitle(if (note == null) getString(R.string.add_note) else getString(R.string.title_label))
            .setView(layout)
            .setNegativeButton(android.R.string.cancel, null)
            .setPositiveButton(android.R.string.ok) { _, _ ->
                val title = titleInput.text.toString().trim()
                val content = contentInput.text.toString().trim()
                if (title.isEmpty() || content.isEmpty()) {
                    Toast.makeText(this, "Debe escribir título y contenido", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                val noteToSave = Note(
                    id = note?.id ?: 0,
                    title = title,
                    content = content,
                    createdAt = System.currentTimeMillis()
                )
                if (note == null) {
                    dbHelper.insertNote(noteToSave)
                } else {
                    dbHelper.updateNote(noteToSave)
                }
                refreshNotes()
            }
            .show()
    }

    private fun deleteNote(note: Note) {
        AlertDialog.Builder(this)
            .setTitle("Eliminar nota")
            .setMessage("¿Eliminar nota '${note.title}'?")
            .setNegativeButton(android.R.string.cancel, null)
            .setPositiveButton(android.R.string.ok) { _, _ ->
                dbHelper.deleteNote(note.id)
                refreshNotes()
            }
            .show()
    }
}
