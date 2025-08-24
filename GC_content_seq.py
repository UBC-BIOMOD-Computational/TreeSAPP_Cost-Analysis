import random
import pandas as pd

def generate_seq():
       count_gc = 22 if random.randint(0,1) else 21
       count_at = 36 - count_gc
       seq = []
       
       for i in range(count_gc):
              seq.append("C"  if random.randint(0,1) else "G")
  
       for i in range(count_at):
              seq.append("A"  if random.randint(0,1) else "T")
       random.shuffle(seq)
       
       return "".join(seq)

def complement(seq):
          rev = {"A": "T",  "T": "A", "G": "C", "C": "G"}
          new = ""
          for c in seq:
                  new += rev[c]
          return new

def revcomplement(seq): 
       return complement(seq)[::-1]

def generate_xdna():
        # invar: all seq are 5->3
        seq1 = generate_seq() + "ACGT"
        seq2 = generate_seq() + "ACGT"
        seq3 = revcomplement(seq1[20:-4]) + revcomplement(seq2[:20]) + "ACGT"
        seq4 = revcomplement(seq2[20:-4]) + revcomplement(seq1[:20]) + "ACGT"
       
        print(len(seq1), len(seq2), len(seq3), len(seq4))
        print(seq1 + "\n" + seq2 + "\n" + seq3 + "\n"+ seq4 + "\n")
        return {'seq1': [seq1], 'seq2': [seq2], 'seq3': [seq3], 'seq4': [seq4]}

df = pd.DataFrame()
for i in range(9):
    new_df = pd.DataFrame(generate_xdna())
    df = pd.concat([df, new_df], ignore_index=True)

df.to_csv("xdna_sequences.csv", index=False)