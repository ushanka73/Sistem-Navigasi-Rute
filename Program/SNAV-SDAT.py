#Baca CSV

def bacaDataCSV(namaFile):
    # Membuat matriks 26x26 (A-Z) diisi None (kosong)
    graph = [[None] * 26 for _ in range(26)]
    try:
        with open(namaFile, mode='r') as file:
            # Membaca seluruh isi file dan memisahkan per baris
            lines = file.read().splitlines()
            if not lines: 
                return graph
            
            # Lewati baris pertama (header), mulai dari indeks 1
            for line in lines[1:]:
                if not line.strip(): 
                    continue
                
                # Memisahkan kolom berdasarkan tanda koma manual
                row = line.split(',')
                if len(row) < 7: 
                    continue
                
                # Konversi huruf ke indeks (A=0, B=1, dst)
                u = ord(row[0][0].upper()) - ord('A')
                v = ord(row[1][0].upper()) - ord('A')
                
                # Simpan data jalur sebagai Dictionary
                data_jalur = {
                    'jarak': int(row[2]),
                    'rusak_mobil': int(row[3]),
                    'nyaman_mobil': int(row[4]),
                    'rusak_motor': int(row[5]),
                    'nyaman_motor': int(row[6]),
                    'bobot_akhir': 0.0,
                    'ada': True
                }
                graph[u][v] = data_jalur.copy()
                graph[v][u] = data_jalur.copy()
    except FileNotFoundError:
        print(f"Gagal membuka file {namaFile}!")
    return graph

def hitungBobotSesuaiKendaraan(kendaraan, graph):
    for i in range(26):
        for j in range(26):
            if graph[i][j] and graph[i][j]['ada']:
                jalur = graph[i][j]
                if kendaraan in ["Mobil", "1"]:
                    rusak, nyaman = jalur['rusak_mobil'], jalur['nyaman_mobil']
                else:
                    rusak, nyaman = jalur['rusak_motor'], jalur['nyaman_motor']
                
                ketidak_nyamanan = 6 - nyaman
                jalur['bobot_akhir'] = (rusak * 0.6) + (ketidak_nyamanan * 0.4)

#Heap

def manual_heappush(heap, item):
    """Menambahkan elemen ke heap dan mengatur ulang posisi (Bubble Up)"""
    heap.append(item)
    index = len(heap) - 1
    
    # Selama belum di root dan nilai child lebih kecil dari parent
    while index > 0:
        parent_index = (index - 1) // 2
        # item selalu berbentuk tuple (bobot, node), kita bandingkan bobotnya
        if heap[index] < heap[parent_index]:
            # Tukar posisi dengan parent
            heap[index], heap[parent_index] = heap[parent_index], heap[index]
            index = parent_index
        else:
            break

def manual_heappop(heap):
    """Mengambil elemen terkecil (root) dan mengatur ulang posisi (Bubble Down)"""
    if len(heap) == 0:
        return None
    if len(heap) == 1:
        return heap.pop()
        
    # Simpan nilai root (terkecil) untuk dikembalikan
    root = heap[0]
    
    # Pindahkan elemen paling akhir menjadi root baru
    heap[0] = heap.pop()
    index = 0
    length = len(heap)
    
    # Atur ulang posisi ke bawah (Bubble Down)
    while True:
        left_child = 2 * index + 1
        right_child = 2 * index + 2
        terkecil = index
        
        # Cek apakah left child lebih kecil dari root saat ini
        if left_child < length and heap[left_child] < heap[terkecil]:
            terkecil = left_child
            
        # Cek apakah right child lebih kecil
        if right_child < length and heap[right_child] < heap[terkecil]:
            terkecil = right_child
            
        # Jika ada yang lebih kecil, tukar posisinya
        if terkecil != index:
            heap[index], heap[terkecil] = heap[terkecil], heap[index]
            index = terkecil
        else:
            break
            
    return root

#Djikstra

def cariRuteDijkstra(start, dest, graph):
    dist = [float('inf')] * 26
    parent = [-1] * 26
    dist[start] = 0
    
    # List kosong yang akan kita jadikan Min-Heap manual
    pq = [] 
    
    # Masukkan titik awal menggunakan heappush buatan kita
    manual_heappush(pq, (0.0, start))
    
    while pq:
        # Ambil jarak terkecil menggunakan heappop buatan kita
        current_dist, u = manual_heappop(pq)
        
        if current_dist > dist[u]: 
            continue
        if u == dest: 
            break
        
        # Proses relaksasi (pencarian rute terpendek)
        for v in range(26):
            if graph[u][v] and graph[u][v]['ada']:
                weight = graph[u][v]['bobot_akhir']
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    parent[v] = u
                    # Masukkan rute baru ke dalam heap manual
                    manual_heappush(pq, (dist[v], v))
                            
    # --- Kode penyusunan rute ke bawahnya tetap sama persis ---
    rute = {'path': [], 'total_bobot': dist[dest], 'total_jarak': 0}
    if dist[dest] == float('inf'):
        return rute # Rute tidak ditemukan
        
    curr = dest
    while curr != -1:
        rute['path'].append(curr)
        curr = parent[curr]
    rute['path'].reverse()
    
    for i in range(len(rute['path']) - 1):
        u, v = rute['path'][i], rute['path'][i+1]
        rute['total_jarak'] += graph[u][v]['jarak']
        
    return rute

def cariDaftarAlternatif(start, dest, graph, ruteUtama):
    daftarAlternatif = []
    if not ruteUtama['path']: 
        return daftarAlternatif
    
    # Putus jalan satu per satu (Edge Elimination)
    for i in range(len(ruteUtama['path']) - 1):
        u, v = ruteUtama['path'][i], ruteUtama['path'][i+1]
        
        # Matikan jalan sementara
        graph[u][v]['ada'] = graph[v][u]['ada'] = False
        
        # Cari rute baru setelah ada jalan diputus
        ruteBaru = cariRuteDijkstra(start, dest, graph)
        
        # Jika rute valid, cek duplikat manual
        if ruteBaru['path']:
            is_duplikat = False
            for r in daftarAlternatif:
                if r['path'] == ruteBaru['path']:
                    is_duplikat = True
                    break
            if not is_duplikat:
                daftarAlternatif.append(ruteBaru)
                
        # Hidupkan kembali jalan semula
        graph[u][v]['ada'] = graph[v][u]['ada'] = True
        
    return daftarAlternatif

# BUBBLE SORT MANUAL (Sama seperti di C++)
def urutkanRuteManual(ruteList):
    n = len(ruteList)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if ruteList[j]['total_bobot'] > ruteList[j + 1]['total_bobot']:
                # Tukar posisi
                ruteList[j], ruteList[j + 1] = ruteList[j + 1], ruteList[j]

#Menu CLI

def format_path(path):
    return " -> ".join([chr(node + ord('A')) for node in path])

def main():
    # Membaca data rute
    graph = bacaDataCSV("data_rute.csv")
    
    while True:
        print("\n========================================================")
        print("  Pengembangan Sistem Navigasi Rute Berdasarkan Jarak   ")
        print("           dan Kenyamanan dalam Berkendara              ")
        print("========================================================")
        print("[1] Cari Rute Navigasi")
        print("[2] Keluar Program")
        
        pilihan = input("Pilih menu (1/2): ")
        
        if pilihan == "2":
            print("\nTerima kasih telah menggunakan Sistem Navigasi Universitas Jember!")
            break
        elif pilihan == "1":
            start_char = input("\nMasukkan Titik Asal (A-Z)       : ").upper()
            dest_char = input("Masukkan Titik Tujuan (A-Z)     : ").upper()
            
            if not ('A' <= start_char <= 'Z' and 'A' <= dest_char <= 'Z'):
                print("[!] Input tidak valid! Harap masukkan huruf A - Z.")
                continue
                
            start = ord(start_char) - ord('A')
            dest = ord(dest_char) - ord('A')
            
            pilihan_kendaraan = input("Pilih Kendaraan (1: Mobil / 2: Motor) : ")
            if pilihan_kendaraan in ["1", "Mobil", "mobil"]:
                tipe_kendaraan = "Mobil"
            elif pilihan_kendaraan in ["2", "Motor", "motor"]:
                tipe_kendaraan = "Motor"
            else:
                print("[!] Pilihan tidak valid! Masukkan angka 1 atau 2.")
                continue
            
            # Eksekusi Algoritma
            hitungBobotSesuaiKendaraan(tipe_kendaraan, graph)
            ruteUtama = cariRuteDijkstra(start, dest, graph)
            
            if not ruteUtama['path']:
                print(f"\nMaaf, rute terputus. Tidak ada jalan dari {start_char} ke {dest_char}.")
            else:
                print("\n========================================================")
                print("             OUTPUT 1: RUTE PALING OPTIMAL              ")
                print("========================================================")
                print(f"Rute Utama Terbaik:\nRute           : {format_path(ruteUtama['path'])}")
                print(f"Total Jarak    : {ruteUtama['total_jarak']} satuan jarak")
                print(f"Bobot Total    : {ruteUtama['total_bobot']:.2f} (Semakin kecil semakin nyaman)")
                print("--------------------------------------------------------")
                
                # Cari rute alternatif
                alternatif = cariDaftarAlternatif(start, dest, graph, ruteUtama)
                
                # Mengurutkan rute menggunakan fungsi Bubble Sort manual kita
                urutkanRuteManual(alternatif)
                
                print("\n========================================================")
                print("             OUTPUT 2: RUTE ALTERNATIF (BACKUP)         ")
                print("========================================================")
                if not alternatif:
                    print("Tidak ada rute cadangan lain yang tersedia.")
                else:
                    for i, alt in enumerate(alternatif):
                        print(f"Alternatif {i + 1}:")
                        print(f"Rute           : {format_path(alt['path'])}")
                        print(f"Total Jarak    : {alt['total_jarak']} satuan jarak")
                        print(f"Bobot Total    : {alt['total_bobot']:.2f}")
                        print("--------------------------------------------------------")
            
            input("\nTekan Enter untuk kembali ke menu utama...")
        else:
            print("\n[!] Pilihan tidak valid! Silakan masukkan 1 atau 2.")

if __name__ == "__main__":
    main()