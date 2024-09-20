import tkinter as tk
from tkinter import filedialog, messagebox

def encrypt_vigenere(plaintext, key):
    key = key.upper()
    ciphertext = ""
    key_length = len(key)
    for i, char in enumerate(plaintext):
        if char.isalpha():
            shift = ord(key[i % key_length]) - ord('A')
            cipher_char = chr((ord(char.upper()) - ord('A') + shift) % 26 + ord('A'))
            ciphertext += cipher_char
        else:
            ciphertext += char
    return ciphertext

def decrypt_vigenere(ciphertext, key):
    key = key.upper()
    plaintext = ""
    key_length = len(key)
    for i, char in enumerate(ciphertext):
        if char.isalpha():
            shift = ord(key[i % key_length]) - ord('A')
            plain_char = chr((ord(char.upper()) - ord('A') - shift + 26) % 26 + ord('A'))
            plaintext += plain_char
        else:
            plaintext += char
    return plaintext

def create_playfair_matrix(key):
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    key = "".join(sorted(set(key.upper()), key=lambda x: key.index(x)))
    matrix = [char for char in key if char in alphabet]
    matrix.extend([char for char in alphabet if char not in matrix])
    return [matrix[i:i+5] for i in range(0, 25, 5)]

def encrypt_playfair(plaintext, key):
    matrix = create_playfair_matrix(key)
    plaintext = plaintext.upper().replace('J', 'I').replace(" ", "")
    digraphs = []
    i = 0
    while i < len(plaintext):
        a = plaintext[i]
        if i + 1 < len(plaintext):
            b = plaintext[i + 1]
            if a != b:
                digraphs.append(a + b)
                i += 2
            else:
                digraphs.append(a + 'X')
                i += 1
        else:
            digraphs.append(a + 'X')
            i += 1

    ciphertext = ""
    for digraph in digraphs:
        a, b = digraph
        a_row, a_col = next((i, j) for i, row in enumerate(matrix) for j, char in enumerate(row) if char == a)
        b_row, b_col = next((i, j) for i, row in enumerate(matrix) for j, char in enumerate(row) if char == b)
        if a_row == b_row:
            ciphertext += matrix[a_row][(a_col + 1) % 5] + matrix[b_row][(b_col + 1) % 5]
        elif a_col == b_col:
            ciphertext += matrix[(a_row + 1) % 5][a_col] + matrix[(b_row + 1) % 5][b_col]
        else:
            ciphertext += matrix[a_row][b_col] + matrix[b_row][a_col]
    
    return ciphertext

def decrypt_playfair(ciphertext, key):
    matrix = create_playfair_matrix(key)
    plaintext = ""
    for i in range(0, len(ciphertext), 2):
        a, b = ciphertext[i], ciphertext[i+1]
        a_row, a_col = next((i, j) for i, row in enumerate(matrix) for j, char in enumerate(row) if char == a)
        b_row, b_col = next((i, j) for i, row in enumerate(matrix) for j, char in enumerate(row) if char == b)
        if a_row == b_row:
            plaintext += matrix[a_row][(a_col - 1) % 5] + matrix[b_row][(b_col - 1) % 5]
        elif a_col == b_col:
            plaintext += matrix[(a_row - 1) % 5][a_col] + matrix[(b_row - 1) % 5][b_col]
        else:
            plaintext += matrix[a_row][b_col] + matrix[b_row][a_col]
    return plaintext

def determinant(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

def mod_inverse(a, m):
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def encrypt_hill(plaintext, key_matrix):
    n = len(key_matrix)
    plaintext = [ord(char) - ord('A') for char in plaintext.upper() if char.isalpha()]
    if len(plaintext) % n != 0:
        plaintext.extend([0] * (n - len(plaintext) % n))  
    ciphertext = ""
    for i in range(0, len(plaintext), n):
        chunk = plaintext[i:i + n]
        result = [(key_matrix[0][0] * chunk[0] + key_matrix[0][1] * chunk[1]) % 26,
                   (key_matrix[1][0] * chunk[0] + key_matrix[1][1] * chunk[1]) % 26]
        ciphertext += "".join(chr(num + ord('A')) for num in result)
    return ciphertext

def decrypt_hill(ciphertext, key_matrix):
    n = len(key_matrix)
    ciphertext = [ord(char) - ord('A') for char in ciphertext.upper() if char.isalpha()]
    
    det = determinant(key_matrix) % 26
    inv_det = mod_inverse(det, 26)
    
    if inv_det is None:
        messagebox.showerror("Error", "Key matrix is not invertible!")
        return ""
    
    adjugate = [[key_matrix[1][1], -key_matrix[0][1]], [-key_matrix[1][0], key_matrix[0][0]]]
    inverse_key = [[(inv_det * adjugate[0][0]) % 26, (inv_det * adjugate[0][1]) % 26],
                   [(inv_det * adjugate[1][0]) % 26, (inv_det * adjugate[1][1]) % 26]]
    
    plaintext = ""
    for i in range(0, len(ciphertext), n):
        chunk = ciphertext[i:i + n]
        result = [(inverse_key[0][0] * chunk[0] + inverse_key[0][1] * chunk[1]) % 26,
                   (inverse_key[1][0] * chunk[0] + inverse_key[1][1] * chunk[1]) % 26]
        plaintext += "".join(chr(num + ord('A')) for num in result)
    return plaintext

def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, 'r') as file:
            content = file.read()
            input_text.delete("1.0", tk.END)
            input_text.insert(tk.END, content)

def validate_key(key):
    if len(key) < 12:
        messagebox.showerror("Error", "Kunci harus minimal 12 karakter!")
        return False
    return True

def run_cipher():
    cipher_type = cipher_var.get()
    key = key_input.get()
    plaintext = input_text.get("1.0", tk.END).strip()

    if not validate_key(key):
        return

    if cipher_type == "Vigenere":
        if action_var.get() == "Encrypt":
            result = encrypt_vigenere(plaintext, key)
        else:
            result = decrypt_vigenere(plaintext, key)
    elif cipher_type == "Playfair":
        if action_var.get() == "Encrypt":
            result = encrypt_playfair(plaintext, key)
        else:
            result = decrypt_playfair(plaintext, key)
    elif cipher_type == "Hill":
        
        key_matrix = [[5, 17], [8, 3]] 
        if action_var.get() == "Encrypt":
            result = encrypt_hill(plaintext, key_matrix)
        else:
            result = decrypt_hill(plaintext, key_matrix)

    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, result)

root = tk.Tk()
root.title("Cryptography GUI")

cipher_label = tk.Label(root, text="Pilih Jenis Cipher:")
cipher_label.pack()
cipher_var = tk.StringVar(value="Vigenere")
cipher_menu = tk.OptionMenu(root, cipher_var, "Vigenere", "Playfair", "Hill")
cipher_menu.pack()

action_label = tk.Label(root, text="Silahkan Pilih:")
action_label.pack()
action_var = tk.StringVar(value="Encrypt")
action_menu = tk.OptionMenu(root, action_var, "Encrypt", "Decrypt")
action_menu.pack()

key_label = tk.Label(root, text="Input Key (Min 12 karakter):")
key_label.pack()
key_input = tk.Entry(root, width=40)
key_input.pack()

upload_button = tk.Button(root, text="Upload .txt File", command=upload_file)
upload_button.pack()

input_label = tk.Label(root, text="Input Plaintext:")
input_label.pack()
input_text = tk.Text(root, height=10, width=40)
input_text.pack()

run_button = tk.Button(root, text="Run", command=run_cipher)
run_button.pack()

output_label = tk.Label(root, text="Output:")
output_label.pack()
output_text = tk.Text(root, height=10, width=40)
output_text.pack()

root.mainloop()
