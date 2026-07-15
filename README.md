# AICHAT DENGAN COLLAB - AICHAT WITH COLLAB

Aplikasi obrolan canggih yang terintegrasi secara mulus dengan proksi LiteLLM menggunakan infrastruktur Google Colab.
--------
An advanced chat application seamlessly integrating with the LiteLLM proxy via Google Colab infrastructure.

## DESKRIPSI SINGKAT - BRIEF DESCRIPTION

Proyek ini memungkinkan Anda untuk menjalankan server Large Language Model (LLM) mandiri melalui Google Colab dan menghubungkannya dengan klien obrolan lokal Anda. Pengguna cukup mengunggah berkas `colab_llm_server.ipynb` ke Google Colab atau menyalin skrip dari `colab_llm_server.py` ke dalam sel Colab, lalu menggunakan runtime GPU untuk performa optimal. Setelah proses instalasi diinisialisasi, server akan menghasilkan kredensial berupa `API_KEY` dan `BASE_URL`, yang selanjutnya digunakan untuk mengonfigurasi environment lokal pada berkas `.env.example`.
--------
This project enables you to run a standalone Large Language Model (LLM) server via Google Colab and interface it with your local chat client. Users simply need to upload the `colab_llm_server.ipynb` file to Google Colab or copy the script from `colab_llm_server.py` into a Colab cell, and select a GPU runtime for optimal performance. Once the installation process is initialized, the server will generate the necessary credentials, specifically an `API_KEY` and `BASE_URL`, which are then used to configure your local environment in the `.env.example` file.

## SPESIFIKASI MINIMUM - MINIMUM SPECIFICATIONS

- **RAM:** 12 GB (Bawaan standar tier gratis Google Colab)
- **VRAM:** 16 GB (Tersedia pada runtime GPU gratis Google Colab)
--------
- **RAM:** 12 GB (Standard default on Google Colab free tier)
- **VRAM:** 16 GB (Available on Google Colab free GPU runtime)

## PERSYARATAN - REQUIREMENTS

- Akun Google yang valid untuk mengakses layanan Google Colab.
- Koneksi internet yang stabil.
- [Node.js](https://nodejs.org/) terinstal pada perangkat lokal Anda.
--------
- A valid Google account to access Google Colab services.
- A stable internet connection.
- [Node.js](https://nodejs.org/) installed on your local machine.

## PANDUAN INSTALASI: SERVER LLM (GOOGLE COLAB) - INSTALLATION GUIDE: LLM SERVER (GOOGLE COLAB)

1. **Persiapan Skrip:** Unggah berkas `colab_llm_server.ipynb` ke [Google Colab](https://colab.research.google.com/), **atau** salin seluruh isi skrip dari `colab_llm_server.py` ke dalam sel notebook baru di environment Colab Anda.
2. **Konfigurasi Runtime:** Pada bilah menu Google Colab, navigasikan ke **Runtime** > **Ubah jenis runtime** (Change runtime type) dan pastikan akselerator perangkat keras disetel ke **GPU**.
3. **Eksekusi:** Jalankan (Run) sel yang berisi skrip tersebut untuk memulai proses instalasi dependensi dan menginisialisasi server. Tunggu hingga proses ini selesai sepenuhnya.
4. **Pengambilan Kredensial:** Setelah server berhasil berjalan, sistem akan mencetak nilai `API_KEY` dan `BASE_URL` pada output terminal/sel.
5. **Konfigurasi Lokal:** Buka berkas `.env.example` yang terdapat pada direktori proyek lokal Anda. Perbarui variabel environment yang relevan dengan menempelkan nilai `API_KEY` dan `BASE_URL` yang telah didapatkan. Terakhir, ubah nama berkas `.env.example` menjadi `.env`.
--------
1. **Script Preparation:** Upload the `colab_llm_server.ipynb` file to [Google Colab](https://colab.research.google.com/), **or** copy the entire script contents from `colab_llm_server.py` into a new notebook cell in your Colab environment.
2. **Runtime Configuration:** In the Google Colab menu bar, navigate to **Runtime** > **Change runtime type** and ensure the hardware accelerator is set to **GPU**.
3. **Execution:** Run the cell containing the script to initiate the dependency installation and server initialization process. Wait for this process to complete entirely.
4. **Credential Retrieval:** Once the server is successfully running, the system will output the `API_KEY` and `BASE_URL` values in the cell/terminal output.
5. **Local Configuration:** Open the `.env.example` file located in your local project directory. Update the relevant environment variables by pasting the acquired `API_KEY` and `BASE_URL` values. Finally, rename the `.env.example` file to `.env`.

## PANDUAN INSTALASI: SERVER WEB LOKAL - INSTALLATION GUIDE: LOCAL WEB SERVER

1. **Prasyarat:** Pastikan lingkungan sistem Anda telah memiliki [Node.js](https://nodejs.org/).
2. **Instalasi Dependensi:** Buka terminal atau command prompt dan arahkan ke direktori root proyek ini. Jalankan perintah `npm install` untuk mengunduh seluruh pustaka yang diperlukan.
3. **Menjalankan Server:** Eksekusi perintah `npm start` untuk menghidupkan server web lokal.
4. **Akses Aplikasi (Lokal):** Buka peramban web (browser) favorit Anda dan kunjungi `http://localhost:3000`.
5. **Akses Aplikasi (Jaringan WiFi Sama):** Aplikasi ini dapat diakses oleh perangkat apa pun (seperti ponsel pintar atau tablet) yang terhubung ke jaringan WiFi yang sama dengan komputer host. Cukup masukkan alamat IP lokal dari komputer host diikuti dengan port server pada peramban perangkat tersebut (contoh: `http://192.168.1.15:3000`).
--------
1. **Prerequisites:** Ensure your system environment has [Node.js](https://nodejs.org/) installed.
2. **Dependency Installation:** Open a terminal or command prompt and navigate to this project's root directory. Run the `npm install` command to download all required libraries.
3. **Starting the Server:** Execute the `npm start` command to boot up the local web server.
4. **Accessing the Application (Local):** Open your preferred web browser and navigate to `http://localhost:3000`.
5. **Accessing the Application (Same WiFi Network):** This application can be accessed by any device (such as a smartphone or tablet) connected to the same WiFi network as the host computer. Simply enter the local IP address of the host computer followed by the server port into the device's browser (e.g., `http://192.168.1.15:3000`).

## LISENSI - LICENSE

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.
This means you are free to use it for individual or non-commercial purposes, but commercial/corporate use requires a separate arrangement.

See the [LICENSE](LICENSE) file for the full text.
