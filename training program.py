import os
import shutil
import string
import unicodedata
from multiprocessing import Pool, cpu_count
import time

IMAGE_EXTENSIONS = ('JPEG', 'PNG', 'JPG', 'SVG')
VIDEO_EXTENSIONS = ('AVI', 'MP4', 'MOV', 'MKV')
DOCUMENT_EXTENSIONS = ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX')
AUDIO_EXTENSIONS = ('MP3', 'OGG', 'WAV', 'AMR')
ARCHIVE_EXTENSIONS = ('ZIP', 'GZ', 'TAR')

def normalise(name):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    name = ''.join(c for c in name if c in valid_chars)
    name = name.lower().replace(' ', '_')
    return name

def organise_folder(path):
    file_list = os.listdir(path)
    folder_count = { 'images': 0, 'video': 0, 'documents': 0, 'audio': 0, 'archives': 0 }

    for file in file_list:
        if os.path.isdir(os.path.join(path, file)):
            organise_folder(os.path.join(path, file))
        else:
            ext = os.path.splitext(file)[1][1:].upper()

            if ext in IMAGE_EXTENSIONS:
                folder = 'images'
            elif ext in VIDEO_EXTENSIONS:
                folder = 'video'
            elif ext in DOCUMENT_EXTENSIONS:
                folder = 'documents'
            elif ext in AUDIO_EXTENSIONS:
                folder = 'audio'
            elif ext in ARCHIVE_EXTENSIONS:
                folder = 'archives'
                temp_dir = os.path.join(path, os.path.splitext(file)[0])
                os.makedirs(temp_dir, exist_ok=True)
                shutil.unpack_archive(os.path.join(path, file), temp_dir)
                organise_folder(temp_dir)
                shutil.rmtree(temp_dir)
            else:
                folder = 'unknown'

            if folder != 'unknown':
                src_path = os.path.join(path, file)
                dest_path = os.path.join(path, folder, normalise(os.path.splitext(file)[0]) + '.' + ext)
                os.makedirs(os.path.join(path, folder), exist_ok=True)
                os.rename(src_path, dest_path)
                folder_count[folder] += 1

    print(f"Files in {path}:")
    for folder, count in folder_count.items():
        if count > 0:
            print(f"{count} file(s) moved to {folder} folder")

def factorize_sync(number):
    factors = []
    for i in range(1, number + 1):
        if number % i == 0:
            factors.append(i)
    return factors

def factorize_parallel(numbers):
    with Pool(cpu_count()) as pool:
        return pool.map(factorize_sync, numbers)

if __name__ == '__main__':
    path = '/Users/kira/Desktop/hw3/file.py'
    if os.path.isdir(path):
        organise_folder(path)
        print("Done.")
    else:
        print("Invalid directory path.")

    numbers_to_factorize = [128, 255, 99999, 10651060]

    start_time = time.time()
    results_sync = [factorize_sync(number) for number in numbers_to_factorize]
    print(f"Synchronous factorization took {time.time() - start_time} seconds")

    start_time = time.time()
    results_parallel = factorize_parallel(numbers_to_factorize)
    print(f"Parallel factorization took {time.time() - start_time} seconds")

    for i in range(len(numbers_to_factorize)):
        assert results_sync[i] == results_parallel[i]
