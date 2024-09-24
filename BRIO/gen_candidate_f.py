from transformers import MBartForConditionalGeneration,AutoTokenizer, T5ForConditionalGeneration, BartTokenizer, PegasusTokenizer, PegasusForConditionalGeneration,AutoTokenizer
import torch
import sys
import os
import argparse
from typing import List
from model import RankingLoss, BRIO
# from model_pho import RankingLoss, BRIO
# from modelT5 import RankingLoss, BRIO
def generate_summaries_cnndm(args):
    device = f"cuda:{args.gpuid}"
    mname = "vinai/bartpho-word-base"
    finetuned_model="/content/drive/MyDrive/LuanVan/Bart-BRIO/brio_project-main/BRIO/finetuned_model_final/eval_bartpho"
    tokenizer = AutoTokenizer.from_pretrained(finetuned_model) #For Bartpho and T5 model, User BartTokenizer for plain old Bart model
    # model = BRIO("./finetuned_model/bartpho2", tokenizer.pad_token_id, False) #For BRIO models from finetuned base model
    model = MBartForConditionalGeneration.from_pretrained(finetuned_model).to(device) #For Bartpho base model
    # model = T5ForConditionalGeneration.from_pretrained(mname).to(device) #For T5 base model
    # model.load_state_dict(torch.load(os.path.join("./cache", "22-11-09-297/model_generation.bin"), map_location=f'cuda:{args.gpuid[0]}')) #Uncomment this line when you already trained a BRIO model
    model=model.cuda()
    model.eval()
    # model.generation_mode()
    max_length = 140
    min_length = 55
    count = 1
    bsz = 8
    dumb_characters=['\u200b','. - .',' . - - - .','-','vov . vn',' . vn',' .']
    with open(args.src_dir,encoding="utf-8") as source, open(args.tgt_dir, 'w') as fout:
        sline = source.readline().strip().lower()
        slines = [sline]
        for sline in source:
            print(count)
            if count % 100 == 0:
                print(count, flush=True)
            if count % bsz == 0:
                with torch.no_grad():
                    dct = tokenizer.batch_encode_plus(slines, max_length=1024, return_tensors="pt", pad_to_max_length=True, truncation=True)
                    summaries = model.generate(
                        input_ids=dct["input_ids"].cuda(),
                        attention_mask=dct["attention_mask"].cuda(),
                        num_return_sequences=6, num_beam_groups=6, diversity_penalty=1.0, num_beams=6,
                        max_length=max_length + 2,  # +2 from original because we start at step=1 and stop before max_length
                        min_length=min_length + 1,  # +1 from original because we start at step=1
                        no_repeat_ngram_size=3,
                        length_penalty=2.0,
                        early_stopping=True,
                    )
                    dec1 = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summaries]
                    dec2=[]
                    for dec in dec1:
                        for d in dumb_characters:
                            dec=dec.replace(d,'')
                        dec=dec.replace('  ',' ')
                        dec2.append(dec)
                for hypothesis in dec2:
                    hypothesis = hypothesis.replace("\n", " ")
                    fout.write(hypothesis + '\n')
                    fout.flush()
                slines = []
            sline = sline.strip().lower()
            if len(sline) == 0:
                sline = " "
            slines.append(sline)
            count += 1
        if slines != []:
            with torch.no_grad():
                dct = tokenizer.batch_encode_plus(slines, max_length=1024, return_tensors="pt", pad_to_max_length=True, truncation=True)
                summaries = model.generate(
                    input_ids=dct["input_ids"].cuda(),
                    attention_mask=dct["attention_mask"].cuda(),
                    num_return_sequences=6, num_beam_groups=6, diversity_penalty=1.0, num_beams=6,
                    max_length=max_length + 2,  # +2 from original because we start at step=1 and stop before max_length
                    min_length=min_length + 1,  # +1 from original because we start at step=1
                    no_repeat_ngram_size=3,
                    length_penalty=2.0,
                    early_stopping=True,
                )
                dec1 = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summaries]
                dec2=[]
                for dec in dec1:
                    for d in dumb_characters:
                        dec=dec.replace(d,'')
                    dec=dec.replace('  ',' ')
                    dec2.append(dec)
            for hypothesis in dec2:
                    hypothesis = hypothesis.replace("\n", " ")
                    fout.write(hypothesis + '\n')
                    fout.flush()


def generate_summaries_xsum(args):
    device = f"cuda:{args.gpuid}"
    mname = "google/pegasus-xsum"
    model = PegasusForConditionalGeneration.from_pretrained(mname).to(device)
    model.eval()
    tok = PegasusTokenizer.from_pretrained(mname)
    count = 1
    bsz = 2
    with open(args.src_dir) as source, open(args.tgt_dir, 'w') as fout:
        sline = source.readline().strip()
        slines = [sline]
        for (i, sline) in enumerate(source):
            if count % 10 == 0:
                print(count)
            if count % bsz == 0:
                with torch.no_grad():
                    batch = tok.prepare_seq2seq_batch(src_texts=slines, return_tensors="pt").to(device)
                    gen = model.generate(**batch, num_return_sequences=128, num_beam_groups=16, diversity_penalty=0.1, num_beams=128, length_penalty=0.6)
                    dec: List[str] = tok.batch_decode(gen, skip_special_tokens=True)
                dec = [dec[i] for i in range(len(dec)) if i % 8 == 0]
                for hypothesis in dec:
                    fout.write(hypothesis + '\n')
                    fout.flush()
                slines = []
            sline = sline.strip()
            if len(sline) == 0:
                sline = " "
            slines.append(sline)
            count += 1
        if slines != []:
            with torch.no_grad():
                batch = tok.prepare_seq2seq_batch(src_texts=slines, return_tensors="pt").to(device)
                gen = model.generate(**batch, num_return_sequences=128, num_beam_groups=16, diversity_penalty=0.1, num_beams=128, length_penalty=0.6)
                dec: List[str] = tok.batch_decode(gen, skip_special_tokens=True)
            dec = [dec[i] for i in range(len(dec)) if i % 8 == 0]
            for hypothesis in dec:
                    fout.write(hypothesis + '\n')
                    fout.flush()


if __name__ ==  "__main__":
    parser = argparse.ArgumentParser(description='Parameters')
    parser.add_argument("--gpuid",nargs='+', type=int, default=0, help="gpu id")
    parser.add_argument("--src_dir", type=str, help="source file")
    parser.add_argument("--tgt_dir", type=str, help="target file")
    parser.add_argument("--dataset", type=str, default="cnndm", help="dataset")
    args = parser.parse_args()
    if args.dataset == "cnndm":
        generate_summaries_cnndm(args)
    
