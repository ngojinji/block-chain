import hashlib


def H(b: bytes):
    return hashlib.sha256(b).digest()


def merkle_root(leaves: list[bytes]) -> bytes:
    level = leaves[:]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        next_level = []
        for i in range(0,len(level),2):
            parent = H(level[i] + level[i+1])
            next_level.append(parent)
        level = next_level
    return level[0]


def merkle_proof(leaves,index):
    proof=[]
    level=leaves[:]
    while len(level)>1:
        if len(level)%2==1:
            level.append(level[-1])
        sibling = (index-1 if index%2 else index+1)
        proof.append(
            (
            level[sibling],
            sibling < index
            )
        )
        new=[]
        for i in range(0,len(level),2):
            new.append(H(level[i]+level[i+1]))
        index//=2
        level=new
    return proof

def verify_proof(leaf_hash, proof, root):
    current = leaf_hash
    for sibling,is_left in proof:
        if is_left:
            current = H(sibling + current)
        else:
            current = H(current + sibling)
    return current == root
# ------------------------------------------------------------------ checks
if __name__ == "__main__":
   txs = [f"tx{i}: A->B {i} coin".encode() for i in range(8)]
   leaves = [H(t) for t in txs]
   root = merkle_root(leaves)


   print("root:", root.hex())


   # CHECK 1: proof đúng cho mọi lá / valid proof for every leaf
   ok = all(verify_proof(leaves[i], merkle_proof(leaves, i), root) for i in range(8))
   print("CHECK 1 (all 8 proofs valid):", "OK" if ok else "FAIL")


   # CHECK 2: proof có đúng log2(8)=3 phần tử / proof has exactly 3 elements
   print("CHECK 2 (proof length == 3):", "OK" if len(merkle_proof(leaves, 4)) == 3 else "FAIL")


   # CHECK 3: lá bị sửa phải trượt / a tampered leaf must fail
   fake = H(b"tx4: A->B 999999 coin")
   print("CHECK 3 (tampered leaf fails):",
         "OK" if not verify_proof(fake, merkle_proof(leaves, 4), root) else "FAIL")


   # CHECK 4: số lá lẻ (7) vẫn chạy / odd leaf count (7) still works
   l7 = leaves[:7]
   r7 = merkle_root(l7)
   print("CHECK 4 (odd count works):",
         "OK" if all(verify_proof(l7[i], merkle_proof(l7, i), r7) for i in range(7)) else "FAIL")
