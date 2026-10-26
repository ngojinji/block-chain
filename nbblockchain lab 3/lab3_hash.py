import hashlib
import time
# Avalanche effect
print(hashlib.sha256(b"Blockchain 2026").hexdigest())
print(hashlib.sha256(b"blockchain 2026").hexdigest())

def mine(data: bytes, k: int):
    target = "0" * k
    nonce = 0
    t0 = time.time()
    while True:
        h = hashlib.sha256(data + str(nonce).encode()).hexdigest()
        if h.startswith(target):
            return nonce, time.time()-t0
        nonce += 1

for k in range(1,7):

    nonce, dt = mine(b"block#1|txroot=abc|", k)

    print(f"k={k} nonce={nonce} time={dt:.3f}s")
