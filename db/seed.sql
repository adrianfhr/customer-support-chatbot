-- Seed data for Customer Support Chatbot
-- Insert demo data for testing

-- Insert sample orders
INSERT INTO orders (id, user_id, status, last_update_at, eta_date, carrier, tracking_number) VALUES
('ORD123', 'user001', 'shipped', '2025-09-16 14:30:00+07', '2025-09-18 17:00:00+07', 'JNE', 'JNE123456789'),
('ORD124', 'user002', 'delivered', '2025-09-15 10:15:00+07', '2025-09-15 16:30:00+07', 'Sicepat', 'SCP987654321'),
('ORD125', 'user003', 'confirmed', '2025-09-16 09:00:00+07', '2025-09-20 12:00:00+07', 'J&T', 'JT555666777'),
('ORD126', 'user001', 'pending', '2025-09-16 16:45:00+07', NULL, NULL, NULL),
('ORD127', 'user004', 'cancelled', '2025-09-14 11:20:00+07', NULL, NULL, NULL);

-- Insert sample products
INSERT INTO products (id, name, features, price, stock) VALUES
('PROD001', 'Laptop Gaming X Pro', 'Processor Intel i7-12700H, RAM 16GB DDR4, GPU RTX 4060 8GB, Storage 1TB NVMe SSD, Display 15.6" 144Hz, Backlit Keyboard, Wi-Fi 6, USB-C Thunderbolt', 18500000.00, 5),
('PROD002', 'Smartphone Y Ultra', 'Chipset Snapdragon 8 Gen 2, RAM 12GB, Storage 256GB, Kamera 108MP triple lens, Layar AMOLED 6.8" 120Hz, Baterai 5000mAh fast charging, 5G ready', 12999000.00, 12),
('PROD003', 'Headphone Wireless Z', 'Driver 40mm, Active Noise Cancellation, Bluetooth 5.3, Battery life 30 jam, Quick charge 15 menit untuk 3 jam, Suport Hi-Res Audio', 2500000.00, 25),
('PROD004', 'Tablet Creator Plus', 'Processor M2 chip, RAM 8GB, Storage 512GB, Layar 12.9" Liquid Retina, Apple Pencil support, USB-C, Battery 10 jam, Cocok untuk design dan editing', 15999000.00, 8),
('PROD005', 'Smartwatch Fitness Pro', 'GPS built-in, Heart rate monitor, Sleep tracking, 50+ workout modes, Water resistant 5ATM, Battery 7 hari, Compatible iOS dan Android', 3200000.00, 0);

-- Insert sample policies
INSERT INTO policies (type, content_markdown) VALUES
('warranty', '# Prosedur Klaim Garansi

## Langkah-langkah Klaim Garansi:

1. **Siapkan Dokumen**
   - Nota pembelian asli
   - Kartu garansi (jika ada)
   - Foto produk yang bermasalah

2. **Hubungi Customer Service**
   - Telepon: 0800-1234-5678 (gratis)
   - Email: cs@toko.com
   - WhatsApp: 0812-3456-7890
   - Jam operasional: Senin-Jumat 08:00-17:00, Sabtu 08:00-15:00

3. **Jelaskan Masalah**
   - Deskripsikan kerusakan dengan detail
   - Kapan mulai terjadi masalah
   - Sudah dicoba cara perbaikan apa

4. **Proses Selanjutnya**
   - Tim CS akan memberikan instruksi (perbaikan atau penggantian)
   - Jika perlu kirim unit, kami akan berikan alamat service center
   - Estimasi perbaikan 3-7 hari kerja

## Syarat dan Ketentuan:

- **Periode Garansi**: 1 tahun dari tanggal pembelian
- **Cakupan**: Kerusakan manufaktur dan cacat pabrik
- **Tidak berlaku untuk**: 
  - Kerusakan akibat kesalahan penggunaan
  - Kerusakan fisik (jatuh, terkena cairan)
  - Kerusakan akibat bencana alam
  - Modifikasi atau perbaikan oleh pihak tidak resmi

## Garansi Internasional:
Tersedia untuk produk tertentu. Silakan konfirmasi saat pembelian.'),

('return', '# Kebijakan Pengembalian Barang

## Syarat Pengembalian:

1. **Waktu**: Maksimal 7 hari dari tanggal penerimaan
2. **Kondisi**: Barang masih baru, segel utuh, kelengkapan utuh
3. **Alasan**: Barang tidak sesuai, cacat, atau salah kirim

## Cara Pengembalian:

1. Hubungi CS untuk mendapat RMA (Return Authorization)
2. Kemas barang dengan aman
3. Kirim ke alamat yang diberikan CS
4. Refund diproses 3-5 hari kerja setelah barang diterima

**Catatan**: Ongkos kirim return ditanggung pembeli kecuali kesalahan toko.');

-- Insert sample conversation for demo
INSERT INTO messages (session_id, role, content, turn_index, created_at) VALUES
('demo-session', 'user', 'Halo, saya butuh bantuan', 1, '2025-09-16 10:00:00+07'),
('demo-session', 'assistant', 'Halo! Saya customer support chatbot yang siap membantu Anda. Saya bisa membantu dengan status pesanan, informasi produk, dan prosedur garansi. Ada yang bisa saya bantu hari ini? Ringkas: Siap membantu pertanyaan seputar pesanan, produk, dan garansi.', 1, '2025-09-16 10:00:05+07'),
('demo-session', 'user', 'Di mana pesanan saya? ID: ORD123', 2, '2025-09-16 10:01:00+07'),
('demo-session', 'assistant', 'Pesanan ORD123 sedang dalam pengiriman via JNE dengan nomor resi JNE123456789 dengan estimasi tiba 18 September 2025. Terakhir diupdate: 16 September 2025 pukul 14:30. Ringkas: Pesanan Anda sedang dikirim dan akan tiba dalam 2 hari.', 2, '2025-09-16 10:01:10+07');
