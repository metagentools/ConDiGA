import csv
import glob
import os
import subprocess
import gzip
import shutil
import logging

from datetime import datetime

# create logger
logger = logging.getLogger("condiga 0.1")

def download_genomes(taxid_list, assembly_summary, output):

    if not os.path.isdir(f"{output}/Assemblies/"):
        subprocess.run(f"mkdir -p {output}/Assemblies/", shell=True)
    else:
        subprocess.run(f"rm -rf {output}/Assemblies/", shell=True)
        subprocess.run(f"mkdir -p {output}/Assemblies/", shell=True)

    taxid_dates = {}
    taxid_urls = {}
    taxid_file_path = {}
    taxid_assembly_level = {}
    taxid_present = {}

    for taxid in taxid_list:
        taxid_urls[taxid] = ""
        taxid_file_path[taxid] = ""
        taxid_present[taxid] = False

    with open(assembly_summary) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        line_count = 0
        
        for row in csv_reader:
            
            if not row[0].startswith("#"):
                
                if row[5] in taxid_list:
                    
                    name = row[0]
                    taxid = row[5]
                    version_status = row[10]
                    assembly_level = row[11]
                    genome_rep = row[13]
                    rel_date = row[14].split("/")
                    url = row[19]
                    
                    myurl = url+"/"+url.split("/")[-1]+"_genomic.fna.gz"
                                
                    local_file = url.split("/")[-1]+"_genomic.fna.gz"

                    myfile_name = output+"/Assemblies/"+url.split("/")[-1]+"_genomic.fna"
                    
                    if version_status == "latest" and genome_rep == "Full":
                    
                        if taxid not in taxid_dates:

                            if assembly_level in ["Complete Genome", "Contig", "Chromosome"]:
                                logger.info(f"Downloading from {myurl}")
                                command = "rsync --copy-links --times --verbose "+myurl.replace("ftp:", "rsync:")+" "+output+"/Assemblies/"
                                subprocess.run(command, shell=True)

                                if os.path.exists(output+"/Assemblies/"+local_file):

                                    try:

                                        with gzip.open(output+"/Assemblies/"+local_file, 'rb') as f_in:
                                            with open(myfile_name, 'wb') as f_out:
                                                shutil.copyfileobj(f_in, f_out)

                                        subprocess.run("rm -f "+output+"/Assemblies/"+local_file, shell=True)

                                        taxid_dates[taxid] = rel_date
                                        taxid_urls[taxid] = url
                                        taxid_file_path[taxid] = myfile_name
                                        taxid_assembly_level[taxid] = assembly_level
                                        taxid_present[taxid] = True

                                    except:

                                        if os.path.exists(output+"/Assemblies/"+local_file):
                                            subprocess.run("rm -f "+output+"/Assemblies/"+local_file, shell=True)


                        else:
                            present = datetime.now()

                            old_diff = present - datetime(int(taxid_dates[taxid][0]), int(taxid_dates[taxid][1]), int(taxid_dates[taxid][2]))
                            new_diff = present - datetime(int(rel_date[0]), int(rel_date[1]), int(rel_date[2]))

                            if old_diff > new_diff:

                                if not ((assembly_level!="Complete Genome" and taxid_assembly_level[taxid]=="Complete Genome") or (assembly_level=="Contig" and taxid_assembly_level[taxid]=="Chromosome")):

                                    if not os.path.exists(output+"/Assemblies/"+local_file):
                                        logger.info(f"Downloading from {myurl}")
                                        command = "rsync --copy-links --times --verbose "+myurl.replace("ftp:", "rsync:")+" "+output+"/Assemblies/"
                                        subprocess.run(command, shell=True)

                                        if os.path.exists(output+"/Assemblies/"+local_file):

                                            try:

                                                with gzip.open(output+"/Assemblies/"+local_file, 'rb') as f_in:
                                                    with open(myfile_name, 'wb') as f_out:
                                                        shutil.copyfileobj(f_in, f_out)

                                                if taxid_file_path[taxid] != "":
                                                    if os.path.exists(taxid_file_path[taxid]):
                                                        subprocess.run("rm -f "+taxid_file_path[taxid], shell=True)

                                                subprocess.run("rm -f "+output+"/Assemblies/"+local_file, shell=True)

                                                taxid_dates[taxid] = rel_date
                                                taxid_urls[taxid] = url
                                                taxid_file_path[taxid] = myfile_name
                                                taxid_assembly_level[taxid] = assembly_level
                                                taxid_present[taxid] = True

                                            except:

                                                if os.path.exists(output+"/Assemblies/"+local_file):
                                                    subprocess.run("rm -f "+output+"/Assemblies/"+local_file, shell=True)

    return taxid_dates, taxid_urls, taxid_file_path, taxid_assembly_level, taxid_present        


def get_ref_lengths(taxid_present, taxid_file_path):

    taxid_file_len = {}

    for taxid in taxid_present:
        
        command = 'grep -v ">" '+taxid_file_path[taxid]+' | wc | awk \'{print $3-$1}\''
        n = subprocess.check_output(command, shell=True)

        taxid_file_len[taxid] = int(n.decode("utf-8").strip())

    return taxid_file_len


def rename_and_copy_genomes(taxid_file_path, species_names_taxid_length, species_genome_coverages, species_rel_abundance, rel_abundance, genome_coverage, output):
    
    if not os.path.isdir(f"{output}/Reference_Sequences/"):
        subprocess.run(f"mkdir -p {output}/Reference_Sequences/", shell=True)
    else:
        subprocess.run(f"rm -rf {output}/Reference_Sequences/*", shell=True)

    with open(output+"species_stats.tsv", "w") as myfile:
    
        myfile.write("Species name\tRelative abundance\tGenome coverage\n")
        
        for species in species_rel_abundance:

            if species_rel_abundance[species] > rel_abundance and species_genome_coverages[species] > genome_coverage:
                
                myfile.write(species+"\t"+str(species_rel_abundance[species])+"\t"+str(species_genome_coverages[species])+"\n")

                for taxid in species_names_taxid_length[species]:
                    subprocess.run("cp "+taxid_file_path[taxid]+" "+output+"/Reference_Sequences/"+taxid+".fna", shell=True)


def get_ref_ids(output):

    reference_files = glob.glob(output+'/Reference_Sequences/*.fna')

    ref_ids = {}

    for ref in reference_files:
        ref_name = ref.split("/")[-1][:-4]
        command = 'grep "^>" ' + ref
        pp = subprocess.check_output(command)
        
        for item in pp:
            myid = item.split(" ")[0][1:]
            
            if ref_name not in ref_ids:
                ref_ids[ref_name] = [myid]
            else:
                ref_ids[ref_name].append(myid)

    return ref_ids
