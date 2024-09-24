import torch
import torch.nn as nn
from transformers.optimization import Adafactor
import argparse
import numpy as np
import os
import random
from compare_mt.rouge.rouge_scorer import RougeScorer
from transformers import T5ForConditionalGeneration,BartTokenizer, PegasusTokenizer,AutoTokenizer
from utils import Recorder
from data_utils import to_cuda, collate_mp_brio, BrioDataset
from torch.utils.data import DataLoader
import torch.distributed as dist
import torch.multiprocessing as mp
from functools import partial
from model import RankingLoss, BRIO
import logging
from label_smoothing_loss import label_smoothing_loss
from nltk import sent_tokenize, word_tokenize
from config import cnndm_setting, xsum_setting
from tqdm import tqdm

def base_setting(args):
    args.batch_size = getattr(args, 'batch_size', 1) # batch size on one gpu, one step
    args.epoch = getattr(args, 'epoch', 1) 
    args.report_freq = getattr(args, "report_freq", 100) # report frequency
    args.accumulate_step = getattr(args, "accumulate_step", 8) # accumulate gradients steps
    args.margin = getattr(args, "margin", 0.001) # margin for ranking loss on candidate summaries
    args.gold_margin = getattr(args, "gold_margin", 0) # margin for ranking loss on gold summaries
    args.gold_weight = getattr(args, "gold_weight", 0) # weight for ranking loss on gold summaries
    args.mle_weight = getattr(args, "mle_weight", 0.1) # weight for mle loss on gold summaries
    args.rank_weight = getattr(args, "rank_weight", 10) # weight for ranking loss on candidate summaries
    args.model_type = getattr(args, "model_type", "VietAI/vit5-base-vietnews-summarization") # model type
    # args.model_type = getattr(args, "model_type", "vinai/bartpho-word-base") # model type
    args.warmup_steps = getattr(args, "warmup_steps", 20000) # warmup steps
    args.normalize = getattr(args, "normalize", True) # normalize predicited likelihood
    args.grad_norm = getattr(args, "grad_norm", 0) # gradient norm
    args.seed = getattr(args, "seed", 970903) # random seed
    args.no_gold = getattr(args, "no_gold", False) # whether to use gold summaries
    args.pretrained = getattr(args, "pretrained", "./finetuned_model/vit5_2") # pretrained model path
    args.max_lr = getattr(args, "max_lr", 2e-3) # max learning rate (* 1e-2)
    args.scale = getattr(args, "scale", 0.5) # scale of ranking loss
    args.score_mode = getattr(args, "score_mode", "log") # use log-likelihood for ranking loss
    args.datatype = getattr(args, "datatype", "diverse") # data type
    args.dataset = getattr(args, "dataset", "ctu_vit_new_4") # dataset
    args.max_len = getattr(args, "max_len", 120) # max length of summary
    args.max_num = getattr(args, "max_num", 6) # max number of candidate summaries
    args.smooth = getattr(args, "smooth", 0.01) # label smoothing
    args.total_len = getattr(args, "total_len", 1024) # total length of source article
    args.length_penalty = getattr(args, "length_penalty", 2.0) # length penalty
    args.do_sample = getattr(args, "do_sample", True) # whether to generaet summaries during evaluation
    args.gen_max_len = getattr(args, "gen_max_len", 140) # max length of generated summaries
    args.gen_min_len = getattr(args, "gen_min_len", 55) # min length of generated summaries
    args.is_pegasus = getattr(args, "is_pegasus", False) # whether to use Pegasus as the baseline model
    args.adding = getattr(args, "adding", 0) # used for numerical stability
    args.eval_interval = getattr(args, "eval_interval", 1000) # evaluation intervals
    args.num_beams = getattr(args, "num_beams", 6) # number of beams for beam search

def evaluation(args):
    # load data
    if args.config == "cnndm":
        cnndm_setting(args)
    elif args.config == "xsum":
        xsum_setting(args)
    else:
        base_setting(args)
    if args.is_pegasus:
        tok = PegasusTokenizer.from_pretrained(args.model_type)
    else:
        tok = AutoTokenizer.from_pretrained(args.model_type)
    # build models
    model_path = args.pretrained
    
    model = BRIO(model_path, tok.pad_token_id, args.is_pegasus)
    # model= T5ForConditionalGeneration.from_pretrained(model_path)
    if args.cuda:
        model = model.cuda()

    model.load_state_dict(torch.load(os.path.join("./cache", args.model_pt), map_location=f'cuda:{args.gpuid[0]}'))
    device = f'cuda:{args.gpuid[0]}'
    model.eval()

    model_name = args.model_pt.split("/")[0]

    def mkdir(path):
        if not os.path.exists(path):
            os.mkdir(path)

    print(model_name)
    root_dir = "./result/%s"%model_name
    mkdir(root_dir)
    dumb_characters=['\u200b','. - .',' . - - - .','-','vov . vn',' . vn',' .','–']
    if args.do_generation:
        # evaluate the model as a generator
        tokenizer = tok
        model.generation_mode()
        # total_num = len(os.listdir(f"./{args.dataset}/{args.datatype}/test"))
        TEXT_TO_SUMMARIZE='trình_bày trong hội_thảo có giáo_viên , chuyên_gia_tài_chính - ngân_hàng người australia , ông dee ethapane ; chuyên_gia luyện thi ielts , ông jerry_lam ( giám_đốc đào_tạo tiếng anh của học_viện công_nghệ quốc_gia new zealand ) ._đáp_ứng nhu_cầu luyện thi ielts của các học_sinh , sinh_viên để có_thể học_tập và sinh_sống ở nước_ngoài , vnpc đang có những lớp luyện ielts cho những học_sinh chuẩn_bị đi du_học ._ngoài_ra , vnpc liên_tục khai_giảng những lớp mới giúp học_viên phát_triển toàn_diện kỹ_năng làm bài thi , làm_quen với cấu_trúc bài thi để : chuẩn_bị vững_vàng_tâm_lý khi làm bài ; có sách_lược phù_hợp cho các phần thi ; kiểm_soát và sử_dụng thời_gian làm bài hợp_lý nhất ; đạt tối_đa điểm_số ở các phần thi ._ngoài_ra , nhằm đáp_ứng nhu_cầu học tiếng anh chuyên_ngành , vnpc cũng khai_giảng các lớp_học tiếng anh chuyên_ngành thương_mại , tài_chính - ngân_hàng .'
        article=TEXT_TO_SUMMARIZE
        max_length=1024
        inputs = tokenizer([article], max_length=max_length, return_tensors="pt", truncation=True)
        summary_ids = model.generate(input_ids=inputs["input_ids"].to(device),
                        attention_mask=inputs["attention_mask"].to(device),
                        max_length=args.gen_max_len + 2,  # +2 from original because we start at step=1 and stop before max_length
                        min_length=args.gen_min_len + 1,  # +1 from original because we start at step=1
                        no_repeat_ngram_size=3,
                        num_beams=4,
                        length_penalty=args.length_penalty,
                        early_stopping=True)
        # summary_ids=model.generate(inputs["input_ids"].cuda())
        # decs = [tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]]
        dec = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids]
        # for dec in decs:
        #   for d in dumb_characters:
        #     dec=dec.replace(d,'')
        #   print(dec)
        print(dec)
        # dec2=[]
        # for dec in decs:
        #   for d in dumb_characters:
        #     dec=dec.replace(d,'')
        #   dec=dec.replace('  ',' ')
        #   dec2.append(dec)

        # print(dec2)
        # print(tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0])


if __name__ ==  "__main__":
    print("demo")
    parser = argparse.ArgumentParser(description='Parameters')
    parser.add_argument("--cuda", action="store_true", help="use cuda")
    parser.add_argument("--gpuid", nargs='+', type=int, default=0, help="gpu ids")
    parser.add_argument("-e", "--evaluate", action="store_true", help="evaluate model")
    parser.add_argument("-r", "--do_reranking", action="store_true", help="do reranking evaluation")
    parser.add_argument("-g", "--do_generation", action="store_true", help="do generation evaluation")
    parser.add_argument("-l", "--log", action="store_true", help="logging")
    parser.add_argument("-p", "--port", type=int, default=12355, help="port")
    parser.add_argument("--model_pt", default="", type=str, help="model path")
    parser.add_argument("--config", default="", type=str, help="config path")
    args = parser.parse_args()
    if args.evaluate:
            with torch.cuda.device(args.gpuid[0]):
                evaluation(args)