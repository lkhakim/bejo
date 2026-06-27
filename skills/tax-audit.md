---
name: tax-audit
description: Analisis rasio keuangan dan benchmarking untuk audit pajak
author: bejo
version: 0.1.0
tags: ["pajak", "audit", "keuangan", "rasio"]
allowed-tools: "Read, calculate_financial_ratios"
compatibility: "bejo >= 1.0"
---

Saat Bos minta audit laporan keuangan:
1. Gunakan `analyze_financial_statement` untuk membaca file PDF/Excel
2. Gunakan `calculate_financial_ratios` untuk menghitung rasio (GPM, NPM, OPM, DER, CR)
3. Bandingkan hasil dengan rata-rata industri
4. Rekomendasikan SP2DK jika ada selisih tidak wajar
