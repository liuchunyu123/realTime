import argparse
import codecs

def load_data(file_path):
    with codecs.open(file_path,'r','utf-8') as f:
        contents = f.readlines()
    return contents

def main(file_path):
    content = load_data(file_path)
    for index,sentence in enumerate(content):
        if sentence.strip().replace("\t",'').startswith("INTENT - PROB"):
            index+=1
            break
    intent_prob_lines=[]
    while index< len(content):
        line  = content[index].strip().replace('\t','').replace('\n','').replace(' ','')
        if line:
            num = line.split('-')[1].split(',')[0]

            print(num)
            intent_prob_lines.append(float(num))
        index+=1
    print("total num:"+str(len(intent_prob_lines)))
    print("avg precision:"+str(sum(intent_prob_lines)/len(intent_prob_lines)))





if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('--f','-f')
    args = parse.parse_args()
    main(args.f)