import gzip
import glob
import collections
import os
import re
import sys


def revCompIterative(watson):  # Gets Reverse Complement
    complements = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N',
                   'R': 'Y', 'Y': 'R', 'S': 'S', 'W': 'W', 'K': 'M',
                   'M': 'K', 'V': 'B', 'B': 'V', 'H': 'D', 'D': 'H'}
    watson = watson.upper()
    watsonrev = watson[::-1]
    crick = ""
    for nt in watsonrev:
        try:
            crick += complements[nt]
        except KeyError:
            crick += nt  # Do not modify non-standard DNA
    return crick

gencode = {
      'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
      'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
      'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
      'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
      'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
      'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
      'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
      'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
      'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
      'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
      'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
      'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
      'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
      'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
      'TAC':'Y', 'TAT':'Y', 'TAA':'', 'TAG':'*',  ##Stop stars removed
      'TGC':'C', 'TGT':'C', 'TGA':'', 'TGG':'W'}

def check_For_Stops(aa_seq): #Check if frame has stops (*) and if they cut the seq down too far
    stops = []
    stops += [match.start() for match in re.finditer(re.escape('*'), aa_seq)]
    for stop in stops:
        if stop > 5 and stop < 70: # not finished
            return None
    return aa_seq

def translate_frame(sequence):
    translate = ''.join([gencode.get(sequence[3 * i:3 * i + 3], 'X') for i in range(len(sequence) // 3)])
    return translate

#combined_out = open('./Extended_CoDing_Sequences_For_Training.faa','w')#, newline='\n', encoding='utf-8')


def fasta_load(sequences,fasta_in):
    first = True
    for line in fasta_in:
        line = line.strip()
        if line.startswith(';'):
            continue
        elif line.startswith('>') and not first:
            sequences.update({sequence_name: seq})
            seq = ''
            sequence_name = line.split()[0]
        elif line.startswith('>'):
            seq = ''
            sequence_name = line.split()[0]
        else:
            seq += str(line)
            first = False
    sequences.update({sequence_name: seq})
    return sequences


sequences = collections.OrderedDict()
aa_sequences = collections.OrderedDict()
out = open('./Extended_CoDing_Sequences_For_Training_Biggest_tmp.faa','w')

count = 0
current_counter = 0
seq_counter = 0

seen_aa = collections.defaultdict()
seen_aa_genera = collections.defaultdict(int)

genera_seen = collections.defaultdict(list)

def get_Genus(clustered):
    clustered_genus = clustered.split('|')[0]
    if '_' in clustered_genus[0]:  # Remove name error
        clustered_genus = clustered_genus.split('_')[1]
    else:
        clustered_genus = clustered_genus.split('_')[0]
    return str(clustered_genus).capitalize()



for gff_file in glob.glob('/home/nick/Nextcloud/Ensem/CDS/*.fa.gz'):
    current_genus = get_Genus(gff_file.split('/')[6])
    #if current_genus not in genera_seen:
    #if "Xylella" in current_taxa:
    size = os.path.getsize(gff_file)
    genera_seen[current_genus].append([gff_file,size])

number_of_CDSs = 0

for genera, data in genera_seen.items():
    size = 0
    genome = ""
    for genus in data:
        if genus[1] > size:
            size = genus[1]
            genome = genus[0]



    print(genome)
    genus = get_Genus(genome.split('/')[6])
    fasta_in = gzip.open(genome, 'rt')
    sequences = fasta_load(sequences,fasta_in)
    number_of_CDSs += len(sequences)
    for seq_name, seq in sequences.items():
        seq_name = seq_name.replace('>','')
        rev_seq = revCompIterative(seq)
        #rev_seq = rev_seq[::-1] # maybe?

        aa_seq = translate_frame(seq)
        aa_seq = aa_seq[1:]
        if aa_seq not in seen_aa:
            seen_aa[aa_seq] = None

            #aa_sequences.update({seq_name+'_0': aa_seq})
            out.write('>'+genus+'_'+seq_name+'_'+str(seq_counter)+','+str(count)+',1\n'+aa_seq+'\n')
            seq_counter +=1

        tmp_seq = seq[1:]
        aa_seq = translate_frame(tmp_seq)
        aa_seq = aa_seq[1:]
        if aa_seq not in seen_aa:
            seen_aa[aa_seq] = None

            #aa_sequences.update({seq_name+'_1': aa_seq})
            out.write('>'+genus+'_'+seq_name+'_'+str(seq_counter)+','+str(count) + ',0\n' + aa_seq+'\n')
            seq_counter +=1

        tmp_seq = tmp_seq[1:]
        aa_seq = translate_frame(tmp_seq)
        aa_seq = aa_seq[1:]
        if aa_seq not in seen_aa:
            seen_aa[aa_seq] = None

            #aa_sequences.update({seq_name+'_2': aa_seq})
            out.write('>'+genus+'_'+seq_name+'_'+str(seq_counter)+','+str(count) + ',0\n' + aa_seq+'\n')
            seq_counter +=1
####################################################GGaaaaaaaatttatatat
        aa_seq = translate_frame(rev_seq)
        aa_seq = aa_seq[1:]
        if aa_seq not in seen_aa:
            seen_aa[aa_seq] = None
            #seen_aa_taxa[current_taxa] += 1
            out.write('>'+genus+'_'+seq_name+'_'+str(seq_counter)+','+str(count) + ',0\n' + aa_seq+'\n')
            seq_counter +=1
            #aa_sequences.update({seq_name+'_3': aa_seq})

        tmp_rev_seq = rev_seq[1:]
        aa_seq = translate_frame(tmp_rev_seq)
        aa_seq = aa_seq[1:]
        if aa_seq not in seen_aa:
            seen_aa[aa_seq] = None

            out.write('>'+genus+'_'+seq_name+'_'+str(seq_counter)+','+str(count) + ',0\n' + aa_seq+'\n')
            seq_counter +=1
            #aa_sequences.update({seq_name+'_4': aa_seq})

        tmp_rev_seq = tmp_rev_seq[1:]
        aa_seq = translate_frame(tmp_rev_seq)
        aa_seq = aa_seq[1:]
        if aa_seq not in seen_aa:
            seen_aa[aa_seq] = None

            out.write('>'+genus+'_'+seq_name+'_'+str(seq_counter)+','+str(count) + ',0\n' + aa_seq+'\n')
            seq_counter +=1
            #aa_sequences.update({seq_name+'_5': aa_seq})

        #print("W")
        count +=1
    current_counter += 1
    #print(current_counter)
    # if current_counter > 99:
    #     sys.exit()
    #break
print(number_of_CDSs)
print(len(seen_aa))



    # dna_regions.update({dna_region_id: (seq, dna_region_length, list(), None)})
    # for line in genome:
    #     if line.startswith(b'#'):
    #         continue
    #     elif line.startswith(b'>'): # Might need to change file[?]
    #
    # with gzip.open(file,'rb') as genome:
    #
    #     print(file)
    #     for line in genome:
    #         if line.startswith(b'#'):
    #             continue
    #         elif line.startswith(b'>'): # Might need to change file[?]
    #             genome = bytes(file.split('/')[3].split('.dna.toplevel.fa_UR.fasta.gz_aa.fasta.gz')[0],'utf-8')
    #             #genome = bytes(file.split('/')[2].split('.dna.toplevel.fa_.fasta.gz_aa.fasta.gz')[0], 'utf-8')
    #             genome = genome.capitalize()
    #             line = line.replace(b'>',b'>'+genome+b'|')
    #             combined_out.write(line)
    #         else:
    #             combined_out.write(line)