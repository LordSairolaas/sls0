import hashlib
import time

class Kok:
    def __init__(self, index, prevHash, timestamp, data):
        self.index = index
        self.prevHash = prevHash
        self.timestamp = timestamp
        self.data = data
        self.hash = self.calc_hash(index, prevHash, data)

    def calc_hash(self, index, prevHash, data):
        # Correctly format the hashing process
        block_string = f"{index}{prevHash}{data}".encode("utf-8")
        return hashlib.sha256(block_string).hexdigest()

class Sls:
    def __init__(self):
        # Start with a Genesis Block
        genesis = Kok(0, "0", int(time.time()), "Genesis Block")
        self.sls = [genesis]

    def add_kok(self, data):
        prev_kok = self.sls[-1]
        new_kok = Kok(
            index=prev_kok.index + 1,
            prevHash=prev_kok.hash,
            timestamp=int(time.time()),
            data=data
        )
        self.sls.append(new_kok)

    def is_chain_valid(self):
        """Checks if the blockchain has been tampered with."""
        for i in range(1, len(self.sls)):
            current = self.sls[i]
            previous = self.sls[i-1]

            # 1. Check if current block's hash is still valid based on its data
            if current.hash != current.calc_hash(current.index, current.prevHash, current.data):
                print(f"--- ALERT: Data tampered at Index {current.index}! ---")
                return False

            # 2. Check if it points to the correct previous hash
            if current.prevHash != previous.hash:
                print(f"--- ALERT: Chain broken at Index {current.index}! ---")
                return False
        return True

    def tamper_with_data(self, index, new_data):
        """Simulates an attack by changing data without recalculating everything."""
        if 0 <= index < len(self.sls):
            self.sls[index].data = new_data
            print(f"Hacker changed Index {index} data to: '{new_data}'")

    def display(self):
        for k in self.sls:
            print(f"[{k.index}] Hash: {k.hash[:15]}... | Prev: {k.prevHash[:15]}... | Data: {k.data}")

# --- Testing the Chain ---
if __name__ == "__main__":
    my_chain = Sls()
    my_chain.add_kok("Payment: $50 to Alice")
    my_chain.add_kok("Payment: $20 to Bob")

    print("Initial Chain Status:")
    my_chain.display()
    print(f"Is chain valid? {my_chain.is_chain_valid()}\n")

    # Let's simulate a hack!
    my_chain.tamper_with_data(1, "Payment: $5000 to Hacker")
    
    print("\nAfter Tampering:")
    my_chain.display()
    print(f"Is chain valid? {my_chain.is_chain_valid()}")
