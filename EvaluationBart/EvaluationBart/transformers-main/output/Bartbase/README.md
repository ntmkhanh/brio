---
license: mit
tags:
- generated_from_trainer
datasets:
- cnn_dailymail
metrics:
- rouge
model-index:
- name: Bartbase
  results:
  - task:
      name: Summarization
      type: summarization
    dataset:
      name: cnn_dailymail 3.0.0
      type: cnn_dailymail
      args: 3.0.0
    metrics:
    - name: Rouge1
      type: rouge
      value: 34.4679
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# Bartbase

This model is a fine-tuned version of [facebook/bart-large-cnn](https://huggingface.co/facebook/bart-large-cnn) on the cnn_dailymail 3.0.0 dataset.
It achieves the following results on the evaluation set:
- Loss: 2.1351
- Rouge1: 34.4679
- Rouge2: 13.5545
- Rougel: 23.3439
- Rougelsum: 31.8783
- Gen Len: 79.2387

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 5e-05
- train_batch_size: 1
- eval_batch_size: 1
- seed: 42
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: linear
- num_epochs: 2.0

### Training results



### Framework versions

- Transformers 4.23.0.dev0
- Pytorch 1.12.1+cu113
- Datasets 2.4.0
- Tokenizers 0.12.1
