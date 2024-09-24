1. Using the `Finetuning_base_model` notebook for the finetuning Base Model.
3. Using brio_tokenized.py to produce .tokenized of .source and .target. Example:
```console
python brio_tokenize.py --fin ./train.source --fout ./train.source.tokenized
```
3. Using gen_candidate.py to produce .out file from .source file If you use base model to generate candidate summaries, uncomment the coresponding class of that model (not BRIO class) If you use BRIO to generate candidate summaries, uncomment the coresponding BRIO import, class and model.generation_mode() You can config the number of candidates inside by altering num_return_sequences=6, num_beam_groups=6, num_beams=6 ( all of them must have the same value) This process will take a lot of time so I recommend you to do it on Google colab. Example:
```console
python gen_candidate.py --gpuid 0 --src_dir ./train.source --tgt_dir ./train.out --dataset data 
```
4. Using brio_tokenizer.py to produce . tokenized of .out
After all those steps above, you should have 6 files each dataset (train.source, train.source.tokenized, train.target, train.target.tokenized, train.out, train.out.tokenized,...). Put all of them in the same folder.
5. Using preprocess.py to create a new dataset
Create a new folder inside the root folder, this is the name of the dataset. Example cnndm_bart and a new folder diverse inside.
```console
python preprocess.py --src_dir "path for the 18 .source, .target, .out files" --tgt_dir data/diverse --split train --cand_num 6 --dataset data -l
```

## Training Base Model with BRIO
Inside the `main.py`:
  - In the base_setting: 
    + Change `args.model_type` for the name of the base model.
    + Change `args.pretrained` for the path of the finetuned base model.
    + Change `args.dataset` for the name of the dataset
  - Uncomment the `from model...` accordingly to the current base model type.
  - Change all the Tokenizer accordingly to the current base model type.
