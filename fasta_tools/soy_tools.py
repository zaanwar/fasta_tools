from fasta_writers import *
from fasta_readers import *
import os


def parse_header_tuple(header):
    '''
    parses a soybase header into a tuple, not currently handling the reference
    for soy base headers
    '''
    return tuple(header.split(' '))

def parse_header_dict(header, delim=' ', delim_key_value='='):
    '''
    parses soybase header as a dictionary with the pre = strings of the header
    as the keys and post = as the values
    '''
    keys, values = [], []
    reference_info = ''
    split_header = header.split(delim)
    for item in split_header:
        e_split = item.split(delim_key_value)
        if len(e_split) == 2:
            keys.append(e_split[0])
            values.append(e_split[1])
        else:
            reference_info += ' ' + item

    dictionary = dict(zip(keys, values))
    dictionary['Reference'] += reference_info

    return dictionary

def identify_LTR(header):
    '''
    Takes in the header of a soybase element and returns true if of an LTR family
    and false otherwise by looking if intact. This is important for the
    transposer pipeline.
    '''
    dict = parse_header_dict(header)
    if dict['Order'] == 'LTR':
        return True
    else:
        return False

def seperate_solos(single_element_fasta, write_path='', file_ext='.fna'):
    '''
    Creates two fasta files one containing intact elements and another containing solo
    elements from a fasta file of a single family of elements but containg both solo and
    intacts. Important for creating consensus sequences to feed to transposer. New files are named
    as family name_status.fna and file names are returned as a tuple
    '''
    pass
    tuples = read_as_tuples(single_element_fasta)
    solos, intacts = [], []
    ind = ('SOLO', 'INTACT')

    for element in tuples:
        header, seq = element
        temp_dict = parse_header_dict(single_element_fasta)
        description = temp_dict['Status']

        if description == 'SOLO':
            solos.append(element)
        elif description == 'INTACT':
            intacts.append(element)


def split_fasta_writer(element_dict, file_name_editor=False, file_ext='.fna'):
    '''
    Writes a fasta file containing only elements of a specific family as specified through
    the data structure created by the fasta_splitter method. It is not recommended to use
    this method on its own and should only be called by fasta_splitter
    '''
    file_name = ''

    for super_family in element_dict:
        try:
            os.mkdir(super_family)
            file_structure[super_family] = []
        except FileExistsError:
            print('Dir exists')

        for family in element_dict[super_family]: # access a given super family
            if file_name_editor is not False:  # apply file editing function if provided
                file_name = file_name_editor(family)
            else:
                file_name = os.path.join(super_family, family + '.fna')

            write_from_tuple_list(element_dict[super_family][family], file_name)


def fasta_splitter(big_fasta_file, dir_key = 'Super_Family', soy_key='Family', file_name_editor=False, file_ext='.fna'):
    '''
    Method that splits a large fasta file containing many different types of elements into
    many fasta files each with one type of element. Splitting is done based on content of the header and so
    each element should have a unique identifier at an index when split by some delimiter (default = ' ')
    To rename a file you can also pass a function that alters a the string at the file_namer_index if that string alone
    is not enough. Defualt file extension for renaming is .fna
    '''
    fasta_tuples = read_as_tuples(big_fasta_file)
    element_dict = {}
    file_names = []
    
    for header, seq in fasta_tuples:
        temp_dict = parse_header_dict(header)
        super_family = temp_dict[dir_key]
        family = temp_dict[soy_key].replace('/', '_')


        if super_family not in element_dict:
            element_dict[super_family] = {family:[(header, seq)]}
            if 'U' in element_dict[super_family]:
                print(super_family)
                print('Found it')
                print(type(family))
        else:
            family_dict = element_dict[super_family]
            if family not in family_dict:
                element_dict[super_family][family] = [(header, seq)]
            else:
                element_dict[super_family][family].append((header, seq))

    split_fasta_writer(element_dict, file_name_editor, file_ext)