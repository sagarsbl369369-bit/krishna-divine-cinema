import sys, os
from cryptography.fernet import Fernet

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    if len(sys.argv) < 4:
        print("Usage: python decrypt_profile.py <KEY> <INPUT_ENC> <OUTPUT_TAR_GZ>")
        sys.exit(1)
    
    key = sys.argv[1].strip().encode('utf-8')
    in_file = sys.argv[2]
    out_file = sys.argv[3]
    
    print(f"Decrypting {in_file} -> {out_file}...")
    f = Fernet(key)
    with open(in_file, 'rb') as fi:
        enc_data = fi.read()
    dec_data = f.decrypt(enc_data)
    with open(out_file, 'wb') as fo:
        fo.write(dec_data)
    print(f"[OK] Decrypted {os.path.getsize(out_file):,} bytes successfully!")

if __name__ == '__main__':
    main()
