# Author: Charity

import pandas as pd
import requests
import re


# EXTRACT FASTA FILE TO CSV
def parse_fasta_to_pd(fasta_file, output_csv):
    with open(fasta_file, 'r') as f:
        lines = f.readlines()

    df_json = {'aa_sequence': [], 'id': [], 'accession_number': [], 'gene': []}

    curr_aa_sequence = ''
    for line in lines:
        if line.startswith('>'):
            df_json['aa_sequence'] = curr_aa_sequence
            curr_aa_sequence = ''

            line = line.strip()
            
            if 'gene' in line:
                df_json['gene'].append(line.split('_gene')[1])
                line = line.split('_gene')[0]
            else:
                df_json['gene'].append(None)

            accession_i = line.find('.')
            if accession_i != -1:
                df_json['id'].append(line[1:accession_i]) #1 to skip '>'
                df_json['accession_number'].append(line[accession_i + 1:])
            else:
                df_json['id'].append(None)
                df_json['accession_number'].append()

            df_json['accession_number'][-1] = df_json['accession_number'][-1].replace('-', '_')
        else:
            curr_aa_sequence += line
    
    df = pd.DataFrame(df_json)
    df.to_csv(output_csv, index=False)


# TRANSFORM CSV TO NCBIBatchEntrez Input format
def transform_csv_to_entrez_input(input_csv, output_filename):
    f = open(output_filename, "w")
    df = pd.read_csv(input_csv)
    for index, row in df.iterrows():
        f.write(f"{row['accession_number']}\n")


def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))

# PARSE NCBI Batch Entrez Output into CSV
def parse_ncbi_batch_entrez_nuccore(output_filename, output_csv):
    with open(output_filename, 'r') as f:
        lines = f.readlines()

    df_json = {'title': [], 'description': [], 'length': [] , 'accession_number': [], 'GI_number': []}
    i = 1
    while i < len(lines): 
        print(lines[i])
        words = lines[i].split(' ')
        nxt_record = 4

        if has_numbers(words[2]):
            df_json['title'].append(words[1])
            df_json['description'].append(''.join(words[2:]))
        else:   
            df_json['title'].append(''.join(words[1:3]))
            df_json['description'].append(''.join(words[3:]))

        df_json['length'].append(lines[i + 1])

        if lines[i + 2].find('updated') >= 0 or lines[i + 2].find('removed') >= 0:
            i += 1

        gi_line_words = lines[i + 2].split(' ')
        df_json['accession_number'].append(gi_line_words[0])
        df_json['GI_number'].append(gi_line_words[1][3:]) #remove 'GI:'
        
        i += nxt_record
    
    df = pd.DataFrame(df_json)
    df.to_csv(output_csv, index=False)



eggnog_lib = 'COG3338'
# parse_fasta_to_pd(f'{eggnog_lib}_fasta.txt', f'{eggnog_lib}_fasta_output.csv')
# transform_csv_to_entrez_input(f'{eggnog_lib}_fasta_output.csv', f'{eggnog_lib}_entrez_input.txt')

# Manually import 'entrez_input.txt' into NCBI Batch Entrez Protein Query 
# > entrez_protein_result.txt
# Manually import 'entrez_input.txt' into NCBI Batch Entrez Nuccore Query 
# > entrez_nuccore_result.txt

parse_ncbi_batch_entrez_nuccore(f'{eggnog_lib}_entrez_nuccore_result.txt', f'{eggnog_lib}_entrez_output_nuccore.csv')
# parse_ncbi_batch_entrez_protein('COG3338_entrez_protein_result.txt', f'{eggnog_lib}_entrez_output_protein.csv')


# =============== EGGNOG EMAPPER =================

# > f'{eggnog_lib}.emapper.annotations.xlsx