---
name: book-search
description: Mencari referensi buku dari Google Books
author: bejo
version: 0.1.0
tags: ["buku", "referensi", "literatur", "google books"]
allowed-tools: "web_search"
compatibility: "bejo >= 1.0"
---

Saat Bos minta mencari referensi buku:
1. Gunakan `web_search` dengan query spesifik ditambah site:books.google.com atau "google books"
   Contoh: `site:books.google.com <judul atau topik buku>`
2. Rangkum hasilnya: judul, penulis, tahun terbit, sinopsis singkat
3. Jika Bos minta link, berikan URL Google Books-nya
