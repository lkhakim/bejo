---
name: memory
description: Mengingat dan mencari fakta user serta memori percakapan
author: bejo
version: 0.1.0
tags: ["memori", "ingatan", "fakta"]
allowed-tools: "save_user_fact, get_user_facts, vector_search"
compatibility: "bejo >= 1.0"
---

Saat Bos menceritakan sesuatu tentang dirinya:
1. Simpan dengan `save_user_fact` agar tidak lupa
2. Saat Bos tanya sesuatu yang pernah dibahas, cari dengan `vector_search`
3. `get_user_facts` untuk lihat semua yang diketahui tentang Bos
