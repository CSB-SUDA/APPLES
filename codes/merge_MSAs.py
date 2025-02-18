#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

@ author: Yu Zhu

@ Email: yzhu99@stu.suda.edu.cn

@ Address: Center for Systems Biology, Department of Bioinformatics, School of Biology and Basic Medical Sciences, Soochow University, Suzhou 215123, China.

"""

### Introduction of merge_MSAs.py
#
# @ This part of program is delicated for merging MSAs by species.
# @ Two separate MSA files are required when running this sub-program.
#
# @ Python package in need: re, pandas
#
#############################################


import re
import pandas as pd


def parse_fasta(fasta_file_name):
    fasta_file = open(fasta_file_name, "r")
    label_list = []
    seq_list = []

    is_first_seq = True
    seq_i = ""
    for line in fasta_file:
        line = line.strip()
        if line == "":
            continue
        if line[0] == ">":
            label_list.append(line)
            if is_first_seq:
                is_first_seq = False
                seq_i = ""
            else:
                seq_list.append(seq_i)
                seq_i = ""
        else:
            seq_i += line
    seq_list.append(seq_i)
    fasta_file.close()

    label_list_list = []
    dict_fasta = dict()

    key_list_2 = ['OS', 'OX', 'GN', 'PE', 'SV']
    for index_i in range(len(label_list)):
        label_one = label_list[index_i]
        label_one_list = label_one[1:].split("|")
        temp_list = re.split(' OS=| OX=| GN=| PE=| SV=', label_one_list[2])
        match_items = re.findall(' OS=| OX=| GN=| PE=| SV=', label_one_list[2])
        match_items = [x[1:3] for x in match_items]
        if key_list_2 != match_items:
            dict_key_temp = dict()
            for key_i in key_list_2:
                dict_key_temp[key_i] = ''
            for i, key_i in enumerate(match_items, start=1):
                dict_key_temp[key_i] = temp_list[i]
            temp_list_use = list(dict_key_temp.values())
        else:
            temp_list_use = temp_list[1:]

        uniprotKB_proteinName_list = temp_list[0].split(" ")
        OX_GN = temp_list_use[1]+'_'+temp_list_use[2]
        OX_GN = OX_GN.upper()
        label_i_list = label_one_list[0:2] + [uniprotKB_proteinName_list[0]] + [" ".join(uniprotKB_proteinName_list[1:])] + temp_list_use + [OX_GN]
        label_list_list.append(label_i_list)
        dict_fasta[label_one_list[1]] = seq_list[index_i]
    
    return [dict_fasta, label_list_list]


def write_aligned_fasta(fasta_01, fasta_02):
    
    # >db|UniqueIdentifier|EntryName ProteinName OS=OrganismName OX=OrganismIdentifier [GN=GeneName ]PE=ProteinExistence SV=SequenceVersion
    # db is 'sp' for UniProtKB/Swiss-Prot and 'tr' for UniProtKB/TrEMBL.
    label_key_list = ['db', 'UniProtID', 'UniProtKB', 'proteinName', 'OS', 'OX', 'GN', 'PE', 'SV', 'OX_GN']
    
    fasta_01 = parse_fasta(fasta_01)
    fasta_02 = parse_fasta(fasta_02)
    
    df_label_01 = pd.DataFrame(list(fasta_01[1]), columns=label_key_list)
    df_label_02 = pd.DataFrame(list(fasta_02[1]), columns=label_key_list)
    
    col_use = 'OX'
    # drop duplicated ones with multiple OX (or OX_GN) values, and keep the first occurrence (sp is preferred: sorted by db)
    df_label_01.sort_values(by=['db','OX'], ascending=[True, False], inplace = True)
    df_label_01.drop_duplicates(col_use, inplace = True)
    df_label_02.sort_values(by=['db','OX'], ascending=[True, False], inplace = True)
    df_label_02.drop_duplicates(col_use, inplace = True)
    
    # drop rows with empty GN values
    df_label_01 = df_label_01[df_label_01['GN'] != '']
    df_label_02 = df_label_02[df_label_02['GN'] != '']
    
    OX_01_list = df_label_01[col_use].to_list()
    OX_02_list = df_label_02[col_use].to_list()
    
    label_01_02 = list(set(OX_01_list) & set(OX_02_list))
        
    df_label_01_02 = df_label_01.loc[df_label_01["OX"].isin(label_01_02)]
    df_label_01_02_sort = df_label_01_02.sort_values("OX")
    df_label_02_01 = df_label_02.loc[df_label_02["OX"].isin(label_01_02)]
    df_label_02_01_sort = df_label_02_01.sort_values("OX")
    
    fasta_file = open("../APPLES_OUT/01_02_blast.fasta", "w")
    for index, row_i in df_label_01_02_sort.iterrows():
        fasta_file.write(">" + row_i["OX"] + "\n")
        fasta_file.write(fasta_01[0][row_i["UniProtID"]] + "\n")
    fasta_file.close()
    
    fasta_file = open("../APPLES_OUT/02_01_blast.fasta", "w")
    for index, row_i in df_label_02_01_sort.iterrows():
        fasta_file.write(">" + row_i["OX"] + "\n")
        fasta_file.write(fasta_02[0][row_i["UniProtID"]] + "\n")
    fasta_file.close()

  