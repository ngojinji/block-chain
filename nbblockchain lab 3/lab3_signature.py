from eth_account import Account
from eth_account.messages import encode_defunct
acct = Account.create()
print("address:",  acct.address)

msg = encode_defunct(text="I attended Session 3 / Toi da hoc Buoi 3")

sig = Account.sign_message(msg, acct.key)

print(
    "r,s,v:",
    hex(sig.r),
    hex(sig.s),
    sig.v
)

who = Account.recover_message(msg,signature=sig.signature)
print(
    "recovered:",
    who,
    "| match:",
    who == acct.address
)

bad = encode_defunct(text="I attended Session 3 / Toi da hoc Buoi 4")

print(
    "tampered ->",
    Account.recover_message(
        bad,
        signature=sig.signature
    )
)
# Task 1: sign the SAME message twice with the SAME key
sig2 = Account.sign_message(msg, acct.key)
print("same key, signed twice -> identical:", sig.signature == sig2.signature)